from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any, Mapping

from bunkerfrequenz.application.district_service import DistrictService
from bunkerfrequenz.application.economy_service import EconomyService
from bunkerfrequenz.application.event_execution_service import EventExecutionService
from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.incident_service import IncidentService
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.application.property_service import PropertyService
from bunkerfrequenz.application.property_upgrade_service import PropertyUpgradeService
from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_COMMAND_FIELDS: dict[str, frozenset[str]] = {
    "profile.update": frozenset({"type", "command_id", "changes"}),
    "street.walk": frozenset({"type", "command_id", "approach_id"}),
    "event.create": frozenset({"type", "command_id", "event"}),
    "event.update_planning": frozenset({"type", "command_id", "changes"}),
    "event.execute": frozenset({"type", "command_id", "action_id"}),
    "economy.initialize": frozenset({"type", "command_id", "economy"}),
    "economy.transact": frozenset({"type", "command_id", "kind", "item_id", "quantity"}),
    "property.purchase": frozenset({"type", "command_id", "location_id"}),
    "property.upgrade": frozenset({"type", "command_id", "location_id", "upgrade_id"}),
    "incident.open": frozenset({"type", "command_id", "incident_type", "severity"}),
    "incident.resolve": frozenset({"type", "command_id", "response_id"}),
    "settlement.complete": frozenset({"type", "command_id"}),
}
_COMMAND_TYPES = frozenset(_COMMAND_FIELDS)
_CHARACTER_COMMANDS = frozenset({"profile.update", "street.walk"})


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
    Profile/Street/Event/Economy/Property/Upgrade/Incident/Settlement/District services.
    District metrics, property prices, upgrade costs/levels, owners and budget
    deltas are never accepted directly from the client.
    """

    def __init__(
        self,
        persistence: PersistenceKernel,
        *,
        incident_catalog: dict[str, dict[str, Any]],
        incident_contract_version: str,
        street_manifest: Mapping[str, Any] | None = None,
        street_world_seed: str | None = None,
        district_manifest: Mapping[str, Any] | None = None,
        city_map_manifest: Mapping[str, Any] | None = None,
        property_manifest: Mapping[str, Any] | None = None,
        property_upgrade_manifest: Mapping[str, Any] | None = None,
    ) -> None:
        if not incident_catalog:
            raise ValueError("incident_catalog darf nicht leer sein")
        if not isinstance(incident_contract_version, str) or not incident_contract_version.strip():
            raise ValueError("incident_contract_version fehlt")
        if (street_manifest is None) != (street_world_seed is None):
            raise ValueError("street_manifest und street_world_seed müssen gemeinsam gesetzt werden")
        if (district_manifest is None) != (city_map_manifest is None):
            raise ValueError("district_manifest und city_map_manifest müssen gemeinsam gesetzt werden")
        if property_manifest is not None and city_map_manifest is None:
            raise ValueError("property_manifest benötigt city_map_manifest")
        if property_upgrade_manifest is not None and (property_manifest is None or city_map_manifest is None):
            raise ValueError("property_upgrade_manifest benötigt Property- und City-Map-Vertrag")
        self.persistence = persistence
        self.profile = CharacterProfileService(persistence)
        self.street = StreetEncounterService(persistence, street_manifest) if street_manifest is not None else None
        self.street_world_seed = street_world_seed
        self.district = (
            DistrictService(persistence, district_manifest, city_map_manifest)
            if district_manifest is not None and city_map_manifest is not None
            else None
        )
        self.property = (
            PropertyService(persistence, property_manifest, city_map_manifest)
            if property_manifest is not None and city_map_manifest is not None
            else None
        )
        self.property_upgrade = (
            PropertyUpgradeService(
                persistence,
                property_upgrade_manifest,
                property_manifest,
                city_map_manifest,
            )
            if property_upgrade_manifest is not None
            and property_manifest is not None
            and city_map_manifest is not None
            else None
        )
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
                    kind.strip(), item_id.strip(), quantity, context=context
                )
                return self._confirmed(result.committed_event_ids, result.idempotent_replay)

            if command_type == "property.purchase":
                if self.property is None:
                    return self._rejected("property_not_configured")
                location_id = command.get("location_id")
                if not isinstance(location_id, str) or not location_id.strip():
                    return self._rejected("invalid_location_id")
                result = self.property.purchase(location_id.strip(), context=context)
                ownership = result.properties.owned.get(location_id.strip())
                return self._confirmed(
                    result.committed_event_ids,
                    result.idempotent_replay,
                    metadata={"property": deepcopy(ownership)} if ownership is not None else None,
                )

            if command_type == "property.upgrade":
                if self.property_upgrade is None:
                    return self._rejected("property_upgrade_not_configured")
                location_id = command.get("location_id")
                upgrade_id = command.get("upgrade_id")
                if not isinstance(location_id, str) or not location_id.strip():
                    return self._rejected("invalid_location_id")
                if not isinstance(upgrade_id, str) or not upgrade_id.strip():
                    return self._rejected("invalid_upgrade_id")
                result = self.property_upgrade.upgrade(
                    location_id.strip(),
                    upgrade_id.strip(),
                    context=context,
                )
                return self._confirmed(
                    result.committed_event_ids,
                    result.idempotent_replay,
                    metadata={
                        "property_upgrade": {
                            "location_id": result.location_id,
                            "upgrade_id": result.upgrade_id,
                            "level": result.new_level,
                            "cost_cents": result.upgrade_cost_cents,
                        }
                    },
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
            overall_replay = result.idempotent_replay
            metadata: dict[str, Any] = {}
            if self.district is not None:
                district_result = self.district.apply_confirmed_settlement(
                    context=replace(context, command_id=f"{command_id}:district")
                )
                committed.extend(district_result.committed_event_ids)
                overall_replay = overall_replay and district_result.idempotent_replay
                metadata["district"] = deepcopy(district_result.metadata)
                metadata["district"]["applied"] = district_result.applied
            return self._confirmed(tuple(committed), overall_replay, metadata=metadata or None)
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
                return self._confirmed((), True)
            self.profile.update(
                character,
                deepcopy(changes),
                event_id=event_id,
                transaction_id=f"tx:{command_id}:profile",
                context=context,
            )
            return self._confirmed((event_id,), False)

        if self.street is None or self.street_world_seed is None:
            return self._rejected("street_not_configured")
        approach_id = command.get("approach_id")
        if approach_id is not None and (not isinstance(approach_id, str) or not approach_id.strip()):
            return self._rejected("invalid_street_approach")
        result = self.street.walk(
            character,
            walk_instance_id=command_id,
            world_seed=self.street_world_seed,
            journal_context=context,
            approach_id=approach_id.strip() if isinstance(approach_id, str) else None,
        )
        committed = list(result.committed_event_ids)
        overall_replay = result.idempotent_replay
        metadata: dict[str, Any] = {
            "street_encounter": {
                "approach_id": result.approach_id,
                "encounter_id": result.encounter_id,
                "polarity": result.polarity,
                "title_key": result.title_key,
                "body_key": result.body_key,
                "effects": deepcopy(result.effects),
            }
        }
        if self.district is not None:
            district_result = self.district.apply_confirmed_street_encounter(
                source_event_id=f"{command_id}:001",
                context=replace(context, command_id=f"{command_id}:district"),
            )
            committed.extend(district_result.committed_event_ids)
            overall_replay = overall_replay and district_result.idempotent_replay
            metadata["district"] = deepcopy(district_result.metadata)
            metadata["district"]["applied"] = district_result.applied
        return self._confirmed(tuple(committed), overall_replay, metadata=metadata)

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
    def _rejected(code: str, detail: str | None = None) -> GameClientCommandResult:
        return GameClientCommandResult("rejected", None, (), False, code, detail)
