from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any

from bunkerfrequenz.domain.assistant import AssistantControlState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel
from bunkerfrequenz.application.scene_job_service import SceneJobService


@dataclass(frozen=True, slots=True)
class ConfirmedRoundTrigger:
    """Internal runtime proof that one game round was already confirmed."""

    round_id: str
    character_id: str


@dataclass(frozen=True, slots=True)
class AssistantRoundResult:
    round_id: str
    job_id: str | None
    executed: bool
    idempotent_replay: bool
    committed_event_ids: tuple[str, ...]


class AssistantRoundExecutionService:
    """Consume one confirmed game round exactly once and delegate work to SceneJobService.

    This service is application-internal. It is intentionally not a browser command surface and
    does not derive authority from system time.
    """

    def __init__(self, persistence: PersistenceKernel, scene_jobs: SceneJobService) -> None:
        if scene_jobs.persistence is not persistence:
            raise ValueError("Assistent und Scene Jobs müssen denselben Persistence-Kernel verwenden")
        self.persistence = persistence
        self.scene_jobs = scene_jobs

    def process(self, trigger: ConfirmedRoundTrigger, *, context: JournalContext) -> AssistantRoundResult:
        round_id = self._text(trigger.round_id, "round_id")
        character_id = self._text(trigger.character_id, "character_id")
        if context.entity_type != "character" or not context.entity_id:
            raise ValueError("Bestätigte Assistenten-Runde benötigt Character-Kontext")
        if context.entity_id != character_id or (context.character_id and context.character_id != character_id):
            raise ValueError("Runden-Character passt nicht zum Assistenten-Kontext")

        round_command_id = f"assistant:{character_id}:round:{round_id}"
        processed_event_id = f"{round_command_id}:processed"
        job_event_id = f"{round_command_id}:job"
        records = self.persistence.read_records()

        processed = next((record for record in records if record.get("event_id") == processed_event_id), None)
        if processed is not None:
            payload = processed.get("payload", {})
            if payload.get("round_id") != round_id or payload.get("character_id") != character_id:
                raise PersistenceError("Verarbeiteter Assistenten-Rundentrigger kollidiert")
            job_id = payload.get("job_id")
            if job_id is not None and job_id not in self.scene_jobs.by_id:
                raise PersistenceError("Verarbeitete Assistenten-Runde verweist auf unbekannten Scene Job")
            return AssistantRoundResult(round_id, job_id, job_id is not None, True, ())

        child_context = replace(context, command_id=round_command_id, character_id=character_id)

        # Crash-safe continuation: if the delegated job is already durable but the round marker
        # is not, finish the original job choice instead of reading a possibly switched control state.
        durable_job = next((record for record in records if record.get("event_id") == job_event_id), None)
        if durable_job is not None:
            job_id = durable_job.get("payload", {}).get("job_id")
            if not isinstance(job_id, str) or job_id not in self.scene_jobs.by_id:
                raise PersistenceError("Durable Assistenten-Jobausführung ist inkonsistent")
            self.scene_jobs.run(job_id, context=child_context)
            marker_ids = self._mark_processed(round_id, character_id, job_id, context=child_context)
            return AssistantRoundResult(round_id, job_id, True, True, marker_ids)

        state = self.persistence.load_state() or {}
        raw_assistant = state.get("assistant")
        assistant = AssistantControlState.from_dict(raw_assistant if isinstance(raw_assistant, dict) else None)
        job_id = assistant.active_job_id

        if job_id is None:
            marker_ids = self._mark_processed(round_id, character_id, None, context=child_context)
            return AssistantRoundResult(round_id, None, False, False, marker_ids)

        job_result = self.scene_jobs.run(job_id, context=child_context)
        marker_ids = self._mark_processed(round_id, character_id, job_id, context=child_context)
        return AssistantRoundResult(
            round_id,
            job_id,
            True,
            job_result.idempotent_replay,
            job_result.committed_event_ids + marker_ids,
        )

    def _mark_processed(
        self,
        round_id: str,
        character_id: str,
        job_id: str | None,
        *,
        context: JournalContext,
    ) -> tuple[str, ...]:
        event_id = f"{context.command_id}:processed"
        existing = next((record for record in self.persistence.read_records() if record.get("event_id") == event_id), None)
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("round_id") != round_id or payload.get("job_id") != job_id:
                raise PersistenceError("Assistenten-Rundenmarker kollidiert")
            return ()

        state = deepcopy(self.persistence.load_state() or {})
        assistant = AssistantControlState.from_dict(state.get("assistant") if isinstance(state.get("assistant"), dict) else None)
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:processed",
            events=[{
                "event_id": event_id,
                "event_type": "assistant.round_processed",
                "payload": {
                    "round_id": round_id,
                    "character_id": character_id,
                    "job_id": job_id,
                    "assistant_revision": assistant.revision,
                },
            }],
            derived_state=state,
            context=context,
        )
        return receipt.event_ids

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} muss nicht-leerer Text sein")
        return value.strip()
