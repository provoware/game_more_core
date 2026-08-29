from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.domain.property_upgrade import (
    MAX_UPGRADE_LEVEL,
    VENUE_VALUE_KEYS,
    PropertyUpgradeState,
    effective_venue_values,
    upgrade_cost_cents,
)


def build_property_upgrade_projection(
    raw_state: Mapping[str, Any] | None,
    *,
    upgrade_manifest: Mapping[str, Any],
    city_map_manifest: Mapping[str, Any],
    property_projection: Mapping[str, Any],
) -> dict[str, Any]:
    version = upgrade_manifest.get("version")
    if version != "0.8.6-b1":
        raise ValueError("Property-Upgrade-Manifest besitzt unerwartete Version")
    if upgrade_manifest.get("city_map_manifest_version") != city_map_manifest.get("version"):
        raise ValueError("Property-Upgrade- und City-Map-Vertrag passen nicht zusammen")
    if upgrade_manifest.get("max_level") != MAX_UPGRADE_LEVEL:
        raise ValueError("Property-Upgrade-Maxlevel weicht von der Domain ab")

    catalog = upgrade_manifest.get("catalog")
    multipliers = upgrade_manifest.get("level_cost_multipliers_bps")
    if not isinstance(catalog, Mapping) or not catalog:
        raise ValueError("Property-Upgrade-Katalog fehlt")
    if not isinstance(multipliers, list) or len(multipliers) != MAX_UPGRADE_LEVEL:
        raise ValueError("Property-Upgrade-Kostenstufen sind ungültig")

    locations = city_map_manifest.get("locations")
    map_catalog = city_map_manifest.get("property_upgrade_catalog")
    if not isinstance(locations, list) or not isinstance(map_catalog, list):
        raise ValueError("City-Map besitzt keine gültige Property-Upgrade-Grundlage")
    labels = {
        item.get("upgrade_id"): item.get("label_key")
        for item in map_catalog
        if isinstance(item, Mapping)
    }
    location_by_id = {
        item.get("location_id"): item
        for item in locations
        if isinstance(item, Mapping) and isinstance(item.get("location_id"), str)
    }

    if raw_state is None:
        state = PropertyUpgradeState(contract_version=version)
        persisted = False
    else:
        state = PropertyUpgradeState.from_dict(raw_state)
        if state.contract_version != version:
            raise ValueError("Persistierter Property-Upgrade-State besitzt falsche Vertragsversion")
        persisted = True

    property_entries = property_projection.get("entries")
    if not isinstance(property_entries, list):
        raise ValueError("Property-Projection besitzt keine gültigen Einträge")
    owned_ids = {
        item.get("location_id")
        for item in property_entries
        if isinstance(item, Mapping) and item.get("owned") is True
    }
    if set(state.properties) - owned_ids:
        raise ValueError("Property-Upgrade-State verweist auf nicht besessene Location")

    entries: list[dict[str, Any]] = []
    levels_by_location: dict[str, dict[str, int]] = {}
    effective_values_by_location: dict[str, dict[str, int]] = {}

    for property_entry in property_entries:
        if not isinstance(property_entry, Mapping):
            raise ValueError("Property-Projection-Eintrag muss Mapping sein")
        location_id = property_entry.get("location_id")
        if not isinstance(location_id, str) or location_id not in location_by_id:
            raise ValueError("Property-Projection verweist auf unbekannte Location")
        location = location_by_id[location_id]
        values = location.get("values")
        slots = location.get("upgrade_slots", [])
        if not isinstance(values, Mapping) or set(values) != set(VENUE_VALUE_KEYS):
            raise ValueError("Location besitzt ungültige Basiswerte")
        if not isinstance(slots, list) or any(slot not in catalog for slot in slots):
            raise ValueError("Location besitzt ungültige Upgrade-Slots")

        record = state.properties.get(location_id, {"location_id": location_id, "upgrades": {}})
        if set(record["upgrades"]) - set(slots):
            raise ValueError("Persistierter Property-Upgrade-State passt nicht zu den Location-Slots")
        levels: dict[str, int] = {}
        upgrades_out: list[dict[str, Any]] = []
        owned = property_entry.get("owned") is True
        purchase_price = property_entry.get("purchase_price_cents")
        if isinstance(purchase_price, bool) or not isinstance(purchase_price, int) or purchase_price < 1:
            raise ValueError("Property-Projection besitzt ungültigen Kaufpreis")

        for slot in slots:
            current = record["upgrades"].get(slot)
            level = 0 if current is None else current["level"]
            levels[slot] = level
            spec = catalog[slot]
            if not isinstance(spec, Mapping):
                raise ValueError("Property-Upgrade-Katalogeintrag muss Mapping sein")
            deltas = spec.get("value_delta_per_level")
            cost_bps = spec.get("cost_bps")
            if not isinstance(deltas, Mapping) or set(deltas) != set(VENUE_VALUE_KEYS):
                raise ValueError("Property-Upgrade-Wertedeltas sind ungültig")
            if isinstance(cost_bps, bool) or not isinstance(cost_bps, int) or cost_bps < 1:
                raise ValueError("Property-Upgrade-Kostenfaktor ist ungültig")

            next_level = level + 1 if level < MAX_UPGRADE_LEVEL else None
            next_cost = None
            if owned and next_level is not None:
                next_cost = upgrade_cost_cents(
                    purchase_price,
                    cost_bps,
                    multipliers[next_level - 1],
                )
            upgrades_out.append({
                "upgrade_id": slot,
                "label_key": labels.get(slot),
                "level": level,
                "max_level": MAX_UPGRADE_LEVEL,
                "next_level": next_level,
                "next_cost_cents": next_cost,
                "can_upgrade": owned and next_level is not None,
                "value_delta_per_level": deepcopy(dict(deltas)),
            })

        effective = effective_venue_values(
            values,
            upgrade_slots=slots,
            upgrade_levels=levels,
            upgrade_catalog=catalog,
        )
        levels_by_location[location_id] = levels
        effective_values_by_location[location_id] = effective
        entries.append({
            "location_id": location_id,
            "owned": owned,
            "effective_values": deepcopy(effective) if owned else None,
            "upgrades": upgrades_out,
        })

    return {
        "contract_version": version,
        "persisted": persisted,
        "revision": state.revision,
        "max_level": MAX_UPGRADE_LEVEL,
        "entries": entries,
        "levels_by_location": levels_by_location,
        "effective_values_by_location": effective_values_by_location,
        "policy": {
            "client_cost_authority": False,
            "client_level_authority": False,
            "resale_supported": False,
            "rent_supported": False,
        },
    }
