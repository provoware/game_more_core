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
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)

    def test_validated_crew_identity_and_active_scene_jobs_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        living_world = status["subsystems"]["living_world"]
        character_forge = status["subsystems"]["character_forge"]
        event_runtime = status["subsystems"]["event_runtime"]
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-A")
        self.assertEqual(status["active_iteration"], "0.8.8-B")
        self.assertEqual(status["next_iteration"], "0.8.8-B")
        self.assertEqual(status["current_focus"], "scene_jobs_wallet_and_a4_visibility")
        self.assertTrue(character_forge["crew_identity_logo_flag"])
        self.assertTrue(presentation["crew_identity_editor_visible"])
        self.assertFalse(event_runtime["always_available_job_actions"])
        self.assertFalse(economy["personal_finance_state_validated"])
        self.assertFalse(presentation["scene_jobs_panel_validated"])
        self.assertTrue(living_world["district_event_timeline_visible"])
        self.assertTrue(living_world["district_event_cadence_enabled"])
        self.assertEqual(living_world["district_event_cooldown_hours"], 24)
        self.assertEqual(living_world["district_event_cadence_authority"], "confirmed_event.time_window.start_local")
        self.assertFalse(living_world["district_event_system_time_fallback"])

    def test_requested_0_8_8_foundations_have_single_pool_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        expected = {
            "POOL-PROFILE-002": "`DONE`",
            "POOL-ECON-003": "`PULLED`",
            "POOL-COMPANION-001": "`DEPENDENCY`",
            "POOL-FINANCE-001": "`READY`",
            "POOL-UX-004": "`READY`",
            "POOL-MAP-002": "`READY`",
        }
        for pool_id, state in expected.items():
            self.assertIn(state, _pool_row(pool, pool_id), pool_id)


if __name__ == "__main__":
    unittest.main()
