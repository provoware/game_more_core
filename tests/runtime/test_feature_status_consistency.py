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

        self.assertIn(f"Zuletzt remote validierte Feature-Stufe vor aktuellem Gameplay-Slice:** `{iteration}", todo)
        self.assertIn(f"PR #{pr_number}", todo)
        self.assertIn(merge_sha, todo)
        self.assertIn(f"**{iteration}:** PR #{pr_number}", pool)
        self.assertIn(merge_sha, pool)
        self.assertEqual(validation["safe_merge_result"], "PASS")
        self.assertTrue(validation["main_provenance_confirmed"])
        self.assertNotIn("codex_review_execution", validation)

    def test_validated_pool_items_and_active_scout_owner_are_consistent(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        for pool_id in (
            "POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002",
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002", "POOL-ECON-003",
            "POOL-COMPANION-001", "POOL-COMPANION-002", "POOL-FINANCE-001",
            "POOL-FINANCE-003", "POOL-FINANCE-004", "POOL-UX-004", "POOL-UX-005",
            "POOL-MAP-002", "POOL-STORY-001", "POOL-ECON-004", "POOL-ECON-005",
            "POOL-UX-006", "POOL-ECON-006", "POOL-UX-003", "POOL-ECON-007",
            "POOL-STREET-002", "POOL-ECON-008", "POOL-QA-007", "POOL-QA-008",
            "POOL-QA-002", "POOL-QA-009",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)
        self.assertIn("`READY`", _pool_row(pool, "POOL-UX-007"))
        self.assertIn("`PULLED`", _pool_row(pool, "POOL-STREET-005"))

    def test_validated_street_effect_audit_and_active_scout_balance_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        economy = status["subsystems"]["economy"]
        living_world = status["subsystems"]["living_world"]
        presentation = status["subsystems"]["presentation"]
        process = status["subsystems"]["development_process"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-STREET-EFFECT-AUDIT")
        self.assertEqual(status["active_iteration"], "0.8.8-STREET-SCOUT-BALANCE")
        self.assertEqual(status["next_iteration"], "0.8.8-UX-RECEIPT-CLARITY")
        self.assertEqual(status["current_focus"], "street_scout_manifest_balance_tradeoff")
        self.assertFalse(economy["recovery_balance_audit_in_validation"])
        self.assertTrue(economy["recovery_balance_audit_validated"])
        self.assertFalse(living_world["district_replay_receipt_precision_in_validation"])
        self.assertTrue(living_world["district_replay_receipt_precision_validated"])
        self.assertFalse(living_world["street_effect_audit_in_validation"])
        self.assertTrue(living_world["street_effect_audit_validated"])
        self.assertFalse(living_world["street_effect_audit_telemetry"])
        self.assertFalse(living_world["street_effect_audit_gameplay_changes"])
        self.assertTrue(living_world["street_scout_balance_in_validation"])
        self.assertFalse(living_world["street_scout_balance_validated"])
        self.assertFalse(living_world["street_scout_balance_second_engine"])
        self.assertEqual(living_world["street_scout_discovery_weight"], 40)
        self.assertEqual(living_world["street_effect_current_strict_dominance"], [])
        self.assertEqual(
            living_world["street_effect_expected_hundredths"]["scout"],
            {"energy": 101, "stress": -9, "reputation": 33},
        )
        self.assertTrue(presentation["control_deck_focus_mutation_loop_hotfixed"])
        self.assertFalse(presentation["browser_gameplay_authority"])
        self.assertTrue(process["focused_read_policy"])
        self.assertTrue(process["planned_read_list_required"])
        self.assertTrue(process["repository_file_classes_enabled"])
        self.assertTrue(process["evidence_logs_on_failure_or_final_proof_only"])
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
            "POOL-ECON-005": "`DONE`",
            "POOL-UX-006": "`DONE`",
            "POOL-ECON-006": "`DONE`",
            "POOL-UX-003": "`DONE`",
            "POOL-ECON-007": "`DONE`",
            "POOL-STREET-002": "`DONE`",
            "POOL-ECON-008": "`DONE`",
            "POOL-QA-007": "`DONE`",
            "POOL-QA-008": "`DONE`",
            "POOL-QA-002": "`DONE`",
            "POOL-QA-009": "`DONE`",
            "POOL-STREET-005": "`PULLED`",
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
