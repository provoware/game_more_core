from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.domain.district import DistrictState
from bunkerfrequenz.presentation.city_map_projection import build_city_map_projection


def _json_stable(value: Any) -> Any:
    """Normalize tuple-based presentation internals for A4 JSON/restart equality."""
    if isinstance(value, tuple):
        return [_json_stable(item) for item in value]
    if isinstance(value, list):
        return [_json_stable(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_stable(item) for key, item in value.items()}
    return deepcopy(value)


def build_living_district_projection(
    raw_state: Mapping[str, Any] | None,
    *,
    district_manifest: Mapping[str, Any],
    city_map_manifest: Mapping[str, Any],
    owned_property_ids: set[str] | frozenset[str] = frozenset(),
    location_value_overrides: Mapping[str, Mapping[str, int]] | None = None,
) -> dict[str, Any]:
    version = district_manifest.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError("District-Manifest besitzt keine Version")
    if district_manifest.get("city_map_manifest_version") != city_map_manifest.get("version"):
        raise ValueError("District- und City-Map-Vertrag passen nicht zusammen")
    districts = city_map_manifest.get("districts")
    defaults = city_map_manifest.get("district_metric_defaults")
    if not isinstance(districts, list) or not isinstance(defaults, Mapping):
        raise ValueError("City-Map besitzt keine gültige District-Grundlage")
    district_ids = [item.get("district_id") for item in districts]
    if any(not isinstance(item, str) or not item for item in district_ids):
        raise ValueError("City-Map besitzt ungültige District-IDs")

    if raw_state is None:
        state = DistrictState.from_city_map(
            contract_version=version,
            district_ids=district_ids,
            defaults=defaults,
        )
        persisted = False
    else:
        state = DistrictState.from_dict(raw_state)
        if state.contract_version != version:
            raise ValueError("Persistierter District-State besitzt falsche Vertragsversion")
        if set(state.metrics) != set(district_ids):
            raise ValueError("Persistierter District-State passt nicht zur City-Map")
        persisted = True

    labels = {item["district_id"]: item.get("label_key") for item in districts}
    entries = [
        {
            "district_id": district_id,
            "label_key": labels[district_id],
            "metrics": deepcopy(state.metrics[district_id]),
        }
        for district_id in district_ids
    ]
    city_map = build_city_map_projection(
        dict(city_map_manifest),
        owned_property_ids=frozenset(owned_property_ids),
        district_metrics=state.metrics,
        location_value_overrides=location_value_overrides,
    )
    return {
        "contract_version": version,
        "persisted": persisted,
        "revision": state.revision,
        "last_change": deepcopy(state.last_change),
        "entries": entries,
        "city_map": _json_stable(city_map),
    }
