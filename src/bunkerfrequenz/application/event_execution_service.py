from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from bunkerfrequenz.application.event_state_service import EventCommitResult, EventStateService
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext


@dataclass(frozen=True, slots=True)
class EventActionSpec:
    action_id: str
    source_phase: str
    target_phase: str
    prerequisites: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EventActionAvailability:
    action_id: str
    source_phase: str
    target_phase: str
    enabled: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EventActionResult:
    action_id: str
    event: EventState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


EVENT_ACTIONS: dict[str, EventActionSpec] = {
    "begin_planning": EventActionSpec("begin_planning", "draft", "planning"),
    "begin_procurement": EventActionSpec(
        "begin_procurement",
        "planning",
        "procurement",
        ("confirmed_act", "confirmed_crew", "positive_budget"),
    ),
    "start_transport": EventActionSpec(
        "start_transport",
        "procurement",
        "transport",
        ("confirmed_acts", "confirmed_crew", "equipment_ready"),
    ),
    "begin_setup": EventActionSpec("begin_setup", "transport", "setup"),
    "confirm_soundcheck": EventActionSpec(
        "confirm_soundcheck",
        "setup",
        "soundcheck",
        ("confirmed_crew", "equipment_ready"),
    ),
    "start_live": EventActionSpec(
        "start_live",
        "soundcheck",
        "live",
        ("confirmed_acts", "confirmed_crew", "equipment_ready"),
    ),
    "finish_live": EventActionSpec("finish_live", "live", "teardown"),
    "finish_teardown": EventActionSpec("finish_teardown", "teardown", "settlement"),
}


def _has_confirmed_act(event: EventState) -> bool:
    return any(act["status"] == "confirmed" for act in event.acts)


def _all_acts_confirmed(event: EventState) -> bool:
    return bool(event.acts) and all(act["status"] == "confirmed" for act in event.acts)


def _all_crew_confirmed(event: EventState) -> bool:
    return bool(event.crew) and all(member["status"] == "confirmed" for member in event.crew)


def _equipment_ready(event: EventState) -> bool:
    return all(item["status"] == "ready" for item in event.equipment)


_PREREQUISITES: dict[str, Callable[[EventState], bool]] = {
    "confirmed_act": _has_confirmed_act,
    "confirmed_acts": _all_acts_confirmed,
    "confirmed_crew": _all_crew_confirmed,
    "positive_budget": lambda event: event.budget_cents > 0,
    "equipment_ready": _equipment_ready,
}


class EventExecutionService:
    """Executes canonical event phase actions without exposing free phase mutation to clients."""

    def __init__(self, event_state_service: EventStateService):
        self._events = event_state_service

    @staticmethod
    def availability(event: EventState, action_id: str) -> EventActionAvailability:
        event.validate()
        spec = EVENT_ACTIONS.get(action_id)
        if spec is None:
            raise ValueError(f"Unbekannte Event-Aktion: {action_id}")

        blockers: list[str] = []
        if event.phase != spec.source_phase:
            blockers.append("wrong_phase")
        for rule in spec.prerequisites:
            checker = _PREREQUISITES[rule]
            if not checker(event):
                blockers.append(rule)

        # Physical target phases remain guarded by EventState.transition_to().
        # Mirror the gate here so clients can show the same blockers before submit.
        if spec.target_phase in {"transport", "setup", "soundcheck", "live", "teardown", "settlement"}:
            if event.location is None:
                blockers.append("location_required")
            elif event.location["access_status"] == "unverified":
                blockers.append("verified_access_required")
            if event.time_window is None:
                blockers.append("time_window_required")
            if event.safety_status != "cleared":
                blockers.append("safety_clearance_required")

        return EventActionAvailability(
            action_id=action_id,
            source_phase=spec.source_phase,
            target_phase=spec.target_phase,
            enabled=not blockers,
            blockers=tuple(blockers),
        )

    @staticmethod
    def available_actions(event: EventState) -> tuple[EventActionAvailability, ...]:
        event.validate()
        return tuple(
            availability
            for action_id in EVENT_ACTIONS
            if (availability := EventExecutionService.availability(event, action_id)).source_phase == event.phase
        )

    def execute(
        self,
        event: EventState,
        action_id: str,
        *,
        context: JournalContext,
    ) -> EventActionResult:
        spec = EVENT_ACTIONS.get(action_id)
        if spec is None:
            raise ValueError(f"Unbekannte Event-Aktion: {action_id}")

        def enforce_action_gate(persisted: EventState) -> None:
            availability = self.availability(persisted, action_id)
            if not availability.enabled:
                raise ValueError(
                    f"Event-Aktion {action_id} ist gesperrt: {', '.join(availability.blockers)}"
                )

        committed: EventCommitResult = self._events.transition_phase(
            event,
            spec.target_phase,
            context=context,
            reason=f"event_action:{action_id}",
            precondition=enforce_action_gate,
        )
        return EventActionResult(
            action_id=action_id,
            event=committed.event,
            committed_event_ids=committed.committed_event_ids,
            idempotent_replay=committed.idempotent_replay,
        )
