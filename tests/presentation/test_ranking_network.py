import json
from copy import deepcopy
from pathlib import Path
import unittest

from bunkerfrequenz.presentation import build_ranking_network_projection


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for path in sorted((ROOT / "content/de/ui").glob("*.json")):
        catalog.update(json.loads(path.read_text(encoding="utf-8")))
    return catalog


def participant(index: int, *, level: int | None = None, reputation: int | None = None, resonance: int | None = None, technik: int | None = None) -> dict:
    value = index if level is None else level
    rep = index * 2 if reputation is None else reputation
    res = index // 3 if resonance is None else resonance
    skill = index + 10 if technik is None else technik
    return {
        "player_id": f"player-{index:03d}",
        "character": {
            "meta": {"projection_version": "0.6", "character_id": f"char.test-{index:03d}"},
            "overview": {
                "display_name": f"Player {index}",
                "alias": f"Alias {index}",
                "level": value,
                "reputation": rep,
                "resonance_rank": res,
            },
            "skills": [
                {"skill_id": "skill.technik", "label_key": "skill.technik.label", "value": skill}
            ],
        },
    }


def network(index: int, *, events: int | None = None, clubs: int | None = None, status: str = "current", authority: str = "server_confirmed_transaction") -> dict:
    metrics = {}
    if events is not None:
        metrics["events"] = events
    if clubs is not None:
        metrics["clubs"] = clubs
    return {
        "player_id": f"player-{index:03d}",
        "character_id": f"char.test-{index:03d}",
        "authority": authority,
        "version": f"v-{index}",
        "sync_status": status,
        "metrics": metrics,
    }


class RankingNetworkTest(unittest.TestCase):
    def setUp(self):
        self.ranking_manifest = load_json("manifests/RANKING_NETWORK_MANIFEST.json")
        self.sync_manifest = load_json("manifests/SYNC_MANIFEST.json")
        self.catalog = load_catalog()

    def build(self, participants, records=(), **kwargs):
        return build_ranking_network_projection(
            participants,
            records,
            self.ranking_manifest,
            self.sync_manifest,
            self.catalog,
            **kwargs,
        )

    def test_default_top10_and_show_all_support_arbitrary_player_count(self):
        players = [participant(index) for index in range(1, 38)]
        top = self.build(players)
        all_players = self.build(players, show_all=True)

        self.assertEqual(top["view"]["total_players"], 37)
        self.assertEqual(top["view"]["shown_players"], 10)
        self.assertEqual(top["view"]["competitive_top_limit"], 10)
        self.assertEqual(len(top["entries"]), 10)
        self.assertEqual(all_players["view"]["shown_players"], 37)
        self.assertEqual(len(all_players["entries"]), 37)
        self.assertEqual(top["entries"][0]["level"], 37)
        self.assertEqual([entry["rank"] for entry in all_players["entries"]], list(range(1, 38)))

    def test_equal_values_never_share_rank_without_history(self):
        players = [
            participant(3, level=9),
            participant(1, level=10),
            participant(2, level=10),
            participant(4, level=8),
        ]
        result = self.build(players, show_all=True)

        self.assertEqual(
            [(entry["character_id"], entry["rank"], entry["level"]) for entry in result["entries"]],
            [
                ("char.test-001", 1, 10),
                ("char.test-002", 2, 10),
                ("char.test-003", 3, 9),
                ("char.test-004", 4, 8),
            ],
        )
        self.assertFalse(result["competition_policy"]["shared_ranks_allowed"])

    def test_rising_challenger_displaces_stationary_player_on_equal_value(self):
        first = self.build(
            [participant(1, level=10), participant(2, level=9)],
            show_all=True,
        )
        second = self.build(
            [participant(1, level=10), participant(2, level=10)],
            show_all=True,
            previous_cycle=first["cycle_snapshot"],
        )

        self.assertEqual(
            [(entry["character_id"], entry["rank"]) for entry in second["entries"]],
            [("char.test-002", 1), ("char.test-001", 2)],
        )
        by_character = {entry["character_id"]: entry for entry in second["entries"]}
        self.assertEqual(by_character["char.test-002"]["history"]["metric_delta"], 1)
        self.assertEqual(by_character["char.test-002"]["history"]["movement"], "up")
        self.assertEqual(by_character["char.test-001"]["history"]["metric_delta"], 0)
        self.assertEqual(by_character["char.test-001"]["history"]["movement"], "down")

    def test_rank_11_and_below_use_one_tenth_momentum_pressure(self):
        previous = {
            "sort_by": "level",
            "skill_id": None,
            "entries": [
                {"character_id": "char.test-010", "rank": 10, "value": 9},
                {"character_id": "char.test-011", "rank": 11, "value": 5},
            ],
        }
        result = self.build(
            [participant(10, level=10), participant(11, level=10)],
            show_all=True,
            previous_cycle=previous,
        )
        by_character = {entry["character_id"]: entry for entry in result["entries"]}

        self.assertEqual(result["competition_policy"]["top_pressure_factor"], 1.0)
        self.assertEqual(result["competition_policy"]["outer_pressure_factor"], 0.1)
        self.assertEqual(by_character["char.test-010"]["history"]["momentum_factor"], 1.0)
        self.assertEqual(by_character["char.test-010"]["history"]["effective_momentum"], 1.0)
        self.assertEqual(by_character["char.test-011"]["history"]["momentum_factor"], 0.1)
        self.assertEqual(by_character["char.test-011"]["history"]["effective_momentum"], 0.5)
        self.assertEqual(result["entries"][0]["character_id"], "char.test-010")

    def test_previous_cycle_must_match_metric_and_have_unique_ranks(self):
        players = [participant(1)]
        wrong_metric = {
            "sort_by": "reputation",
            "skill_id": None,
            "entries": [{"character_id": "char.test-001", "rank": 1, "value": 1}],
        }
        with self.assertRaises(ValueError):
            self.build(players, previous_cycle=wrong_metric)

        duplicate_rank = {
            "sort_by": "level",
            "skill_id": None,
            "entries": [
                {"character_id": "char.test-001", "rank": 1, "value": 1},
                {"character_id": "char.test-002", "rank": 1, "value": 1},
            ],
        }
        with self.assertRaises(ValueError):
            self.build([participant(1), participant(2)], previous_cycle=duplicate_rank)

    def test_level_reputation_resonance_and_skill_sorting(self):
        players = [
            participant(1, level=2, reputation=90, resonance=1, technik=20),
            participant(2, level=8, reputation=30, resonance=7, technik=99),
            participant(3, level=5, reputation=60, resonance=4, technik=40),
        ]
        expectations = {
            "level": "char.test-002",
            "reputation": "char.test-001",
            "resonance": "char.test-002",
        }
        for mode, expected in expectations.items():
            with self.subTest(mode=mode):
                result = self.build(players, sort_by=mode, show_all=True)
                self.assertEqual(result["entries"][0]["character_id"], expected)

        skill_result = self.build(players, sort_by="skill", skill_id="skill.technik", show_all=True)
        self.assertEqual(skill_result["entries"][0]["character_id"], "char.test-002")
        self.assertEqual(skill_result["sort"]["label_key"], "skill.technik.label")
        with self.assertRaises(ValueError):
            self.build(players, sort_by="skill")

    def test_events_and_clubs_use_only_server_confirmed_values(self):
        players = [participant(index) for index in range(1, 5)]
        records = [
            network(1, events=8, clubs=1),
            network(2, events=12, clubs=0),
            network(3, clubs=5),
        ]
        events = self.build(players, records, sort_by="events", show_all=True)
        clubs = self.build(players, records, sort_by="clubs", show_all=True)

        self.assertEqual(events["entries"][0]["character_id"], "char.test-002")
        self.assertEqual(events["entries"][0]["rank"], 1)
        unavailable_events = [entry for entry in events["entries"] if not entry["selected_metric"]["available"]]
        self.assertEqual({entry["character_id"] for entry in unavailable_events}, {"char.test-003", "char.test-004"})
        self.assertTrue(all(entry["selected_metric"]["value"] is None for entry in unavailable_events))
        self.assertTrue(all(entry["rank"] is None for entry in unavailable_events))
        self.assertEqual(clubs["entries"][0]["character_id"], "char.test-003")
        self.assertTrue(events["metric_availability"]["events"])
        self.assertTrue(clubs["metric_availability"]["clubs"])

    def test_missing_network_data_never_infers_online_or_zero_metrics(self):
        result = self.build([participant(1)], sort_by="events", show_all=True)
        entry = result["entries"][0]

        self.assertFalse(entry["sync"]["available"])
        self.assertEqual(entry["sync"]["status"], "unknown")
        self.assertEqual(entry["sync"]["label_key"], "ui.sync.unknown")
        self.assertIsNone(entry["sync"]["version"])
        self.assertEqual(entry["network_metrics"], {})
        self.assertFalse(entry["selected_metric"]["available"])
        self.assertIsNone(entry["selected_metric"]["value"])
        self.assertEqual(entry["selected_metric"]["value_label_key"], "ui.ranking.unavailable")
        self.assertIsNone(entry["rank"])
        self.assertEqual(entry["competition"]["zone"], "unranked")
        self.assertFalse(result["network_policy"]["online_presence_inferred"])
        self.assertFalse(result["network_policy"]["unconfirmed_metrics_are_displayed"])

    def test_wrong_authority_unknown_metrics_and_identity_mismatch_fail_closed(self):
        player = participant(1)
        with self.assertRaises(ValueError):
            self.build([player], [network(1, events=2, authority="client_claim")])

        bad_metric = network(1, events=2)
        bad_metric["metrics"]["wealth"] = 999
        with self.assertRaises(ValueError):
            self.build([player], [bad_metric])

        wrong_character = network(1, events=2)
        wrong_character["character_id"] = "char.other"
        with self.assertRaises(ValueError):
            self.build([player], [wrong_character])

        unknown_player = network(2, events=2)
        with self.assertRaises(ValueError):
            self.build([player], [unknown_player])

    def test_duplicate_identity_and_network_records_are_rejected(self):
        first = participant(1)
        duplicate_player = participant(2)
        duplicate_player["player_id"] = first["player_id"]
        with self.assertRaises(ValueError):
            self.build([first, duplicate_player])

        duplicate_character = participant(2)
        duplicate_character["character"]["meta"]["character_id"] = first["character"]["meta"]["character_id"]
        with self.assertRaises(ValueError):
            self.build([first, duplicate_character])

        with self.assertRaises(ValueError):
            self.build([first], [network(1, events=1), network(1, events=2)])

    def test_projection_is_detached_from_participant_network_and_cycle_inputs(self):
        players = [participant(1)]
        records = [network(1, events=4, clubs=2)]
        previous = {
            "sort_by": "events",
            "skill_id": None,
            "entries": [{"character_id": "char.test-001", "rank": 1, "value": 3}],
        }
        before_players = deepcopy(players)
        before_records = deepcopy(records)
        before_previous = deepcopy(previous)

        result = self.build(players, records, sort_by="events", show_all=True, previous_cycle=previous)
        result["entries"][0]["display_name"] = "changed"
        result["entries"][0]["network_metrics"]["events"] = 999
        result["entries"][0]["skills"]["skill.technik"] = 1
        result["cycle_snapshot"]["entries"][0]["value"] = 999

        self.assertEqual(players, before_players)
        self.assertEqual(records, before_records)
        self.assertEqual(previous, before_previous)

    def test_missing_visible_text_key_fails_closed(self):
        broken = dict(self.catalog)
        del broken["ui.ranking.metric.events"]
        with self.assertRaises(KeyError):
            build_ranking_network_projection(
                [participant(1)],
                [network(1, events=1)],
                self.ranking_manifest,
                self.sync_manifest,
                broken,
                sort_by="events",
            )

    def test_sync_status_is_display_metadata_not_presence(self):
        result = self.build(
            [participant(1), participant(2)],
            [network(1, events=1, status="offline"), network(2, events=2, status="current")],
            sort_by="events",
            show_all=True,
        )
        by_player = {entry["player_id"]: entry for entry in result["entries"]}
        self.assertEqual(by_player["player-001"]["sync"]["label_key"], "ui.sync.offline")
        self.assertEqual(by_player["player-002"]["sync"]["label_key"], "ui.sync.current")
        self.assertNotIn("online", by_player["player-001"])
        self.assertNotIn("online", by_player["player-002"])
        self.assertFalse(result["network_policy"]["online_presence_inferred"])


if __name__ == "__main__":
    unittest.main()
