from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import start_a4_acceptance as acceptance  # noqa: E402


class AvatarContextBrowserE2ETests(unittest.TestCase):
    def test_harness_uses_existing_ui_and_confirmed_identity_paths(self):
        source = acceptance._avatar_context_harness()
        self.assertIn('d.getElementById("new-game").click()', source)
        self.assertIn('d.getElementById("save-profile").click()', source)
        self.assertIn('.hud-crew-identity', source)
        self.assertIn('.hall-local-crew .hud-crew-mark', source)
        self.assertIn('className = "map-marker owned"', source)
        self.assertIn('BunkerUIPrefs.set("highContrast", true)', source)
        self.assertIn('width: 760px', source)
        self.assertNotIn('fetch("/api/command")', source)
        self.assertNotIn("property.purchase", source)
        self.assertNotIn('"Timeline wird geladen"', source)

    def test_avatar_context_url_preserves_startup_query_on_harness_path(self):
        self.assertEqual(
            acceptance._avatar_context_url("http://127.0.0.1:8044/?startup=cache-token"),
            "http://127.0.0.1:8044/__avatar_context_e2e__.html?startup=cache-token",
        )

    def test_browser_acceptance_requires_avatar_context_pass_and_cleans_harness(self):
        completed = Mock(
            returncode=0,
            stdout=(
                "<html><body>AVATAR_CONTEXT_E2E: PASS\n"
                "● BEREIT\nBUNKERFREQUENZ – Control Deck</body></html>"
            ),
            stderr="",
        )
        with tempfile.TemporaryDirectory() as root_value:
            root = Path(root_value)
            (root / "web" / "a4").mkdir(parents=True)
            with (
                patch.object(acceptance, "ROOT", root),
                patch.object(acceptance, "find_browser", return_value="/usr/bin/chromium"),
                patch.object(acceptance.subprocess, "run", return_value=completed) as run,
            ):
                dom = acceptance.browser_dom(
                    "http://127.0.0.1:8044/?startup=cache-token",
                    require_browser=True,
                )

            self.assertIn(acceptance.AVATAR_CONTEXT_PASS, dom)
            command = run.call_args.args[0]
            self.assertIn("--window-size=900,760", command)
            self.assertIn(
                f"--virtual-time-budget={acceptance.BROWSER_VIRTUAL_TIME_BUDGET_MS}",
                command,
            )
            self.assertEqual(
                command[-1],
                "http://127.0.0.1:8044/__avatar_context_e2e__.html?startup=cache-token",
            )
            self.assertFalse((root / "web" / "a4" / acceptance.AVATAR_CONTEXT_HARNESS).exists())

    def test_browser_acceptance_fails_closed_without_avatar_context_pass(self):
        completed = Mock(
            returncode=0,
            stdout="<html><body>AVATAR_CONTEXT_E2E: FAIL Timeout: bestätigte HUD-Crew</body></html>",
            stderr="",
        )
        with tempfile.TemporaryDirectory() as root_value:
            root = Path(root_value)
            (root / "web" / "a4").mkdir(parents=True)
            with (
                patch.object(acceptance, "ROOT", root),
                patch.object(acceptance, "find_browser", return_value="/usr/bin/chromium"),
                patch.object(acceptance.subprocess, "run", return_value=completed),
            ):
                with self.assertRaisesRegex(RuntimeError, "Avatar-Context-E2E"):
                    acceptance.browser_dom(
                        "http://127.0.0.1:8044/",
                        require_browser=True,
                    )
            self.assertFalse((root / "web" / "a4" / acceptance.AVATAR_CONTEXT_HARNESS).exists())


if __name__ == "__main__":
    unittest.main()
