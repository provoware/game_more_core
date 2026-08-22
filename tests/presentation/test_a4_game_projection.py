from copy import deepcopy
import unittest

from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection


INCIDENT_MANIFEST = {
    "version": "0.8.3-b1",
    "trigger_phases": ["live"],
    "incident_types": [{
        "incident_type": "power_drop",
        "title_key": "incident.power_drop.title",
        "base_severity": 3,
        "responses": [
            {"response_id": "power_drop.generator", "label_key": "incident.power_drop.generator", "target_phase": "live", "effects": {"budget_delta_cents": -1, "reputation_delta": 1, "crew_stress_delta": 1, "stability_delta": 1, "heat_delta": 0}},
            {"response_id": "power_drop.stop", "label_key": "incident.power_drop.stop", "target_phase": "teardown", "effects": {"budget_delta_cents": 0, "reputation_delta": -1, "crew_stress_delta": 0, "stability_delta": -1, "heat_delta": 0}},
        ],
    }],
}
CATALOG = build_incident_catalog(INCIDENT_MANIFEST)


def event(phase: str = "procurement") -> EventState:
    return EventState(
        event_id="event-a4",
        display_name="Projection Test",
        location={"location_id": "loc", "display_name": "Ort", "region": "Berlin", "access_status": "authorized"},
        budget_cents=100_000,
        acts=[{"act_id": "a", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-local", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "missing"}],
        time_window={"start_local": "2026-08-22T20:00:00+02:00", "end_local": "2026-08-23T05:00:00+02:00", "timezone": "Europe/Berlin"},
        safety_status="cleared",
        phase=phase,
        revision=2,
    )


class A4GameProjectionTests(unittest.TestCase):
    def test_empty_state_is_first_run(self):
        projected = build_a4_game_projection({}, incident_catalog=CATALOG)
        self.assertEqual(projected["stage"], "first_run")
        self.assertIsNone(projected["event"])

    def test_character_projection_exposes_profile_values_without_mutating_source(self):
        character = CharacterState("player-local", "Crew")
        character.alias = "Pegelpilot"
        character.additional_nicknames = ["Kabelkönig", "Betonkind"]
        character.motto = "Bass bleibt an"
        state = {"character": character.to_dict()}
        original = deepcopy(state)

        projected = build_a4_game_projection(state, incident_catalog=CATALOG)
        self.assertEqual(projected["character"]["display_name"], "Crew")
        self.assertEqual(projected["character"]["alias"], "Pegelpilot")
        self.assertEqual(projected["character"]["additional_nicknames"], ["Kabelkönig", "Betonkind"])
        self.assertEqual(projected["character"]["motto"], "Bass bleibt an")
        self.assertEqual(projected["character"]["character_id"], "player-local")
        self.assertEqual(state, original)

    def test_event_blockers_come_from_canonical_availability(self):
        state = {
            "character": CharacterState("player-local", "Crew").to_dict(),
            "event": event().to_dict(),
            "economy": EconomyState(catalog={
                "equipment.pa": {"label": "PA", "base_price_cents": 10000, "volatility_bps": 0, "consumable": False}
            }).to_dict(),
        }
        original = deepcopy(state)
        projected = build_a4_game_projection(state, incident_catalog=CATALOG)
        action = projected["event"]["actions"][0]
        self.assertEqual(action["action_id"], "start_transport")
        self.assertFalse(action["enabled"])
        self.assertIn("equipment_ready", action["blockers"])
        self.assertEqual(state, original)

    def test_live_projection_exposes_only_catalogued_incident_choices(self):
        live = event("live")
        live.equipment[0]["status"] = "ready"
        state = {
            "character": CharacterState("player-local", "Crew").to_dict(),
            "event": live.to_dict(),
        }
        projected = build_a4_game_projection(state, incident_catalog=CATALOG)
        incident = projected["incident_catalog"][0]
        self.assertEqual(incident["incident_type"], "power_drop")
        self.assertEqual(
            {item["response_id"] for item in incident["responses"]},
            {"power_drop.generator", "power_drop.stop"},
        )
        self.assertEqual(projected["event"]["actions"][0]["action_id"], "finish_live")


if __name__ == "__main__":
    unittest.main()
