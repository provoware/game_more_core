from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
HELP = ROOT / "docs" / "VENUE_BENEFITS_LAIENHILFE.md"


class VenueBenefitsHelpCurrentStageTests(unittest.TestCase):
    def test_help_tracks_existing_resolver_and_next_receipt_boundary(self):
        text = HELP.read_text(encoding="utf-8")

        self.assertIn("Seit PR #273 existiert außerdem der **read-only Evidence-Resolver**", text)
        self.assertIn("resolve_owned_venue_evidence(...)`", text)
        self.assertIn("Damit ist die reine Authority-Brücke **bereits vorhanden**", text)
        self.assertIn("nicht im Settlement-State, Settlement-Receipt, Journal oder Save gespeichert", text)
        self.assertIn("nicht mehr der Resolver selbst", text)
        self.assertIn("minimale versionierte Aufnahme der bereits bestätigten Venue-Evidence", text)
        self.assertIn("mechanische Bonus weiterhin gesperrt", text)
        self.assertNotIn(
            "Der nächste sinnvolle Gameplay-Schritt ist jetzt die minimale, versionierte Venue→Settlement-Evidence-Brücke.",
            text,
        )


if __name__ == "__main__":
    unittest.main()
