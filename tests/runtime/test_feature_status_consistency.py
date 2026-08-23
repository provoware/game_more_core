import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class FeatureStatusConsistencyTests(unittest.TestCase):
    def test_last_validated_feature_is_consistent_across_status_todo_and_pool(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")

        iteration = status["last_validated_feature_iteration"]
        validation = status["remote_validation"]
        merge_sha = validation["merged_commit"]
        pr_number = validation["pull_request"]

        self.assertIn(f"Zuletzt remote validierte Feature-Stufe:** `{iteration}", todo)
        self.assertIn(f"PR #{pr_number}", todo)
        self.assertIn(merge_sha, todo)
        self.assertIn(f"**{iteration}:** PR #{pr_number}", pool)
        self.assertIn(merge_sha, pool)
        self.assertEqual(validation["safe_merge_result"], "PASS")
        self.assertTrue(validation["main_provenance_confirmed"])

    def test_validated_control_deck_pool_items_are_done(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        for pool_id in ("POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002", "POOL-UX-002", "POOL-WORLD-004"):
            matching = [line for line in pool.splitlines() if f"`{pool_id}`" in line]
            self.assertEqual(len(matching), 1, pool_id)
            self.assertIn("`DONE`", matching[0], pool_id)

    def test_c5_status_matches_visible_timeline_and_confirmed_cadence(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        living_world = status["subsystems"]["living_world"]
        presentation = status["subsystems"]["presentation"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.7-C5")
        self.assertEqual(status["active_iteration"], "0.8.8-A")
        self.assertEqual(status["next_iteration"], "0.8.8-A")
        self.assertEqual(status["current_focus"], "crew_identity_contract_and_sync_ready_profile")
        self.assertTrue(living_world["district_event_runtime_implemented"])
        self.assertTrue(living_world["district_event_application_integration"])
        self.assertEqual(living_world["district_event_authorized_trigger"], "settlement.complete")
        self.assertFalse(living_world["district_event_client_authority"])
        self.assertTrue(living_world["district_event_timeline_visible"])
        self.assertTrue(living_world["district_event_cadence_enabled"])
        self.assertEqual(living_world["district_event_cooldown_hours"], 24)
        self.assertEqual(living_world["district_event_cadence_authority"], "confirmed_event.time_window.start_local")
        self.assertFalse(living_world["district_event_system_time_fallback"])
        self.assertTrue(presentation["event_timeline_projection_ready"])
        self.assertTrue(presentation["event_timeline_visible"])

    def test_requested_0_8_8_foundations_have_single_pool_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        expected = {
            "POOL-PROFILE-002": "`PULLED`",
            "POOL-ECON-003": "`READY`",
            "POOL-COMPANION-001": "`DEPENDENCY`",
            "POOL-FINANCE-001": "`READY`",
            "POOL-UX-004": "`READY`",
            "POOL-MAP-002": "`READY`",
        }
        for pool_id, state in expected.items():
            matching = [line for line in pool.splitlines() if f"`{pool_id}`" in line]
            self.assertEqual(len(matching), 1, pool_id)
            self.assertIn(state, matching[0], pool_id)


if __name__ == "__main__":
    unittest.main()
