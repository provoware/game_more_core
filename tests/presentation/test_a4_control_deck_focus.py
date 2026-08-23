from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
FOCUS = (ROOT / "web" / "a4" / "control_deck_focus.js").read_text(encoding="utf-8")
UI_PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")


class ControlDeckFocusContractTests(unittest.TestCase):
    def test_focus_module_is_local_presentation_only(self):
        self.assertIn('const FOCUS_CLASS = "deck-focus-active"', FOCUS)
        self.assertIn('const PANEL_CLASS = "is-deck-focused"', FOCUS)
        self.assertIn('"GESAMTANSICHT"', FOCUS)
        self.assertIn('"FOKUS"', FOCUS)
        self.assertNotIn("fetch(", FOCUS)
        self.assertNotIn("/api/command", FOCUS)
        self.assertNotIn("localStorage", FOCUS)
        self.assertNotIn("sessionStorage", FOCUS)

    def test_focus_module_highlights_only_enabled_runtime_event_action(self):
        self.assertIn('#event-actions button:not(:disabled)', FOCUS)
        self.assertIn('NÄCHSTER SCHRITT:', FOCUS)
        self.assertIn('Runtime-Gate abwarten', FOCUS)
        self.assertNotIn("ACTION_LABELS", FOCUS)

    def test_reduced_motion_keeps_signal_without_required_animation(self):
        self.assertIn("prefers-reduced-motion: no-preference", FOCUS)
        self.assertIn("next-action-signal", FOCUS)

    def test_existing_ui_prefs_loads_focus_module_without_new_dashboard(self):
        self.assertIn('script.src = "control_deck_focus.js"', UI_PREFS)
        self.assertIn('data-control-deck-focus', UI_PREFS.replace("dataset.controlDeckFocus", "data-control-deck-focus"))
        self.assertNotIn("dashboard", FOCUS.lower())

    def test_codex_review_is_explicitly_removed_from_development_process(self):
        self.assertIn("Codex-Code-Review ist kein Bestandteil", AGENTS)
        self.assertIn("wird weder angefordert noch als Evidenz geführt", AGENTS)
        self.assertIn("keinen Codex-Code-Review", AGENTS)


if __name__ == "__main__":
    unittest.main()
