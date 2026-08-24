import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
TEXTS = json.loads((ROOT / "content" / "de" / "ui" / "street_encounters.json").read_text(encoding="utf-8"))


class StreetPackContractTests(unittest.TestCase):
    def test_pack_expands_catalog_without_changing_macro_distribution(self):
        self.assertEqual(STREET["version"], "0.8.8-street-pack")
        self.assertIn("0.8.7-b1", STREET["approach_policy"]["compatible_replay_versions"])
        self.assertEqual(len(STREET["encounters"]), 16)

        new_ids = {
            "street.poster_wall",
            "street.open_door",
            "street.night_bus_seat",
            "street.cable_tip",
            "street.lost_glove",
            "street.construction_detour",
        }
        ids = {item["encounter_id"] for item in STREET["encounters"]}
        self.assertTrue(new_ids <= ids)

        totals = {"neutral": 0, "positive": 0, "negative": 0}
        for encounter in STREET["encounters"]:
            totals[encounter["polarity"]] += encounter["weight"]
        self.assertEqual(totals, {"neutral": 25, "positive": 60, "negative": 15})
        self.assertEqual(sum(totals.values()), STREET["selection"]["weight_total"])
        self.assertFalse(STREET["selection"]["system_time_as_seed"])

    def test_all_approaches_keep_same_catalog_and_total_weight(self):
        encounter_weights = {item["encounter_id"]: item["weight"] for item in STREET["encounters"]}
        encounter_ids = set(encounter_weights)
        balanced = next(item for item in STREET["approaches"] if item["approach_id"] == "balanced")
        self.assertEqual(balanced["weights"], encounter_weights)

        for approach in STREET["approaches"]:
            self.assertEqual(set(approach["weights"]), encounter_ids)
            self.assertEqual(sum(approach["weights"].values()), 100)
            self.assertNotIn("effects", approach)

    def test_every_encounter_has_complete_german_copy(self):
        for encounter in STREET["encounters"]:
            title_key = encounter["title_key"]
            body_key = encounter["body_key"]
            self.assertIsInstance(TEXTS.get(title_key), str, title_key)
            self.assertTrue(TEXTS[title_key].strip(), title_key)
            self.assertIsInstance(TEXTS.get(body_key), str, body_key)
            self.assertTrue(TEXTS[body_key].strip(), body_key)

    def test_pack_does_not_add_economy_or_inventory_effects(self):
        self.assertFalse(STREET["policy"]["inventory_changes"])
        self.assertFalse(STREET["policy"]["economy_changes"])
        for encounter in STREET["encounters"]:
            self.assertEqual(
                set(encounter["effects"]),
                {"energy_delta", "stress_delta", "reputation_delta"},
            )
            self.assertTrue(all(abs(value) <= 10 for value in encounter["effects"].values()))


if __name__ == "__main__":
    unittest.main()
