import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.district_projection import build_living_district_projection
from bunkerfrequenz.presentation.property_projection import build_property_projection
from bunkerfrequenz.presentation.property_upgrade_projection import build_property_upgrade_projection


ROOT = Path(__file__).parents[2]
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
PROPERTY = json.loads((ROOT / "manifests" / "PROPERTY_MANIFEST.json").read_text(encoding="utf-8"))
UPGRADES = json.loads((ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))


def owned_signalwerk() -> dict:
    return {
        "contract_version": PROPERTY["version"],
        "revision": 1,
        "owned": {
            "signalwerk": {
                "location_id": "signalwerk",
                "owner_character_id": "char.presentation",
                "purchase_price_cents": 6_200_000,
                "economy_transaction_id": "property:buy-signalwerk",
                "event_id": "event-presentation",
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
                        "economy_transaction_ids": [f"property_upgrade:stage-{index}" for index in range(1, level + 1)],
                    }
                },
            }
        },
    }


class PropertyUpgradeProjectionTests(unittest.TestCase):
    def test_level_two_stage_changes_confirmed_values_and_map_tier(self):
        properties = build_property_projection(
            owned_signalwerk(),
            property_manifest=PROPERTY,
            city_map_manifest=CITY_MAP,
        )
        upgrades = build_property_upgrade_projection(
            stage_level(2),
            upgrade_manifest=UPGRADES,
            city_map_manifest=CITY_MAP,
            property_projection=properties,
        )
        entry = next(item for item in upgrades["entries"] if item["location_id"] == "signalwerk")
        self.assertEqual(entry["effective_values"], {
            "prestige": 84,
            "audience_pull": 94,
            "risk": 52,
            "underground_factor": 88,
            "utility": 84,
        })
        stage = next(item for item in entry["upgrades"] if item["upgrade_id"] == "stage")
        self.assertEqual(stage["level"], 2)
        self.assertEqual(stage["next_level"], 3)
        self.assertEqual(stage["next_cost_cents"], 1_255_500)

        living = build_living_district_projection(
            None,
            district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP,
            owned_property_ids={"signalwerk"},
            location_value_overrides=upgrades["effective_values_by_location"],
        )
        map_entry = next(
            item for item in living["city_map"]["locations"]
            if item["location_id"] == "signalwerk"
        )
        self.assertEqual(map_entry["values"], entry["effective_values"])
        self.assertEqual(map_entry["score"], 85.5)
        self.assertEqual(map_entry["tier"], "legendary")
        self.assertTrue(map_entry["owned"])

    def test_projection_without_upgrade_state_stays_level_zero_and_preserves_base_values(self):
        properties = build_property_projection(
            owned_signalwerk(),
            property_manifest=PROPERTY,
            city_map_manifest=CITY_MAP,
        )
        upgrades = build_property_upgrade_projection(
            None,
            upgrade_manifest=UPGRADES,
            city_map_manifest=CITY_MAP,
            property_projection=properties,
        )
        entry = next(item for item in upgrades["entries"] if item["location_id"] == "signalwerk")
        stage = next(item for item in entry["upgrades"] if item["upgrade_id"] == "stage")
        self.assertEqual(stage["level"], 0)
        self.assertEqual(stage["next_level"], 1)
        self.assertEqual(stage["next_cost_cents"], 558_000)
        base = next(item for item in CITY_MAP["locations"] if item["location_id"] == "signalwerk")
        self.assertEqual(entry["effective_values"], base["values"])

    def test_unowned_location_keeps_internal_values_but_exposes_no_operating_profile(self):
        properties = build_property_projection(
            None,
            property_manifest=PROPERTY,
            city_map_manifest=CITY_MAP,
        )
        upgrades = build_property_upgrade_projection(
            None,
            upgrade_manifest=UPGRADES,
            city_map_manifest=CITY_MAP,
            property_projection=properties,
        )
        entry = next(item for item in upgrades["entries"] if item["location_id"] == "signalwerk")
        base = next(item for item in CITY_MAP["locations"] if item["location_id"] == "signalwerk")

        self.assertFalse(entry["owned"])
        self.assertIsNone(entry["effective_values"])
        self.assertEqual(upgrades["effective_values_by_location"]["signalwerk"], base["values"])

    def test_upgrade_state_for_unowned_property_fails_closed(self):
        properties = build_property_projection(
            None,
            property_manifest=PROPERTY,
            city_map_manifest=CITY_MAP,
        )
        with self.assertRaises(ValueError):
            build_property_upgrade_projection(
                stage_level(1),
                upgrade_manifest=UPGRADES,
                city_map_manifest=CITY_MAP,
                property_projection=properties,
            )

    def test_persisted_upgrade_outside_location_slots_fails_closed_before_filtering(self):
        properties = build_property_projection(
            owned_signalwerk(),
            property_manifest=PROPERTY,
            city_map_manifest=CITY_MAP,
        )
        raw_state = stage_level(1)
        raw_state["revision"] = 2
        raw_state["properties"]["signalwerk"]["upgrades"]["ghost_slot"] = {
            "level": 1,
            "economy_transaction_ids": ["property_upgrade:ghost-slot-1"],
        }

        with self.assertRaisesRegex(ValueError, "passt nicht zu den Location-Slots"):
            build_property_upgrade_projection(
                raw_state,
                upgrade_manifest=UPGRADES,
                city_map_manifest=CITY_MAP,
                property_projection=properties,
            )


if __name__ == "__main__":
    unittest.main()
