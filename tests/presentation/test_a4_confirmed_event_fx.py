from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
FX = (ROOT / "web" / "a4" / "confirmed_event_fx.js").read_text(encoding="utf-8")
MOTION = (ROOT / "web" / "a4" / "motion_depth.css").read_text(encoding="utf-8")


class A4ConfirmedEventFxTests(unittest.TestCase):
    def test_existing_ui_bootstrap_loads_fx_without_gaining_command_authority(self):
        self.assertIn('appendModule("confirmed_event_fx.js", "confirmed-event-fx")', PREFS)
        for forbidden in ("/api/", "fetch(", "XMLHttpRequest", "sendCommand", "command_id:"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, PREFS)

    def test_fx_observes_existing_command_receipt_without_second_api_path(self):
        for token in (
            'new Set(["street.walk", "recovery.run", "incident.resolve"])',
            "const baseRequest = request;",
            "const payload = await baseRequest(path, options);",
            'if (path === "/api/command") lastCommandReceipt = payload;',
            "const baseSendCommand = sendCommand;",
            "await baseSendCommand(command);",
            "window.setTimeout(() => render(command.type, before, receipt), 0);",
        ):
            with self.subTest(token=token):
                self.assertIn(token, FX)
        self.assertNotIn("fetch(", FX)
        self.assertNotIn("command_id:", FX)

    def test_replay_and_rejection_cannot_invent_confirmed_feedback(self):
        for token in (
            "if (!receipt || receipt.idempotent_replay === true) return;",
            "lastCommandReceipt = null;",
            "if (!SUPPORTED_COMMANDS.has(command?.type) || !receipt) return;",
        ):
            with self.subTest(token=token):
                self.assertIn(token, FX)

    def test_identical_new_street_round_still_uses_confirmed_receipt(self):
        self.assertIn('commandType === "street.walk" && receipt.metadata?.street_encounter', FX)
        self.assertIn("receipt.metadata.street_encounter.polarity", FX)
        self.assertNotIn("streetText", FX)

    def test_crisis_feedback_uses_hud_surface_that_survives_phase_transition(self):
        self.assertIn('commandType === "incident.resolve"', FX)
        self.assertIn('pulse(document.getElementById("hud-phase"), "neutral")', FX)
        self.assertNotIn('pulse(document.getElementById("incident-panel"), "neutral")', FX)

    def test_resource_feedback_uses_confirmed_before_after_values(self):
        for token in (
            '["energy", "hud-energy"]',
            '["stress", "hud-stress"]',
            '["reputation", "hud-reputation"]',
            '["budget", "hud-budget"]',
            'if (key === "stress") return after < before ? "positive" : "negative";',
        ):
            with self.subTest(token=token):
                self.assertIn(token, FX)

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
