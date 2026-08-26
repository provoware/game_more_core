from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


SUPPORTED_EVENT_TYPES = frozenset({
    "street.encounter_resolved",
    "world.district_effect_applied",
    "world.district_followup_resolved",
    "event.incident_resolved",
})
DISTRICT_METRICS = ("heat", "prestige", "police_pressure", "scene_activity")


def build_event_timeline_projection(
    journal_records: Sequence[Mapping[str, Any]],
    *,
    street_text_catalog: Mapping[str, str],
    district_event_manifest: Mapping[str, Any],
    district_text_catalog: Mapping[str, str],
    incident_catalog: Mapping[str, Mapping[str, Any]],
    incident_text_catalog: Mapping[str, str],
    limit: int = 12,
) -> list[dict[str, Any]]:
    """Project confirmed journal records into a compact read-only story timeline.

    The journal remains the only ordering/source authority. Unknown or malformed
    records are ignored instead of inventing fallback story content.
    """
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise ValueError("Timeline-Limit muss positive Ganzzahl sein")

    district_specs = _district_specs(district_event_manifest)
    projected: list[dict[str, Any]] = []
    for raw in journal_records:
        if not isinstance(raw, Mapping):
            continue
        event_type = raw.get("event_type")
        if event_type not in SUPPORTED_EVENT_TYPES:
            continue
        sequence = raw.get("sequence")
        event_id = raw.get("event_id")
        payload = raw.get("payload")
        if (
            isinstance(sequence, bool)
            or not isinstance(sequence, int)
            or sequence <= 0
            or not isinstance(event_id, str)
            or not event_id
            or not isinstance(payload, Mapping)
        ):
            continue

        entry: dict[str, Any] | None
        if event_type == "street.encounter_resolved":
            entry = _street_entry(sequence, event_id, payload, street_text_catalog)
        elif event_type == "world.district_effect_applied":
            entry = _district_entry(
                sequence,
                event_id,
                payload,
                district_specs,
                district_text_catalog,
            )
        elif event_type == "world.district_followup_resolved":
            entry = _district_followup_entry(
                sequence,
                event_id,
                payload,
                district_text_catalog,
                causation_id=raw.get("causation_id"),
            )
        else:
            entry = _incident_entry(
                sequence,
                event_id,
                payload,
                incident_catalog,
                incident_text_catalog,
            )
        if entry is not None:
            projected.append(entry)

    _attach_district_causes(projected)
    projected.sort(key=lambda item: (item["sequence"], item["event_id"]))
    return deepcopy(projected[-limit:])


def _street_entry(
    sequence: int,
    event_id: str,
    payload: Mapping[str, Any],
    texts: Mapping[str, str],
) -> dict[str, Any] | None:
    title_key = payload.get("title_key")
    body_key = payload.get("body_key")
    encounter_id = payload.get("encounter_id")
    polarity = payload.get("polarity")
    if not all(isinstance(value, str) and value for value in (title_key, body_key, encounter_id, polarity)):
        return None
    title = texts.get(title_key)
    body = texts.get(body_key)
    if not isinstance(title, str) or not title or not isinstance(body, str) or not body:
        return None
    approach_id = payload.get("approach_id")
    if not isinstance(approach_id, str) or not approach_id:
        approach_id = "balanced"
    return {
        "sequence": sequence,
        "event_id": event_id,
        "kind": "street",
        "title": title,
        "body": body,
        "metadata": {
            "encounter_id": encounter_id,
            "polarity": polarity,
            "approach_id": approach_id,
        },
    }


def _district_entry(
    sequence: int,
    event_id: str,
    payload: Mapping[str, Any],
    specs: Mapping[str, Mapping[str, Any]],
    texts: Mapping[str, str],
) -> dict[str, Any] | None:
    if payload.get("source_type") != "district_event":
        return None
    source_id = payload.get("source_id")
    district_id = payload.get("district_id")
    if not isinstance(source_id, str) or not source_id or not isinstance(district_id, str) or not district_id:
        return None
    catalog_event_id = source_id.rsplit(":", 1)[-1]
    spec = specs.get(catalog_event_id)
    if spec is None:
        return None
    title_key = spec.get("title_key")
    body_key = spec.get("body_key")
    title = texts.get(title_key) if isinstance(title_key, str) else None
    body = texts.get(body_key) if isinstance(body_key, str) else None
    if not isinstance(title, str) or not title or not isinstance(body, str) or not body:
        return None
    return {
        "sequence": sequence,
        "event_id": event_id,
        "kind": "district",
        "title": title,
        "body": body,
        "metadata": {
            "district_id": district_id,
            "district_event_id": catalog_event_id,
            "deltas": _district_deltas(payload.get("deltas")),
        },
    }


def _district_followup_entry(
    sequence: int,
    event_id: str,
    payload: Mapping[str, Any],
    texts: Mapping[str, str],
    *,
    causation_id: Any,
) -> dict[str, Any] | None:
    parent_event_id = payload.get("parent_event_id")
    district_id = payload.get("district_id")
    followup_id = payload.get("followup_id")
    title_key = payload.get("title_key")
    body_key = payload.get("body_key")
    required = (parent_event_id, district_id, followup_id, title_key, body_key, causation_id)
    if not all(isinstance(value, str) and value for value in required):
        return None
    if causation_id != parent_event_id:
        return None
    title = texts.get(title_key)
    body = texts.get(body_key)
    if not isinstance(title, str) or not title or not isinstance(body, str) or not body:
        return None
    return {
        "sequence": sequence,
        "event_id": event_id,
        "kind": "district",
        "title": title,
        "body": body,
        "metadata": {
            "district_id": district_id,
            "followup_id": followup_id,
            "parent_event_id": parent_event_id,
        },
    }


def _attach_district_causes(projected: Sequence[dict[str, Any]]) -> None:
    parents: dict[str, dict[str, Any]] = {}
    for entry in projected:
        metadata = entry.get("metadata")
        if (
            entry.get("kind") == "district"
            and isinstance(metadata, Mapping)
            and isinstance(metadata.get("district_event_id"), str)
        ):
            parents[entry["event_id"]] = entry

    for entry in projected:
        metadata = entry.get("metadata")
        if not isinstance(metadata, Mapping) or not isinstance(metadata.get("followup_id"), str):
            continue
        parent_id = metadata.get("parent_event_id")
        parent = parents.get(parent_id) if isinstance(parent_id, str) else None
        if parent is None:
            continue
        parent_metadata = parent.get("metadata")
        if not isinstance(parent_metadata, Mapping):
            continue
        if parent_metadata.get("district_id") != metadata.get("district_id"):
            continue
        if parent.get("sequence", 0) >= entry.get("sequence", 0):
            continue
        entry["caused_by"] = {
            "event_id": parent["event_id"],
            "title": parent["title"],
        }


def _incident_entry(
    sequence: int,
    event_id: str,
    payload: Mapping[str, Any],
    catalog: Mapping[str, Mapping[str, Any]],
    texts: Mapping[str, str],
) -> dict[str, Any] | None:
    incident_type = payload.get("incident_type")
    response_id = payload.get("response_id")
    if not isinstance(incident_type, str) or not incident_type or not isinstance(response_id, str) or not response_id:
        return None
    spec = catalog.get(incident_type)
    if not isinstance(spec, Mapping):
        return None
    responses = spec.get("responses")
    response = responses.get(response_id) if isinstance(responses, Mapping) else None
    if not isinstance(response, Mapping):
        return None
    title_key = spec.get("title_key")
    label_key = response.get("label_key")
    title = texts.get(title_key) if isinstance(title_key, str) else None
    body = texts.get(label_key) if isinstance(label_key, str) else None
    if not isinstance(title, str) or not title or not isinstance(body, str) or not body:
        return None
    target_phase = payload.get("target_phase")
    if not isinstance(target_phase, str) or not target_phase:
        target_phase = None
    return {
        "sequence": sequence,
        "event_id": event_id,
        "kind": "crisis",
        "title": title,
        "body": body,
        "metadata": {
            "incident_type": incident_type,
            "response_id": response_id,
            "target_phase": target_phase,
        },
    }


def _district_deltas(raw: Any) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, int] = {}
    for metric in DISTRICT_METRICS:
        value = raw.get(metric)
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        result[metric] = value
    return result


def _district_specs(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    events = manifest.get("events")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise ValueError("District-Event-Manifest besitzt keine Ereignisliste")
    result: dict[str, Mapping[str, Any]] = {}
    for raw in events:
        if not isinstance(raw, Mapping):
            continue
        event_id = raw.get("event_id")
        if isinstance(event_id, str) and event_id and event_id not in result:
            result[event_id] = raw
    return result
