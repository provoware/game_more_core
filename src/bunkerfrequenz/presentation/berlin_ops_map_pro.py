from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


_DISTRICT_METRICS = ("heat", "prestige", "police_pressure", "scene_activity")
_LOCATION_VALUES = ("prestige", "audience_pull", "risk", "underground_factor", "utility")


def _bounded_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise ValueError(f"{field_name} muss Ganzzahl zwischen 0 und 100 sein")
    return value


def _coordinate(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 100:
        raise ValueError(f"{field_name} muss zwischen 0 und 100 liegen")
    return float(value)


def build_berlin_ops_map_pro_projection(
    living_districts: Mapping[str, Any],
    *,
    property_upgrades: Mapping[str, Any] | None,
    map_pro_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Compose confirmed read-only world projections for the visual Berlin map.

    This adapter has no gameplay authority. It validates and copies already
    confirmed District/CityMap/PropertyUpgrade projection data into a renderer-
    friendly shape. Score, tier, ownership, costs and upgrade levels are never
    recomputed here.
    """
    if map_pro_manifest.get("version") != "0.8.6-c1":
        raise ValueError("Berlin-Ops-Map-PRO-Manifest besitzt unerwartete Version")
    if map_pro_manifest.get("geography_mode") != "stylized_game_map_not_navigation":
        raise ValueError("Berlin Ops Map PRO darf keine Navigationskarte sein")
    if map_pro_manifest.get("source_city_map_version") != "0.8.3-b2-foundation":
        raise ValueError("Berlin-Ops-Map-PRO-Manifest referenziert falschen City-Map-Vertrag")
    interaction = map_pro_manifest.get("interaction")
    if not isinstance(interaction, Mapping) or interaction.get("domain_write") is not False:
        raise ValueError("Berlin Ops Map PRO muss read-only bleiben")

    city_map = living_districts.get("city_map")
    if not isinstance(city_map, Mapping):
        raise ValueError("Living-District-Projection besitzt keine City-Map")
    if city_map.get("version") != map_pro_manifest["source_city_map_version"]:
        raise ValueError("City-Map und Berlin-Ops-Map-PRO-Vertrag passen nicht zusammen")
    if city_map.get("geography_mode") != map_pro_manifest["geography_mode"]:
        raise ValueError("City-Map besitzt unerwarteten Geography-Modus")

    tier_order = map_pro_manifest.get("tier_order")
    filters = map_pro_manifest.get("filters")
    if not isinstance(tier_order, list) or not tier_order or any(not isinstance(item, str) for item in tier_order):
        raise ValueError("Map-PRO tier_order ist ungültig")
    if filters != ["all", "owned", "prime", "hall"]:
        raise ValueError("Map-PRO Filtervertrag ist unerwartet")
    tier_set = set(tier_order)

    raw_districts = city_map.get("districts")
    raw_locations = city_map.get("locations")
    if not isinstance(raw_districts, list) or not raw_districts:
        raise ValueError("City-Map besitzt keine Districts")
    if not isinstance(raw_locations, list) or not raw_locations:
        raise ValueError("City-Map besitzt keine Locations")

    districts: list[dict[str, Any]] = []
    district_ids: set[str] = set()
    for raw in raw_districts:
        if not isinstance(raw, Mapping):
            raise ValueError("Map-District muss Mapping sein")
        district_id = raw.get("district_id")
        if not isinstance(district_id, str) or not district_id or district_id in district_ids:
            raise ValueError("Map-District-ID fehlt oder ist doppelt")
        district_ids.add(district_id)
        box = raw.get("map_box")
        metrics = raw.get("metrics")
        if not isinstance(box, Mapping) or set(box) != {"x", "y", "w", "h"}:
            raise ValueError("Map-District benötigt x/y/w/h")
        if not isinstance(metrics, Mapping) or set(metrics) != set(_DISTRICT_METRICS):
            raise ValueError("Map-District besitzt unvollständige Metriken")
        normalized_box = {key: _coordinate(box[key], f"district.{district_id}.{key}") for key in ("x", "y", "w", "h")}
        if normalized_box["x"] + normalized_box["w"] > 100 or normalized_box["y"] + normalized_box["h"] > 100:
            raise ValueError("Map-District ragt aus der Kartenfläche")
        normalized_metrics = {
            key: _bounded_int(metrics[key], f"district.{district_id}.{key}")
            for key in _DISTRICT_METRICS
        }
        districts.append({
            "district_id": district_id,
            "label_key": raw.get("label_key"),
            "map_box": normalized_box,
            "metrics": normalized_metrics,
        })

    upgrade_by_location: dict[str, Mapping[str, Any]] = {}
    if property_upgrades is not None:
        raw_upgrade_entries = property_upgrades.get("entries")
        if not isinstance(raw_upgrade_entries, list):
            raise ValueError("Property-Upgrade-Projection besitzt keine Einträge")
        for raw in raw_upgrade_entries:
            if not isinstance(raw, Mapping):
                raise ValueError("Property-Upgrade-Eintrag muss Mapping sein")
            location_id = raw.get("location_id")
            if not isinstance(location_id, str) or not location_id or location_id in upgrade_by_location:
                raise ValueError("Property-Upgrade-Location-ID fehlt oder ist doppelt")
            upgrade_by_location[location_id] = raw

    locations: list[dict[str, Any]] = []
    location_ids: set[str] = set()
    hall_count = 0
    owned_count = 0
    for raw in raw_locations:
        if not isinstance(raw, Mapping):
            raise ValueError("Map-Location muss Mapping sein")
        location_id = raw.get("location_id")
        if not isinstance(location_id, str) or not location_id or location_id in location_ids:
            raise ValueError("Map-Location-ID fehlt oder ist doppelt")
        location_ids.add(location_id)
        district_id = raw.get("district_id")
        if district_id not in district_ids:
            raise ValueError("Map-Location verweist auf unbekannten District")
        position = raw.get("position")
        values = raw.get("values")
        tier = raw.get("tier")
        score = raw.get("score")
        if not isinstance(position, Mapping) or set(position) != {"x", "y"}:
            raise ValueError("Map-Location benötigt x/y")
        if not isinstance(values, Mapping) or set(values) != set(_LOCATION_VALUES):
            raise ValueError("Map-Location besitzt unvollständige Werte")
        if tier not in tier_set:
            raise ValueError("Map-Location besitzt unbekanntes Tier")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
            raise ValueError("Map-Location besitzt ungültigen Score")
        owned = raw.get("owned") is True
        is_hall = raw.get("is_hall_of_tribute") is True
        owned_count += int(owned)
        hall_count += int(is_hall)

        upgrade_entry = upgrade_by_location.get(location_id)
        upgrades: list[dict[str, Any]] = []
        if upgrade_entry is not None:
            raw_upgrades = upgrade_entry.get("upgrades")
            if not isinstance(raw_upgrades, list):
                raise ValueError("Map-Upgrade-Eintrag besitzt keine Upgrades")
            for upgrade in raw_upgrades:
                if not isinstance(upgrade, Mapping):
                    raise ValueError("Map-Upgrade muss Mapping sein")
                level = upgrade.get("level")
                if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 3:
                    raise ValueError("Map-Upgrade-Level ist ungültig")
                upgrade_id = upgrade.get("upgrade_id")
                if not isinstance(upgrade_id, str) or not upgrade_id:
                    raise ValueError("Map-Upgrade-ID fehlt")
                upgrades.append({
                    "upgrade_id": upgrade_id,
                    "label_key": upgrade.get("label_key"),
                    "level": level,
                    "max_level": upgrade.get("max_level"),
                })

        locations.append({
            "location_id": location_id,
            "label_key": raw.get("label_key"),
            "district_id": district_id,
            "category": raw.get("category"),
            "position": {
                "x": _coordinate(position["x"], f"location.{location_id}.x"),
                "y": _coordinate(position["y"], f"location.{location_id}.y"),
            },
            "values": {
                key: _bounded_int(values[key], f"location.{location_id}.{key}")
                for key in _LOCATION_VALUES
            },
            "score": float(score),
            "tier": tier,
            "rank": raw.get("rank"),
            "purchasable": raw.get("purchasable") is True,
            "purchase_price_cents": raw.get("purchase_price_cents"),
            "owned": owned,
            "is_hall_of_tribute": is_hall,
            "upgrades": upgrades,
            "upgrade_level_total": sum(item["level"] for item in upgrades),
            "maxed_upgrade_count": sum(1 for item in upgrades if item["level"] == item["max_level"]),
        })

    unknown_upgrade_locations = set(upgrade_by_location) - location_ids
    if unknown_upgrade_locations:
        raise ValueError("Property-Upgrade-Projection enthält unbekannte Map-Location")
    if hall_count != 1:
        raise ValueError("Berlin Ops Map PRO benötigt exakt eine Hall of Tribute")

    return {
        "version": map_pro_manifest["version"],
        "map_id": city_map.get("map_id"),
        "geography_mode": city_map.get("geography_mode"),
        "districts": districts,
        "locations": locations,
        "filters": list(filters),
        "tier_order": list(tier_order),
        "summary": {
            "district_count": len(districts),
            "location_count": len(locations),
            "owned_count": owned_count,
            "hall_count": hall_count,
        },
        "policy": {
            "read_only": True,
            "domain_write": False,
            "navigation": False,
            "geocoding": False,
            "coordinates": "stylized_0_100",
        },
        "accessibility": deepcopy(dict(map_pro_manifest.get("accessibility", {}))),
    }
