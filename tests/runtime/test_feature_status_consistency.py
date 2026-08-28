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
    def test_last_validated_feature_tracks_productive_trade_history(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")

        iteration = status["last_validated_feature_iteration"]
        latest_feature = status["validated_feature_history"][-1]

        self.assertEqual(iteration, "0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY")
        self.assertEqual(latest_feature["iteration"], iteration)
        self.assertEqual(latest_feature["pull_request"], 238)
        self.assertEqual(latest_feature["merged_commit"], "52934e08dfc5c24e6b9c2933f6c53d8374018079")
        self.assertIn(f"Zuletzt remote validierte Feature-Stufe:** `{iteration}`", todo)
        self.assertIn("PR #238", todo)
        self.assertIn("52934e08dfc5c24e6b9c2933f6c53d8374018079", todo)
        self.assertIn(f"**{iteration}:** PR #238", pool)
        self.assertIn("52934e08dfc5c24e6b9c2933f6c53d8374018079", pool)

    def test_latest_safe_merge_anchor_tracks_productive_trade_history(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        validation = status["remote_validation"]
        sync = status["status_sync"]

        self.assertEqual(validation["pull_request"], 238)
        self.assertEqual(validation["validated_head"], "20b0ed21b97d16babd2108e76cecc25aaa32a889")
        self.assertEqual(validation["merged_commit"], "52934e08dfc5c24e6b9c2933f6c53d8374018079")
        self.assertEqual(validation["safe_merge_result"], "PASS")
        self.assertTrue(validation["main_provenance_confirmed"])
        self.assertNotIn("codex_review_execution", validation)
        self.assertEqual(sync["anchor_pull_request"], 238)
        self.assertEqual(sync["anchor_merge_commit"], validation["merged_commit"])
        self.assertEqual(sync["anchor_iteration"], "0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY")
        self.assertIn("Status-Sync-Anker:** PR #238", todo)
        self.assertIn("Status-Sync-Anker:** PR #238", pool)
        self.assertIn("**0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY:** PR #238", pool)

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
            "POOL-QA-017", "POOL-WORLD-003", "POOL-STREET-003", "POOL-ECON-009",
            "POOL-STORY-002", "POOL-UX-010", "POOL-UX-011", "POOL-UX-012", "POOL-UX-013",
            "POOL-ECON-010",
        )
        for pool_id in done:
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)
        self.assertIn("`PULLED`", _pool_row(pool, "POOL-QA-018"))

    def test_current_status_describes_trade_history_and_next_browser_e2e(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]
        process = status["subsystems"]["development_process"]
        sync = status["status_sync"]
        validation = status["remote_validation"]

        self.assertIn(status["active_iteration"], todo)
        self.assertEqual(status["active_iteration"], "0.8.8-QA-EQUIPMENT-TRADE-HISTORY-BROWSER-E2E")
        self.assertEqual(status["current_focus"], "equipment_trade_history_browser_e2e")
        self.assertIsNone(status["next_iteration"])
        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY")

        self.assertTrue(economy["equipment_trade_history_audit_validated"])
        self.assertTrue(economy["equipment_trade_history_readonly_supported_by_ledger"])
        self.assertEqual(economy["equipment_trade_history_source_kinds"], ["buy", "sell"])
        self.assertIn("unit_price_cents", economy["equipment_trade_history_fields"])
        self.assertFalse(economy["equipment_trade_history_realized_profit_supported"])
        self.assertFalse(economy["equipment_trade_history_cost_basis_contract"])
        self.assertFalse(economy["equipment_trade_history_compensates_is_cost_basis"])
        self.assertTrue(economy["equipment_trade_history_product_ui_visible"])
        self.assertEqual(economy["equipment_trade_history_visible_limit"], 8)
        self.assertTrue(economy["equipment_trade_history_compensated_pairs_filtered"])

        self.assertTrue(presentation["equipment_trade_history_visible"])
        self.assertEqual(presentation["equipment_trade_history_location"], "existing_equipment_economy_panel")
        self.assertFalse(presentation["equipment_trade_history_browser_commands"])
        self.assertFalse(presentation["equipment_trade_history_profit_calculation"])
        self.assertFalse(presentation["browser_gameplay_authority"])

        self.assertIn("leere Handelshistorie", todo)
        self.assertIn("kompensierte", todo)
        self.assertIn("Hoher Kontrast", todo)

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
            "POOL-WORLD-003": "`DONE`", "POOL-STREET-003": "`DONE`",
            "POOL-ECON-009": "`DONE`", "POOL-STORY-002": "`DONE`",
            "POOL-UX-010": "`DONE`", "POOL-UX-011": "`DONE`",
            "POOL-UX-012": "`DONE`", "POOL-UX-013": "`DONE`",
            "POOL-ECON-010": "`DONE`", "POOL-QA-018": "`PULLED`",
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
