from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
STYLES = (ROOT / "web" / "a4" / "styles.css").read_text(encoding="utf-8")


class A4MotionDepthTests(unittest.TestCase):
    def test_interactive_surfaces_have_restrained_motion_feedback(self):
        for token in (
            "button:hover:not(:disabled) { transform: translateY(-2px)",
            ".panel:hover { border-color: #465361; transform: translateY(-2px)",
            ".equipment-row:hover",
            ".incident-choice:hover",
            ".map-marker:hover, .map-marker:focus-visible",
            ".street-approach-card.is-selected::after",
        ):
            with self.subTest(token=token):
                self.assertIn(token, STYLES)

    def test_motion_is_presentation_only_and_reduced_motion_remains_authoritative(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", STYLES)
        reduced = STYLES[STYLES.index("@media (prefers-reduced-motion: reduce)"):]
        self.assertIn("transition: none !important", reduced)
        self.assertIn("animation: none !important", reduced)
        for forbidden in ("url(http", "@import", "javascript:"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, STYLES)


if __name__ == "__main__":
    unittest.main()
