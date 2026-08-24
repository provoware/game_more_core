from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
START = (ROOT / "START_BUNKERFREQUENZ.sh").read_text(encoding="utf-8")


class StartLauncherTests(unittest.TestCase):
    def test_launcher_uses_explicit_browser_fallbacks_and_visible_manual_url(self):
        self.assertIn('python3 tools/start_a4_game_client.py --no-browser "$@"', START)
        self.assertIn('command -v xdg-open', START)
        self.assertIn('command -v firefox', START)
        self.assertIn('command -v google-chrome', START)
        self.assertIn('command -v chromium', START)
        self.assertIn('BITTE IM BROWSER ÖFFNEN: $URL', START)

    def test_launcher_waits_for_real_server_address_and_explains_long_running_server(self):
        self.assertIn("^ADRESSE: ", START)
        self.assertIn("SERVER: läuft. Dieses Fenster während des Spielens offen lassen.", START)
        self.assertIn("STOPP: Strg+C", START)
        self.assertIn('wait "$SERVER_PID"', START)

    def test_no_browser_option_is_preserved_for_manual_start(self):
        self.assertIn('if [[ "$arg" == "--no-browser" ]]', START)
        self.assertIn('BROWSER: Automatik deaktiviert. Bitte öffnen: $URL', START)


if __name__ == "__main__":
    unittest.main()
