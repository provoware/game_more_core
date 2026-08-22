from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.application.economy_service import EconomyService
from bunkerfrequenz.application.event_execution_service import EventExecutionService
from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.incident_service import IncidentService
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_COMMAND_FIELDS: dict[str, frozenset[str]] = {
    "profile.update": frozenset({"type", "command_id", "changes"}),
    "event.create": frozenset({"type", "command_id", "event"}),
    "event.update_planning": frozenset({"type", "command_id", "changes"}),
    "event.execute": frozenset({"type", "command_id", "action_id"}),
    "economy.initialize": frozenset({"type", "command_id", "economy"}),
    "economy.transact": frozenset({"type", "command_id", "kind", "item_id", "quantity"}),
    "incident.open": frozenset({"type", "command_id", "incident_type", "severity"}),
    "incident.resolve": frozenset({"type", "command_id", "response_id"}),
    "settlement.complete": frozenset({"type", "command_id"}),
}
_COMMAND_TYPES = frozenset(_COMMAND_FIELDS)
_PROFILE_COMMANDS = frozenset({"profile.update"})


@dataclass(frozen=True, slots=True)
class GameClientCommandResult:
    status: str
    confirmed_state: dict[str, Any] | None
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool
    error_code: str | None
    error_detail: str | None = None


class GameClientSession:
    """Thin write adapter for the local A4 client.

    It owns no gameplay rules. Persistent commands are delegated to the
    canonical Profile/Event/Economy/Incident/Settlement application services.
    """

    def __init__(
        self,
        persistence: PersistenceKernel,
        *,
        incident_catalog: dict[str, dict[str, Any]],
        incident_contract_version: str,
    ) -> None:
        if not incident_catalog:
            raise ValueError("incident_catalog darf nicht leer sein")
        if not isinstance(incident_contract_version, str) or not incident_contract_version.strip():
            raise ValueError("incident_contract_version fehlt")
        self.persistence = persistence
        self.profile = CharacterProfileService(persistence)
        self.event_state = EventStateService(persistence)
        self.event_execution = EventExecutionService(self.event_state)
        self.economy = EconomyService(persistence)
        self.incidents = IncidentService(
            persistence,
            deepcopy(incident_catalog),
            contract_version=incident_contract_version,
        )
        self.settlement = SettlementService(persistence)

    def read_state(self) -> dict[str, Any]:
        """Return a defensive copy of the confirmed save state."""
        return deepcopy(self.persistence.load_state() or {})

    def bootstrap_character(self, character: CharacterState) -> dict[str, Any]:
        """Create the immutable GENESIS character for a fresh local save.

        Character creation has no canonical journal event yet. Therefore the
        first-run shell may only seed the GENESIS checkpoint before any journal
        record exists. It never mutates an already active save.
        """
        character.validate()
        current = self.persistence.load_state()
        if current is None:
            if self.persistence.last_sequence != 0:
                raise PersistenceError("GENESIS-Character fehlt trotz bestehendem Journal")
            self.persistence.initialize_state({"character": character.to_dict()})
            return self.read_state()

        existing = current.get("character")
        if existing is None:
            raise PersistenceError("Bestehender Save besitzt keinen GENESIS-Character")
        confirmed = CharacterState.from_dict(existing)
        if confirmed.to_dict() != character.to_dict():
            raise PersistenceError("Bestehender Save gehört zu einem anderen Character")
        return self.read_state()

    def create_checkpoint(self, reason: str = "a4_manual_checkpoint") -> str:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Checkpoint-Grund fehlt")
        return self.persistence.create_snapshot(reason.strip())

    def dispatch(
        self,
        command: Mapping[str, Any],
        *,
        context: JournalContext,
    ) -> GameClientCommandResult:
        """Validate the client envelope and delegate one command to canonical services."""
        command_type = command.get("type")
        if not isinstance(command_type, str) or command_type not in _COMMAND_TYPES:
            return self._rejected("unknown_command")
        unknown_fields = set(command) - _COMMAND_FIELDS[command_type]
        if unknown_fields:
            return self._rejected(
                "unexpected_command_fields",
                ", ".join(sorted(str(field) for field in unknown_fields)),
            )

        command_id = command.get("command_id")
        if not isinstance(command_id, str) or not command_id.strip():
            return self._rejected("invalid_command_id")
        command_id = command_id.strip()
        if context.command_id != command_id:
            return self._rejected("command_context_mismatch")

        try:
            if command_type in _PROFILE_COMMANDS:
                return self._dispatch_profile(command, command_id=command_id, context=context)

            if context.entity_type != "event" or not context.entity_id:
                return self._rejected("invalid_event_context")

            if command_type == "event.create":
                raw = command.get("event")
                if not isinstance(raw, dict):
                    return self._rejected("invalid_event")
                event = EventState.from_dict(raw)
                if event.event_id != context.entity_id:
                    return self._rejected("event_context_mismatch")
                result = self.event_state.create(event, context=context)
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "economy.initialize":
                raw = command.get("economy")
                if not isinstance(raw, dict):
                    return self._rejected("invalid_economy")
                result = self.economy.initialize(EconomyState.from_dict(raw), context=context)
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            event = self._confirmed_event()
            if event.event_id != context.entity_id:
                return self._rejected("event_context_mismatch")

            if command_type == "event.update_planning":
                changes = command.get("changes")
                if not isinstance(changes, dict) or not changes:
                    return self._rejected("invalid_planning_changes")
                result = self.event_state.update_planning(event, deepcopy(changes), context=context)
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "event.execute":
                action_id = command.get("action_id")
                if not isinstance(action_id, str) or not action_id.strip():
                    return self._rejected("invalid_action_id")
                result = self.event_execution.execute(event, action_id.strip(), context=context)
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "economy.transact":
                kind = command.get("kind")
                item_id = command.get("item_id")
                quantity = command.get("quantity")
                if not isinstance(kind, str) or not kind.strip():
                    return self._rejected("invalid_economy_kind")
                if not isinstance(item_id, str) or not item_id.strip():
                    return self._rejected("invalid_item_id")
                if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
                    return self._rejected("invalid_quantity")
                result = self.economy.transact(
                    kind.strip(),
                    item_id.strip(),
                    quantity,
                    context=context,
                )
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "incident.open":
                incident_type = command.get("incident_type")
                severity = command.get("severity")
                if not isinstance(incident_type, str) or not incident_type.strip():
                    return self._rejected("invalid_incident_type")
                if severity is not None and (
                    isinstance(severity, bool) or not isinstance(severity, int)
                ):
                    return self._rejected("invalid_severity")
                result = self.incidents.open(
                    incident_type.strip(),
                    context=context,
                    severity=severity,
                )
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "incident.resolve":
                response_id = command.get("response_id")
                if not isinstance(response_id, str) or not response_id.strip():
                    return self._rejected("invalid_response_id")
                result = self.incidents.resolve(response_id.strip(), context=context)
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            result = self.settlement.complete(context=context)
            return self._confirmed(result.committed_event_ids, result.idempotent_replay)
        except PersistenceError as exc:
            return self._rejected("persistence_error", str(exc))
        except (ValueError, KeyError, TypeError) as exc:
            return self._rejected("validation_error", str(exc))
        except RuntimeError as exc:
            return self._rejected("runtime_error", str(exc))

    def _dispatch_profile(
        self,
        command: Mapping[str, Any],
        *,
        command_id: str,
        context: JournalContext,
    ) -> GameClientCommandResult:
        if context.entity_type != "character" or not context.entity_id:
            return self._rejected("invalid_character_context")
        raw_character = self.read_state().get("character")
        if not isinstance(raw_character, dict):
            return self._rejected("character_missing")
        character = CharacterState.from_dict(raw_character)
        if character.character_id != context.entity_id:
            return self._rejected("character_context_mismatch")
        changes = command.get("changes")
        if not isinstance(changes, dict) or not changes:
            return self._rejected("invalid_profile_changes")

        event_id = f"{command_id}:profile"
        if self.persistence.has_event(event_id):
            return self._confirmed((), True)
        self.profile.update(
            character,
            deepcopy(changes),
            event_id=event_id,
            transaction_id=f"tx:{command_id}:profile",
            context=context,
        )
        return self._confirmed((event_id,), False)

    def _confirmed_event(self) -> EventState:
        state = self.persistence.load_state() or {}
        raw = state.get("event")
        if not isinstance(raw, dict):
            raise PersistenceError("Kein bestätigter Eventzustand vorhanden")
        return EventState.from_dict(raw)

    def _confirmed(
        self,
        committed_event_ids: tuple[str, ...],
        idempotent_replay: bool,
    ) -> GameClientCommandResult:
        return GameClientCommandResult(
            "confirmed",
            self.read_state(),
            tuple(committed_event_ids),
            bool(idempotent_replay),
            None,
            None,
        )

    @staticmethod
    def _rejected(code: str, detail: str | None = None) -> GameClientCommandResult:
        return GameClientCommandResult("rejected", None, (), False, code, detail)
