from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.presentation.event_timeline import build_event_timeline_projection


def build_district_biography_projection(
    journal_records: Sequence[Mapping[str, Any]],
    *,
    street_text_catalog: Mapping[str, str],
    district_event_manifest: Mapping[str, Any],
    district_text_catalog: Mapping[str, str],
    incident_catalog: Mapping[str, Mapping[str, Any]],
    incident_text_catalog: Mapping[str, str],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Project confirmed district events into small read-only biography memories.

    The event timeline remains the validation/translation source. This projection
    only filters confirmed district entries and never creates journal records,
    progression, timestamps or gameplay effects.
    """
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("Biografie-Limit muss positive Ganzzahl sein")

    timeline = build_event_timeline_projection(
        journal_records,
        street_text_catalog=street_text_catalog,
        district_event_manifest=district_event_manifest,
        district_text_catalog=district_text_catalog,
        incident_catalog=incident_catalog,
        incident_text_catalog=incident_text_catalog,
        limit=max(200, limit),
    )

    memories: list[dict[str, Any]] = []
    for entry in timeline:
        if entry.get("kind") != "district":
            continue
        metadata = entry.get("metadata")
        if not isinstance(metadata, Mapping):
            continue
        district_id = metadata.get("district_id")
        district_event_id = metadata.get("district_event_id")
        if not all(isinstance(value, str) and value for value in (district_id, district_event_id)):
            continue
        memories.append({
            "memory_id": f"district-memory:{entry['event_id']}",
            "source_event_id": entry["event_id"],
            "sequence": entry["sequence"],
            "district_id": district_id,
            "district_event_id": district_event_id,
            "title": entry["title"],
            "body": entry["body"],
            "deltas": deepcopy(dict(metadata.get("deltas") or {})),
        })

    memories.sort(key=lambda item: (item["sequence"], item["source_event_id"]))
    return deepcopy(memories[-limit:])
