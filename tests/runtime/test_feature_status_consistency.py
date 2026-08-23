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
            "POOL-COMPANION-001", "POOL-COMPANION-002",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)

    def test_validated_d_and_active_d2_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]
        process = status["subsystems"]["development_process"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-D")
        self.assertEqual(status["active_iteration"], "0.8.8-D2")
        self.assertEqual(status["next_iteration"], "0.8.8-E")
        self.assertEqual(status["current_focus"], "confirmed_finance_period_savings_interest_exactly_once")
        self.assertTrue(economy["personal_finance_state_validated"])
        self.assertTrue(economy["bank_account_supported"])
        self.assertTrue(economy["bank_transfer_service_implemented"])
        self.assertTrue(economy["bank_transfer_recoverable"])
        self.assertTrue(economy["bank_transfer_idempotent"])
        self.assertFalse(economy["browser_can_supply_bank_target_balances"])
        self.assertTrue(economy["savings_interest_supported"])
        self.assertEqual(economy["savings_interest_basis_points_per_confirmed_period"], 100)
        self.assertTrue(economy["savings_interest_compounds_on_current_bank_balance"])
        self.assertTrue(economy["savings_interest_confirmed_period_required"])
        self.assertTrue(economy["savings_interest_sequential_finance_tick"])
        self.assertTrue(economy["savings_interest_zero_period_consumed"])
        self.assertFalse(economy["savings_interest_system_time_sole_authority"])
        self.assertFalse(economy["browser_can_confirm_savings_period"])
        self.assertFalse(economy["browser_can_supply_interest_amount"])
        self.assertTrue(presentation["personal_bank_controls_in_jobs_panel"])
        self.assertFalse(presentation["personal_bank_second_dashboard"])
        self.assertTrue(process["focused_read_policy"])
        self.assertTrue(process["planned_read_list_required"])
        self.assertTrue(process["broad_scan_requires_concrete_reason"])
        self.assertTrue(process["red_gate_reads_specific_failure_first"])

    def test_requested_0_8_8_foundations_have_single_pool_owners(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        expected = {
            "POOL-PROFILE-002": "`DONE`",
            "POOL-ECON-003": "`DONE`",
            "POOL-COMPANION-001": "`DONE`",
            "POOL-COMPANION-002": "`DONE`",
            "POOL-FINANCE-001": "`PULLED`",
            "POOL-FINANCE-003": "`READY`",
            "POOL-UX-004": "`READY`",
            "POOL-MAP-002": "`READY`",
        }
        for pool_id, state in expected.items():
            self.assertIn(state, _pool_row(pool, pool_id), pool_id)

    def test_agents_requires_focused_read_before_broad_scan(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("## Focused-Read-Strategie – verbindlich", agents)
        self.assertIn("Planned-Read-Liste", agents)
        self.assertIn("Breitenscans", agents)
        self.assertIn("konkreten fehlerhafte Job", agents)


if __name__ == "__main__":
    unittest.main()
