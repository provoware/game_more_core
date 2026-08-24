from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
APP = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "crew_identity.css").read_text(encoding="utf-8")


class A4CrewIdentityControlDeckTests(unittest.TestCase):
    def test_editor_uses_projection_choices_and_sends_only_compact_identity_recipe(self):
        for token in (
            "crew.choices.modes",
            "crew.choices.styles",
            "crew.choices.symbols",
            "crew.choices.colors",
            "primary_color_id",
            "secondary_color_id",
            "accent_color_id",
            "changes.crew_identity = crewIdentity",
        ):
            self.assertIn(token, APP)
        for forbidden in ("FileReader", "readAsDataURL", "base64", "<canvas", "image_data"):
            self.assertNotIn(forbidden, APP)

    def test_preview_is_accessible_and_does_not_create_gameplay_authority(self):
        self.assertIn('preview.setAttribute("role", "img")', APP)
        self.assertIn('preview.setAttribute("aria-label"', APP)
        self.assertIn("Gameplaywerte und Character-ID ändern sich dadurch nicht", APP)
        self.assertNotIn("fetch(", STYLES)
        self.assertIn(".crew-identity-preview", STYLES)

    def test_avatar_geometry_is_stable_and_mode_specific(self):
        for token in (
            "aspect-ratio: 8 / 5",
            '.crew-identity-preview[data-mode="logo"]',
            "aspect-ratio: 1",
            "border-radius: 50%",
            "width: min(100%, 210px)",
        ):
            with self.subTest(token=token):
                self.assertIn(token, STYLES)
        self.assertNotIn("min-height: 132px", STYLES)
        self.assertNotIn("min-height: 112px", STYLES)

    def test_avatar_symbol_mark_and_controls_are_clipping_safe(self):
        for token in (
            ".crew-identity-symbol",
            "width: clamp(4.5rem, 42%, 6rem)",
            ".crew-identity-mark",
            "max-width: calc(100% - 1.1rem)",
            "text-overflow: ellipsis",
            ".crew-identity-controls select:focus-visible",
            "min-width: 0",
        ):
            with self.subTest(token=token):
                self.assertIn(token, STYLES)

    def test_avatar_presentation_remains_local_and_reduced_motion_safe(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", STYLES)
        for forbidden in ("url(http", "@import", "javascript:", "/api/", "fetch("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, STYLES)


if __name__ == "__main__":
    unittest.main()
