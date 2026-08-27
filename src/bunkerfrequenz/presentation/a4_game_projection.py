from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.application.event_execution_service import EventExecutionService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState, market_price
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.presentation.berlin_ops_map_pro import build_berlin_ops_map_pro_projection
from bunkerfrequenz.presentation.crew_identity_projection import build_crew_identity_projection
from bunkerfrequenz.presentation.district_projection import build_living_district_projection
from bunkerfrequenz.presentation.hall_of_tribute import build_hall_of_tribute_projection
from bunkerfrequenz.presentation.property_projection import build_property_projection
from bunkerfrequenz.presentation.property_upgrade_projection import build_property_upgrade_projection
from bunkerfrequenz.presentation.seasonal_hall import (
    build_seasonal_hall_projection,
    derive_cycle_contexts_from_completed_event,
)


def _incident_catalog_projection(catalog: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for incident_type, spec in catalog.items():
        responses = spec.get("responses", {})
        if not isinstance(responses, Mapping):
            raise ValueError("Incident-Katalog enthält ungültige Responses")
        result.append({
            "incident_type": incident_type,
            "title_key": spec.get("title_key"),
            "base_severity": spec.get("base_severity"),
            "responses": [
                {
                    "response_id": response_id,
                    "label_key": response.get("label_key"),
                    "target_phase": response.get("target_phase"),
                    "effects": deepcopy(response.get("effects", {})),
                }
                for response_id, response in responses.items()
            ],
        })
    return result


def _street_approaches_projection(
    manifest: Mapping[str, Any] | None,
    text_catalog: Mapping[str, str] | None,
) -> list[dict[str, str]]:
    if manifest is None and text_catalog is None:
        return []
    if manifest is None or text_catalog is None:
        raise ValueError("Street-Ansätze benötigen Manifest und Textkatalog gemeinsam")
    policy = manifest.get("approach_policy")
    approaches = manifest.get("approaches")
    if not isinstance(policy, Mapping) or not isinstance(approaches, Sequence) or isinstance(approaches, (str, bytes)):
        raise ValueError("Street-Ansatzvertrag ist unvollständig")
    default_id = policy.get("default_approach_id")
    if not isinstance(default_id, str) or not default_id:
        raise ValueError("Street-Ansatzvertrag besitzt keinen Standard")

    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in approaches:
        if not isinstance(raw, Mapping):
            raise ValueError("Street-Ansatz muss Mapping sein")
        approach_id = raw.get("approach_id")
        label_key = raw.get("label_key")
        description_key = raw.get("description_key")
        if not all(isinstance(value, str) and value for value in (approach_id, label_key, description_key)):
            raise ValueError("Street-Ansatz besitzt ungültige Anzeige-Metadaten")
        if approach_id in seen:
            raise ValueError("Street-Ansatz-ID ist doppelt")
        seen.add(approach_id)
        if label_key not in text_catalog or description_key not in text_catalog:
            raise KeyError(f"Street-Ansatztext fehlt: {approach_id}")
        result.append({
            "approach_id": approach_id,
            "label": text_catalog[label_key],
            "description": text_catalog[description_key],
            "selected_by_default": approach_id == default_id,
        })
    if default_id not in seen:
        raise ValueError("Standard-Street-Ansatz ist nicht katalogisiert")
    return result


def build_a4_game_projection(
    state: Mapping[str, Any] | None,
    *,
    incident_catalog: Mapping[str, Mapping[str, Any]],
    district_manifest: Mapping[str, Any] | None = None,
    city_map_manifest: Mapping[str, Any] | None = None,
    property_manifest: Mapping[str, Any] | None = None,
    property_upgrade_manifest: Mapping[str, Any] | None = None,
    map_pro_manifest: Mapping[str, Any] | None = None,
    hall_manifest: Mapping[str, Any] | None = None,
    ranking_manifest: Mapping[str, Any] | None = None,
    sync_manifest: Mapping[str, Any] | None = None,
    ranking_text_catalog: Mapping[str, str] | None = None,
    hall_season_manifest: Mapping[str, Any] | None = None,
    zeit_manifest: Mapping[str, Any] | None = None,
    street_manifest: Mapping[str, Any] | None = None,
    street_text_catalog: Mapping[str, str] | None = None,
    confirmed_hall_cycles: Mapping[str, Mapping[str, Any]] | None = None,
    confirmed_ranking_participants: Sequence[Mapping[str, Any]] = (),
    confirmed_network_records: Sequence[Mapping[str, Any]] = (),
    previous_ranking_cycles: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a read-only A4 game projection from confirmed state blocks."""
    if (district_manifest is None) != (city_map_manifest is None):
        raise ValueError("district_manifest und city_map_manifest müssen gemeinsam gesetzt werden")
    if property_manifest is not None and city_map_manifest is None:
        raise ValueError("property_manifest benötigt city_map_manifest")
    if property_upgrade_manifest is not None and (property_manifest is None or city_map_manifest is None):
        raise ValueError("property_upgrade_manifest benötigt Property- und City-Map-Vertrag")
    if map_pro_manifest is not None and (district_manifest is None or city_map_manifest is None):
        raise ValueError("map_pro_manifest benötigt District- und City-Map-Vertrag")
    hall_parts = (hall_manifest, ranking_manifest, sync_manifest, ranking_text_catalog, city_map_manifest)
    if any(part is not None for part in hall_parts[:4]) and not all(part is not None for part in hall_parts):
        raise ValueError("Hall of Tribute benötigt Hall-, Ranking-, Sync-, Text- und City-Map-Vertrag")
    if (hall_season_manifest is None) != (zeit_manifest is None):
        raise ValueError("Hall-Saison benötigt Saison- und Zeit-Manifest gemeinsam")
    if hall_season_manifest is not None and hall_manifest is None:
        raise ValueError("Hall-Saison benötigt Hall-of-Tribute-Vertrag")
    if confirmed_hall_cycles is not None and hall_season_manifest is None:
        raise ValueError("Bestätigte Hall-Zyklen benötigen Saisonvertrag")
    if (street_manifest is None) != (street_text_catalog is None):
        raise ValueError("Street-Ansätze benötigen Manifest und Textkatalog gemeinsam")

    raw = deepcopy(dict(state or {}))
    projection: dict[str, Any] = {
        "view_model_version": "0.8.8-a1",
        "stage": "first_run" if "character" not in raw else "ready",
        "state_blocks": {
            key: key in raw
            for key in (
                "character", "event", "economy", "incidents", "settlement", "districts",
                "properties", "property_upgrades",
            )
        },
        "character": None,
        "event": None,
        "economy": None,
        "incidents": None,
        "settlement": None,
        "districts": None,
        "properties": None,
        "property_upgrades": None,
        "berlin_ops_map": None,
        "hall_of_tribute": None,
        "street_approaches": _street_approaches_projection(street_manifest, street_text_catalog),
        "incident_catalog": _incident_catalog_projection(incident_catalog),
    }

    if "character" in raw:
        character = CharacterState.from_dict(raw["character"])
        projection["character"] = {
            "character_id": character.character_id,
            "display_name": character.display_name,
            "alias": character.alias,
            "additional_nicknames": list(character.additional_nicknames),
            "motto": character.motto,
            "crew_identity": build_crew_identity_projection(character.crew_identity),
            "level": character.level,
            "energy": character.energy,
            "stress": character.stress,
            "reputation": character.reputation,
        }

    if "event" in raw:
        event = EventState.from_dict(raw["event"])
        actions = [
            {
                "action_id": item.action_id,
                "source_phase": item.source_phase,
                "target_phase": item.target_phase,
                "enabled": item.enabled,
                "blockers": list(item.blockers),
            }
            for item in EventExecutionService.available_actions(event)
        ]
        projection["event"] = {
            "event_id": event.event_id,
            "display_name": event.display_name,
            "phase": event.phase,
            "revision": event.revision,
            "budget_cents": event.budget_cents,
            "location": deepcopy(event.location),
            "acts": deepcopy(event.acts),
            "crew": deepcopy(event.crew),
            "equipment": deepcopy(event.equipment),
            "time_window": deepcopy(event.time_window),
            "safety_status": event.safety_status,
            "actions": actions,
        }
        projection["stage"] = "completed" if event.phase == "completed" else "event"

    if "economy" in raw:
        economy = EconomyState.from_dict(raw["economy"])
        projection["economy"] = {
            "revision": economy.revision,
            "market_tick": economy.market_tick,
            "items": [
                {
                    "item_id": item_id,
                    "label": spec["label"],
                    "base_price_cents": spec["base_price_cents"],
                    "current_price_cents": market_price(
                        spec["base_price_cents"], economy.market_tick, spec["volatility_bps"]
                    ),
                    "price_delta_cents": market_price(
                        spec["base_price_cents"], economy.market_tick, spec["volatility_bps"]
                    ) - spec["base_price_cents"],
                    "volatility_bps": spec["volatility_bps"],
                    "consumable": spec["consumable"],
                    "owned": economy.inventory.get(item_id, {}).get("owned", 0),
                    "reserved": economy.inventory.get(item_id, {}).get("reserved", 0),
                    "available_to_sell": (
                        economy.inventory.get(item_id, {}).get("owned", 0)
                        - economy.inventory.get(item_id, {}).get("reserved", 0)
                    ),
                }
                for item_id, spec in economy.catalog.items()
            ],
            "ledger_entries": len(economy.ledger),
        }

    if "incidents" in raw:
        incidents = IncidentState.from_dict(raw["incidents"])
        projection["incidents"] = {
            "revision": incidents.revision,
            "active": deepcopy(incidents.active),
            "history": deepcopy(incidents.history),
            "pending_settlement": deepcopy(incidents.pending_settlement),
        }

    if "settlement" in raw:
        settlement = SettlementState.from_dict(raw["settlement"])
        projection["settlement"] = settlement.to_dict()

    owned_property_ids: frozenset[str] = frozenset()
    property_projection: dict[str, Any] | None = None
    if property_manifest is not None and city_map_manifest is not None:
        raw_properties = raw.get("properties")
        if raw_properties is not None and not isinstance(raw_properties, Mapping):
            raise ValueError("Persistierter Property-State muss ein Mapping sein")
        property_projection = build_property_projection(
            raw_properties,
            property_manifest=property_manifest,
            city_map_manifest=city_map_manifest,
        )
        projection["properties"] = property_projection
        owned_property_ids = frozenset(property_projection["owned_location_ids"])

    location_value_overrides: Mapping[str, Mapping[str, int]] | None = None
    if property_upgrade_manifest is not None and city_map_manifest is not None and property_projection is not None:
        raw_upgrades = raw.get("property_upgrades")
        if raw_upgrades is not None and not isinstance(raw_upgrades, Mapping):
            raise ValueError("Persistierter Property-Upgrade-State muss ein Mapping sein")
        upgrade_projection = build_property_upgrade_projection(
            raw_upgrades,
            upgrade_manifest=property_upgrade_manifest,
            city_map_manifest=city_map_manifest,
            property_projection=property_projection,
        )
        projection["property_upgrades"] = upgrade_projection
        location_value_overrides = upgrade_projection["effective_values_by_location"]

    if district_manifest is not None and city_map_manifest is not None:
        raw_districts = raw.get("districts")
        if raw_districts is not None and not isinstance(raw_districts, Mapping):
            raise ValueError("Persistierter District-State muss ein Mapping sein")
        projection["districts"] = build_living_district_projection(
            raw_districts,
            district_manifest=district_manifest,
            city_map_manifest=city_map_manifest,
            owned_property_ids=owned_property_ids,
            location_value_overrides=location_value_overrides,
        )

    if map_pro_manifest is not None and projection["districts"] is not None:
        projection["berlin_ops_map"] = build_berlin_ops_map_pro_projection(
            projection["districts"],
            property_upgrades=projection["property_upgrades"],
            map_pro_manifest=map_pro_manifest,
        )

    if hall_manifest is not None:
        hall_projection = build_hall_of_tribute_projection(
            raw,
            hall_manifest=hall_manifest,
            ranking_manifest=ranking_manifest,
            sync_manifest=sync_manifest,
            city_map_manifest=city_map_manifest,
            text_catalog=ranking_text_catalog,
            confirmed_participants=confirmed_ranking_participants,
            confirmed_network_records=confirmed_network_records,
            previous_cycles=previous_ranking_cycles,
        )
        if hall_projection is not None and hall_season_manifest is not None:
            cycle_contexts = confirmed_hall_cycles
            if cycle_contexts is None:
                raw_event = raw.get("event")
                if raw_event is not None and not isinstance(raw_event, Mapping):
                    raise ValueError("Event für Hall-Saison muss Mapping sein")
                cycle_contexts = derive_cycle_contexts_from_completed_event(
                    raw_event,
                    season_manifest=hall_season_manifest,
                    hall_manifest=hall_manifest,
                    ranking_manifest=ranking_manifest,
                    zeit_manifest=zeit_manifest,
                )
            hall_projection["seasonal"] = build_seasonal_hall_projection(
                hall_projection,
                season_manifest=hall_season_manifest,
                hall_manifest=hall_manifest,
                ranking_manifest=ranking_manifest,
                zeit_manifest=zeit_manifest,
                confirmed_cycle_contexts=cycle_contexts,
            )
        projection["hall_of_tribute"] = hall_projection

    return projection
