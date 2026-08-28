from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
SCENE_PROJECTION = (ROOT / "src" / "bunkerfrequenz" / "presentation" / "scene_jobs_projection.py").read_text(encoding="utf-8")
GAME_PROJECTION = (ROOT / "src" / "bunkerfrequenz" / "presentation" / "a4_game_projection.py").read_text(encoding="utf-8")
JOB_BROWSER = (ROOT / "web" / "a4" / "scene_job_payout_preview.js").read_text(encoding="utf-8")
FOCUS = (ROOT / "web" / "a4" / "control_deck_focus.js").read_text(encoding="utf-8")
AUDIT = (ROOT / "docs" / "RUNTIME_OWNED_STRATEGIC_GUIDANCE_AUDIT.md").read_text(encoding="utf-8")


class RuntimeOwnedStrategicGuidanceAuditTests(unittest.TestCase):
    def test_job_payout_reduction_is_projection_owned_and_uses_canonical_service(self):
        self.assertIn(
            "from bunkerfrequenz.application.scene_job_service import calculate_scene_job_payout_cents",
            SCENE_PROJECTION,
        )
        self.assertIn("effective = calculate_scene_job_payout_cents(projected, character.energy)", SCENE_PROJECTION)
        self.assertIn('projected["effective_payout_cents"] = effective', SCENE_PROJECTION)
        self.assertIn(
            'projected["payout_reduced_by_energy"] = effective < projected["payout_cents"]',
            SCENE_PROJECTION,
        )

    def test_job_browser_consumes_explicit_projection_fact_instead_of_recalculating_strategy(self):
        self.assertIn("const reduced = job.payout_reduced_by_energy === true;", JOB_BROWSER)
        self.assertIn("job.effective_payout_cents", JOB_BROWSER)
        for forbidden in (
            "calculate_scene_job_payout_cents",
            "character.energy",
            "hud-energy",
            "recovery.koffein_kalte_luft",
            "recovery.mate_zucker_vollgas",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, JOB_BROWSER)

    def test_event_blockers_are_owned_by_event_service_projection(self):
        self.assertIn("EventExecutionService.available_actions(event)", GAME_PROJECTION)
        self.assertIn('"enabled": item.enabled', GAME_PROJECTION)
        self.assertIn('"blockers": list(item.blockers)', GAME_PROJECTION)
        self.assertIn('document.getElementById("blockers")', FOCUS)
        self.assertIn('text.startsWith("Blockiert:")', FOCUS)

    def test_global_next_action_help_remains_free_of_strategy_heuristics_and_auto_actions(self):
        for forbidden in (
            "hud-energy",
            "hud-cash",
            "market_price",
            "payout_reduced_by_energy",
            "effective_payout_cents",
            "sendCommand",
            "/api/command",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, FOCUS)

    def test_audit_deliberately_rejects_a_second_global_recommendation_contract_for_now(self):
        self.assertIn("Kein neuer gemeinsamer `strategic_guidance`-/Recommendation-Vertrag", AUDIT)
        self.assertIn("Aus einem reduzierten Joblohn darf nicht automatisch „Recovery starten“ werden.", AUDIT)
        self.assertIn("Kein Hinweis führt automatisch einen Command aus.", AUDIT)
        self.assertIn("fachlich", AUDIT)


if __name__ == "__main__":
    unittest.main()
