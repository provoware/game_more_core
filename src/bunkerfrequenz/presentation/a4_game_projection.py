from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.application.event_execution_service import EventExecutionService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.presentation.district_projection import build_living_district_projection


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
                }
                for response_id, response in responses.items()
            ],
        })
    return result


def build_a4_game_projection(
    state: Mapping[str, Any] | None,
    *,
    incident_catalog: Mapping[str, Mapping[str, Any]],
    district_manifest: Mapping[str, Any] | None = None,
    city_map_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only A4 game projection from confirmed state blocks.

    Event button availability delegates to EventExecutionService. Districts
    delegate to their read-only projection; this module never writes state.
    """
    if (district_manifest is None) != (city_map_manifest is None):
        raise ValueError("district_manifest und city_map_manifest müssen gemeinsam gesetzt werden")
    raw = deepcopy(dict(state or {}))
    projection: dict[str, Any] = {
        "view_model_version": "0.8.5-d1",
        "stage": "first_run" if "character" not in raw else "ready",
        "state_blocks": {
            key: key in raw
            for key in ("character", "event", "economy", "incidents", "settlement", "districts")
        },
        "character": None,
        "event": None,
        "economy": None,
        "incidents": None,
        "settlement": None,
        "districts": None,
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
                    "consumable": spec["consumable"],
                    "owned": economy.inventory.get(item_id, {}).get("owned", 0),
                    "reserved": economy.inventory.get(item_id, {}).get("reserved", 0),
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

    if district_manifest is not None and city_map_manifest is not None:
        raw_districts = raw.get("districts")
        if raw_districts is not None and not isinstance(raw_districts, Mapping):
            raise ValueError("Persistierter District-State muss ein Mapping sein")
        projection["districts"] = build_living_district_projection(
            raw_districts,
            district_manifest=district_manifest,
            city_map_manifest=city_map_manifest,
        )

    return projection
