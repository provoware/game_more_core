from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.domain.assistant import AssistantControlState
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class AssistantControlResult:
    assistant: AssistantControlState
    changed: bool
    idempotent_replay: bool


class AssistantControlService:
    """Persist start/stop/switch only; automatic round execution is intentionally out of scope."""

    def __init__(self, persistence: PersistenceKernel, scene_job_manifest: Mapping[str, Any]) -> None:
        self.persistence = persistence
        jobs = scene_job_manifest.get("jobs")
        if not isinstance(jobs, list) or not jobs:
            raise ValueError("Assistent benötigt den kanonischen Scene-Job-Katalog")
        self.allowed_job_ids = frozenset(
            job.get("job_id") for job in jobs if isinstance(job, Mapping) and isinstance(job.get("job_id"), str)
        )
        if len(self.allowed_job_ids) != len(jobs):
            raise ValueError("Scene-Job-Katalog enthält ungültige oder doppelte IDs")

    def set_active_job(self, job_id: str | None, *, context: JournalContext) -> AssistantControlResult:
        if context.entity_type != "character" or not context.entity_id or not context.command_id:
            raise ValueError("Assistenten-Steuerung benötigt Character-Kontext")
        if job_id is not None:
            if not isinstance(job_id, str) or not job_id.strip():
                raise ValueError("job_id muss Text oder null sein")
            job_id = job_id.strip()
            if job_id not in self.allowed_job_ids:
                raise ValueError("Unbekannter Scene Job für Assistent")

        event_id = f"{context.command_id}:assistant-control"
        existing = next((r for r in self.persistence.read_records() if r.get("event_id") == event_id), None)
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("active_job_id") != job_id:
                raise PersistenceError("Command-ID wurde bereits für andere Assistenten-Steuerung verwendet")
            return AssistantControlResult(self._load_control(), False, True)

        state = deepcopy(self.persistence.load_state() or {})
        raw_character = state.get("character")
        if not isinstance(raw_character, dict):
            raise PersistenceError("Assistenten-Steuerung benötigt bestätigten Character-State")
        character = CharacterState.from_dict(raw_character)
        if character.character_id != context.entity_id:
            raise ValueError("Assistenten-Kontext passt nicht zum Character")

        current = AssistantControlState.from_dict(state.get("assistant") if isinstance(state.get("assistant"), dict) else None)
        if current.active_job_id == job_id:
            return AssistantControlResult(current, False, False)

        target = AssistantControlState(active_job_id=job_id, revision=current.revision + 1)
        target.validate()
        derived = deepcopy(state)
        derived["assistant"] = target.to_dict()
        self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:assistant-control",
            events=[{
                "event_id": event_id,
                "event_type": "assistant.control_changed",
                "payload": target.to_dict(),
            }],
            derived_state=derived,
            context=context,
        )
        return AssistantControlResult(target, True, False)

    def _load_control(self) -> AssistantControlState:
        state = self.persistence.load_state() or {}
        return AssistantControlState.from_dict(state.get("assistant") if isinstance(state.get("assistant"), dict) else None)


def replay_assistant_control_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("event_type") != "assistant.control_changed":
        return derived_state
    payload = record.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("assistant.control_changed benötigt Zielzustand")
    target = AssistantControlState.from_dict(payload)
    state = deepcopy(derived_state)
    current = AssistantControlState.from_dict(state.get("assistant") if isinstance(state.get("assistant"), dict) else None)
    if target.revision < current.revision:
        raise ValueError("Assistenten-Replay würde Revision zurücksetzen")
    if target.revision == current.revision:
        if target.to_dict() != current.to_dict():
            raise ValueError("Assistenten-Replay kollidiert auf gleicher Revision")
        return state
    if target.revision != current.revision + 1:
        raise ValueError("Assistenten-Replay überspringt Revision")
    state["assistant"] = target.to_dict()
    return state
