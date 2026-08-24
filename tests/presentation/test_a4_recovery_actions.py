from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
UI = (ROOT / "web" / "a4" / "recovery_actions_ui.js").read_text(encoding="utf-8")
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
PROJECTION = (ROOT / "src" / "bunkerfrequenz" / "presentation" / "scene_jobs_projection.py").read_text(encoding="utf-8")
SESSION = (ROOT / "src" / "bunkerfrequenz" / "application" / "assistant_game_client_session.py").read_text(encoding="utf-8")
SERVICE = (ROOT / "src" / "bunkerfrequenz" / "application" / "recovery_action_service.py").read_text(encoding="utf-8")


class A4RecoveryActionsTests(unittest.TestCase):
    def test_projection_uses_canonical_recovery_contract_and_confirmed_character_state(self):
        self.assertIn("RECOVERY_ACTIONS", PROJECTION)
        self.assertIn("recovery_action_availability", PROJECTION)
        self.assertIn('"recovery_actions"', PROJECTION)
        self.assertIn('"can_run"', PROJECTION)
        self.assertIn('"blocker"', PROJECTION)

    def test_browser_sends_only_recovery_identity_not_resource_values(self):
        self.assertIn('type: "recovery.run"', UI)
        self.assertIn("recovery_id: action.recovery_id", UI)
        for forbidden in ("energy_delta:", "stress_delta:", "max_energy_before:", "max_stress_before:"):
            self.assertNotIn(forbidden, UI)
        self.assertNotIn("/api/command", UI)
        self.assertNotIn("fetch(", UI)

    def test_runtime_owns_availability_and_exact_trade(self):
        self.assertIn('"energy_delta": 20', SERVICE)
        self.assertIn('"stress_delta": 12', SERVICE)
        self.assertIn('"max_energy_before": 80', SERVICE)
        self.assertIn('"max_stress_before": 88', SERVICE)
        self.assertIn("recovery_action_availability(action, character)", SERVICE)
        self.assertNotIn("datetime", SERVICE)
        self.assertNotIn("random", SERVICE)
        self.assertNotIn("skill_xp", SERVICE)
        self.assertNotIn("trait_evidence", SERVICE)

    def test_a4_session_accepts_only_command_id_and_recovery_id(self):
        self.assertIn('_RECOVERY_FIELDS = frozenset({"type", "command_id", "recovery_id"})', SESSION)
        self.assertIn('if command_type == "recovery.run"', SESSION)
        self.assertIn("self.recovery_actions.run(recovery_id.strip()", SESSION)
        self.assertNotIn('"energy_delta"})', SESSION)

    def test_recovery_module_is_loaded_by_existing_ui_loader(self):
        self.assertIn('appendModule("recovery_actions_ui.js", "recovery-actions")', PREFS)
        self.assertIn('url.searchParams.set("v", ASSET_REVISION)', PREFS)
        self.assertIn("ensureRecoveryActionsModule();", PREFS)

    def test_feedback_uses_confirmed_before_after_projections_and_next_runtime_availability(self):
        self.assertIn('id = "jobs-recovery-feedback"', UI)
        self.assertIn('aria-live", "polite"', UI)
        self.assertIn("const beforeCharacter = state.projection?.character", UI)
        self.assertIn("const afterCharacter = state.projection?.character", UI)
        self.assertIn("await sendCommand", UI)
        self.assertIn("state.projection?.scene_jobs?.recovery_actions", UI)
        self.assertIn("action?.can_run", UI)
        self.assertIn('action?.blocker === "energy_above_recovery_threshold"', UI)
        self.assertIn('action?.blocker === "stress_above_recovery_threshold"', UI)
        self.assertIn("Energie ${beforeCharacter.energy} → ${afterCharacter.energy}", UI)
        self.assertIn("Stress ${beforeCharacter.stress} → ${afterCharacter.stress}", UI)
        self.assertNotIn("beforeCharacter.energy +", UI)
        self.assertNotIn("beforeCharacter.stress +", UI)
        self.assertNotIn("max_energy_before", UI)
        self.assertNotIn("max_stress_before", UI)


if __name__ == "__main__":
    unittest.main()
