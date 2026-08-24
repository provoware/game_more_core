from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
START = (ROOT / "START_BUNKERFREQUENZ.sh").read_text(encoding="utf-8")
DESKTOP = (ROOT / "BUNKERFREQUENZ.desktop").read_text(encoding="utf-8")
ACCEPTANCE = (ROOT / "tools" / "start_a4_acceptance.py").read_text(encoding="utf-8")


class StartLauncherTests(unittest.TestCase):
    def test_launcher_reuses_http_acceptance_probe_before_browser_open(self):
        self.assertIn('python3 tools/start_a4_acceptance.py --address "$URL" --no-browser-check', START)
        self.assertIn("/api/health", ACCEPTANCE)
        self.assertIn("/api/state", ACCEPTANCE)
        self.assertIn("START-SELBSTTEST FEHLGESCHLAGEN", ACCEPTANCE)

    def test_launcher_has_verified_browser_fallbacks_and_manual_url(self):
        self.assertIn("launch_checked", START)
        self.assertIn("kill -0", START)
        self.assertIn("command -v xdg-open", START)
        self.assertIn("command -v firefox", START)
        self.assertIn("command -v google-chrome", START)
        self.assertIn("command -v chromium", START)
        self.assertIn("BITTE IM BROWSER ÖFFNEN: $URL", START)

    def test_failure_writes_beginner_readable_diagnostic_file(self):
        self.assertIn('DIAG_FILE="$ROOT/START_DIAGNOSE.txt"', START)
        self.assertIn("BUNKERFREQUENZ STARTDIAGNOSE", START)
        self.assertIn("PROJEKTORDNER:", START)
        self.assertIn("PYTHON:", START)
        self.assertIn("LETZTE SERVERMELDUNGEN", START)
        self.assertIn("DIAGNOSE GESPEICHERT:", START)

    def test_no_browser_option_is_preserved(self):
        self.assertIn('if [[ "$arg" == "--no-browser" ]]', START)
        self.assertIn("BROWSER: Automatik deaktiviert.", START)

    def test_desktop_launcher_uses_the_same_shell_start_path(self):
        self.assertIn("[Desktop Entry]", DESKTOP)
        self.assertIn("Terminal=true", DESKTOP)
        self.assertIn("START_BUNKERFREQUENZ.sh", DESKTOP)
        self.assertNotIn("start_a4_game_client.py", DESKTOP)


if __name__ == "__main__":
    unittest.main()
