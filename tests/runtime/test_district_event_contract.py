import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
TEXT = json.loads((ROOT / "content" / "de" / "ui" / "district_events.json").read_text(encoding="utf-8"))


class DistrictEventContractTests(unittest.TestCase):
    def test_contract_reuses_existing_district_and_city_map_authority(self):
        self.assertEqual(EVENTS["district_state_manifest_version"], DISTRICTS["version"])
        self.assertEqual(EVENTS["city_map_manifest_version"], CITY_MAP["version"])
        self.assertEqual(EVENTS["effect_contract"]["metrics"], DISTRICTS["metrics"])
        self.assertEqual(EVENTS["effect_contract"]["district_bounds_remain"], DISTRICTS["bounds"])

    def test_selection_is_replayable_and_client_has_no_gameplay_authority(self):
        selection = EVENTS["selection"]
        self.assertEqual(selection["method"], "sha256_stable_weighted")
        self.assertFalse(selection["system_time_as_seed"])
        self.assertFalse(selection["reroll_on_reload"])
        self.assertEqual(selection["seed_fields"], ["world_seed", "district_id", "trigger_id"])
        policy = EVENTS["activation_policy"]
        self.assertEqual(policy["maximum_active_instances_per_context"], 1)
        self.assertFalse(policy["client_can_activate"])
        self.assertFalse(policy["client_can_supply_effects"])
        self.assertTrue(policy["effects_apply_only_after_confirmed_resolution"])

    def test_catalog_has_unique_ids_bounded_effects_and_exact_weight_total(self):
        events = EVENTS["events"]
        ids = [item["event_id"] for item in events]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item.startswith("district.") for item in ids))
        self.assertEqual(sum(item["weight"] for item in events), EVENTS["selection"]["weight_total"])
        minimum = EVENTS["effect_contract"]["per_event_delta_minimum"]
        maximum = EVENTS["effect_contract"]["per_event_delta_maximum"]
        expected_metrics = set(DISTRICTS["metrics"])
        for event in events:
            with self.subTest(event=event["event_id"]):
                self.assertGreater(event["weight"], 0)
                self.assertEqual(set(event["effects"]), expected_metrics)
                self.assertTrue(all(minimum <= value <= maximum for value in event["effects"].values()))
                self.assertIn(event["title_key"], TEXT)
                self.assertIn(event["body_key"], TEXT)

    def test_requirements_reference_only_existing_bounded_district_metrics(self):
        allowed = {
            "minimum_heat": "heat",
            "minimum_prestige": "prestige",
            "minimum_police_pressure": "police_pressure",
            "minimum_scene_activity": "scene_activity",
            "maximum_heat": "heat",
            "maximum_prestige": "prestige",
            "maximum_police_pressure": "police_pressure",
            "maximum_scene_activity": "scene_activity",
        }
        for event in EVENTS["events"]:
            for key, value in event["requirements"].items():
                with self.subTest(event=event["event_id"], requirement=key):
                    self.assertIn(key, allowed)
                    self.assertIn(allowed[key], DISTRICTS["metrics"])
                    self.assertIs(type(value), int)
                    self.assertGreaterEqual(value, DISTRICTS["bounds"]["minimum"])
                    self.assertLessEqual(value, DISTRICTS["bounds"]["maximum"])


if __name__ == "__main__":
    unittest.main()
