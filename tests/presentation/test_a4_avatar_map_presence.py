from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MODULE = (ROOT / "web" / "a4" / "avatar_map_presence.js").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "avatar_map_presence.css").read_text(encoding="utf-8")
UI_PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")


class A4AvatarMapPresenceTests(unittest.TestCase):
    def test_module_reuses_confirmed_hud_identity_and_only_marks_owned_locations(self):
        for token in (
            '.hud-crew-preview',
            '.hud-crew-identity',
            '#berlin-map-canvas .map-marker.owned',
            '.map-chip.owned',
            'map-crew-badge',
            'map-detail-crew',
            'baseMap.render(model);',
        ):
            with self.subTest(token=token):
                self.assertIn(token, MODULE)
        self.assertNotIn('.map-marker:not(.owned)', MODULE)

    def test_map_presence_stays_read_only_and_uses_existing_render_boundary(self):
        self.assertIn('appendModule("avatar_map_presence.js", "avatar-map-presence")', UI_PREFS)
        for forbidden in ("fetch(", "/api/", "sendCommand", "localStorage", "sessionStorage"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, MODULE)
        self.assertNotIn("MutationObserver", MODULE)

    def test_map_badges_are_compact_accessible_and_reduced_motion_safe(self):
        for token in (
            ".map-marker.owned .map-crew-badge",
            ".map-detail-crew",
            ".map-detail-crew-preview",
            '@media (prefers-reduced-motion: reduce)',
        ):
            with self.subTest(token=token):
                self.assertIn(token, STYLES)
        self.assertIn('aria-hidden', MODULE)
        self.assertIn('Bestätigte Crew-Marke für diesen eigenen Ort', MODULE)


if __name__ == "__main__":
    unittest.main()
