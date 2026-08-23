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

    def test_validated_control_deck_finance_map_and_story_pool_items_are_done(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        for pool_id in (
            "POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002",
            "POOL-UX-002", "POOL-WORLD-004", "POOL-PROFILE-002", "POOL-ECON-003",
            "POOL-COMPANION-001", "POOL-COMPANION-002", "POOL-FINANCE-001",
            "POOL-FINANCE-003", "POOL-UX-004", "POOL-UX-005", "POOL-MAP-002",
            "POOL-STORY-001",
        ):
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)

    def test_validated_story_and_active_fin_export_match_status(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        economy = status["subsystems"]["economy"]
        presentation = status["subsystems"]["presentation"]
        living_world = status["subsystems"]["living_world"]
        process = status["subsystems"]["development_process"]

        self.assertEqual(status["last_validated_feature_iteration"], "0.8.8-STORY-DISTRICT-BIO")
        self.assertEqual(status["active_iteration"], "0.8.8-FIN-EXPORT")
        self.assertEqual(status["next_iteration"], "0.8.8-ECON-ANTI-GRIND")
        self.assertEqual(status["current_focus"], "finance_statement_local_txt_csv_export")
        self.assertTrue(presentation["district_biography_visible"])
        self.assertEqual(presentation["district_biography_location"], "existing_profile_panel")
        self.assertEqual(presentation["district_biography_entries_limit"], 5)
        self.assertEqual(presentation["district_biography_source"], "event_timeline")
        self.assertFalse(presentation["district_biography_state_persisted"])
        self.assertFalse(presentation["district_biography_invents_timestamp"])
        self.assertEqual(living_world["district_biography_source"], "event_timeline_district_entries")
        self.assertTrue(living_world["district_biography_afterglow_validated"])
        self.assertFalse(living_world["district_biography_progression_engine"])
        self.assertFalse(living_world["district_biography_new_journal_event"])
        self.assertTrue(economy["account_statement_export_in_validation"])
        self.assertEqual(economy["account_statement_export_formats"], ["txt", "csv"])
        self.assertEqual(economy["account_statement_export_source"], "finance_statement_projection")
        self.assertFalse(economy["account_statement_export_recalculates_totals"])
        self.assertFalse(economy["account_statement_export_write_back"])
        self.assertFalse(economy["account_statement_export_invents_timestamp"])
        self.assertTrue(presentation["personal_finance_statement_export_visible"])
        self.assertEqual(presentation["personal_finance_statement_export_formats"], ["txt", "csv"])
        self.assertTrue(presentation["personal_finance_statement_export_local_only"])
        self.assertFalse(presentation["personal_finance_statement_export_uses_filter"])
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
            "POOL-FINANCE-003": "`DONE`",
            "POOL-FINANCE-004": "`PULLED`",
            "POOL-UX-004": "`DONE`",
            "POOL-UX-005": "`DONE`",
            "POOL-MAP-002": "`DONE`",
            "POOL-STORY-001": "`DONE`",
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