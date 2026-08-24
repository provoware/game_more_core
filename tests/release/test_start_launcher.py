from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
START = (ROOT / "START_BUNKERFREQUENZ.sh").read_text(encoding="utf-8")
DESKTOP = (ROOT / "BUNKERFREQUENZ.desktop").read_text(encoding="utf-8")
ORCHESTRATOR = (ROOT / "tools" / "start_orchestrator.py").read_text(encoding="utf-8")
ACCEPTANCE = (ROOT / "tools" / "start_a4_acceptance.py").read_text(encoding="utf-8")


class StartLauncherTests(unittest.TestCase):
    def test_public_launcher_delegates_to_exactly_one_orchestrator(self):
        self.assertIn('exec "$PYTHON_BIN" tools/start_orchestrator.py "$@"', START)
        self.assertNotIn("start_a4_game_client.py", START)
        self.assertIn("SERVER = ROOT / \"tools\" / \"start_a4_game_client.py\"", ORCHESTRATOR)

    def test_launcher_accepts_python3_or_compatible_python_and_explains_missing_dependency(self):
        self.assertIn("for candidate in python3 python", START)
        self.assertIn("sys.version_info >= (3, 10)", START)
        self.assertIn("sudo apt install python3", START)

    def test_orchestrator_has_full_pre_and_post_validation_sequence(self):
        for marker in (
            "VORPRÜFUNG",
            "ABHÄNGIGKEITEN",
            "SERVERSTART",
            "API-PRÜFUNG",
            "BROWSERPRÜFUNG",
            "BROWSERSTART",
            "NACHVALIDIERUNG",
            "BEREIT",
        ):
            self.assertIn(marker, ORCHESTRATOR)
        self.assertIn("probe_http(address)", ORCHESTRATOR)
        self.assertIn("browser_dom(address", ORCHESTRATOR)
        self.assertIn("START_STATUS.txt", ORCHESTRATOR)
        self.assertIn("START_DIAGNOSE.txt", ORCHESTRATOR)
        self.assertIn("AUTO-AUFLÖSUNG", ORCHESTRATOR)
        self.assertIn("🟢", ORCHESTRATOR)
        self.assertIn("🟡", ORCHESTRATOR)
        self.assertIn("🔴", ORCHESTRATOR)

    def test_orchestrator_reuses_existing_http_browser_acceptance_contract(self):
        self.assertIn("from start_a4_acceptance import browser_dom, probe_http", ORCHESTRATOR)
        self.assertIn("/api/health", ACCEPTANCE)
        self.assertIn("/api/state", ACCEPTANCE)
        self.assertIn("● BEREIT", ACCEPTANCE)

    def test_desktop_launcher_still_uses_the_same_shell_start_path(self):
        self.assertIn("[Desktop Entry]", DESKTOP)
        self.assertIn("Terminal=true", DESKTOP)
        self.assertIn("START_BUNKERFREQUENZ.sh", DESKTOP)
        self.assertNotIn("start_a4_game_client.py", DESKTOP)
        self.assertNotIn("start_orchestrator.py", DESKTOP)


if __name__ == "__main__":
    unittest.main()
