from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class VenueOperatingProfileBrowserE2EContractTests(unittest.TestCase):
    def setUp(self):
        self.tool = (ROOT / "tools/venue_operating_profile_browser_e2e.py").read_text(encoding="utf-8")
        self.workflow = (ROOT / ".github/workflows/release-acceptance.yml").read_text(encoding="utf-8")

    def test_harness_uses_canonical_owned_fixture_and_real_chromium(self):
        self.assertIn("acceptance.prepare_owned_map_fixture(save_dir)", self.tool)
        self.assertIn("acceptance._start_server(save_dir)", self.tool)
        self.assertIn('"--headless=new"', self.tool)
        self.assertIn('"--window-size=760,680"', self.tool)
        self.assertIn('"--dump-dom"', self.tool)

    def test_harness_checks_owned_only_five_value_profile_under_accessibility_modes(self):
        for label in ("Prestige", "Publikumskraft", "Risiko", "Underground-Faktor", "Nutzen"):
            self.assertIn(label, self.tool)
        self.assertIn('w.BunkerUIPrefs.set("largeText", true)', self.tool)
        self.assertIn('w.BunkerUIPrefs.set("highContrast", true)', self.tool)
        self.assertIn("owned.length !== 1", self.tool)
        self.assertIn("Fremder Ort zeigt ein Besitz-Betriebsprofil", self.tool)
        self.assertIn("horizontale Überbreite", self.tool)

    def test_release_acceptance_executes_the_browser_proof(self):
        self.assertIn("tools/venue_operating_profile_browser_e2e.py", self.workflow)
        self.assertIn("Real browser Venue operating profile acceptance", self.workflow)
        self.assertIn("PYTHONPATH=src python3 tools/venue_operating_profile_browser_e2e.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
