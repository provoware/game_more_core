import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.property import PropertyState
from bunkerfrequenz.presentation.district_projection import build_living_district_projection
from bunkerfrequenz.presentation.property_projection import build_property_projection


ROOT = Path(__file__).parents[2]
PROPERTY = json.loads((ROOT / "manifests" / "PROPERTY_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))


class PropertyProjectionTests(unittest.TestCase):
    def test_empty_projection_lists_exactly_seven_catalogued_purchasable_locations(self):
        result = build_property_projection(None, property_manifest=PROPERTY, city_map_manifest=CITY_MAP)
        self.assertFalse(result["persisted"])
        self.assertEqual(result["owned_count"], 0)
        self.assertEqual(result["purchasable_count"], 7)
        self.assertEqual(len(result["entries"]), 7)
        self.assertTrue(all(not item["owned"] for item in result["entries"]))
        self.assertNotIn("hall_of_tribute", {item["location_id"] for item in result["entries"]})

    def test_confirmed_ownership_feeds_existing_city_map_owned_flag(self):
        state = PropertyState(
            contract_version=PROPERTY["version"],
            revision=1,
            owned={
                "signalwerk": {
                    "location_id": "signalwerk",
                    "owner_character_id": "char.property",
                    "purchase_price_cents": 6_200_000,
                    "economy_transaction_id": "property:buy-signalwerk",
                    "event_id": "event-property",
                }
            },
        )
        property_projection = build_property_projection(
            state.to_dict(), property_manifest=PROPERTY, city_map_manifest=CITY_MAP
        )
        self.assertTrue(property_projection["persisted"])
        self.assertEqual(property_projection["owned_count"], 1)
        signal = next(item for item in property_projection["entries"] if item["location_id"] == "signalwerk")
        self.assertTrue(signal["owned"])
        self.assertEqual(signal["purchase_price_cents"], 6_200_000)

        district_projection = build_living_district_projection(
            None,
            district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP,
            owned_property_ids=frozenset(property_projection["owned_location_ids"]),
        )
        mapped = next(item for item in district_projection["city_map"]["locations"] if item["location_id"] == "signalwerk")
        hall = next(item for item in district_projection["city_map"]["locations"] if item["location_id"] == "hall_of_tribute")
        self.assertTrue(mapped["owned"])
        self.assertFalse(hall["owned"])

    def test_unknown_or_non_purchasable_persisted_ownership_fails_closed(self):
        bad = {
            "contract_version": PROPERTY["version"],
            "revision": 1,
            "owned": {
                "hall_of_tribute": {
                    "location_id": "hall_of_tribute",
                    "owner_character_id": "char.property",
                    "purchase_price_cents": 1,
                    "economy_transaction_id": "property:invalid",
                    "event_id": "event-property",
                }
            },
        }
        with self.assertRaises(ValueError):
            build_property_projection(bad, property_manifest=PROPERTY, city_map_manifest=CITY_MAP)


if __name__ == "__main__":
    unittest.main()
