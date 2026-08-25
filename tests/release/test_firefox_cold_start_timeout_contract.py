from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools" / "desktop_browser_e2e_pro.py"


class FirefoxColdStartTimeoutContractTests(unittest.TestCase):
    def test_session_creation_has_bounded_cold_start_headroom_without_weakening_gate(self):
        source = RUNNER.read_text(encoding="utf-8")

        self.assertIn("FIREFOX_SESSION_TIMEOUT_SECONDS = 55.0", source)
        self.assertIn("FIREFOX_DOM_READY_TIMEOUT_SECONDS = 40.0", source)
        self.assertIn("first = _single_run", source)
        self.assertIn("second = _single_run", source)
        self.assertIn('return "FLAKY"', source)
        self.assertIn('return "PASS" if all(value == "PASS"', source)


if __name__ == "__main__":
    unittest.main()
