from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class VenueOperatingProfilePresentationContractTests(unittest.TestCase):
    def setUp(self):
        self.projection = (ROOT / "src/bunkerfrequenz/presentation/property_upgrade_projection.py").read_text(encoding="utf-8")
        self.contract = (ROOT / "docs/VENUE_OPERATING_PROFILE_PRESENTATION_CONTRACT.md").read_text(encoding="utf-8")

    def test_projection_keeps_single_authoritative_value_set(self):
        self.assertIn(
            '_VALUE_KEYS = ("prestige", "audience_pull", "risk", "underground_factor", "utility")',
            self.projection,
        )
        self.assertIn('"effective_values": deepcopy(effective)', self.projection)
        self.assertIn('"effective_values_by_location": effective_values_by_location', self.projection)

    def test_contract_reuses_projection_without_mechanical_bonus_authority(self):
        self.assertIn("ausschließlich `property_upgrades.entries[*].effective_values`", self.contract)
        self.assertIn("keine zweite Berechnung derselben Werte im Browser", self.contract)
        self.assertIn("keine neuen Save-, Journal- oder Replay-Daten", self.contract)
        self.assertIn("keine Ableitung von Event-Verfügbarkeit, Kosten, Kapazität oder laufendem Ertrag", self.contract)

    def test_contract_is_owned_location_and_text_layer_safe(self):
        self.assertIn("nicht besessene Locations dürfen kein eigenes Betriebsprofil vortäuschen", self.contract)
        self.assertIn("Text-/Presentation-Schicht", self.contract)
        self.assertIn("nicht in Domain- oder Runtime-Code", self.contract)


if __name__ == "__main__":
    unittest.main()
