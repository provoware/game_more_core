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

    def test_validated_control_deck_pool_items_are_done(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        for pool_id in (
            "POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002",
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002", "POOL-ECON-003",
            "POOL-COMPANION-001", "POOL-COMPANION-002", "POOL-FINANCE-001",
            "POOL-UX-004", "POOL-UX-005",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)

    def test_validated_e_and_active_fin_statements_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]
        process = status["subsystems"]["development_process"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-E")
        self.assertEqual(status["active_iteration"], "0.8.8-FIN-STATEMENTS")
        self.assertEqual(status["next_iteration"], "0.8.8-F")
        self.assertEqual(status["current_focus"], "read_only_personal_finance_ledger_statements")
        self.assertEqual(economy["status"], "e_remote_validated_fin_statements_in_validation")
        self.assertTrue(economy["account_statements_supported"])
        self.assertTrue(economy["account_statements_read_only"])
        self.assertEqual(
            economy["account_statement_kinds"],
            ["job_income", "bank_deposit", "bank_withdrawal", "savings_interest"],
        )
        self.assertTrue(economy["account_statement_totals_from_confirmed_ledger"])
        self.assertFalse(economy["account_statement_invents_timestamp"])
        self.assertFalse(economy["account_statement_second_ledger"])
        self.assertTrue(presentation["personal_finance_statement_visible"])
        self.assertEqual(presentation["personal_finance_statement_location"], "existing_jobs_bank_control")
        self.assertFalse(presentation["personal_finance_statement_filter_persisted"])
        self.assertTrue(presentation["focus_maximize_restore"])
        self.assertTrue(presentation["next_action_attention_signal"])
        self.assertFalse(presentation["browser_gameplay_authority"])
        self.assertTrue(process["focused_read_policy"])
        self.assertTrue(process["planned_read_list_required"])
        self.assertTrue(process["broad_scan_requires_concrete_reason"])
        self.assertTrue(process["red_gate_reads_specific_failure_first"])
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
            "POOL-FINANCE-003": "`PULLED`",
            "POOL-UX-004": "`DONE`",
            "POOL-UX-005": "`DONE`",
            "POOL-MAP-002": "`READY`",
        }
        for pool_id, state in expected.items():
            self.assertIn(state, _pool_row(pool, pool_id), pool_id)

    def test_agents_requires_focused_read_and_excludes_codex_review(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Focused-Read-Strategie – verbindlich", agents)
        self.assertIn("Planned-Read-Liste", agents)
        self.assertIn("Breitenscans", agents)
        self.assertIn("der konkrete fehlerhafte Job", agents)
        self.assertIn("Kein erneuter Breitenscan ohne neuen Befund", agents)
        self.assertIn("Codex-Code-Review ist kein Bestandteil", agents)
        self.assertIn("wird weder angefordert noch als Evidenz geführt", agents)


if __name__ == "__main__":
    unittest.main()
