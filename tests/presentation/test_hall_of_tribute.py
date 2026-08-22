import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.hall_of_tribute import build_hall_of_tribute_projection


ROOT = Path(__file__).parents[2]
HALL = json.loads((ROOT / "manifests" / "HALL_OF_TRIBUTE_MANIFEST.json").read_text(encoding="utf-8"))
RANKING = json.loads((ROOT / "manifests" / "RANKING_NETWORK_MANIFEST.json").read_text(encoding="utf-8"))
SYNC = json.loads((ROOT / "manifests" / "SYNC_MANIFEST.json").read_text(encoding="utf-8"))
CITY = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
TEXT = json.loads((ROOT / "content" / "de" / "ui" / "character_forge.json").read_text(encoding="utf-8"))


def participant(index: int, *, reputation: int, level: int = 1, resonance: int = 0) -> dict:
    return {
        "player_id": f"remote-{index:02d}",
        "character": {
            "meta": {"projection_version": "test", "character_id": f"char.remote-{index:02d}"},
            "overview": {
                "display_name": f"Remote {index}",
                "alias": "",
                "level": level,
                "reputation": reputation,
                "resonance_rank": resonance,
            },
            "skills": [],
        },
    }


class HallOfTributeTests(unittest.TestCase):
    def build(self, state, **kwargs):
        return build_hall_of_tribute_projection(
            state,
            hall_manifest=HALL,
            ranking_manifest=RANKING,
            sync_manifest=SYNC,
            city_map_manifest=CITY,
            text_catalog=TEXT,
            **kwargs,
        )

    def test_local_a4_hall_never_invents_competitors(self):
        character = CharacterState("player-local", "Local Crew", reputation=7)
        result = self.build({"character": character.to_dict()})
        self.assertEqual(result["confirmed_participant_count"], 1)
        self.assertFalse(result["network_competition_available"])
        self.assertFalse(result["network_policy"]["invented_competitors"])
        self.assertEqual(result["boards"]["reputation"]["entries"][0]["character_id"], "player-local")
        self.assertEqual(result["boards"]["reputation"]["entries"][0]["rank"], 1)
        self.assertEqual(result["boards"]["reputation"]["entries"][0]["history"]["movement"], "new")
        self.assertEqual(result["location"]["location_id"], "hall_of_tribute")

    def test_confirmed_roster_shows_top10_and_challenger_displacement(self):
        local = CharacterState("player-local", "Local Crew", reputation=50)
        peers = [
            participant(1, reputation=100),
            participant(2, reputation=100),
            participant(3, reputation=89),
            participant(4, reputation=80),
            participant(5, reputation=70),
            participant(6, reputation=60),
            participant(7, reputation=55),
            participant(8, reputation=45),
            participant(9, reputation=40),
            participant(10, reputation=35),
            participant(11, reputation=30),
        ]
        previous = {
            "reputation": {
                "sort_by": "reputation",
                "skill_id": None,
                "entries": [
                    {"character_id": "char.remote-01", "rank": 1, "value": 100},
                    {"character_id": "char.remote-02", "rank": 2, "value": 90},
                    {"character_id": "char.remote-03", "rank": 3, "value": 89},
                    {"character_id": "char.remote-04", "rank": 4, "value": 80},
                    {"character_id": "char.remote-05", "rank": 5, "value": 70},
                    {"character_id": "char.remote-06", "rank": 6, "value": 60},
                    {"character_id": "char.remote-07", "rank": 7, "value": 55},
                    {"character_id": "player-local", "rank": 8, "value": 49},
                    {"character_id": "char.remote-08", "rank": 9, "value": 45},
                    {"character_id": "char.remote-09", "rank": 10, "value": 40},
                    {"character_id": "char.remote-10", "rank": 11, "value": 35},
                    {"character_id": "char.remote-11", "rank": 12, "value": 30}
                ],
            }
        }
        result = self.build(
            {"character": local.to_dict()},
            confirmed_participants=peers,
            previous_cycles=previous,
        )
        board = result["boards"]["reputation"]
        self.assertEqual(board["view"]["shown_players"], 10)
        self.assertEqual(board["view"]["total_players"], 12)
        self.assertEqual([entry["rank"] for entry in board["entries"]], list(range(1, 11)))
        self.assertEqual(board["entries"][0]["character_id"], "char.remote-02")
        self.assertEqual(board["entries"][0]["history"]["movement"], "up")
        self.assertEqual(board["entries"][1]["character_id"], "char.remote-01")
        self.assertEqual(board["entries"][1]["history"]["movement"], "down")
        self.assertTrue(result["network_competition_available"])

    def test_duplicate_local_participant_and_wrong_contract_fail_closed(self):
        local = CharacterState("player-local", "Local Crew")
        duplicate = {
            "player_id": "player-local",
            "character": {
                "meta": {"projection_version": "test", "character_id": "char.other"},
                "overview": {"display_name": "Other", "alias": "", "level": 1, "reputation": 0, "resonance_rank": 0},
                "skills": [],
            },
        }
        with self.assertRaises(ValueError):
            self.build({"character": local.to_dict()}, confirmed_participants=[duplicate])

        broken = json.loads(json.dumps(HALL))
        broken["ranking_manifest_version"] = "wrong"
        with self.assertRaises(ValueError):
            build_hall_of_tribute_projection(
                {"character": local.to_dict()},
                hall_manifest=broken,
                ranking_manifest=RANKING,
                sync_manifest=SYNC,
                city_map_manifest=CITY,
                text_catalog=TEXT,
            )


if __name__ == "__main__":
    unittest.main()
