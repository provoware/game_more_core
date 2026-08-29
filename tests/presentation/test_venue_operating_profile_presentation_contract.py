from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class VenueOperatingProfilePresentationContractTests(unittest.TestCase):
    def setUp(self):
        self.domain = (ROOT / "src/bunkerfrequenz/domain/property_upgrade.py").read_text(encoding="utf-8")
        self.projection = (ROOT / "src/bunkerfrequenz/presentation/property_upgrade_projection.py").read_text(encoding="utf-8")
        self.contract = (ROOT / "docs/VENUE_OPERATING_PROFILE_PRESENTATION_CONTRACT.md").read_text(encoding="utf-8")
        self.app = (ROOT / "web/a4/app.js").read_text(encoding="utf-8")

    def test_projection_keeps_single_authoritative_value_set(self):
        self.assertIn(
            'VENUE_VALUE_KEYS = ("prestige", "audience_pull", "risk", "underground_factor", "utility")',
            self.domain,
        )
        self.assertIn("def effective_venue_values", self.domain)
        self.assertIn("effective_venue_values(", self.projection)
        self.assertNotIn("def _bounded", self.projection)
        self.assertIn('"effective_values": deepcopy(effective) if owned else None', self.projection)
        self.assertIn('"effective_values_by_location": effective_values_by_location', self.projection)

    def test_contract_reuses_projection_without_mechanical_bonus_authority(self):
        self.assertIn("ausschließlich `property_upgrades.entries[*].effective_values`", self.contract)
        self.assertIn("keine zweite Berechnung derselben Werte im Browser", self.contract)
        self.assertIn("keine neuen Save-, Journal- oder Replay-Daten", self.contract)
        self.assertIn("keine Ableitung von Event-Verfügbarkeit, Kosten, Kapazität oder laufendem Ertrag", self.contract)

    def test_contract_is_owned_location_and_text_layer_safe(self):
        self.assertIn("per Eintrag sichtbaren `effective_values` werden nur für besessene Locations ausgegeben", self.contract)
        self.assertIn("nicht besessene Locations dürfen kein eigenes Betriebsprofil vortäuschen", self.contract)
        self.assertIn("Text-/Presentation-Schicht", self.contract)
        self.assertIn("nicht in Domain- oder Runtime-Code", self.contract)

    def test_browser_uses_clear_german_labels_for_all_five_confirmed_values(self):
        expected = (
            "Prestige ${values.prestige} · Publikumskraft ${values.audience_pull} · "
            "Risiko ${values.risk} · Underground-Faktor ${values.underground_factor} · "
            "Nutzen ${values.utility}"
        )
        self.assertIn(expected, self.app)
        self.assertNotIn("` · P ${values.prestige}", self.app)
        self.assertNotIn("· Pull ${values.audience_pull}", self.app)
        self.assertNotIn("· UG ${values.underground_factor}", self.app)


if __name__ == "__main__":
    unittest.main()
