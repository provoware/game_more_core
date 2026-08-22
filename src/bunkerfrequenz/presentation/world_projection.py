from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.world import WorldState


def _text(texts: Mapping[str, Any], key: Any) -> str:
    if not isinstance(key, str) or not key:
        return ""
    value = texts.get(key, key)
    return value if isinstance(value, str) else key


def build_world_projection(
    state: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    texts: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Project confirmed Living-City state without exposing hidden-rule metadata."""
    raw_world = state.get("world")
    raw_character = state.get("character")
    if not isinstance(raw_world, Mapping) or not isinstance(raw_character, Mapping):
        return None

    world = WorldState.from_dict(raw_world)
    character = CharacterState.from_dict(raw_character)
    player = world.players.get(character.character_id)
    if player is None:
        return None

    cities_raw = manifest.get("cities", [])
    locations_raw = manifest.get("locations", [])
    if not isinstance(cities_raw, list) or not isinstance(locations_raw, list):
        raise ValueError("WORLD_MANIFEST Städte/Orte ungültig")
    cities = {
        item["city_id"]: dict(item)
        for item in cities_raw
        if isinstance(item, Mapping) and isinstance(item.get("city_id"), str)
    }
    locations = {
        item["location_id"]: dict(item)
        for item in locations_raw
        if isinstance(item, Mapping) and isinstance(item.get("location_id"), str)
    }
    aliases = manifest.get("legacy_location_aliases", {})
    if not isinstance(aliases, Mapping):
        raise ValueError("WORLD_MANIFEST legacy_location_aliases ungültig")

    position = deepcopy(world.positions[character.character_id])
    city = cities.get(position["city_id"])
    if city is None:
        raise ValueError("World-Position verweist auf unbekannte Stadt")
    current_location = locations.get(position.get("location_id")) if position.get("location_id") else None
    metrics = deepcopy(world.districts[position["city_id"]][position["district_id"]])
    housing = deepcopy(world.housing[character.character_id])

    intro_key = manifest.get("intro", {}).get("story_key") if isinstance(manifest.get("intro"), Mapping) else None
    intro_template = _text(texts, intro_key)
    intro_text = intro_template.format(name=character.display_name) if intro_template else ""

    title_specs = {
        item["title_id"]: item
        for item in manifest.get("honor_titles", [])
        if isinstance(item, Mapping) and isinstance(item.get("title_id"), str)
    }
    honors = [
        {
            "title_id": title_id,
            "label": _text(texts, title_specs.get(title_id, {}).get("label_key")),
            "kind": title_specs.get(title_id, {}).get("kind", "honor"),
        }
        for title_id in world.honors.get(character.character_id, [])
    ]

    deed_specs = {
        item["deed_id"]: item
        for item in manifest.get("great_deeds", [])
        if isinstance(item, Mapping) and isinstance(item.get("deed_id"), str)
    }
    deeds = [
        {
            "record_id": deed["record_id"],
            "deed_id": deed["deed_id"],
            "label": _text(texts, deed_specs.get(deed["deed_id"], {}).get("label_key")),
            "valence": deed["valence"],
            "source_event_id": deed["source_event_id"],
        }
        for deed in world.great_deeds
        if deed["character_id"] == character.character_id
    ]

    city_options = []
    for city_id, spec in cities.items():
        districts = list(spec.get("districts", []))
        city_locations = [
            {
                "location_id": loc_id,
                "district_id": loc["district_id"],
                "category": loc.get("category"),
            }
            for loc_id, loc in locations.items()
            if loc.get("city_id") == city_id
        ]
        city_options.append({
            "city_id": city_id,
            "label": spec.get("label", city_id),
            "price_multiplier_bps": spec.get("price_multiplier_bps", 10000),
            "customs": list(spec.get("customs", [])),
            "districts": districts,
            "locations": city_locations,
        })

    event = EventState.from_dict(state["event"]) if isinstance(state.get("event"), Mapping) else None
    party_check = deepcopy(world.party_checks.get(event.event_id)) if event is not None else None
    party_mode = world.party_modes.get(event.event_id, "official") if event is not None else None
    event_location_id = None
    event_location = None
    if event is not None and event.location is not None:
        raw_event_location_id = event.location.get("location_id")
        if isinstance(raw_event_location_id, str):
            event_location_id = str(aliases.get(raw_event_location_id, raw_event_location_id))
            event_location = locations.get(event_location_id)
    party_eligible = bool(
        event is not None
        and event.phase == "live"
        and party_mode == "unofficial"
        and event_location is not None
        and event_location.get("party_risk_eligible")
    )
    party_choices = [
        {
            "choice_id": choice["choice_id"],
            "label": _text(texts, choice.get("label_key")),
        }
        for choice in manifest.get("party_encounter", {}).get("choices", [])
        if isinstance(choice, Mapping)
    ]

    outgoing_blocks = [
        deepcopy(block) for block in world.trust_blocks if block["offender_id"] == character.character_id
    ]
    incoming_blocks = [
        deepcopy(block) for block in world.trust_blocks if block["target_id"] == character.character_id
    ]

    return {
        "revision": world.revision,
        "booking_id": player["booking_id"],
        "intro": {
            "acknowledged": player["intro_acknowledged"],
            "text": intro_text,
        },
        "housing": housing,
        "position": position,
        "city": {
            "city_id": position["city_id"],
            "label": city.get("label", position["city_id"]),
            "price_multiplier_bps": int(city.get("price_multiplier_bps", 10000)),
            "customs": list(city.get("customs", [])),
            "description": _text(texts, f"city.{position['city_id']}.customs"),
        },
        "district_metrics": metrics,
        "cities": city_options,
        "current_location": None if current_location is None else {
            "location_id": current_location["location_id"],
            "category": current_location.get("category"),
            "mini_games": list(current_location.get("mini_games", [])),
            "party_risk_eligible": bool(current_location.get("party_risk_eligible")),
            "storefront_available": current_location["location_id"] in {
                item.get("location_id")
                for item in manifest.get("storefronts", [])
                if isinstance(item, Mapping)
            },
        },
        "honors": honors,
        "great_deeds": deeds,
        "trust": {
            "outgoing_blocks": outgoing_blocks,
            "incoming_blocks": incoming_blocks,
        },
        "mini_games": deepcopy(world.mini_games[character.character_id]),
        "party": {
            "mode": party_mode,
            "event_location_id": event_location_id,
            "check": party_check,
            "eligible_to_check": party_eligible and party_check is None,
            "choices": party_choices if party_check and party_check.get("triggered") and not party_check.get("resolved") else [],
        },
    }
