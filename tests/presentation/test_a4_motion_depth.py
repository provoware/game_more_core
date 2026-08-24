from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MOTION = (ROOT / "web" / "a4" / "motion_depth.css").read_text(encoding="utf-8")
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
BASE_STYLES = (ROOT / "web" / "a4" / "styles.css").read_text(encoding="utf-8")


class A4MotionDepthTests(unittest.TestCase):
    def test_interactive_surfaces_have_restrained_motion_feedback(self):
        for token in (
            "button:not(.map-marker):hover:not(:disabled)",
            ".panel:hover",
            ".equipment-row:hover",
            ".incident-choice:hover",
            ".map-marker:hover, .map-marker:focus-visible",
            ".street-approach-card.is-selected::after",
        ):
            with self.subTest(token=token):
                self.assertIn(token, MOTION)

    def test_map_motion_preserves_centering_and_existing_heat_indicator(self):
        self.assertIn("translate(-50%, -50%) scale(1.08)", MOTION)
        self.assertIn(".map-district::after", BASE_STYLES)
        self.assertIn("var(--district-heat, 0)", BASE_STYLES)

    def test_motion_is_loaded_locally_and_reduced_motion_remains_authoritative(self):
        self.assertIn('assetUrl("motion_depth.css")', PREFS)
        self.assertIn("@media (prefers-reduced-motion: reduce)", MOTION)
        reduced = MOTION[MOTION.index("@media (prefers-reduced-motion: reduce)"):]
        self.assertIn("transition: none !important", reduced)
        self.assertIn("animation: none !important", reduced)
        for forbidden in ("url(http", "@import", "javascript:", "/api/", "fetch("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, MOTION)


if __name__ == "__main__":
    unittest.main()
