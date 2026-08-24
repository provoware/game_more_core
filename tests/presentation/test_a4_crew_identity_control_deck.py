from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
APP = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "crew_identity.css").read_text(encoding="utf-8")
UI_PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
HUD_SYNC = (ROOT / "web" / "a4" / "crew_identity_hud_sync.js").read_text(encoding="utf-8")


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

    def test_avatar_preview_stays_visible_during_profile_editing_without_mobile_overlap(self):
        for token in (
            "position: sticky",
            "top: 5.5rem",
            'content: "DEINE CREW // VORSCHAU"',
            "align-self: start",
            "@media (max-width: 720px)",
            "position: static",
            "width: 100%",
        ):
            with self.subTest(token=token):
                self.assertIn(token, STYLES)

    def test_confirmed_identity_is_copied_to_hud_only_at_renderer_boundaries(self):
        for token in (
            "function copyConfirmedCrewPreview()",
            'document.getElementById("crew-identity-preview")',
            'editorObserver.observe(editor, { childList: true })',
            'panelObserver.observe(profilePanel, { childList: true })',
            'host.setAttribute("aria-label", `Bestätigt:',
            "observeConfirmedCrewIdentity();",
        ):
            with self.subTest(token=token):
                self.assertIn(token, UI_PREFS)
        self.assertNotIn("/api/state", UI_PREFS)
        self.assertNotIn("fetch(", UI_PREFS)
        self.assertNotIn("input", UI_PREFS[UI_PREFS.index("function observeConfirmedCrewIdentity"):])

    def test_confirmed_hud_refresh_precedes_editor_focus_guard(self):
        self.assertIn('appendModule("crew_identity_hud_sync.js", "crew-identity-hud-sync")', UI_PREFS)
        self.assertIn("const baseRenderCrewIdentity = renderCrewIdentity;", HUD_SYNC)
        wrapper = HUD_SYNC[HUD_SYNC.index("renderCrewIdentity = function renderCrewIdentityWithConfirmedHud"):]
        self.assertLess(wrapper.index("renderConfirmedHudCrew(crew);"), wrapper.index("baseRenderCrewIdentity(crew)"))
        for token in (
            "crew?.identity",
            "crew?.render",
            "render.symbol_glyph",
            "render.accent",
            "identity.mark",
        ):
            with self.subTest(token=token):
                self.assertIn(token, HUD_SYNC)
        for forbidden in ("fetch(", "/api/", "sendCommand", "localStorage", "readCrewIdentity("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, HUD_SYNC)

    def test_confirmed_hud_avatar_is_compact_and_does_not_break_responsive_hud(self):
        for token in (
            ".hud-crew-identity",
            "width: 2.75rem",
            ".hud-crew-preview[data-mode=\"logo\"]",
            ".hud-crew-mark",
            "@media (max-width: 1100px)",
            "display: none",
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