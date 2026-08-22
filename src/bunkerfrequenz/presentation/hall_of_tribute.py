from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.ranking_network import build_ranking_network_projection


def _local_participant(character: CharacterState) -> dict[str, Any]:
    character.validate()
    return {
        "player_id": character.character_id,
        "character": {
            "meta": {
                "projection_version": "0.8.5-e1",
                "character_id": character.character_id,
            },
            "overview": {
                "display_name": character.display_name,
                "alias": character.alias,
                "level": character.level,
                "reputation": max(0, character.reputation),
                "resonance_rank": character.resonance_rank,
            },
            "skills": [
                {
                    "skill_id": f"skill.{skill_id}",
                    "label_key": f"skill.{skill_id}.label",
                    "value": value,
                }
                for skill_id, value in sorted(character.skills.items())
            ],
        },
    }


def build_hall_of_tribute_projection(
    state: Mapping[str, Any] | None,
    *,
    hall_manifest: Mapping[str, Any],
    ranking_manifest: Mapping[str, Any],
    sync_manifest: Mapping[str, Any],
    city_map_manifest: Mapping[str, Any],
    text_catalog: Mapping[str, str],
    confirmed_participants: Sequence[Mapping[str, Any]] = (),
    confirmed_network_records: Sequence[Mapping[str, Any]] = (),
    previous_cycles: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Build Hall-of-Tribute boards without inventing local competitors.

    The local CharacterState is authoritative for its own progression values.
    Additional participants/network records must be supplied explicitly by a
    confirmed source. Ranking/tie/momentum rules remain in ranking_network.py.
    """
    version = hall_manifest.get("version")
    if version != "0.8.5-e1":
        raise ValueError("Hall-of-Tribute-Manifest besitzt unerwartete Version")
    if hall_manifest.get("ranking_manifest_version") != ranking_manifest.get("version"):
        raise ValueError("Hall- und Ranking-Vertrag passen nicht zusammen")
    if hall_manifest.get("city_map_manifest_version") != city_map_manifest.get("version"):
        raise ValueError("Hall- und City-Map-Vertrag passen nicht zusammen")
    modes = hall_manifest.get("modes")
    if not isinstance(modes, list) or modes != ["reputation", "level", "resonance"]:
        raise ValueError("Hall-Modi müssen Ruf, Level und Resonanz sein")
    top_limit = hall_manifest.get("top_limit")
    if isinstance(top_limit, bool) or not isinstance(top_limit, int) or top_limit != 10:
        raise ValueError("Hall of Tribute benötigt Top-10-Limit")

    locations = city_map_manifest.get("locations")
    if not isinstance(locations, list):
        raise ValueError("City-Map besitzt keine gültigen Locations")
    halls = [item for item in locations if item.get("category") == "tribute_hall"]
    if len(halls) != 1 or halls[0].get("ranking_enabled") is not True:
        raise ValueError("City-Map benötigt genau eine rankingfähige Hall of Tribute")
    hall_location = halls[0]

    raw = deepcopy(dict(state or {}))
    raw_character = raw.get("character")
    if raw_character is None:
        return None
    if not isinstance(raw_character, dict):
        raise ValueError("Hall of Tribute benötigt gültigen Character-State")
    local_character = CharacterState.from_dict(raw_character)

    participants: list[Mapping[str, Any]] = [_local_participant(local_character)]
    participants.extend(deepcopy(list(confirmed_participants)))
    player_ids = [item.get("player_id") for item in participants]
    if len(player_ids) != len(set(player_ids)):
        raise ValueError("Hall-Teilnehmer enthalten doppelte player_id")

    cycles = previous_cycles or {}
    if not isinstance(cycles, Mapping):
        raise ValueError("previous_cycles muss Mapping sein")
    unknown_cycles = set(cycles) - set(modes)
    if unknown_cycles:
        raise ValueError("previous_cycles enthält unbekannten Hall-Modus")

    boards: dict[str, Any] = {}
    for mode in modes:
        board = build_ranking_network_projection(
            participants,
            confirmed_network_records,
            ranking_manifest,
            sync_manifest,
            text_catalog,
            sort_by=mode,
            top_limit=top_limit,
            previous_cycle=cycles.get(mode),
        )
        boards[mode] = board

    return {
        "projection_version": version,
        "location": {
            "location_id": hall_location.get("location_id"),
            "label_key": hall_location.get("label_key"),
            "district_id": hall_location.get("district_id"),
        },
        "default_mode": hall_manifest.get("default_mode"),
        "modes": list(modes),
        "top_limit": top_limit,
        "confirmed_participant_count": len(participants),
        "network_competition_available": len(participants) > 1,
        "local_character_id": local_character.character_id,
        "movement_labels": deepcopy(hall_manifest.get("movement_labels", {})),
        "boards": boards,
        "network_policy": {
            "invented_competitors": False,
            "invented_network_metrics": False,
            "additional_participants_require_confirmed_input": True,
        },
    }
