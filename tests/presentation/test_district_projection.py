from copy import deepcopy
import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.district import DistrictState
from bunkerfrequenz.presentation.district_projection import build_living_district_projection


ROOT = Path(__file__).parents[2]
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))


class DistrictProjectionTests(unittest.TestCase):
    def build(self, state=None):
        return build_living_district_projection(
            state,
            district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP,
        )

    def test_defaults_are_visible_but_not_claimed_persisted(self):
        result = self.build()
        self.assertFalse(result["persisted"])
        self.assertEqual(result["revision"], 0)
        self.assertEqual(len(result["entries"]), 8)
        self.assertEqual(result["entries"][0]["metrics"], CITY_MAP["district_metric_defaults"])
        self.assertEqual(result["city_map"]["map_id"], "berlin_ops")

    def test_persisted_metrics_feed_existing_city_map_projection(self):
        state = DistrictState.from_city_map(
            contract_version=DISTRICTS["version"],
            district_ids=[item["district_id"] for item in CITY_MAP["districts"]],
            defaults=CITY_MAP["district_metric_defaults"],
        ).to_dict()
        state["metrics"]["friedrichshain"]["heat"] = 73
        state["metrics"]["friedrichshain"]["prestige"] = 66
        state["revision"] = 2
        before = deepcopy(state)
        result = self.build(state)
        by_id = {item["district_id"]: item for item in result["entries"]}
        map_by_id = {item["district_id"]: item for item in result["city_map"]["districts"]}
        self.assertTrue(result["persisted"])
        self.assertEqual(by_id["friedrichshain"]["metrics"]["heat"], 73)
        self.assertEqual(map_by_id["friedrichshain"]["metrics"]["prestige"], 66)
        self.assertEqual(state, before)

    def test_wrong_contract_and_unknown_district_fail_closed(self):
        state = DistrictState.from_city_map(
            contract_version=DISTRICTS["version"],
            district_ids=[item["district_id"] for item in CITY_MAP["districts"]],
            defaults=CITY_MAP["district_metric_defaults"],
        ).to_dict()
        state["contract_version"] = "wrong"
        with self.assertRaises(ValueError):
            self.build(state)

        state["contract_version"] = DISTRICTS["version"]
        state["metrics"]["fantasiebezirk"] = dict(CITY_MAP["district_metric_defaults"])
        with self.assertRaises(ValueError):
            self.build(state)


if __name__ == "__main__":
    unittest.main()
