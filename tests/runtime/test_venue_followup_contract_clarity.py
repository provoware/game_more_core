import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[2]
HELP = ROOT / "docs" / "VENUE_BENEFITS_LAIENHILFE.md"
SETTLEMENT_MANIFEST = ROOT / "manifests" / "SETTLEMENT_MANIFEST.json"
PROPERTY_UPGRADE_MANIFEST = ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json"
APP = ROOT / "web" / "a4" / "app.js"


class VenueFollowupContractClarityTests(unittest.TestCase):
    def test_help_names_one_concrete_followup_with_benefit_and_reason(self):
        text = HELP.read_text(encoding="utf-8")

        self.assertIn("## Konkrete Folgeidee: Venue→Settlement-Authority-Vertrag", text)
        self.assertIn(
            "bestätigtes Event → eigener Ort → zum Settlement-Zeitpunkt gültige Publikumskraft",
            text,
        )
        self.assertIn("**Nutzen:**", text)
        self.assertIn("**Begründung:**", text)
        self.assertIn("Settlement-Receipt", text)
        self.assertIn("ändert heute noch keine Balance", text)
        self.assertIn("zweite Bonusengine", text)

    def test_authority_followup_is_explicitly_non_mechanical_and_implementation_backed(self):
        text = HELP.read_text(encoding="utf-8")
        boundary = text.split("### Harte Grenze für diesen Folgeschritt", 1)[1].split(
            "### Spätere Verbesserungsidee", 1
        )[0]
        settlement = json.loads(SETTLEMENT_MANIFEST.read_text(encoding="utf-8"))
        upgrades = json.loads(PROPERTY_UPGRADE_MANIFEST.read_text(encoding="utf-8"))
        app = APP.read_text(encoding="utf-8")
        render = re.search(
            r"function renderProperties\(properties, propertyUpgrades\) \{(?P<body>.*?)\n\}",
            app,
            re.DOTALL,
        )

        self.assertIn("nur den Beweisweg", boundary)
        self.assertIn("noch keine Bonusformel", boundary)
        self.assertIn("keinen Multiplikator", boundary)
        self.assertIn("keine neue Auszahlung", boundary)
        self.assertIn("keine Browser-Berechnung", boundary)
        self.assertIn("erst Autorität und Evidence, danach separat Balance und Wirkung", boundary)

        self.assertFalse(settlement["scope_boundaries"]["property_changes"])
        self.assertNotIn("audience_pull", settlement["source_effects"])
        self.assertNotIn("venue_audience_pull", settlement["application"])
        self.assertFalse(upgrades["projection"]["gameplay_event_rules_changed"])

        self.assertIsNotNone(render, "renderProperties fehlt")
        renderer = render.group("body")
        self.assertIn("upgradeEntry?.effective_values", renderer)
        self.assertRegex(renderer, r"detail\.textContent\s*=")
        self.assertNotRegex(renderer, r"detail\.innerHTML\s*=")

    def test_help_keeps_future_receipt_feedback_read_only_and_confirmed(self):
        text = HELP.read_text(encoding="utf-8")

        self.assertIn("### Spätere Verbesserungsidee: sichtbarer Receipt-Hinweis", text)
        self.assertIn("read-only", text)
        self.assertIn("bestätigte Ursache", text)
        self.assertIn("keine neue Berechnung im Browser", text)


if __name__ == "__main__":
    unittest.main()
