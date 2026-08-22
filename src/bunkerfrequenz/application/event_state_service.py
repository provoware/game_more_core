from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable

from bunkerfrequenz.application.state_blocks import merge_state_block
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_PLANNING_FIELDS = {
    "display_name",
    "location",
    "budget_cents",
    "acts",
    "crew",
    "equipment",
    "time_window",
    "safety_status",
}


@dataclass(frozen=True, slots=True)
class EventCommitResult:
    event: EventState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class EventStateService:
    def __init__(self, persistence: PersistenceKernel):
        self.persistence = persistence

    @staticmethod
    def _validate_context(event_id: str, context: JournalContext) -> None:
        if context.entity_type != "event":
            raise ValueError("Event-Commit benötigt entity_type=event")
        if context.entity_id != event_id:
            raise ValueError("JournalContext.entity_id passt nicht zum Event")
        if not context.command_id:
            raise ValueError("Event-Commit benötigt command_id")

    def _existing_record(self, context: JournalContext) -> dict[str, Any] | None:
        journal_event_id = f"{context.command_id}:event"
        if not self.persistence.has_event(journal_event_id):
            return None
        for record in self.persistence.read_records():
            if record["event_id"] == journal_event_id:
                return record
        raise PersistenceError("Event-ID ist registriert, aber Journalrecord fehlt")

    def _replay_result(self, event_id: str) -> EventCommitResult:
        state = self.persistence.load_state()
        if state is None or "event" not in state:
            raise PersistenceError("Journal enthält Event-Command, aber Eventzustand fehlt")
        persisted = EventState.from_dict(state["event"])
        if persisted.event_id != event_id:
            raise PersistenceError("Idempotenter Event-Replay verweist auf anderes Event")
        return EventCommitResult(persisted, (), True)

    def create(self, event: EventState, *, context: JournalContext) -> EventCommitResult:
        event.validate()
        self._validate_context(event.event_id, context)
        existing_record = self._existing_record(context)
        if existing_record is not None:
            if (
                existing_record["event_type"] != "event.created"
                or existing_record.get("payload", {}).get("event") != event.to_dict()
            ):
                raise PersistenceError("Command-ID wurde bereits mit anderem Eventinhalt verwendet")
            return self._replay_result(event.event_id)

        current = self.persistence.load_state()
        if current is not None and "event" in current:
            raise PersistenceError("Ein Eventzustand existiert bereits in diesem Save")
        if current is None:
            self.persistence.initialize_state({})

        derived = merge_state_block(self.persistence, "event", event.to_dict())
        journal_event_id = f"{context.command_id}:event"
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}",
            events=[{
                "event_id": journal_event_id,
                "event_type": "event.created",
                "payload": {"event": event.to_dict()},
            }],
            derived_state=derived,
            context=context,
        )
        return EventCommitResult(event, receipt.event_ids, False)

    def update_planning(
        self,
        event: EventState,
        changes: dict[str, Any],
        *,
        context: JournalContext,
    ) -> EventCommitResult:
        event.validate()
        self._validate_context(event.event_id, context)
        unknown = set(changes) - _PLANNING_FIELDS
        if unknown:
            raise ValueError(f"Nicht editierbare Eventfelder: {', '.join(sorted(unknown))}")
        if not changes:
            raise ValueError("Event-Planungsupdate benötigt mindestens eine Änderung")
        current_state = self.persistence.load_state() or {}
        if "budget_cents" in changes and "economy" in current_state:
            raise ValueError("Budget darf nach Economy-Start nur durch bestätigte Transaktionen geändert werden")

        existing_record = self._existing_record(context)
        if existing_record is not None:
            payload = existing_record.get("payload", {})
            recorded_changes = {
                key: deepcopy(block.get("new"))
                for key, block in payload.get("changes", {}).items()
                if isinstance(block, dict)
            }
            if existing_record["event_type"] != "event.planning_updated" or recorded_changes != changes:
                raise PersistenceError("Command-ID wurde bereits mit anderem Planungsupdate verwendet")
            return self._replay_result(event.event_id)

        if event.phase not in {"draft", "planning", "procurement"}:
            raise ValueError("Planungsdaten dürfen nach Beginn des Transports nicht mehr direkt geändert werden")
        persisted = self._load_current(event)
        data = persisted.to_dict()
        payload_changes: dict[str, dict[str, Any]] = {}
        for key, value in changes.items():
            old_value = deepcopy(data[key])
            new_value = deepcopy(value)
            data[key] = new_value
            payload_changes[key] = {"old": old_value, "new": new_value}
        data["revision"] = persisted.revision + 1
        updated = EventState.from_dict(data)
        payload = {
            "event_id": event.event_id,
            "changes": payload_changes,
            "old_revision": persisted.revision,
            "new_revision": updated.revision,
        }
        return self._commit(updated, "event.planning_updated", payload, context)

    def transition_phase(
        self,
        event: EventState,
        new_phase: str,
        *,
        context: JournalContext,
        reason: str | None = None,
        precondition: Callable[[EventState], None] | None = None,
    ) -> EventCommitResult:
        event.validate()
        self._validate_context(event.event_id, context)
        if new_phase == "completed":
            raise ValueError("Eventphase completed darf ausschließlich SettlementService nach bestätigter Abrechnung erzeugen")
        normalized_reason = None
        if reason is not None:
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("reason muss nicht leerer Text sein")
            normalized_reason = reason.strip()

        existing_record = self._existing_record(context)
        if existing_record is not None:
            payload = existing_record.get("payload", {})
            if (
                existing_record["event_type"] != "event.phase_changed"
                or payload.get("new_phase") != new_phase
                or payload.get("reason") != normalized_reason
            ):
                raise PersistenceError("Command-ID wurde bereits mit anderem Phasenwechsel verwendet")
            return self._replay_result(event.event_id)

        persisted = self._load_current(event)
        if precondition is not None:
            precondition(persisted)
        updated = persisted.transition_to(new_phase)
        payload = {
            "event_id": event.event_id,
            "old_phase": persisted.phase,
            "new_phase": updated.phase,
            "old_revision": persisted.revision,
            "new_revision": updated.revision,
            "reason": normalized_reason,
        }
        return self._commit(updated, "event.phase_changed", payload, context)

    def _load_current(self, supplied: EventState) -> EventState:
        state = self.persistence.load_state()
        if state is None or "event" not in state:
            raise PersistenceError("Kein persistierter Eventzustand vorhanden")
        current = EventState.from_dict(state["event"])
        if current.event_id != supplied.event_id:
            raise PersistenceError("Event-ID passt nicht zum persistierten Zustand")
        if current.revision != supplied.revision:
            raise PersistenceError(
                f"Veralteter Eventzustand: Revision {supplied.revision}, bestätigt ist {current.revision}"
            )
        return current

    def _commit(
        self,
        updated: EventState,
        event_type: str,
        payload: dict[str, Any],
        context: JournalContext,
    ) -> EventCommitResult:
        journal_event_id = f"{context.command_id}:event"
        derived = merge_state_block(self.persistence, "event", updated.to_dict())
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}",
            events=[{"event_id": journal_event_id, "event_type": event_type, "payload": payload}],
            derived_state=derived,
            context=context,
        )
        return EventCommitResult(updated, receipt.event_ids, False)


def replay_event_state_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    event_type = record["event_type"]
    if event_type not in {"event.created", "event.planning_updated", "event.phase_changed"}:
        return derived_state

    payload = record.get("payload", {})
    state = deepcopy(derived_state)

    if event_type == "event.created":
        created = EventState.from_dict(payload["event"])
        if "event" in state:
            current = EventState.from_dict(state["event"])
            if current.to_dict() != created.to_dict():
                raise ValueError("event.created kollidiert mit vorhandenem Eventzustand")
            return state
        state["event"] = created.to_dict()
        return state

    if "event" not in state:
        raise ValueError(f"{event_type} kann ohne event.created nicht replayt werden")
    current = EventState.from_dict(state["event"])
    if payload.get("event_id") != current.event_id:
        raise ValueError("Event-Replay verweist auf anderes Event")
    if payload.get("old_revision") != current.revision:
        raise ValueError("Event-Replay besitzt unerwartete Ausgangsrevision")
    if payload.get("new_revision") != current.revision + 1:
        raise ValueError("Event-Replay besitzt ungültige Zielrevision")

    if event_type == "event.planning_updated":
        data = current.to_dict()
        changes = payload.get("changes")
        if not isinstance(changes, dict) or not changes:
            raise ValueError("event.planning_updated benötigt changes")
        unknown = set(changes) - _PLANNING_FIELDS
        if unknown:
            raise ValueError("Event-Replay enthält unbekannte Planungsfelder")
        for key, block in changes.items():
            if not isinstance(block, dict) or set(block) != {"old", "new"}:
                raise ValueError("Event-Replay-Änderung benötigt old/new")
            if data[key] != block["old"]:
                raise ValueError(f"Event-Replay-Ausgangswert für {key} stimmt nicht")
            data[key] = deepcopy(block["new"])
        data["revision"] = payload["new_revision"]
        state["event"] = EventState.from_dict(data).to_dict()
        return state

    if current.phase != payload.get("old_phase"):
        raise ValueError("Event-Phasenreplay besitzt falsche Ausgangsphase")
    updated = current.transition_to(payload["new_phase"])
    if updated.revision != payload["new_revision"]:
        raise ValueError("Event-Phasenreplay ist inkonsistent")
    state["event"] = updated.to_dict()
    return state
