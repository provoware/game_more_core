import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.property_upgrade import effective_venue_values


ROOT = Path(__file__).parents[2]
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
UPGRADES = json.loads((ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))


class VenueValueAuthorityTests(unittest.TestCase):
    def test_signalwerk_stage_level_two_matches_existing_projection_contract(self):
        location = next(item for item in CITY_MAP["locations"] if item["location_id"] == "signalwerk")

        values = effective_venue_values(
            location["values"],
            upgrade_slots=location["upgrade_slots"],
            upgrade_levels={"stage": 2},
            upgrade_catalog=UPGRADES["catalog"],
        )

        self.assertEqual(values, {
            "prestige": 84,
            "audience_pull": 94,
            "risk": 52,
            "underground_factor": 88,
            "utility": 84,
        })

    def test_authority_is_read_only_and_bounds_values(self):
        base = {
            "prestige": 99,
            "audience_pull": 1,
            "risk": 50,
            "underground_factor": 50,
            "utility": 50,
        }
        catalog = {
            "test": {
                "value_delta_per_level": {
                    "prestige": 10,
                    "audience_pull": -10,
                    "risk": 0,
                    "underground_factor": 0,
                    "utility": 0,
                }
            }
        }
        original = dict(base)

        values = effective_venue_values(
            base,
            upgrade_slots=["test"],
            upgrade_levels={"test": 1},
            upgrade_catalog=catalog,
        )

        self.assertEqual(values["prestige"], 100)
        self.assertEqual(values["audience_pull"], 0)
        self.assertEqual(base, original)

    def test_invalid_upgrade_level_fails_closed(self):
        location = next(item for item in CITY_MAP["locations"] if item["location_id"] == "signalwerk")

        with self.assertRaises(ValueError):
            effective_venue_values(
                location["values"],
                upgrade_slots=location["upgrade_slots"],
                upgrade_levels={"stage": 4},
                upgrade_catalog=UPGRADES["catalog"],
            )

    def test_upgrade_level_for_unavailable_location_slot_fails_closed(self):
        location = next(item for item in CITY_MAP["locations"] if item["location_id"] == "signalwerk")

        with self.assertRaisesRegex(ValueError, "passt nicht zu den Location-Slots"):
            effective_venue_values(
                location["values"],
                upgrade_slots=location["upgrade_slots"],
                upgrade_levels={"stage": 2, "ghost_slot": 1},
                upgrade_catalog=UPGRADES["catalog"],
            )


if __name__ == "__main__":
    unittest.main()
