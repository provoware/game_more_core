import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


def _pool_row(pool: str, pool_id: str) -> str:
    matching = [line for line in pool.splitlines() if line.startswith(f"| `{pool_id}` |")]
    if len(matching) != 1:
        raise AssertionError(f"{pool_id}: expected exactly one canonical pool table row, got {len(matching)}")
    return matching[0]


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
        for pool_id in (
            "POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002",
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002", "POOL-ECON-003",
            "POOL-COMPANION-001",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)

    def test_validated_assistant_c4_and_active_c5a_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        event_runtime = status["subsystems"]["event_runtime"]
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]
        assistant = status["subsystems"]["assistant"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-C4")
        self.assertEqual(status["active_iteration"], "0.8.8-C5A")
        self.assertEqual(status["next_iteration"], "0.8.8-C5B")
        self.assertEqual(status["current_focus"], "assistant_confirmed_afterglow_read_only_projection")
        self.assertTrue(event_runtime["always_available_job_actions"])
        self.assertTrue(economy["personal_finance_state_validated"])
        self.assertTrue(presentation["scene_jobs_panel_validated"])
        self.assertTrue(presentation["assistant_controls_in_scene_jobs_panel"])
        self.assertFalse(presentation["assistant_second_dashboard"])
        self.assertTrue(presentation["assistant_afterglow_projection_implemented"])
        self.assertFalse(presentation["assistant_afterglow_visible"])
        self.assertEqual(assistant["status"], "c4_remote_validated_c5a_afterglow_projection_in_validation")
        self.assertTrue(assistant["contract_policy_defined"])
        self.assertEqual(assistant["task_source"], "scene_jobs")
        self.assertEqual(assistant["max_active_tasks"], 1)
        self.assertTrue(assistant["confirmed_round_required"])
        self.assertFalse(assistant["system_time_authority"])
        self.assertFalse(assistant["client_round_authority"])
        self.assertTrue(assistant["control_state_implemented"])
        self.assertTrue(assistant["control_state_recoverable"])
        self.assertTrue(assistant["automatic_round_execution"])
        self.assertTrue(assistant["round_processed_marker"])
        self.assertTrue(assistant["round_retry_idempotent"])
        self.assertTrue(assistant["off_round_consumed_without_retroactive_execution"])
        self.assertTrue(assistant["single_active_task_runtime"])
        self.assertTrue(assistant["jobs_ui_integration"])
        self.assertEqual(assistant["browser_control_fields"], ["job_id"])
        self.assertFalse(assistant["browser_can_supply_round"])
        self.assertFalse(assistant["browser_can_supply_payout_or_effects"])
        self.assertTrue(assistant["friendship_afterglow_projection_implemented"])
        self.assertTrue(assistant["friendship_afterglow_requires_round_and_job_pair"])
        self.assertFalse(assistant["friendship_afterglow_progression_engine"])
        self.assertFalse(assistant["friendship_afterglow_visible"])

    def test_requested_0_8_8_foundations_have_single_pool_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        expected = {
            "POOL-PROFILE-002": "`DONE`",
            "POOL-ECON-003": "`DONE`",
            "POOL-COMPANION-001": "`DONE`",
            "POOL-COMPANION-002": "`PULLED`",
            "POOL-FINANCE-001": "`READY`",
            "POOL-UX-004": "`READY`",
            "POOL-MAP-002": "`READY`",
        }
        for pool_id, state in expected.items():
            self.assertIn(state, _pool_row(pool, pool_id), pool_id)


if __name__ == "__main__":
    unittest.main()
