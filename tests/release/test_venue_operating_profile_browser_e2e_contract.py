from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import venue_operating_profile_browser_e2e as venue  # noqa: E402


class VenueOperatingProfileBrowserE2EContractTests(unittest.TestCase):
    def setUp(self):
        self.tool = (ROOT / "tools/venue_operating_profile_browser_e2e.py").read_text(encoding="utf-8")
        self.harness = venue._harness()
        self.workflow = (ROOT / ".github/workflows/release-acceptance.yml").read_text(encoding="utf-8")

    def test_harness_uses_canonical_owned_fixture_and_real_chromium(self):
        self.assertIn("acceptance.prepare_owned_map_fixture(save_dir)", self.tool)
        self.assertIn("acceptance._start_server(save_dir)", self.tool)
        self.assertIn('"--headless=new"', self.tool)
        self.assertIn('"--window-size=760,680"', self.tool)
        self.assertIn('"--dump-dom"', self.tool)

    def test_harness_checks_owned_only_five_value_profile_under_accessibility_modes(self):
        for label in ("Prestige", "Publikumskraft", "Risiko", "Underground-Faktor", "Nutzen"):
            self.assertIn(label, self.harness)
        self.assertIn('w.BunkerUIPrefs.set("largeText", true)', self.harness)
        self.assertIn('w.BunkerUIPrefs.set("highContrast", true)', self.harness)
        self.assertIn("owned.length !== 1", self.harness)
        self.assertIn('owned[0].querySelector(":scope > div > span")', self.harness)
        self.assertIn('style.visibility === "hidden"', self.harness)
        self.assertIn("Fremder Ort zeigt ein Besitz-Betriebsprofil", self.harness)
        self.assertIn("horizontale Überbreite", self.harness)

    def test_release_acceptance_executes_the_browser_proof(self):
        self.assertIn("tools/venue_operating_profile_browser_e2e.py", self.workflow)
        self.assertIn("Real browser Venue operating profile acceptance", self.workflow)
        self.assertIn("PYTHONPATH=src python3 tools/venue_operating_profile_browser_e2e.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
