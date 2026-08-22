from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.domain.property import PropertyState


def build_property_projection(
    raw_state: Mapping[str, Any] | None,
    *,
    property_manifest: Mapping[str, Any],
    city_map_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    version = property_manifest.get("version")
    if version != "0.8.6-a1":
        raise ValueError("Property-Manifest besitzt unerwartete Version")
    if property_manifest.get("city_map_manifest_version") != city_map_manifest.get("version"):
        raise ValueError("Property- und City-Map-Vertrag passen nicht zusammen")

    locations = city_map_manifest.get("locations")
    if not isinstance(locations, list):
        raise ValueError("City-Map besitzt keine gültige Location-Liste")
    purchasable: dict[str, dict[str, Any]] = {}
    for raw in locations:
        if not isinstance(raw, Mapping):
            raise ValueError("City-Map-Location muss Mapping sein")
        location_id = raw.get("location_id")
        if not isinstance(location_id, str) or not location_id:
            raise ValueError("City-Map besitzt ungültige Location-ID")
        if raw.get("purchasable") is True:
            price = raw.get("purchase_price_cents")
            if isinstance(price, bool) or not isinstance(price, int) or price < 1:
                raise ValueError("Kaufbare Location besitzt keinen gültigen Kaufpreis")
            purchasable[location_id] = deepcopy(dict(raw))

    if raw_state is None:
        state = PropertyState(contract_version=version)
        persisted = False
    else:
        state = PropertyState.from_dict(raw_state)
        if state.contract_version != version:
            raise ValueError("Persistierter Property-State besitzt falsche Vertragsversion")
        persisted = True

    invalid = set(state.owned) - set(purchasable)
    if invalid:
        raise ValueError("Property-State besitzt unbekannte oder nicht kaufbare Location")

    entries = []
    for location_id, location in purchasable.items():
        ownership = state.owned.get(location_id)
        entries.append({
            "location_id": location_id,
            "label_key": location.get("label_key"),
            "district_id": location.get("district_id"),
            "category": location.get("category"),
            "purchase_price_cents": location["purchase_price_cents"],
            "upgrade_slots": list(location.get("upgrade_slots", [])),
            "owned": ownership is not None,
            "ownership": deepcopy(ownership),
        })

    return {
        "contract_version": version,
        "persisted": persisted,
        "revision": state.revision,
        "owned_count": len(state.owned),
        "purchasable_count": len(entries),
        "owned_location_ids": list(state.owned),
        "entries": entries,
        "policy": {
            "client_price_authority": False,
            "resale_supported": False,
            "rent_supported": False,
            "upgrades_supported": False,
        },
    }
