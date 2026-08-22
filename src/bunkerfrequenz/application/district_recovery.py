from __future__ import annotations

from typing import Any, Mapping

from bunkerfrequenz.domain.district import DistrictState


def replay_district_event(derived_state: dict[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    if record.get("event_type") != "world.district_effect_applied":
        return derived_state
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("District-Replay benötigt Payload")
    raw_state = payload.get("district_state")
    if not isinstance(raw_state, Mapping):
        raise ValueError("District-Replay benötigt district_state")
    state = DistrictState.from_dict(raw_state)
    source_id = payload.get("source_id")
    district_id = payload.get("district_id")
    if not isinstance(source_id, str) or source_id not in state.applied_sources:
        raise ValueError("District-Replay-Quelle fehlt im bestätigten State")
    if not isinstance(district_id, str) or district_id not in state.metrics:
        raise ValueError("District-Replay verweist auf unbekannten Bezirk")
    last_change = state.last_change
    if not isinstance(last_change, dict):
        raise ValueError("District-Replay benötigt last_change")
    if last_change.get("source_id") != source_id or last_change.get("district_id") != district_id:
        raise ValueError("District-Replay-State passt nicht zum Journalrecord")
    if payload.get("contract_version") != state.contract_version:
        raise ValueError("District-Replay-Vertragsversion ist inkonsistent")
    result = dict(derived_state)
    result["districts"] = state.to_dict()
    return result
