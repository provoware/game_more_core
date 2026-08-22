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
from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.application.world_service import WorldService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_COMMAND_FIELDS: dict[str, frozenset[str]] = {
    "profile.update": frozenset({"type", "command_id", "changes"}),
    "street.walk": frozenset({"type", "command_id"}),
    "world.intro_acknowledge": frozenset({"type", "command_id"}),
    "world.move": frozenset({"type", "command_id", "city_id", "district_id", "location_id"}),
    "world.housing_guest": frozenset({"type", "command_id", "host_character_id"}),
    "world.inspect_storefront": frozenset({"type", "command_id"}),
    "world.minigame": frozenset({"type", "command_id", "game_id", "cell"}),
    "world.party_mode": frozenset({"type", "command_id", "mode"}),
    "world.party_check": frozenset({"type", "command_id"}),
    "world.party_resolve": frozenset({"type", "command_id", "choice_id"}),
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
_CHARACTER_COMMANDS = frozenset({
    "profile.update",
    "street.walk",
    "world.intro_acknowledge",
    "world.move",
    "world.housing_guest",
    "world.inspect_storefront",
    "world.minigame",
})
_WORLD_EVENT_COMMANDS = frozenset({"world.party_mode", "world.party_check", "world.party_resolve"})


@dataclass(frozen=True, slots=True)
class GameClientCommandResult:
    status: str
    confirmed_state: dict[str, Any] | None
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool
    error_code: str | None
    error_detail: str | None = None
    metadata: dict[str, Any] | None = None


class GameClientSession:
    """Thin write adapter for the local A4 client.

    It owns no gameplay rules. Persistent commands are delegated to canonical
    Profile/Street/Event/Economy/Incident/Settlement/World application services.
    """

    def __init__(
        self,
        persistence: PersistenceKernel,
        *,
        incident_catalog: dict[str, dict[str, Any]],
        incident_contract_version: str,
        street_manifest: Mapping[str, Any] | None = None,
        street_world_seed: str | None = None,
        world_manifest: Mapping[str, Any] | None = None,
    ) -> None:
        if not incident_catalog:
            raise ValueError("incident_catalog darf nicht leer sein")
        if not isinstance(incident_contract_version, str) or not incident_contract_version.strip():
            raise ValueError("incident_contract_version fehlt")
        if (street_manifest is None) != (street_world_seed is None):
            raise ValueError("street_manifest und street_world_seed müssen gemeinsam gesetzt werden")
        self.persistence = persistence
        self.profile = CharacterProfileService(persistence)
        self.street = StreetEncounterService(persistence, street_manifest) if street_manifest is not None else None
        self.street_world_seed = street_world_seed
        self.world = WorldService(persistence, world_manifest) if world_manifest is not None else None
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
        return deepcopy(self.persistence.load_state() or {})

    def bootstrap_character(self, character: CharacterState) -> dict[str, Any]:
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

    def ensure_world_player(
        self,
        character: CharacterState,
        *,
        context: JournalContext,
    ) -> GameClientCommandResult:
        if self.world is None:
            return self._rejected("world_not_configured")
        try:
            result = self.world.ensure_player(character, context=context)
            return self._confirmed(
                result.committed_event_ids,
                result.idempotent_replay,
                metadata=deepcopy(result.metadata),
            )
        except PersistenceError as exc:
            return self._rejected("persistence_error", str(exc))
        except (ValueError, KeyError, TypeError) as exc:
            return self._rejected("validation_error", str(exc))

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
            if command_type in _CHARACTER_COMMANDS:
                return self._dispatch_character(command, command_id=command_id, context=context)

            if context.entity_type != "event" or not context.entity_id:
                return self._rejected("invalid_event_context")

            if command_type in _WORLD_EVENT_COMMANDS:
                return self._dispatch_world_event(command, command_id=command_id, context=context)

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
                multiplier = 10000
                if self.world is not None:
                    if not context.character_id:
                        return self._rejected("character_context_missing")
                    multiplier = self.world.city_price_multiplier_bps(context.character_id)
                result = self.economy.transact(
                    kind.strip(),
                    item_id.strip(),
                    quantity,
                    context=context,
                    price_multiplier_bps=multiplier,
                )
                return self._confirmed(
                    result.committed_event_ids,
                    result.idempotent_replay,
                    metadata={"city_price_multiplier_bps": multiplier},
                )

            if command_type == "incident.open":
                incident_type = command.get("incident_type")
                severity = command.get("severity")
                if not isinstance(incident_type, str) or not incident_type.strip():
                    return self._rejected("invalid_incident_type")
                if severity is not None and (isinstance(severity, bool) or not isinstance(severity, int)):
                    return self._rejected("invalid_severity")
                result = self.incidents.open(
                    incident_type.strip(), context=context, severity=severity
                )
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "incident.resolve":
                response_id = command.get("response_id")
                if not isinstance(response_id, str) or not response_id.strip():
                    return self._rejected("invalid_response_id")
                result = self.incidents.resolve(response_id.strip(), context=context)
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            result = self.settlement.complete(context=context)
            committed = list(result.committed_event_ids)
            replay = result.idempotent_replay
            metadata: dict[str, Any] = {}
            if self.world is not None:
                world_context = self._with_command(context, f"{command_id}:world")
                world_result = self.world.apply_confirmed_settlement(context=world_context)
                committed.extend(world_result.committed_event_ids)
                replay = replay and world_result.idempotent_replay
                metadata["world_settlement_applied"] = True
                metadata["world_settlement_replay"] = world_result.idempotent_replay
            return self._confirmed(tuple(committed), replay, metadata=metadata or None)
        except PersistenceError as exc:
            return self._rejected("persistence_error", str(exc))
        except (ValueError, KeyError, TypeError) as exc:
            return self._rejected("validation_error", str(exc))
        except RuntimeError as exc:
            return self._rejected("runtime_error", str(exc))

    def _dispatch_character(
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

        if command["type"] == "profile.update":
            changes = command.get("changes")
            if not isinstance(changes, dict) or not changes:
                return self._rejected("invalid_profile_changes")
            event_id = f"{command_id}:profile"
            if self.persistence.has_event(event_id):
                existing = next(
                    (record for record in self.persistence.read_records() if record["event_id"] == event_id),
                    None,
                )
                if (
                    existing is None
                    or existing.get("event_type") != "character.profile_updated"
                    or existing.get("payload", {}).get("new") != deepcopy(changes)
                ):
                    raise PersistenceError("Command-ID wurde mit anderem Profilupdate verwendet")
                return self._confirmed((), True)
            self.profile.update(
                character,
                deepcopy(changes),
                event_id=event_id,
                transaction_id=f"tx:{command_id}:profile",
                context=context,
            )
            return self._confirmed((event_id,), False)

        if command["type"] == "street.walk":
            if self.street is None or self.street_world_seed is None:
                return self._rejected("street_not_configured")
            result = self.street.walk(
                character,
                walk_instance_id=command_id,
                world_seed=self.street_world_seed,
                journal_context=context,
            )
            return self._confirmed(
                result.committed_event_ids,
                result.idempotent_replay,
                metadata={
                    "street_encounter": {
                        "encounter_id": result.encounter_id,
                        "polarity": result.polarity,
                        "title_key": result.title_key,
                        "body_key": result.body_key,
                        "effects": deepcopy(result.effects),
                    }
                },
            )

        if self.world is None:
            return self._rejected("world_not_configured")
        command_type = command["type"]
        if command_type == "world.intro_acknowledge":
            result = self.world.acknowledge_intro(character.character_id, context=context)
            return self._confirmed(result.committed_event_ids, result.idempotent_replay)
        if command_type == "world.move":
            city_id = command.get("city_id")
            district_id = command.get("district_id")
            location_id = command.get("location_id")
            if not isinstance(city_id, str) or not isinstance(district_id, str):
                return self._rejected("invalid_world_position")
            if location_id is not None and not isinstance(location_id, str):
                return self._rejected("invalid_world_position")
            result = self.world.move(
                character.character_id,
                city_id=city_id,
                district_id=district_id,
                location_id=location_id,
                context=context,
            )
            return self._confirmed(
                result.committed_event_ids,
                result.idempotent_replay,
                metadata={"city_price_multiplier_bps": self.world.city_price_multiplier_bps(character.character_id)},
            )
        if command_type == "world.housing_guest":
            host = command.get("host_character_id")
            if host is not None and not isinstance(host, str):
                return self._rejected("invalid_host_character_id")
            result = self.world.set_guest_housing(character.character_id, host, context=context)
            return self._confirmed(result.committed_event_ids, result.idempotent_replay)
        if command_type == "world.inspect_storefront":
            result = self.world.inspect_storefront(character.character_id, context=context)
            return self._confirmed(
                result.committed_event_ids,
                result.idempotent_replay,
                metadata={"storefront": deepcopy(result.metadata)},
            )
        game_id = command.get("game_id")
        cell = command.get("cell")
        if not isinstance(game_id, str) or not game_id.strip():
            return self._rejected("invalid_minigame_id")
        result = self.world.play_minigame(
            character.character_id,
            game_id.strip(),
            cell=cell,
            context=context,
        )
        return self._confirmed(
            result.committed_event_ids,
            result.idempotent_replay,
            metadata={"minigame": deepcopy(result.metadata)},
        )

    def _dispatch_world_event(
        self,
        command: Mapping[str, Any],
        *,
        command_id: str,
        context: JournalContext,
    ) -> GameClientCommandResult:
        if self.world is None:
            return self._rejected("world_not_configured")
        command_type = command["type"]
        if command_type == "world.party_mode":
            mode = command.get("mode")
            if not isinstance(mode, str):
                return self._rejected("invalid_party_mode")
            result = self.world.set_party_mode(context.entity_id, mode, context=context)
        elif command_type == "world.party_check":
            result = self.world.check_party_encounter(context.entity_id, context=context)
        else:
            choice_id = command.get("choice_id")
            if not isinstance(choice_id, str) or not choice_id.strip():
                return self._rejected("invalid_party_choice")
            result = self.world.resolve_party_encounter(
                context.entity_id,
                choice_id.strip(),
                context=context,
            )
        return self._confirmed(
            result.committed_event_ids,
            result.idempotent_replay,
            metadata={"world": deepcopy(result.metadata)} if result.metadata is not None else None,
        )

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
        *,
        metadata: dict[str, Any] | None = None,
    ) -> GameClientCommandResult:
        return GameClientCommandResult(
            "confirmed",
            self.read_state(),
            tuple(committed_event_ids),
            bool(idempotent_replay),
            None,
            None,
            deepcopy(metadata) if metadata is not None else None,
        )

    @staticmethod
    def _with_command(context: JournalContext, command_id: str) -> JournalContext:
        return JournalContext(
            timestamp_local=context.timestamp_local,
            session_id=context.session_id,
            player_id=context.player_id,
            entity_type=context.entity_type,
            entity_id=context.entity_id,
            command_id=command_id,
            source=context.source,
            game_version=context.game_version,
            character_id=context.character_id,
        )

    @staticmethod
    def _rejected(code: str, detail: str | None = None) -> GameClientCommandResult:
        return GameClientCommandResult("rejected", None, (), False, code, detail)
