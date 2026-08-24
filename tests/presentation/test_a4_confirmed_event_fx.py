from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
MOTION = (ROOT / "web" / "a4" / "motion_depth.css").read_text(encoding="utf-8")


class A4ConfirmedEventFxTests(unittest.TestCase):
    def test_fx_runs_only_after_existing_confirmed_command_path(self):
        for token in (
            'new Set(["street.walk", "recovery.run", "incident.resolve"])',
            "const baseSendCommand = sendCommand;",
            "await baseSendCommand(command);",
            "window.setTimeout(() => renderConfirmedEventFx(command.type, before), 0);",
        ):
            with self.subTest(token=token):
                self.assertIn(token, PREFS)
        self.assertNotIn('fetch("/api/command"', PREFS)
        self.assertNotIn("command_id:", PREFS)

    def test_replay_or_rejection_cannot_invent_a_visible_effect_without_change(self):
        for token in (
            "before.streetText !== after.streetText",
            "before.recoveryText !== after.recoveryText",
            "before.incidentText !== after.incidentText",
            "before === after",
        ):
            with self.subTest(token=token):
                self.assertIn(token, PREFS)

    def test_resource_feedback_uses_confirmed_before_after_values(self):
        for token in (
            '["energy", "hud-energy"]',
            '["stress", "hud-stress"]',
            '["reputation", "hud-reputation"]',
            '["budget", "hud-budget"]',
            'if (key === "stress") return after < before ? "positive" : "negative";',
        ):
            with self.subTest(token=token):
                self.assertIn(token, PREFS)

    def test_motion_is_nonblocking_and_reduced_motion_has_static_fallback(self):
        for token in (
            ".confirmed-fx",
            "@keyframes confirmed-fx-pulse",
            ".confirmed-fx-positive",
            ".confirmed-fx-negative",
            ".confirmed-fx-neutral",
            "@media (prefers-reduced-motion: reduce)",
            "animation: none !important",
            "outline: 2px solid var(--confirmed-fx-color)",
        ):
            with self.subTest(token=token):
                self.assertIn(token, MOTION)
        for forbidden in ("pointer-events: none", "position: fixed", "z-index: 999", "url(http", "@import"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, MOTION)


if __name__ == "__main__":
    unittest.main()
