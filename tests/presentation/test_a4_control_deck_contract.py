import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection


ROOT = Path(__file__).parents[2]
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "styles.css").read_text(encoding="utf-8")
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
STREET_TEXT = json.loads((ROOT / "content" / "de" / "ui" / "street_encounters.json").read_text(encoding="utf-8"))


INCIDENT = {
    "power_drop": {
        "incident_type": "power_drop",
        "title_key": "incident.power_drop.title",
        "base_severity": 3,
        "responses": {
            "power_drop.generator": {
                "label_key": "incident.power_drop.generator",
                "target_phase": "live",
                "effects": {
                    "budget_delta_cents": -5000,
                    "reputation_delta": 2,
                    "crew_stress_delta": 1,
                    "stability_delta": 2,
                    "heat_delta": 0,
                },
            }
        },
    }
}


class A4ControlDeckContractTests(unittest.TestCase):
    def test_projection_exposes_only_display_metadata_for_street_approaches(self):
        result = build_a4_game_projection(
            {},
            incident_catalog=INCIDENT,
            street_manifest=STREET,
            street_text_catalog=STREET_TEXT,
        )
        self.assertEqual(
            [item["approach_id"] for item in result["street_approaches"]],
            ["balanced", "recovery", "network", "scout"],
        )
        self.assertEqual(sum(item["selected_by_default"] for item in result["street_approaches"]), 1)
        for item in result["street_approaches"]:
            self.assertEqual(set(item), {"approach_id", "label", "description", "selected_by_default"})
            self.assertNotIn("weights", item)
            self.assertNotIn("effects", item)

    def test_incident_projection_carries_confirmed_effect_preview(self):
        result = build_a4_game_projection({}, incident_catalog=INCIDENT)
        response = result["incident_catalog"][0]["responses"][0]
        self.assertEqual(response["target_phase"], "live")
        self.assertEqual(response["effects"]["budget_delta_cents"], -5000)
        self.assertEqual(response["effects"]["reputation_delta"], 2)

    def test_ui_preferences_are_local_only_and_script_order_is_safe(self):
        self.assertLess(INDEX.index('src="ui_prefs.js"'), INDEX.index('src="app.js"'))
        self.assertIn('data-ui-pref="compact"', INDEX)
        self.assertIn('data-ui-pref="highContrast"', INDEX)
        self.assertIn('data-ui-pref="largeText"', INDEX)
        self.assertIn("localStorage", PREFS)
        for token in ("/api/", "fetch(", "XMLHttpRequest", "sendCommand", "navigator.geolocation"):
            with self.subTest(token=token):
                self.assertNotIn(token, PREFS)

    def test_street_browser_sends_only_approach_id_not_weights_or_effects(self):
        self.assertIn('approach_id: state.streetApproach', APP)
        command_fragment = APP[APP.index('$("street-walk").addEventListener'):]
        command_fragment = command_fragment[:command_fragment.index("for (const mode")]
        self.assertNotIn("weights", command_fragment)
        self.assertNotIn("effects", command_fragment)
        self.assertIn('role="radiogroup" aria-label="Ansatz für die Straßenrunde"', INDEX)

    def test_control_deck_has_hud_navigation_choices_and_accessibility_modes(self):
        for marker in (
            'class="ops-hud"',
            'class="quick-nav"',
            'id="ui-options-panel"',
            'id="street-approaches"',
            'id="incident-content"',
        ):
            self.assertIn(marker, INDEX)
        for css in (
            ".ops-hud",
            ".quick-nav",
            ".street-approach-card",
            ".incident-choice",
            "body.ui-compact",
            "body.ui-high-contrast",
            "body.ui-large-text",
            "@media (prefers-reduced-motion: reduce)",
        ):
            self.assertIn(css, STYLES)


if __name__ == "__main__":
    unittest.main()
