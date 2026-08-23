from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.domain.assistant import AssistantState


def build_assistant_projection(
    state: Mapping[str, Any] | None,
    *,
    manifest: Mapping[str, Any],
    scene_jobs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    raw = deepcopy(dict(state or {}))
    raw_assistant = raw.get("assistant")
    if raw_assistant is not None and not isinstance(raw_assistant, Mapping):
        raise ValueError("Persistierter Assistant-State muss Mapping sein")
    assistant = AssistantState.from_dict(
        dict(raw_assistant) if isinstance(raw_assistant, Mapping) else None
    )
    jobs_by_id = {
        job.get("job_id"): deepcopy(dict(job))
        for job in scene_jobs
        if isinstance(job, Mapping) and isinstance(job.get("job_id"), str)
    }
    active = jobs_by_id.get(assistant.active_task_id)
    if assistant.active_task_id is not None and active is None:
        raise ValueError("Aktive Assistenten-Aufgabe ist nicht katalogisiert")
    label = manifest.get("label")
    story = manifest.get("story")
    if not isinstance(label, str) or not label.strip() or not isinstance(story, str) or not story.strip():
        raise ValueError("Assistant-Manifest benötigt Anzeigetext")
    return {
        "available": isinstance(raw.get("character"), Mapping),
        "assistant_id": manifest.get("assistant_id"),
        "label": label,
        "story": story,
        "active_task_id": assistant.active_task_id,
        "active_task": active,
        "completed_rounds": assistant.completed_rounds,
        "last_completed_round_id": assistant.last_completed_round_id,
        "revision": assistant.revision,
        "trigger_label": "nach jeder bestätigten Straßenrunde",
    }
