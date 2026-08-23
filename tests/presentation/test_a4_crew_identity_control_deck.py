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


if __name__ == "__main__":
    unittest.main()
