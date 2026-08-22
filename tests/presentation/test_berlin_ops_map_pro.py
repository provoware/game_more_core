import json
from copy import deepcopy
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.berlin_ops_map_pro import build_berlin_ops_map_pro_projection
from bunkerfrequenz.presentation.district_projection import build_living_district_projection
from bunkerfrequenz.presentation.property_projection import build_property_projection
from bunkerfrequenz.presentation.property_upgrade_projection import build_property_upgrade_projection


ROOT = Path(__file__).parents[2]
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
PROPERTY = json.loads((ROOT / "manifests" / "PROPERTY_MANIFEST.json").read_text(encoding="utf-8"))
UPGRADES = json.loads((ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
MAP_PRO = json.loads((ROOT / "manifests" / "BERLIN_OPS_MAP_PRO_MANIFEST.json").read_text(encoding="utf-8"))


def owned_signalwerk() -> dict:
    return {
        "contract_version": PROPERTY["version"],
        "revision": 1,
        "owned": {
            "signalwerk": {
                "location_id": "signalwerk",
                "owner_character_id": "char.map-pro",
                "purchase_price_cents": 6_200_000,
                "economy_transaction_id": "property:buy-signalwerk",
                "event_id": "event-map-pro",
            }
        },
    }


def stage_level(level: int) -> dict:
    return {
        "contract_version": UPGRADES["version"],
        "revision": level,
        "properties": {
            "signalwerk": {
                "location_id": "signalwerk",
                "upgrades": {
                    "stage": {
                        "level": level,
                        "economy_transaction_ids": [
                            f"property_upgrade:signalwerk:stage:L{index}"
                            for index in range(1, level + 1)
                        ],
                    }
                },
            }
        },
    }


def confirmed_world(*, upgraded_stage_level: int | None = None):
    properties = build_property_projection(
        owned_signalwerk() if upgraded_stage_level is not None else None,
        property_manifest=PROPERTY,
        city_map_manifest=CITY_MAP,
    )
    upgrade_projection = None
    overrides = None
    owned_ids = frozenset(properties["owned_location_ids"])
    if upgraded_stage_level is not None:
        upgrade_projection = build_property_upgrade_projection(
            stage_level(upgraded_stage_level),
            upgrade_manifest=UPGRADES,
            city_map_manifest=CITY_MAP,
            property_projection=properties,
        )
        overrides = upgrade_projection["effective_values_by_location"]
    living = build_living_district_projection(
        None,
        district_manifest=DISTRICTS,
        city_map_manifest=CITY_MAP,
        owned_property_ids=owned_ids,
        location_value_overrides=overrides,
    )
    return living, upgrade_projection


class BerlinOpsMapProProjectionTests(unittest.TestCase):
    def test_base_world_is_read_only_complete_and_stylized(self):
        living, upgrades = confirmed_world()
        model = build_berlin_ops_map_pro_projection(
            living,
            property_upgrades=upgrades,
            map_pro_manifest=MAP_PRO,
        )
        self.assertEqual(model["version"], "0.8.6-c1")
        self.assertEqual(model["geography_mode"], "stylized_game_map_not_navigation")
        self.assertEqual(model["summary"], {
            "district_count": 8,
            "location_count": 12,
            "owned_count": 0,
            "hall_count": 1,
        })
        self.assertEqual(model["filters"], ["all", "owned", "prime", "hall"])
        self.assertEqual(model["policy"], {
            "read_only": True,
            "domain_write": False,
            "navigation": False,
            "geocoding": False,
            "coordinates": "stylized_0_100",
        })
        self.assertTrue(model["accessibility"]["keyboard"])
        self.assertTrue(model["accessibility"]["visible_focus"])
        self.assertTrue(model["accessibility"]["reduced_motion"])
        self.assertTrue(model["accessibility"]["information_without_color"])
        for district in model["districts"]:
            box = district["map_box"]
            self.assertGreaterEqual(box["x"], 0)
            self.assertGreaterEqual(box["y"], 0)
            self.assertLessEqual(box["x"] + box["w"], 100)
            self.assertLessEqual(box["y"] + box["h"], 100)
        for location in model["locations"]:
            self.assertGreaterEqual(location["position"]["x"], 0)
            self.assertLessEqual(location["position"]["x"], 100)
            self.assertGreaterEqual(location["position"]["y"], 0)
            self.assertLessEqual(location["position"]["y"], 100)

    def test_confirmed_property_upgrade_propagates_without_recomputing_score_or_tier(self):
        living, upgrades = confirmed_world(upgraded_stage_level=2)
        source = next(
            item for item in living["city_map"]["locations"]
            if item["location_id"] == "signalwerk"
        )
        model = build_berlin_ops_map_pro_projection(
            living,
            property_upgrades=upgrades,
            map_pro_manifest=MAP_PRO,
        )
        location = next(
            item for item in model["locations"]
            if item["location_id"] == "signalwerk"
        )
        self.assertTrue(location["owned"])
        self.assertEqual(model["summary"]["owned_count"], 1)
        self.assertEqual(location["values"], source["values"])
        self.assertEqual(location["score"], source["score"])
        self.assertEqual(location["tier"], source["tier"])
        self.assertEqual(location["score"], 85.5)
        self.assertEqual(location["tier"], "legendary")
        self.assertEqual(location["upgrade_level_total"], 2)
        stage = next(item for item in location["upgrades"] if item["upgrade_id"] == "stage")
        self.assertEqual(stage["level"], 2)
        self.assertEqual(stage["max_level"], 3)

    def test_unknown_tier_and_unknown_upgrade_location_fail_closed(self):
        living, upgrades = confirmed_world(upgraded_stage_level=1)
        bad_living = deepcopy(living)
        bad_living["city_map"]["locations"][0]["tier"] = "impossible"
        with self.assertRaises(ValueError):
            build_berlin_ops_map_pro_projection(
                bad_living,
                property_upgrades=upgrades,
                map_pro_manifest=MAP_PRO,
            )

        bad_upgrades = deepcopy(upgrades)
        bad_upgrades["entries"].append({
            "location_id": "unknown_location",
            "upgrades": [],
        })
        with self.assertRaises(ValueError):
            build_berlin_ops_map_pro_projection(
                living,
                property_upgrades=bad_upgrades,
                map_pro_manifest=MAP_PRO,
            )

    def test_renderer_contract_rejects_navigation_or_domain_write(self):
        living, upgrades = confirmed_world()
        for path, value in (
            (("interaction", "domain_write"), True),
            (("geography_mode",), "real_navigation"),
            (("filters",), ["all", "owned"]),
        ):
            with self.subTest(path=path):
                bad = deepcopy(MAP_PRO)
                if len(path) == 2:
                    bad[path[0]][path[1]] = value
                else:
                    bad[path[0]] = value
                with self.assertRaises(ValueError):
                    build_berlin_ops_map_pro_projection(
                        living,
                        property_upgrades=upgrades,
                        map_pro_manifest=bad,
                    )


if __name__ == "__main__":
    unittest.main()
