import json
from pathlib import Path
import unittest

from bunkerfrequenz.application.venue_settlement_evidence import resolve_owned_venue_evidence
from bunkerfrequenz.domain.property import PropertyState
from bunkerfrequenz.domain.property_upgrade import PropertyUpgradeState


ROOT = Path(__file__).parents[2]
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
UPGRADES = json.loads((ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))


def _property_state() -> PropertyState:
    return PropertyState(
        contract_version="0.8.6-a1",
        revision=7,
        owned={
            "signalwerk": {
                "location_id": "signalwerk",
                "owner_character_id": "char:operator",
                "purchase_price_cents": 6_200_000,
                "economy_transaction_id": "tx:property:signalwerk",
                "event_id": "event:purchase:signalwerk",
            }
        },
    )


def _upgrade_state() -> PropertyUpgradeState:
    return PropertyUpgradeState(
        contract_version="0.8.6-b1",
        revision=4,
        properties={
            "signalwerk": {
                "location_id": "signalwerk",
                "upgrades": {
                    "stage": {
                        "level": 2,
                        "economy_transaction_ids": ["tx:stage:1", "tx:stage:2"],
                    }
                },
            }
        },
    )


class VenueSettlementEvidenceResolverTests(unittest.TestCase):
    def test_owned_event_location_resolves_confirmed_audience_pull(self):
        evidence = resolve_owned_venue_evidence(
            event_location={"location_id": "signalwerk"},
            settlement_character_id="char:operator",
            property_state=_property_state(),
            property_upgrade_state=_upgrade_state(),
            city_map_manifest=CITY_MAP,
            upgrade_manifest=UPGRADES,
        )

        self.assertEqual(
            evidence,
            {
                "schema_version": 1,
                "location_id": "signalwerk",
                "owner_character_id": "char:operator",
                "audience_pull": 94,
                "property_revision": 7,
                "property_upgrade_revision": 4,
            },
        )

    def test_unowned_or_foreign_owned_location_produces_no_evidence(self):
        for location, character_id in (
            ({"location_id": "concrete_orbit"}, "char:operator"),
            ({"location_id": "signalwerk"}, "char:other"),
        ):
            with self.subTest(location=location, character_id=character_id):
                self.assertIsNone(
                    resolve_owned_venue_evidence(
                        event_location=location,
                        settlement_character_id=character_id,
                        property_state=_property_state(),
                        property_upgrade_state=_upgrade_state(),
                        city_map_manifest=CITY_MAP,
                        upgrade_manifest=UPGRADES,
                    )
                )

    def test_foreign_persisted_upgrade_fails_closed(self):
        upgrades = _upgrade_state()
        upgrades.properties["signalwerk"]["upgrades"]["ghost_slot"] = {
            "level": 1,
            "economy_transaction_ids": ["tx:ghost:1"],
        }

        with self.assertRaisesRegex(ValueError, "Location-Slots"):
            resolve_owned_venue_evidence(
                event_location={"location_id": "signalwerk"},
                settlement_character_id="char:operator",
                property_state=_property_state(),
                property_upgrade_state=upgrades,
                city_map_manifest=CITY_MAP,
                upgrade_manifest=UPGRADES,
            )


if __name__ == "__main__":
    unittest.main()
