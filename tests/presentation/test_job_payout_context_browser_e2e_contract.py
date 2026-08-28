from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
HARNESS = (ROOT / "tools" / "job_payout_context_browser_e2e.py").read_text(encoding="utf-8")


class JobPayoutContextBrowserE2EContractTests(unittest.TestCase):
    def test_fixture_produces_mixed_runtime_owned_job_payout_states(self):
        self.assertIn("FIXTURE_ENERGY = 8", HARNESS)
        self.assertIn('job.get("payout_reduced_by_energy") is True', HARNESS)
        self.assertIn('job.get("payout_reduced_by_energy") is False', HARNESS)
        self.assertIn("Projection-Fixture braucht volle und reduzierte Jobs", HARNESS)

    def test_real_browser_waits_for_payout_decoration_before_classification(self):
        self.assertIn("found.length >= 5 && found.every", HARNESS)
        self.assertIn('row.dataset.payoutReducedByEnergy === \\"true\\" ||', HARNESS)
        self.assertIn('row.dataset.payoutReducedByEnergy === \\"false\\"', HARNESS)
        self.assertIn('}, \\"dekorierte Jobkarten\\");', HARNESS)

    def test_real_browser_checks_visible_copy_accessibility_and_small_window(self):
        self.assertIn(
            "Aktueller Lohn reduziert – deine Energie reicht nicht für die volle Auszahlung.",
            HARNESS,
        )
        self.assertIn('row.dataset.payoutReducedByEnergy === \\"true\\"', HARNESS)
        self.assertIn('row.dataset.payoutReducedByEnergy === \\"false\\"', HARNESS)
        self.assertIn('getAttribute(\\"aria-label\\")', HARNESS)
        self.assertIn('BunkerUIPrefs.set(\\"highContrast\\", true)', HARNESS)
        self.assertIn("width: 760px; height: 680px", HARNESS)
        self.assertIn("rect.right > viewportWidth + 1", HARNESS)

    def test_browser_harness_does_not_recommend_or_execute_recovery(self):
        lowered = HARNESS.lower()
        self.assertNotIn("recovery.koffein_kalte_luft", lowered)
        self.assertNotIn("recovery.mate_zucker_vollgas", lowered)
        self.assertNotIn("/api/command", lowered)
        self.assertNotIn("sendcommand", lowered)
        self.assertNotIn("erholen", lowered)
        self.assertNotIn("regener", lowered)


if __name__ == "__main__":
    unittest.main()
