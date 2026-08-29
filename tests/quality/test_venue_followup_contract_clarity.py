from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
HELP = ROOT / "docs" / "VENUE_BENEFITS_LAIENHILFE.md"


class VenueFollowupContractClarityTests(unittest.TestCase):
    def test_help_names_one_concrete_followup_with_benefit_and_reason(self):
        text = HELP.read_text(encoding="utf-8")

        self.assertIn("## Konkrete Folgeidee: Venue→Settlement-Authority-Vertrag", text)
        self.assertIn("bestätigtes Event → eigener Ort → zum Settlement-Zeitpunkt gültige Publikumskraft", text)
        self.assertIn("**Nutzen:**", text)
        self.assertIn("**Begründung:**", text)
        self.assertIn("Settlement-Receipt", text)
        self.assertIn("ändert heute noch keine Balance", text)
        self.assertIn("keine Bonusengine", text)


if __name__ == "__main__":
    unittest.main()
