from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
A4 = ROOT / "web" / "a4"
CSS = (A4 / "visual_hierarchy_3.css").read_text(encoding="utf-8")
PREFS = (A4 / "ui_prefs.js").read_text(encoding="utf-8")
INDEX = (A4 / "index.html").read_text(encoding="utf-8")


class A4VisualHierarchy3Tests(unittest.TestCase):
    def test_existing_loader_adds_one_visual_stylesheet_without_second_dashboard(self):
        self.assertIn('appendStylesheet("visual_hierarchy_3.css", "visual-hierarchy-3")', PREFS)
        self.assertIn("ensureVisualHierarchy3Stylesheet();", PREFS)
        self.assertEqual(PREFS.count('appendStylesheet("visual_hierarchy_3.css"'), 1)
        self.assertNotIn("dashboard", CSS.lower())

    def test_only_existing_event_surface_is_promoted_to_full_width_action_hierarchy(self):
        self.assertIn('id="event-panel" class="panel hidden"', INDEX)
        self.assertIn('id="event-actions" class="action-grid"', INDEX)
        self.assertIn('id="blockers" class="notice"', INDEX)
        self.assertIn("#event-panel {", CSS)
        self.assertIn("grid-column: 1 / -1;", CSS)
        self.assertIn("#event-panel > .summary-grid", CSS)
        self.assertIn("#event-actions {", CSS)
        self.assertIn("#event-panel > #blockers", CSS)

    def test_visual_layer_is_presentation_only_and_does_not_create_gameplay_authority(self):
        for token in ("fetch(", "/api/command", "sendCommand", "localStorage", "sessionStorage"):
            with self.subTest(token=token):
                self.assertNotIn(token, CSS)
        self.assertNotIn("price", CSS.lower())
        self.assertNotIn("energy", CSS.lower())
        self.assertNotIn("budget_cents", CSS)

    def test_small_screen_high_contrast_and_reduced_motion_remain_explicit(self):
        self.assertIn("body.ui-high-contrast #event-panel", CSS)
        self.assertIn("@media (max-width: 860px)", CSS)
        self.assertIn("@media (max-width: 560px)", CSS)
        self.assertIn("@media (prefers-reduced-motion: reduce)", CSS)
        self.assertIn("transition: none !important; animation: none !important;", CSS)


if __name__ == "__main__":
    unittest.main()
