from __future__ import annotations

from typing import Any, Mapping

from bunkerfrequenz.domain.property import PropertyState
from bunkerfrequenz.domain.property_upgrade import PropertyUpgradeState, effective_venue_values


def resolve_owned_venue_evidence(
    *,
    event_location: Mapping[str, Any] | None,
    settlement_character_id: str,
    property_state: PropertyState,
    property_upgrade_state: PropertyUpgradeState,
    city_map_manifest: Mapping[str, Any],
    upgrade_manifest: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Resolve confirmed read-only venue evidence for one settlement candidate.

    This is evidence plumbing only. It does not alter settlement effects, payout,
    ownership, upgrades, or persistence.
    """
    if event_location is None:
        return None
    if not isinstance(settlement_character_id, str) or not settlement_character_id.strip():
        raise ValueError("Settlement-Character-ID muss nicht-leerer Text sein")

    property_state.validate()
    property_upgrade_state.validate()

    location_id = event_location.get("location_id")
    if not isinstance(location_id, str) or not location_id.strip():
        raise ValueError("Event-Location benötigt location_id")
    location_id = location_id.strip()

    ownership = property_state.owned.get(location_id)
    if ownership is None or ownership["owner_character_id"] != settlement_character_id.strip():
        return None

    locations = city_map_manifest.get("locations")
    if not isinstance(locations, list):
        raise ValueError("City-Map besitzt keine gültigen Locations")
    matches = [
        item
        for item in locations
        if isinstance(item, Mapping) and item.get("location_id") == location_id
    ]
    if len(matches) != 1:
        raise ValueError("Eigene Event-Location muss genau einmal im City-Map-Katalog existieren")
    location = matches[0]

    city_map_version = city_map_manifest.get("version")
    upgrade_manifest_version = upgrade_manifest.get("version")
    if not isinstance(city_map_version, str) or not city_map_version.strip():
        raise ValueError("City-Map benötigt eine gültige Vertragsversion")
    if not isinstance(upgrade_manifest_version, str) or not upgrade_manifest_version.strip():
        raise ValueError("Property-Upgrade-Katalog benötigt eine gültige Vertragsversion")
    if upgrade_manifest.get("city_map_manifest_version") != city_map_version:
        raise ValueError("Property-Upgrade- und City-Map-Vertrag passen nicht zusammen")
    if property_upgrade_state.contract_version != upgrade_manifest_version:
        raise ValueError("Property-Upgrade-State besitzt falsche Vertragsversion")

    upgrade_catalog = upgrade_manifest.get("catalog")
    if not isinstance(upgrade_catalog, Mapping):
        raise ValueError("Property-Upgrade-Katalog fehlt")
    base_values = location.get("values")
    upgrade_slots = location.get("upgrade_slots", [])
    if not isinstance(base_values, Mapping):
        raise ValueError("Location besitzt keine gültigen Basiswerte")
    if not isinstance(upgrade_slots, list):
        raise ValueError("Location besitzt ungültige Upgrade-Slots")

    record = property_upgrade_state.properties.get(location_id)
    upgrade_levels = (
        {}
        if record is None
        else {upgrade_id: value["level"] for upgrade_id, value in record["upgrades"].items()}
    )
    effective = effective_venue_values(
        base_values,
        upgrade_slots=upgrade_slots,
        upgrade_levels=upgrade_levels,
        upgrade_catalog=upgrade_catalog,
    )

    return {
        "schema_version": 1,
        "location_id": location_id,
        "owner_character_id": ownership["owner_character_id"],
        "audience_pull": effective["audience_pull"],
        "city_map_manifest_version": city_map_version,
        "property_upgrade_manifest_version": upgrade_manifest_version,
        "property_revision": property_state.revision,
        "property_upgrade_revision": property_upgrade_state.revision,
    }
