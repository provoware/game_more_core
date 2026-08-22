from __future__ import annotations

from copy import deepcopy
from typing import Any


_VALUE_KEYS = ("prestige", "audience_pull", "risk", "underground_factor", "utility")
_DISTRICT_METRICS = ("heat", "prestige", "police_pressure", "scene_activity")


def _bounded_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise ValueError(f"{field_name} muss Ganzzahl zwischen 0 und 100 sein")
    return value


def _score(values: dict[str, int]) -> float:
    for key in _VALUE_KEYS:
        _bounded_int(values.get(key), f"values.{key}")
    return round(
        values["prestige"] * 0.30
        + values["audience_pull"] * 0.25
        + values["underground_factor"] * 0.20
        + values["utility"] * 0.20
        + (100 - values["risk"]) * 0.05,
        1,
    )


def _tier(score: float, thresholds: list[dict[str, Any]]) -> str:
    normalized = sorted(thresholds, key=lambda item: item["minimum_score"], reverse=True)
    for item in normalized:
        minimum = item.get("minimum_score")
        tier = item.get("tier")
        if not isinstance(minimum, (int, float)) or not isinstance(tier, str) or not tier:
            raise ValueError("highlight_thresholds sind ungültig")
        if score >= minimum:
            return tier
    raise ValueError("highlight_thresholds benötigen eine 0-Basis")


def build_city_map_projection(
    manifest: dict[str, Any],
    *,
    owned_property_ids: set[str] | frozenset[str] = frozenset(),
    district_metrics: dict[str, dict[str, int]] | None = None,
) -> dict[str, Any]:
    if manifest.get("version") != "0.8.3-b2-foundation":
        raise ValueError("CITY_MAP_MANIFEST besitzt unerwartete Version")
    if manifest.get("geography_mode") != "stylized_game_map_not_navigation":
        raise ValueError("Berlin Ops Map muss als stilisierte Spielkarte markiert sein")

    districts = manifest.get("districts")
    locations = manifest.get("locations")
    thresholds = manifest.get("highlight_thresholds")
    defaults = manifest.get("district_metric_defaults")
    if not isinstance(districts, list) or not isinstance(locations, list) or not isinstance(thresholds, list):
        raise ValueError("CITY_MAP_MANIFEST besitzt ungültige Kernlisten")
    if not isinstance(defaults, dict) or set(defaults) != set(_DISTRICT_METRICS):
        raise ValueError("district_metric_defaults sind ungültig")
    for key in _DISTRICT_METRICS:
        _bounded_int(defaults[key], f"district_metric_defaults.{key}")

    district_ids: set[str] = set()
    district_projection = []
    overrides = district_metrics or {}
    if not isinstance(overrides, dict):
        raise ValueError("district_metrics muss ein Mapping sein")
    for district in districts:
        district_id = district.get("district_id")
        if not isinstance(district_id, str) or not district_id or district_id in district_ids:
            raise ValueError("District-IDs müssen eindeutig sein")
        district_ids.add(district_id)
        box = district.get("map_box")
        if not isinstance(box, dict) or set(box) != {"x", "y", "w", "h"}:
            raise ValueError("District benötigt map_box x/y/w/h")
        for key, value in box.items():
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                raise ValueError(f"map_box.{key} liegt außerhalb der Kartenfläche")
        metrics = dict(defaults)
        if district_id in overrides:
            override = overrides[district_id]
            if not isinstance(override, dict) or set(override) - set(_DISTRICT_METRICS):
                raise ValueError("Unbekannte District-Metrik")
            metrics.update(override)
        for key in _DISTRICT_METRICS:
            _bounded_int(metrics[key], f"district.{district_id}.{key}")
        district_projection.append({
            "district_id": district_id,
            "label_key": district["label_key"],
            "map_box": deepcopy(box),
            "metrics": metrics,
        })
    unknown_districts = set(overrides) - district_ids
    if unknown_districts:
        raise ValueError("district_metrics enthält unbekannte District-ID")

    location_ids: set[str] = set()
    purchasable_ids: set[str] = set()
    location_projection = []
    tribute_count = 0
    upgrade_ids = {item["upgrade_id"] for item in manifest.get("property_upgrade_catalog", [])}
    for location in locations:
        location_id = location.get("location_id")
        if not isinstance(location_id, str) or not location_id or location_id in location_ids:
            raise ValueError("Location-IDs müssen eindeutig sein")
        location_ids.add(location_id)
        if location.get("district_id") not in district_ids:
            raise ValueError("Location verweist auf unbekannten District")
        position = location.get("position")
        if not isinstance(position, dict) or set(position) != {"x", "y"}:
            raise ValueError("Location benötigt x/y-Position")
        for key in ("x", "y"):
            value = position[key]
            if not isinstance(value, (int, float)) or not 0 <= value <= 100:
                raise ValueError("Location-Position liegt außerhalb der Kartenfläche")
        values = location.get("values")
        if not isinstance(values, dict) or set(values) != set(_VALUE_KEYS):
            raise ValueError("Location-Werte sind unvollständig")
        score = _score(values)
        purchasable = location.get("purchasable") is True
        purchase_price = location.get("purchase_price_cents")
        slots = list(location.get("upgrade_slots", []))
        if purchasable:
            purchasable_ids.add(location_id)
            if isinstance(purchase_price, bool) or not isinstance(purchase_price, int) or purchase_price < 1:
                raise ValueError("Kaufbare Location benötigt purchase_price_cents")
            if not slots or any(slot not in upgrade_ids for slot in slots):
                raise ValueError("Kaufbare Location besitzt ungültige upgrade_slots")
        elif purchase_price is not None or slots:
            raise ValueError("Nicht kaufbare Location darf keine Kaufdaten besitzen")
        is_tribute = location.get("category") == "tribute_hall"
        tribute_count += int(is_tribute)
        location_projection.append({
            "location_id": location_id,
            "label_key": location["label_key"],
            "district_id": location["district_id"],
            "category": location["category"],
            "position": deepcopy(position),
            "values": dict(values),
            "score": score,
            "tier": _tier(score, thresholds),
            "purchasable": purchasable,
            "purchase_price_cents": purchase_price if purchasable else None,
            "upgrade_slots": slots,
            "owned": purchasable and location_id in owned_property_ids,
            "ranking_enabled": location.get("ranking_enabled") is True,
            "special_effect": location.get("special_effect"),
            "is_hall_of_tribute": is_tribute,
        })
    if tribute_count != 1:
        raise ValueError("Berlin Ops Map benötigt exakt eine Hall of Tribute")
    invalid_owned = set(owned_property_ids) - purchasable_ids
    if invalid_owned:
        raise ValueError("owned_property_ids enthält unbekannte oder nicht kaufbare Location")

    ranked = sorted(location_projection, key=lambda item: (-item["score"], item["location_id"]))
    rank_by_id = {item["location_id"]: index + 1 for index, item in enumerate(ranked)}
    for item in location_projection:
        item["rank"] = rank_by_id[item["location_id"]]

    return {
        "map_id": manifest["map_id"],
        "version": manifest["version"],
        "geography_mode": manifest["geography_mode"],
        "visual_style": deepcopy(manifest["visual_style"]),
        "districts": tuple(district_projection),
        "locations": tuple(location_projection),
        "top_locations": tuple(deepcopy(ranked[:5])),
        "hall_of_tribute": deepcopy(next(item for item in location_projection if item["is_hall_of_tribute"])),
    }
