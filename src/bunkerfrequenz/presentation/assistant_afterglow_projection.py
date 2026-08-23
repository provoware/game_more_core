from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


def build_assistant_afterglow_projection(
    records: Sequence[Mapping[str, Any]],
    jobs: Sequence[Mapping[str, Any]],
    text_catalog: Mapping[str, Any],
    *,
    limit: int = 3,
) -> dict[str, Any]:
    """Project small read-only story reactions from confirmed assistant work.

    A reaction is emitted only when an ``assistant.round_processed`` record with
    a job is paired with the exact durable ``finance.job_completed`` child event
    for the same character, round and job. Manual jobs and assistant-off rounds
    therefore never create friendship story on their own.
    """
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1 or limit > 10:
        raise ValueError("assistant_afterglow.limit muss zwischen 1 und 10 liegen")

    by_job: dict[str, dict[str, Any]] = {}
    for index, raw_job in enumerate(jobs):
        if not isinstance(raw_job, Mapping):
            raise ValueError(f"assistant_afterglow.jobs[{index}] muss Mapping sein")
        job_id = raw_job.get("job_id")
        label = raw_job.get("label")
        if not isinstance(job_id, str) or not job_id.strip():
            raise ValueError(f"assistant_afterglow.jobs[{index}].job_id fehlt")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"assistant_afterglow.jobs[{index}].label fehlt")
        if job_id in by_job:
            raise ValueError(f"assistant_afterglow doppelte Job-ID: {job_id}")
        by_job[job_id] = {"job_id": job_id, "label": label}

    entries = text_catalog.get("entries")
    if not isinstance(entries, Mapping):
        raise ValueError("assistant_afterglow Textkatalog benötigt entries")
    for job_id in by_job:
        text = entries.get(job_id)
        if not isinstance(text, Mapping):
            raise ValueError(f"assistant_afterglow Text fehlt für {job_id}")
        for field in ("headline", "body"):
            value = text.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"assistant_afterglow {job_id}.{field} fehlt")

    records_copy = [deepcopy(dict(record)) for record in records if isinstance(record, Mapping)]
    durable_jobs = {
        record.get("event_id"): record
        for record in records_copy
        if record.get("event_type") == "finance.job_completed" and isinstance(record.get("event_id"), str)
    }

    projected: list[dict[str, Any]] = []
    for record in records_copy:
        if record.get("event_type") != "assistant.round_processed":
            continue
        payload = record.get("payload")
        if not isinstance(payload, Mapping):
            continue
        job_id = payload.get("job_id")
        if job_id is None:
            continue
        round_id = payload.get("round_id")
        character_id = payload.get("character_id")
        if not all(isinstance(value, str) and value.strip() for value in (job_id, round_id, character_id)):
            continue
        if job_id not in by_job:
            raise ValueError(f"assistant_afterglow Marker verweist auf unbekannten Scene Job: {job_id}")

        processed_event_id = record.get("event_id")
        expected_prefix = f"assistant:{character_id}:round:{round_id}"
        if processed_event_id != f"{expected_prefix}:processed":
            continue
        durable = durable_jobs.get(f"{expected_prefix}:job")
        durable_payload = durable.get("payload") if isinstance(durable, Mapping) else None
        if not isinstance(durable_payload, Mapping) or durable_payload.get("job_id") != job_id:
            continue

        text = entries[job_id]
        sequence = record.get("sequence")
        projected.append({
            "sequence": sequence if isinstance(sequence, int) else 0,
            "round_id": round_id,
            "job_id": job_id,
            "job_label": by_job[job_id]["label"],
            "headline": text["headline"],
            "body": text["body"],
        })

    projected.sort(key=lambda item: (item["sequence"], item["round_id"]))
    latest = projected[-limit:]
    return {
        "available": bool(latest),
        "entries": latest,
        "source": "confirmed_assistant_round_and_scene_job",
    }
