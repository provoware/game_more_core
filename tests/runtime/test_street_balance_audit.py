import json
from collections import Counter
from itertools import combinations
from pathlib import Path
import unittest

from bunkerfrequenz.application.street_encounter_service import _select, _stable_bucket


ROOT = Path(__file__).parents[2]
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))


def approach_map() -> dict[str, dict[str, int]]:
    return {item["approach_id"]: item["weights"] for item in STREET["approaches"]}


def total_variation_distance(left: dict[str, int], right: dict[str, int]) -> float:
    total = STREET["selection"]["weight_total"]
    return 0.5 * sum(abs(left[key] - right[key]) for key in left) / total


def polarity_totals(weights: dict[str, int]) -> dict[str, int]:
    polarity_by_id = {item["encounter_id"]: item["polarity"] for item in STREET["encounters"]}
    totals = {"neutral": 0, "positive": 0, "negative": 0}
    for encounter_id, weight in weights.items():
        totals[polarity_by_id[encounter_id]] += weight
    return totals


class StreetBalanceAuditTests(unittest.TestCase):
    def test_four_profiles_are_mathematically_distinct(self):
        approaches = approach_map()
        self.assertEqual(list(approaches), ["balanced", "recovery", "network", "scout"])
        self.assertEqual(len(STREET["encounters"]), 16)

        distances = {
            (left_id, right_id): total_variation_distance(approaches[left_id], approaches[right_id])
            for left_id, right_id in combinations(approaches, 2)
        }
        self.assertEqual(
            {pair: round(distance, 2) for pair, distance in distances.items()},
            {
                ("balanced", "recovery"): 0.17,
                ("balanced", "network"): 0.27,
                ("balanced", "scout"): 0.34,
                ("recovery", "network"): 0.35,
                ("recovery", "scout"): 0.42,
                ("network", "scout"): 0.32,
            },
        )
        self.assertGreaterEqual(min(distances.values()), 0.15)

    def test_no_single_encounter_dominates_any_profile(self):
        for approach_id, weights in approach_map().items():
            highest = max(weights.values())
            self.assertLessEqual(highest, 20, approach_id)
            self.assertGreaterEqual(sum(1 for value in weights.values() if value > 0), 12, approach_id)

    def test_polarity_mix_stays_visible_and_profile_specific(self):
        actual = {approach_id: polarity_totals(weights) for approach_id, weights in approach_map().items()}
        self.assertEqual(
            actual,
            {
                "balanced": {"neutral": 25, "positive": 60, "negative": 15},
                "recovery": {"neutral": 30, "positive": 55, "negative": 15},
                "network": {"neutral": 15, "positive": 70, "negative": 15},
                "scout": {"neutral": 15, "positive": 60, "negative": 25},
            },
        )
        for approach_id, totals in actual.items():
            self.assertEqual(sum(totals.values()), 100, approach_id)
            self.assertGreater(totals["positive"], totals["negative"], approach_id)
            self.assertGreaterEqual(totals["positive"], 55, approach_id)
            self.assertLessEqual(totals["negative"], 25, approach_id)

    def test_all_100_buckets_match_declared_weights_exactly(self):
        encounters = STREET["encounters"]
        total = STREET["selection"]["weight_total"]
        self.assertEqual(total, 100)

        for approach_id, weights in approach_map().items():
            observed = Counter(
                _select(encounters, weights, bucket)["encounter_id"]
                for bucket in range(total)
            )
            self.assertEqual(dict(observed), {key: value for key, value in weights.items() if value > 0}, approach_id)

    def test_selection_boundaries_are_half_open_without_off_by_one(self):
        encounters = STREET["encounters"]
        total = STREET["selection"]["weight_total"]

        for approach_id, weights in approach_map().items():
            cursor = 0
            for encounter in encounters:
                encounter_id = encounter["encounter_id"]
                weight = weights[encounter_id]
                if weight == 0:
                    continue
                first_bucket = cursor
                last_bucket = cursor + weight - 1
                self.assertEqual(_select(encounters, weights, first_bucket)["encounter_id"], encounter_id, approach_id)
                self.assertEqual(_select(encounters, weights, last_bucket)["encounter_id"], encounter_id, approach_id)
                cursor += weight
            self.assertEqual(cursor, total, approach_id)

    def test_stable_bucket_edge_inputs_are_replay_stable_and_bounded(self):
        fixtures = (
            ("stable-world", "edge-none", None, 69),
            ("stable-world", "edge-zero", 0, 97),
            ("stable-world", "edge-one", 1, 19),
            ("ß-world", "walk|edge", 999999, 54),
        )
        total = STREET["selection"]["weight_total"]
        for world_seed, walk_id, sequence, expected in fixtures:
            first = _stable_bucket(world_seed, walk_id, sequence, total)
            second = _stable_bucket(world_seed, walk_id, sequence, total)
            self.assertEqual(first, expected)
            self.assertEqual(second, expected)
            self.assertGreaterEqual(first, 0)
            self.assertLess(first, total)


if __name__ == "__main__":
    unittest.main()
