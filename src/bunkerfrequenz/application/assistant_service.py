from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any, Mapping

from bunkerfrequenz.application.scene_job_service import SceneJobService
from bunkerfrequenz.domain.assistant import AssistantState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class AssistantResult:
    assistant: AssistantState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool
    executed: bool
    task: dict[str, Any] | None = None


class AssistantService:
    """Persist one active Scene Job and execute it once per confirmed street round."""

    def __init__(
        self,
        persistence: PersistenceKernel,
        scene_jobs: SceneJobService,
        manifest: Mapping[str, Any],
    ) -> None:
        self.persistence = persistence
        self.scene_jobs = scene_jobs
        self.manifest = deepcopy(dict(manifest))
        self.version = self._text(self.manifest.get("version"), "ASSISTANT_MANIFEST.version")
        if self.manifest.get("task_source") != "scene_jobs":
            raise ValueError("Assistent muss vorhandene Scene Jobs wiederverwenden")
        trigger = self.manifest.get("trigger")
        selection = self.manifest.get("selection")
        if not isinstance(trigger, Mapping) or not isinstance(selection, Mapping):
            raise ValueError("Assistant-Manifest benötigt trigger und selection")
        if trigger.get("authority") != "confirmed_street_walk":
            raise ValueError("Assistent benötigt bestätigte Straßenrunde als Autorität")
        if trigger.get("execute_once_per_confirmed_round") is not True:
            raise ValueError("Assistent muss exakt einmal pro bestätigter Runde laufen")
        if trigger.get("system_time_allowed") is not False:
            raise ValueError("Systemzeit darf den Assistenten nicht antreiben")
        if selection.get("single_active_task") is not True:
            raise ValueError("Assistent erlaubt genau eine aktive Aufgabe")
        if selection.get("client_can_supply_payout_or_effects") is not False:
            raise ValueError("Client darf Assistentenfolgen nicht liefern")
        self.assistant_id = self._text(self.manifest.get("assistant_id"), "assistant_id")
        self.label = self._text(self.manifest.get("label"), "label")
        self.story = self._text(self.manifest.get("story"), "story")

    def assign(self, task_id: str, *, context: JournalContext) -> AssistantResult:
        self._require_character_context(context)
        task_id = self._text(task_id, "task_id")
        task = self.scene_jobs.by_id.get(task_id)
        if task is None:
            raise ValueError("Assistent kann nur katalogisierte Scene Jobs übernehmen")
        event_id = f"{context.command_id}:assistant-assigned"
        if self.persistence.has_event(event_id):
            return self._current_result(task=task, replay=True)

        state = deepcopy(self.persistence.load_state() or {})
        assistant = self._state_from(state)
        if assistant.active_task_id == task_id:
            return AssistantResult(assistant, (), False, False, deepcopy(task))
        updated = AssistantState.from_dict(assistant.to_dict())
        updated.active_task_id = task_id
        updated.revision += 1
        updated.validate()
        state["assistant"] = updated.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:assistant-assign",
            events=[{
                "event_id": event_id,
                "event_type": "assistant.task_assigned",
                "payload": {
                    "contract_version": self.version,
                    "previous_task_id": assistant.active_task_id,
                    "task_id": task_id,
                    "assistant": updated.to_dict(),
                },
            }],
            derived_state=state,
            context=context,
        )
        return AssistantResult(updated, receipt.event_ids, False, False, deepcopy(task))

    def deactivate(self, *, context: JournalContext) -> AssistantResult:
        self._require_character_context(context)
        event_id = f"{context.command_id}:assistant-deactivated"
        if self.persistence.has_event(event_id):
            return self._current_result(task=None, replay=True)
        state = deepcopy(self.persistence.load_state() or {})
        assistant = self._state_from(state)
        if assistant.active_task_id is None:
            return AssistantResult(assistant, (), False, False, None)
        previous = assistant.active_task_id
        updated = AssistantState.from_dict(assistant.to_dict())
        updated.active_task_id = None
        updated.revision += 1
        updated.validate()
        state["assistant"] = updated.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:assistant-deactivate",
            events=[{
                "event_id": event_id,
                "event_type": "assistant.task_deactivated",
                "payload": {
                    "contract_version": self.version,
                    "previous_task_id": previous,
                    "assistant": updated.to_dict(),
                },
            }],
            derived_state=state,
            context=context,
        )
        return AssistantResult(updated, receipt.event_ids, False, False, None)

    def run_confirmed_round(
        self,
        round_id: str,
        *,
        context: JournalContext,
    ) -> AssistantResult:
        self._require_character_context(context)
        round_id = self._text(round_id, "round_id")
        marker_event_id = f"assistant-round:{round_id}"
        if self.persistence.has_event(marker_event_id):
            return self._current_result(task=None, replay=True)

        state = deepcopy(self.persistence.load_state() or {})
        assistant = self._state_from(state)
        task_id = assistant.active_task_id
        if task_id is None:
            return AssistantResult(assistant, (), False, False, None)
        task = self.scene_jobs.by_id.get(task_id)
        if task is None:
            raise PersistenceError("Aktive Assistenten-Aufgabe ist nicht mehr katalogisiert")

        job_result = self.scene_jobs.run(
            task_id,
            context=replace(context, command_id=f"assistant-job:{round_id}"),
        )
        current = deepcopy(self.persistence.load_state() or {})
        assistant_after_job = self._state_from(current)
        if assistant_after_job.active_task_id != task_id:
            raise PersistenceError("Assistenten-Aufgabe änderte sich während bestätigter Runde")
        updated = AssistantState.from_dict(assistant_after_job.to_dict())
        updated.last_completed_round_id = round_id
        updated.completed_rounds += 1
        updated.revision += 1
        updated.validate()
        current["assistant"] = updated.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:assistant-round",
            events=[{
                "event_id": marker_event_id,
                "event_type": "assistant.round_completed",
                "payload": {
                    "contract_version": self.version,
                    "round_id": round_id,
                    "task_id": task_id,
                    "job_event_id": f"assistant-job:{round_id}:job",
                    "assistant": updated.to_dict(),
                },
            }],
            derived_state=current,
            context=context,
        )
        committed = tuple(job_result.committed_event_ids) + tuple(receipt.event_ids)
        return AssistantResult(updated, committed, False, True, deepcopy(task))

    def _current_result(self, *, task: Mapping[str, Any] | None, replay: bool) -> AssistantResult:
        state = self.persistence.load_state() or {}
        assistant = self._state_from(state)
        active = self.scene_jobs.by_id.get(assistant.active_task_id) if assistant.active_task_id else None
        selected = active if active is not None else task
        return AssistantResult(
            assistant,
            (),
            replay,
            False,
            deepcopy(dict(selected)) if isinstance(selected, Mapping) else None,
        )

    @staticmethod
    def _state_from(state: Mapping[str, Any]) -> AssistantState:
        raw = state.get("assistant")
        return AssistantState.from_dict(dict(raw) if isinstance(raw, Mapping) else None)

    @staticmethod
    def _require_character_context(context: JournalContext) -> None:
        if context.entity_type != "character" or not context.entity_id or not context.command_id:
            raise ValueError("Assistent benötigt Character-Kontext")

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} muss nicht-leerer Text sein")
        return value.strip()


def replay_assistant_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("event_type") not in {
        "assistant.task_assigned",
        "assistant.task_deactivated",
        "assistant.round_completed",
    }:
        return derived_state
    payload = record.get("payload", {})
    target_raw = payload.get("assistant")
    if not isinstance(target_raw, dict):
        raise ValueError("Assistant-Replay benötigt Zielzustand")
    target = AssistantState.from_dict(target_raw)
    state = deepcopy(derived_state)
    current = AssistantState.from_dict(state.get("assistant") if isinstance(state.get("assistant"), dict) else None)
    if target.revision < current.revision:
        raise ValueError("Assistant-Replay würde Revision zurücksetzen")
    if target.revision == current.revision:
        if target.to_dict() != current.to_dict():
            raise ValueError("Assistant-Replay kollidiert auf gleicher Revision")
        return state
    if target.revision != current.revision + 1:
        raise ValueError("Assistant-Replay überspringt Revision")
    state["assistant"] = target.to_dict()
    return state
