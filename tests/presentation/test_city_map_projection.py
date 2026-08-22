import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.city_map_projection import build_city_map_projection


class CityMapProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (Path(__file__).parents[2] / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8")
        )

    def test_projection_has_unique_hall_ranking_and_property_metadata(self):
        projection = build_city_map_projection(self.manifest, owned_property_ids={"sublevel_44"})
        self.assertEqual(projection["geography_mode"], "stylized_game_map_not_navigation")
        self.assertEqual(projection["hall_of_tribute"]["location_id"], "hall_of_tribute")
        self.assertEqual(projection["hall_of_tribute"]["tier"], "legendary")
        owned = next(item for item in projection["locations"] if item["location_id"] == "sublevel_44")
        self.assertTrue(owned["owned"])
        self.assertTrue(owned["purchasable"])
        self.assertGreater(owned["purchase_price_cents"], 0)
        self.assertEqual(projection["top_locations"][0]["rank"], 1)

    def test_district_metrics_are_read_only_overrides_and_bounded(self):
        projection = build_city_map_projection(
            self.manifest,
            district_metrics={"friedrichshain": {"heat": 77, "scene_activity": 91}},
        )
        district = next(item for item in projection["districts"] if item["district_id"] == "friedrichshain")
        self.assertEqual(district["metrics"]["heat"], 77)
        self.assertEqual(district["metrics"]["scene_activity"], 91)
        self.assertEqual(district["metrics"]["prestige"], 20)
        with self.assertRaises(ValueError):
            build_city_map_projection(self.manifest, district_metrics={"friedrichshain": {"heat": 101}})

    def test_location_scores_and_tiers_are_deterministic(self):
        first = build_city_map_projection(self.manifest)
        second = build_city_map_projection(self.manifest)
        self.assertEqual(first, second)
        ranks = sorted(item["rank"] for item in first["locations"])
        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))
        for item in first["locations"]:
            self.assertGreaterEqual(item["score"], 0)
            self.assertLessEqual(item["score"], 100)
            self.assertIn(item["tier"], {"legendary", "prime", "strong", "standard"})

    def test_unknown_owned_property_fails_closed(self):
        with self.assertRaises(ValueError):
            build_city_map_projection(self.manifest, owned_property_ids={"does-not-exist"})


if __name__ == "__main__":
    unittest.main()
