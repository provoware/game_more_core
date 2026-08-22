import json
from pathlib import Path
import unittest

from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection


ROOT = Path(__file__).parents[2]


def load(name: str) -> dict:
    return json.loads((ROOT / "manifests" / name).read_text(encoding="utf-8"))


HALL = load("HALL_OF_TRIBUTE_MANIFEST.json")
SEASON = load("HALL_SEASON_MANIFEST.json")
RANKING = load("RANKING_NETWORK_MANIFEST.json")
SYNC = load("SYNC_MANIFEST.json")
ZEIT = load("ZEIT_MANIFEST.json")
CITY = load("CITY_MAP_MANIFEST.json")
DISTRICT = load("DISTRICT_STATE_MANIFEST.json")
INCIDENT = load("INCIDENT_MANIFEST.json")
TEXT = json.loads((ROOT / "content" / "de" / "ui" / "character_forge.json").read_text(encoding="utf-8"))


class A4SeasonIntegrationTests(unittest.TestCase):
    def build_projection(self, state: dict) -> dict:
        return build_a4_game_projection(
            state,
            incident_catalog=build_incident_catalog(INCIDENT),
            district_manifest=DISTRICT,
            city_map_manifest=CITY,
            hall_manifest=HALL,
            ranking_manifest=RANKING,
            sync_manifest=SYNC,
            ranking_text_catalog=TEXT,
            hall_season_manifest=SEASON,
            zeit_manifest=ZEIT,
        )

    def test_completed_event_exposes_stable_week_month_without_fake_title(self):
        character = CharacterState("player-local", "Local Crew", reputation=42)
        event = EventState(
            event_id="event-season-integration",
            display_name="Season Integration",
            location={
                "location_id": "loc",
                "display_name": "Ort",
                "region": "Berlin",
                "access_status": "authorized",
            },
            budget_cents=100_000,
            acts=[{"act_id": "act", "display_name": "Act", "status": "confirmed"}],
            crew=[{"character_id": "player-local", "role": "leitung", "status": "confirmed"}],
            equipment=[],
            time_window={
                "start_local": "2026-08-22T20:00:00+02:00",
                "end_local": "2026-08-23T04:00:00+02:00",
                "timezone": "Europe/Berlin",
            },
            safety_status="cleared",
            phase="completed",
            revision=17,
        )
        state = {"character": character.to_dict(), "event": event.to_dict()}

        projection = self.build_projection(state)
        hall = projection["hall_of_tribute"]
        season = hall["season"]
        self.assertTrue(season["available"])
        self.assertEqual(season["cycles"]["weekly"]["cycle_id"], "week:2026-W34")
        self.assertEqual(season["cycles"]["monthly"]["cycle_id"], "month:2026-08")
        self.assertEqual(season["cycles"]["weekly"]["authority"], "game_world_time")
        self.assertFalse(season["cycles"]["weekly"]["closed"])
        self.assertFalse(season["cycles"]["weekly"]["titles_final"])
        self.assertEqual(season["local_titles"], [])

        projection_again = self.build_projection(state)
        self.assertEqual(
            projection_again["hall_of_tribute"]["season"]["cycles"],
            season["cycles"],
        )


if __name__ == "__main__":
    unittest.main()
