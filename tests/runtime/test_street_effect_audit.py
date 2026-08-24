import json
from itertools import permutations
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
STREET = json.loads(
    (ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8")
)


def _weighted_effect_totals(weights: dict[str, int]) -> dict[str, int]:
    effects = {
        encounter["encounter_id"]: encounter["effects"]
        for encounter in STREET["encounters"]
    }
    return {
        effect_name: sum(
            weight * effects[encounter_id][effect_name]
            for encounter_id, weight in weights.items()
        )
        for effect_name in ("energy_delta", "stress_delta", "reputation_delta")
    }


def _effect_profiles() -> dict[str, dict[str, int]]:
    return {
        approach["approach_id"]: _weighted_effect_totals(approach["weights"])
        for approach in STREET["approaches"]
    }


def _strictly_dominates(left: dict[str, int], right: dict[str, int]) -> bool:
    left_desirability = (
        left["energy_delta"],
        -left["stress_delta"],
        left["reputation_delta"],
    )
    right_desirability = (
        right["energy_delta"],
        -right["stress_delta"],
        right["reputation_delta"],
    )
    return all(a >= b for a, b in zip(left_desirability, right_desirability)) and any(
        a > b for a, b in zip(left_desirability, right_desirability)
    )


class StreetEffectAuditTests(unittest.TestCase):
    def test_expected_effect_vectors_match_the_declared_catalog(self):
        self.assertEqual(STREET["selection"]["weight_total"], 100)
        self.assertEqual(
            _effect_profiles(),
            {
                "balanced": {
                    "energy_delta": 100,
                    "stress_delta": -49,
                    "reputation_delta": 35,
                },
                "recovery": {
                    "energy_delta": 123,
                    "stress_delta": -49,
                    "reputation_delta": 23,
                },
                "network": {
                    "energy_delta": 53,
                    "stress_delta": -59,
                    "reputation_delta": 65,
                },
                "scout": {
                    "energy_delta": 91,
                    "stress_delta": -14,
                    "reputation_delta": 33,
                },
            },
        )

    def test_each_approach_has_a_positive_average_direction(self):
        for approach_id, profile in _effect_profiles().items():
            self.assertGreater(profile["energy_delta"], 0, approach_id)
            self.assertLess(profile["stress_delta"], 0, approach_id)
            self.assertGreater(profile["reputation_delta"], 0, approach_id)

    def test_strengths_and_current_dominance_are_explicit(self):
        profiles = _effect_profiles()
        self.assertEqual(max(profiles, key=lambda key: profiles[key]["energy_delta"]), "recovery")
        self.assertEqual(min(profiles, key=lambda key: profiles[key]["stress_delta"]), "network")
        self.assertEqual(max(profiles, key=lambda key: profiles[key]["reputation_delta"]), "network")

        dominance = {
            (left_id, right_id)
            for left_id, right_id in permutations(profiles, 2)
            if _strictly_dominates(profiles[left_id], profiles[right_id])
        }
        self.assertEqual(dominance, {("balanced", "scout")})


if __name__ == "__main__":
    unittest.main()
