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
        self.assertNotIn("codex_review_execution", validation)

    def test_validated_pool_items_and_active_preview_owner_are_consistent(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        for pool_id in (
            "POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002",
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002", "POOL-ECON-003",
            "POOL-COMPANION-001", "POOL-COMPANION-002", "POOL-FINANCE-001",
            "POOL-FINANCE-003", "POOL-FINANCE-004", "POOL-UX-004", "POOL-UX-005",
            "POOL-MAP-002", "POOL-STORY-001", "POOL-ECON-004",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)
        self.assertIn("`PULLED`", _pool_row(pool, "POOL-ECON-005"))

    def test_validated_anti_grind_and_active_job_preview_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]
        process = status["subsystems"]["development_process"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-ECON-ANTI-GRIND")
        self.assertEqual(status["active_iteration"], "0.8.8-ECON-JOB-PREVIEW")
        self.assertEqual(status["next_iteration"], "0.8.8-UX-EXPORT-PROOF")
        self.assertEqual(status["current_focus"], "scene_job_confirmed_effective_payout_preview")
        self.assertTrue(economy["scene_job_anti_grind_validated"])
        self.assertEqual(economy["scene_job_exhaustion_mode"], "pre_job_energy_proportional_payout")
        self.assertTrue(economy["scene_job_full_payout_requires_energy_cost"])
        self.assertEqual(economy["scene_job_zero_energy_payout_cents"], 0)
        self.assertFalse(economy["scene_job_exhaustion_requires_system_time"])
        self.assertFalse(economy["scene_job_second_exhaustion_resource"])
        self.assertTrue(economy["assistant_uses_same_scene_job_exhaustion_rule"])
        self.assertTrue(economy["scene_job_effective_payout_preview_in_validation"])
        self.assertEqual(economy["scene_job_effective_payout_preview_source"], "confirmed_character_energy")
        self.assertTrue(economy["scene_job_effective_payout_preview_same_canonical_calculation"])
        self.assertFalse(economy["browser_calculates_scene_job_payout"])
        self.assertTrue(presentation["scene_job_effective_payout_preview_visible"])
        self.assertEqual(presentation["scene_job_effective_payout_preview_location"], "existing_jobs_panel")
        self.assertFalse(presentation["scene_job_effective_payout_preview_write_back"])
        self.assertFalse(presentation["browser_gameplay_authority"])
        self.assertTrue(process["focused_read_policy"])
        self.assertTrue(process["planned_read_list_required"])
        self.assertTrue(process["repository_file_classes_enabled"])
        self.assertTrue(process["basis_files_on_contract_or_status_need"])
        self.assertTrue(process["evidence_logs_on_failure_or_final_proof_only"])
        self.assertTrue(process["green_logs_compact_only"])
        self.assertFalse(process["codex_code_review_enabled"])
        self.assertFalse(process["codex_code_review_is_gate"])

    def test_requested_0_8_8_foundations_have_single_pool_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        expected = {
            "POOL-PROFILE-002": "`DONE`",
            "POOL-ECON-003": "`DONE`",
            "POOL-COMPANION-001": "`DONE`",
            "POOL-COMPANION-002": "`DONE`",
            "POOL-FINANCE-001": "`DONE`",
            "POOL-FINANCE-003": "`DONE`",
            "POOL-FINANCE-004": "`DONE`",
            "POOL-UX-004": "`DONE`",
            "POOL-UX-005": "`DONE`",
            "POOL-MAP-002": "`DONE`",
            "POOL-STORY-001": "`DONE`",
            "POOL-ECON-004": "`DONE`",
            "POOL-ECON-005": "`PULLED`",
        }
        for pool_id, state in expected.items():
            self.assertIn(state, _pool_row(pool, pool_id), pool_id)

    def test_agents_requires_focused_read_file_classes_and_excludes_codex_review(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Focused-Read-Strategie – verbindlich", agents)
        self.assertIn("Planned-Read-Liste", agents)
        self.assertIn("Breitenscans", agents)
        self.assertIn("der konkrete fehlerhafte Job", agents)
        self.assertIn("Kein erneuter Breitenscan ohne neuen Befund", agents)
        self.assertIn("## Repository-Dateiklassen – verbindlich", agents)
        self.assertIn("**Basisdateien**", agents)
        self.assertIn("**Arbeitsdateien**", agents)
        self.assertIn("**Evidenzdateien und Logs**", agents)
        self.assertIn("Ein grünes Gate wird nicht durch erneutes Übertragen seines vollständigen Logs", agents)
        self.assertIn("Codex-Code-Review ist kein Bestandteil", agents)
        self.assertIn("wird weder angefordert noch als Evidenz geführt", agents)


if __name__ == "__main__":
    unittest.main()
