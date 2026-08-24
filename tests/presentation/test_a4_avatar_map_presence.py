from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MAP_UI = (ROOT / "web" / "a4" / "map_usability.js").read_text(encoding="utf-8")
UI_PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")


class A4AvatarMapPresenceTests(unittest.TestCase):
    def test_existing_map_usability_layer_reuses_confirmed_hud_identity_for_owned_places(self):
        for token in (
            '.hud-crew-preview',
            '.hud-crew-identity',
            '#berlin-map-canvas .map-marker.owned',
            '.map-chip.owned',
            'map-crew-badge',
            'map-detail-crew',
            'Bestätigte Crew-Marke für diesen eigenen Ort',
        ):
            with self.subTest(token=token):
                self.assertIn(token, MAP_UI)
        self.assertNotIn('.map-marker:not(.owned)', MAP_UI)

    def test_map_presence_stays_read_only_and_uses_existing_map_loader_and_observer(self):
        self.assertIn('appendModule("map_usability.js", "map-usability")', UI_PREFS)
        self.assertIn('observer = new MutationObserver(scheduleEnhance)', MAP_UI)
        self.assertIn('observer?.disconnect()', MAP_UI)
        for forbidden in ("fetch(", "/api/", "sendCommand", "localStorage", "sessionStorage"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, MAP_UI)

    def test_badges_are_compact_and_cannot_change_map_semantics(self):
        for token in (
            'crewBadge("map-crew-badge", "1.35rem")',
            'crewBadge("map-detail-crew-preview", "2rem")',
            'badge.setAttribute("aria-hidden", "true")',
            'badge.style.pointerEvents = "none"',
            'identity.append(badge, node("span", "", "DEINE CREW"))',
        ):
            with self.subTest(token=token):
                self.assertIn(token, MAP_UI)


if __name__ == "__main__":
    unittest.main()
