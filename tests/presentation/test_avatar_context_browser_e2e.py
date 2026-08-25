from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import start_a4_acceptance as acceptance  # noqa: E402

CREW_STYLES = (ROOT / "web" / "a4" / "crew_identity.css").read_text(encoding="utf-8")


class AvatarContextBrowserE2ETests(unittest.TestCase):
    def test_harness_uses_existing_ui_and_confirmed_identity_paths(self):
        source = acceptance._avatar_context_harness()
        self.assertIn("Runtime-Owned-Map-Fixture fehlt", source)
        self.assertNotIn('d.getElementById("new-game").click()', source)
        self.assertIn('d.getElementById("save-profile").click()', source)
        self.assertIn('.hud-crew-identity', source)
        self.assertIn('.hall-local-crew .hud-crew-mark', source)
        self.assertIn('canvas?.querySelector(".map-marker.owned")', source)
        self.assertNotIn('className = "map-marker owned"', source)
        self.assertIn('BunkerUIPrefs.set("highContrast", true)', source)
        self.assertIn('width: 760px', source)
        self.assertIn('Boolean(node && !node.hidden', source)
        self.assertNotIn('instanceof HTMLElement', source)
        self.assertIn('new w.Event("input"', source)
        self.assertIn('new w.Event("change"', source)
        self.assertNotIn('new Event("input"', source)
        self.assertIn('<iframe id="app"></iframe>', source)
        self.assertIn('frame.addEventListener("load"', source)
        self.assertIn('frame.src = "/";', source)
        self.assertLess(source.index('frame.addEventListener("load"'), source.index('frame.src = "/";'))
        self.assertIn('document.body.textContent = `AVATAR_CONTEXT_E2E: PASS', source)
        self.assertIn('document.body.textContent = `AVATAR_CONTEXT_E2E: FAIL ·', source)
        self.assertIn('href.endsWith("/crew_identity.css")', source)
        self.assertIn('w.getComputedStyle(hudPreview)', source)
        self.assertIn('hudStyle.borderTopColor !== "rgb(255, 255, 255)"', source)
        self.assertIn('Crew-Geometrie ungültig:', source)
        self.assertNotIn('fetch("/api/command")', source)
        self.assertNotIn("property.purchase", source)
        self.assertNotIn('"Timeline wird geladen"', source)

    def test_compact_hud_keeps_confirmed_identity_visible_without_extra_grid_row(self):
        media = '@media (max-width: 1100px)'
        block = CREW_STYLES[CREW_STYLES.index(media):CREW_STYLES.index('@media (min-width: 721px)')]
        self.assertIn('.hud-brand {\n    display: block;', block)
        self.assertIn('position: absolute;', block)
        self.assertIn('.hud-brand > span:not(.hud-crew-identity)', block)
        self.assertNotIn('.hud-brand > span,\n', block)
        self.assertIn('.ops-hud > .hud-metric:first-of-type', block)
        self.assertIn('padding-left: 3.15rem;', block)
        self.assertIn('.hud-crew-identity {\n    position: static;', block)
        self.assertIn('width: 2.25rem;', block)
        self.assertIn('height: 2.25rem;', block)
        self.assertIn('transform: none;', block)

    def test_avatar_context_url_preserves_startup_query_on_harness_path(self):
        self.assertEqual(
            acceptance._avatar_context_url("http://127.0.0.1:8044/?startup=cache-token"),
            "http://127.0.0.1:8044/__avatar_context_e2e__.html?startup=cache-token",
        )

    def test_avatar_pass_requires_executed_body_not_script_source(self):
        source_only = (
            "<html><body><div>AVATAR_CONTEXT_E2E: RUNNING</div>"
            "<script>const result = 'AVATAR_CONTEXT_E2E: PASS';</script></body></html>"
        )
        executed = (
            "<html><head></head><body>AVATAR_CONTEXT_E2E: PASS\n"
            "● BEREIT\nBUNKERFREQUENZ – Control Deck</body></html>"
        )
        self.assertFalse(acceptance._avatar_context_passed(source_only))
        self.assertTrue(acceptance._avatar_context_passed(executed))

    def test_existing_address_browser_check_stays_read_only_and_uses_original_url(self):
        completed = Mock(
            returncode=0,
            stdout="<html><body>● BEREIT\nBUNKERFREQUENZ – Control Deck</body></html>",
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
                acceptance.browser_dom(
                    "http://127.0.0.1:8044/?startup=real-session",
                    require_browser=True,
                    avatar_context=False,
                )
            self.assertEqual(run.call_args.args[0][-1], "http://127.0.0.1:8044/?startup=real-session")
            self.assertFalse((root / "web" / "a4" / acceptance.AVATAR_CONTEXT_HARNESS).exists())

    def test_browser_acceptance_requires_avatar_context_pass_and_cleans_harness(self):
        completed = Mock(
            returncode=0,
            stdout=(
                "<html><head></head><body>AVATAR_CONTEXT_E2E: PASS\n"
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
                    avatar_context=True,
                )

            self.assertTrue(acceptance._avatar_context_passed(dom))
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

    def test_browser_acceptance_fails_closed_without_executed_avatar_context_pass(self):
        completed = Mock(
            returncode=0,
            stdout=(
                "<html><body><div>AVATAR_CONTEXT_E2E: RUNNING</div>"
                "<script>const result='AVATAR_CONTEXT_E2E: PASS';</script>"
                "● BEREIT BUNKERFREQUENZ – Control Deck</body></html>"
            ),
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
                with self.assertRaisesRegex(RuntimeError, "ausgeführten PASS-Nachweis"):
                    acceptance.browser_dom(
                        "http://127.0.0.1:8044/",
                        require_browser=True,
                        avatar_context=True,
                    )
            self.assertFalse((root / "web" / "a4" / acceptance.AVATAR_CONTEXT_HARNESS).exists())


if __name__ == "__main__":
    unittest.main()
