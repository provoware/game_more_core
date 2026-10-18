from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
HELP = ROOT / "docs" / "VENUE_BENEFITS_LAIENHILFE.md"


class VenueBenefitsHelpCurrentStageTests(unittest.TestCase):
    def test_help_tracks_existing_resolver_and_next_receipt_boundary(self):
        text = HELP.read_text(encoding="utf-8")

        self.assertIn("0.8.8-venue-evidence-v1", text)
        self.assertIn("0.8.3-c1", text)
        self.assertIn("zusammen mit der Abrechnung gespeichert", text)
        self.assertIn("Ein späterer Ausbau ändert den bereits gespeicherten Nachweis nicht", text)
        self.assertIn("kein nachträglicher Ortswert", text)
        self.assertIn("keinen zusätzlichen Gewinn oder Bonus", text)
        self.assertIn("Eine mechanische Wirkung bleibt NO-GO", text)
        self.assertNotIn("nicht im Settlement-State, Settlement-Receipt, Journal oder Save gespeichert", text)


if __name__ == "__main__":
    unittest.main()
