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
        history = status["validated_feature_history"]
        latest = history[-1]
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
            "POOL-QA-017",
        )
        for pool_id in done:
            self.assertIn("`DONE`", _pool_row(pool, pool_id), pool_id)
        self.assertIn("`PULLED`", _pool_row(pool, "POOL-WORLD-003"))

    def test_current_status_describes_readonly_projection_and_next_micro_story_002_audit(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        living_world = status["subsystems"]["living_world"]
        presentation = status["subsystems"]["presentation"]
        ranking = status["subsystems"]["ranking"]
        process = status["subsystems"]["development_process"]
        sync = status["status_sync"]
        validation = status["remote_validation"]

        self.assertIn(status["active_iteration"], todo)
        self.assertIn(status["active_iteration"], readme)
        self.assertIn(status["last_validated_feature_iteration"], readme)
        self.assertEqual(status["current_focus"], "district_micro_story_002_audit")
        self.assertIsNone(status["next_iteration"])

        self.assertEqual(validation["pull_request"], 200)
        self.assertEqual(validation["validated_head"], "10b00a872f9a986404800323401883590d0ba6dd")
        self.assertEqual(validation["merged_commit"], "5f403defcf3773c3c44fefa3b282b0015ad9d68e")

        self.assertTrue(living_world["street_boundary_clamping_audit_validated"])
        self.assertTrue(living_world["street_replay_boundary_matrix_validated"])
        self.assertTrue(living_world["street_real_catalog_replay_audit_validated"])
        self.assertTrue(living_world["street_approach_catalog_matrix_audit_validated"])
        self.assertTrue(living_world["street_distribution_report_validated"])
        self.assertEqual(living_world["street_effect_current_strict_dominance"], [])
        self.assertTrue(living_world["district_event_chain_contract_audit_validated"])
        self.assertEqual(
            living_world["district_event_chain_parent_evidence_event_type"],
            "world.district_effect_applied",
        )
        self.assertTrue(living_world["district_event_chain_parent_source_replayable"])
        self.assertFalse(living_world["district_event_chain_biography_authority"])
        self.assertTrue(living_world["district_event_chain_child_event_contract_present"])
        self.assertEqual(living_world["district_event_chain_child_event_type"], "world.district_followup_resolved")
        self.assertEqual(living_world["district_event_chain_parent_binding"], "causation_id=parent_event_id")
        self.assertTrue(living_world["district_event_chain_district_must_match_parent"])
        self.assertTrue(living_world["district_event_chain_exactly_once_retry_validated"])
        self.assertTrue(living_world["district_event_chain_conflicting_retry_rejected"])
        self.assertTrue(living_world["district_event_chain_micro_story_implemented"])
        self.assertEqual(living_world["district_event_chain_micro_story_id"], "power_flicker_afterglow")
        self.assertEqual(living_world["district_event_chain_micro_story_parent_catalog_event_id"], "district.power_flicker")
        self.assertTrue(living_world["district_event_chain_micro_story_delayed_to_later_cycle"])
        self.assertFalse(living_world["district_event_chain_micro_story_cross_district_allowed"])
        self.assertFalse(living_world["district_event_chain_micro_story_balance_effects"])
        self.assertTrue(living_world["district_event_chain_readonly_projection_validated"])
        self.assertEqual(
            living_world["district_event_chain_readonly_projection_parent_source"],
            "confirmed_journal_parent",
        )
        self.assertTrue(living_world["district_event_chain_readonly_projection_requires_same_district"])
        self.assertTrue(living_world["district_event_chain_readonly_projection_requires_parent_before_child"])
        self.assertFalse(living_world["district_event_chain_readonly_projection_browser_authority"])
        self.assertEqual(
            living_world["district_event_chain_next_contract"],
            "0.8.8-STORY-DISTRICT-MICRO-STORY-002-AUDIT",
        )

        self.assertTrue(presentation["crew_identity_visual_consistency_validated"])
        self.assertTrue(presentation["crew_identity_browser_context_e2e_validated"])
        self.assertTrue(presentation["crew_identity_firefox_context_e2e_validated"])
        self.assertTrue(presentation["crew_identity_micro_polish_validated"])
        self.assertEqual(presentation["crew_identity_compact_mark_floor_rem"], 0.34)
        self.assertTrue(presentation["crew_identity_computed_size_e2e_validated"])
        self.assertEqual(presentation["crew_identity_computed_size_floor_rem"], 0.34)
        self.assertTrue(presentation["crew_identity_text_clip_e2e_validated"])
        self.assertEqual(presentation["crew_identity_text_clip_e2e_contexts"], ["hud", "map", "ranking"])
        self.assertFalse(presentation["crew_identity_text_clip_e2e_css_fix_required"])
        self.assertFalse(presentation["map_viewport_mini_overview_supported"])
        self.assertFalse(presentation["map_viewport_mini_overview_audit_pending"])
        self.assertTrue(presentation["map_viewport_mini_overview_audit_validated"])
        self.assertEqual(presentation["map_viewport_orientation_fallback"], "accessible_1_to_1_reset")
        self.assertFalse(presentation["map_viewport_second_overview_created"])
        self.assertIn("world.district_followup_resolved", presentation["event_timeline_sources"])
        self.assertTrue(presentation["district_chain_cause_projection_validated"])
        self.assertEqual(presentation["district_chain_cause_projection_label"], "Folge von:")
        self.assertFalse(presentation["district_chain_cause_projection_invents_missing_parent"])
        self.assertFalse(presentation["district_chain_cause_projection_browser_write_authority"])
        self.assertEqual(
            presentation["crew_identity_browser_e2e_map_fixture"],
            "runtime_property_purchase_projection",
        )
        self.assertTrue(presentation["crew_identity_browser_e2e_real_property_purchase"])
        self.assertFalse(presentation["crew_identity_browser_e2e_dom_owned_marker"])
        self.assertTrue(presentation["runtime_owned_evidence_receipt_validated"])
        self.assertFalse(presentation["crew_identity_second_fetch"])
        self.assertFalse(presentation["crew_identity_second_projection"])
        self.assertFalse(presentation["browser_gameplay_authority"])

        self.assertTrue(ranking["local_confirmed_crew_badge"])
        self.assertEqual(
            ranking["crew_badge_match"],
            "entry.character_id_equals_hall.local_character_id",
        )
        self.assertFalse(ranking["foreign_crew_badges_invented"])

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
            "POOL-STREET-005": "`DONE`",
            "POOL-UX-007": "`DONE`",
            "POOL-QA-010": "`DONE`",
            "POOL-QA-006": "`DONE`",
            "POOL-UX-008": "`DONE`",
            "POOL-QA-011": "`DONE`",
            "POOL-QA-013": "`DONE`",
            "POOL-QA-014": "`DONE`",
            "POOL-QA-015": "`DONE`",
            "POOL-UX-009": "`DONE`",
            "POOL-QA-016": "`DONE`",
            "POOL-MAP-003": "`DONE`",
            "POOL-QA-017": "`DONE`",
            "POOL-WORLD-003": "`PULLED`",
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
