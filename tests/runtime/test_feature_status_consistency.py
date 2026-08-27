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
    def test_last_validated_feature_is_consistent_across_status_todo_pool_and_history(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")

        iteration = status["last_validated_feature_iteration"]
        validation = status["remote_validation"]
        latest = status["validated_feature_history"][-1]
        merge_sha = validation["merged_commit"]
        pr_number = validation["pull_request"]

        self.assertEqual(latest["iteration"], iteration)
        self.assertEqual(latest["pull_request"], pr_number)
        self.assertEqual(latest["merged_commit"], merge_sha)
        self.assertIn(f"Zuletzt remote validierte Feature-Stufe:** `{iteration}`", todo)
        self.assertIn(f"PR #{pr_number}", todo)
        self.assertIn(merge_sha, todo)
        self.assertIn(f"**{iteration}:** PR #{pr_number}", pool)
        self.assertIn(merge_sha, pool)
        self.assertEqual(validation["safe_merge_result"], "PASS")
        self.assertTrue(validation["main_provenance_confirmed"])
        self.assertNotIn("codex_review_execution", validation)

    def test_validated_and_next_pool_items_have_single_current_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        done = (
            "POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002",
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002", "POOL-ECON-003",
            "POOL-COMPANION-001", "POOL-COMPANION-002", "POOL-FINANCE-001",
            "POOL-FINANCE-003", "POOL-FINANCE-004", "POOL-UX-004", "POOL-UX-005",
            "POOL-MAP-002", "POOL-STORY-001", "POOL-ECON-004", "POOL-ECON-005",
            "POOL-UX-006", "POOL-ECON-006", "POOL-UX-003", "POOL-ECON-007",
            "POOL-STREET-002", "POOL-ECON-008", "POOL-QA-007", "POOL-QA-008",
            "POOL-QA-002", "POOL-QA-009", "POOL-STREET-005", "POOL-UX-007",
            "POOL-QA-010", "POOL-QA-006", "POOL-UX-008", "POOL-QA-011", "POOL-QA-013",
            "POOL-QA-014", "POOL-QA-015", "POOL-UX-009", "POOL-QA-016", "POOL-MAP-003",
            "POOL-QA-017", "POOL-WORLD-003",
        )
        for pool_id in done:
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)
        self.assertIn("`PULLED`", _pool_row(pool, "POOL-STREET-003"))

    def test_current_status_describes_district_chain_e2e_and_active_street_chain_audit(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        living_world = status["subsystems"]["living_world"]
        presentation = status["subsystems"]["presentation"]
        process = status["subsystems"]["development_process"]
        sync = status["status_sync"]
        validation = status["remote_validation"]

        self.assertIn(status["active_iteration"], todo)
        self.assertIn(status["active_iteration"], readme)
        self.assertIn(status["last_validated_feature_iteration"], readme)
        self.assertEqual(status["current_focus"], "street_mini_chain_contract_audit")
        self.assertIsNone(status["next_iteration"])

        self.assertEqual(validation["pull_request"], 206)
        self.assertEqual(validation["validated_head"], "14a1c2914c6b366bda1ca71198340f00f58cef3a")
        self.assertEqual(validation["merged_commit"], "75aea005dcbf95abf80159b0ed96b0149bec0973")

        self.assertTrue(living_world["district_event_chain_contract_audit_validated"])
        self.assertEqual(living_world["district_event_chain_child_event_type"], "world.district_followup_resolved")
        self.assertEqual(living_world["district_event_chain_parent_binding"], "causation_id=parent_event_id")
        self.assertTrue(living_world["district_event_chain_district_must_match_parent"])
        self.assertTrue(living_world["district_event_chain_exactly_once_retry_validated"])
        self.assertTrue(living_world["district_event_chain_readonly_projection_validated"])
        self.assertFalse(living_world["district_event_chain_readonly_projection_browser_authority"])
        self.assertTrue(living_world["district_micro_story_002_audit_validated"])
        self.assertTrue(living_world["district_micro_story_002_implemented"])
        self.assertEqual(living_world["district_micro_story_002_parent_catalog_event_id"], "district.temporary_space_opens")
        self.assertEqual(living_world["district_micro_story_002_followup_id"], "temporary_space_afterimage")
        self.assertEqual(living_world["district_micro_story_002_title"], "Die Tür ist zu – die Adresse lebt weiter.")
        self.assertTrue(living_world["district_micro_story_002_delayed_to_later_cycle"])
        self.assertFalse(living_world["district_micro_story_002_cross_district_allowed"])
        self.assertFalse(living_world["district_micro_story_002_balance_effects"])
        self.assertEqual(living_world["district_micro_story_catalog_count"], 2)
        self.assertEqual(living_world["district_micro_story_max_followups_per_cycle"], 1)
        self.assertTrue(living_world["district_chain_runtime_browser_e2e_validated"])
        self.assertEqual(living_world["district_chain_runtime_browser_e2e_browser"], "chromium")
        self.assertTrue(living_world["district_chain_runtime_browser_e2e_retry_validated"])
        self.assertTrue(living_world["district_chain_runtime_browser_e2e_cross_district_fail_closed"])
        self.assertEqual(
            living_world["district_event_chain_next_contract"],
            "0.8.8-STORY-STREET-MINI-CHAIN-CONTRACT-AUDIT",
        )

        self.assertIn("world.district_followup_resolved", presentation["event_timeline_sources"])
        self.assertTrue(presentation["district_chain_cause_projection_validated"])
        self.assertEqual(presentation["district_chain_cause_projection_label"], "Folge von:")
        self.assertFalse(presentation["district_chain_cause_projection_invents_missing_parent"])
        self.assertFalse(presentation["district_chain_cause_projection_browser_write_authority"])
        self.assertFalse(presentation["browser_gameplay_authority"])

        self.assertEqual(sync["anchor_pull_request"], validation["pull_request"])
        self.assertEqual(sync["anchor_merge_commit"], validation["merged_commit"])
        self.assertFalse(sync["direct_main_write"])
        self.assertTrue(process["status_sync_automatic_drift_check"])
        self.assertFalse(process["status_sync_direct_main_write"])
        self.assertTrue(process["focused_read_policy"])
        self.assertTrue(process["planned_read_list_required"])
        self.assertTrue(process["repository_file_classes_enabled"])
        self.assertTrue(process["evidence_logs_on_failure_or_final_proof_only"])
        self.assertFalse(process["codex_code_review_enabled"])
        self.assertFalse(process["codex_code_review_is_gate"])

    def test_requested_0_8_8_foundations_have_single_pool_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        expected = {
            "POOL-PROFILE-002": "`DONE`", "POOL-ECON-003": "`DONE`",
            "POOL-COMPANION-001": "`DONE`", "POOL-COMPANION-002": "`DONE`",
            "POOL-FINANCE-001": "`DONE`", "POOL-FINANCE-003": "`DONE`",
            "POOL-FINANCE-004": "`DONE`", "POOL-UX-004": "`DONE`",
            "POOL-UX-005": "`DONE`", "POOL-MAP-002": "`DONE`",
            "POOL-STORY-001": "`DONE`", "POOL-ECON-004": "`DONE`",
            "POOL-ECON-005": "`DONE`", "POOL-UX-006": "`DONE`",
            "POOL-ECON-006": "`DONE`", "POOL-UX-003": "`DONE`",
            "POOL-ECON-007": "`DONE`", "POOL-STREET-002": "`DONE`",
            "POOL-ECON-008": "`DONE`", "POOL-QA-007": "`DONE`",
            "POOL-QA-008": "`DONE`", "POOL-QA-002": "`DONE`",
            "POOL-QA-009": "`DONE`", "POOL-STREET-005": "`DONE`",
            "POOL-UX-007": "`DONE`", "POOL-QA-010": "`DONE`",
            "POOL-QA-006": "`DONE`", "POOL-UX-008": "`DONE`",
            "POOL-QA-011": "`DONE`", "POOL-QA-013": "`DONE`",
            "POOL-QA-014": "`DONE`", "POOL-QA-015": "`DONE`",
            "POOL-UX-009": "`DONE`", "POOL-QA-016": "`DONE`",
            "POOL-MAP-003": "`DONE`", "POOL-QA-017": "`DONE`",
            "POOL-WORLD-003": "`DONE`", "POOL-STREET-003": "`PULLED`",
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
