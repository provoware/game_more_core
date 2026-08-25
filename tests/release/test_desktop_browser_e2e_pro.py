from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import desktop_browser_e2e_pro as desktop  # noqa: E402
import start_a4_acceptance as acceptance  # noqa: E402


class DesktopBrowserE2EContractTests(unittest.TestCase):
    def test_anti_flake_mismatch_can_never_be_pass(self):
        first = {name: {"status": "PASS"} for name in desktop.REQUIRED_SCENARIOS}
        second = {name: {"status": "PASS"} for name in desktop.REQUIRED_SCENARIOS}
        second["chromium_dom_ready"] = {"status": "FAIL"}
        self.assertEqual(desktop.evaluate_runs(first, second), "FLAKY")
        self.assertEqual(desktop.evaluate_runs(first, first), "PASS")
        failed = {name: {"status": "FAIL"} for name in desktop.REQUIRED_SCENARIOS}
        self.assertEqual(desktop.evaluate_runs(failed, failed), "FAIL")

    def test_multi_browser_contract_requires_native_firefox_scenario(self):
        self.assertIn("chromium_dom_ready", desktop.REQUIRED_SCENARIOS)
        self.assertIn("firefox_dom_ready", desktop.REQUIRED_SCENARIOS)
        first = {name: {"status": "PASS"} for name in desktop.REQUIRED_SCENARIOS}
        second = {name: {"status": "PASS"} for name in desktop.REQUIRED_SCENARIOS}
        second["firefox_dom_ready"] = {"status": "FAIL"}
        self.assertEqual(desktop.evaluate_runs(first, second), "FLAKY")

    def test_firefox_scenario_fails_closed_without_native_binaries(self):
        with patch.object(desktop.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Firefox und Geckodriver"):
                desktop._scenario_firefox_dom(Path("/unused"), Path("/unused"))

    def test_firefox_harness_is_bounded_and_reuses_avatar_context_contract(self):
        source = (ROOT / "tools" / "desktop_browser_e2e_pro.py").read_text(encoding="utf-8")
        self.assertEqual(desktop.FIREFOX_DRIVER_READY_TIMEOUT_SECONDS, 20.0)
        self.assertEqual(desktop.FIREFOX_SESSION_TIMEOUT_SECONDS, 55.0)
        self.assertEqual(desktop.FIREFOX_NAVIGATION_TIMEOUT_SECONDS, 20.0)
        self.assertEqual(desktop.FIREFOX_DOM_READY_TIMEOUT_SECONDS, 40.0)
        self.assertEqual(desktop.FIREFOX_WEBDRIVER_CALL_TIMEOUT_SECONDS, 8.0)
        self.assertIn('"--log", "fatal"', source)
        self.assertIn("stdout=subprocess.DEVNULL", source)
        self.assertIn("stderr=subprocess.DEVNULL", source)
        self.assertIn('"pageLoadStrategy": "eager"', source)
        self.assertIn("acceptance._avatar_context_harness()", source)
        self.assertIn("acceptance._avatar_context_url(address)", source)
        self.assertIn("acceptance.AVATAR_CONTEXT_PASS in body_text", source)
        self.assertIn('"avatar_context_pass": True', source)
        self.assertIn('"runtime_owned_map_fixture": True', source)
        self.assertIn('"small_viewport": True', source)
        self.assertIn('"high_contrast": True', source)
        self.assertIn('"--prepare-owned-map-fixture"', source)
        self.assertIn("harness_path.unlink(missing_ok=True)", source)
        self.assertIn("except (TimeoutError, OSError, URLError, HTTPError, json.JSONDecodeError):", source)
        self.assertNotIn("driver.stdout.close()", source)
        self.assertIn("runtime_owned_map_fixture_from_property_purchase", source)
        self.assertIn("firefox_avatar_context_profile_hud_map_ranking", source)
        self.assertIn("firefox_avatar_context_high_contrast_small_viewport", source)

    def test_avatar_context_map_requires_runtime_owned_marker(self):
        harness = acceptance._avatar_context_harness()
        self.assertIn('canvas?.querySelector(".map-marker.owned")', harness)
        self.assertIn("bestätigter Eigentumsmarker", harness)
        self.assertIn("Runtime-Owned-Map-Fixture fehlt", harness)
        self.assertNotIn("syntheticOwned", harness)
        self.assertNotIn('className = "map-marker owned"', harness)
        self.assertNotIn("E2E read-only owned marker fixture", harness)

    def test_owned_map_fixture_uses_cheapest_catalogued_property_and_canonical_command(self):
        fake_runtime = Mock()
        fake_runtime.city_map_manifest = {
            "locations": [
                {
                    "location_id": "expensive",
                    "purchasable": True,
                    "purchase_price_cents": 9_000_000,
                },
                {
                    "location_id": "cheap",
                    "purchasable": True,
                    "purchase_price_cents": 3_100_000,
                },
                {
                    "location_id": "not-for-sale",
                    "purchasable": False,
                    "purchase_price_cents": 1,
                },
            ]
        }
        fake_runtime.starter = {
            "event": {"event_id": "event-e2e", "budget_cents": 100_000},
            "character": {"character_id": "player-local"},
        }
        fake_runtime.bootstrap.return_value = {"status": "confirmed"}
        fake_runtime._context.return_value = object()
        fake_runtime.session.dispatch.return_value = Mock(status="confirmed", error_code=None)

        with patch.object(acceptance.game_client, "A4ClientRuntime", return_value=fake_runtime):
            location_id = acceptance.prepare_owned_map_fixture(Path("/isolated/save"))

        self.assertEqual(location_id, "cheap")
        self.assertEqual(fake_runtime.starter["event"]["budget_cents"], 3_100_000)
        fake_runtime.bootstrap.assert_called_once_with({"command_id": "acceptance-owned-map-bootstrap"})
        fake_runtime._context.assert_called_once_with(
            "acceptance-owned-map-purchase", "event", "event-e2e", "player-local"
        )
        fake_runtime.session.dispatch.assert_called_once()
        command = fake_runtime.session.dispatch.call_args.args[0]
        self.assertEqual(
            command,
            {
                "type": "property.purchase",
                "command_id": "acceptance-owned-map-purchase",
                "location_id": "cheap",
            },
        )
        self.assertNotIn("purchase_price_cents", command)
        self.assertNotIn("owner_character_id", command)

    def test_source_identity_rejects_tracked_drift_but_not_untracked_evidence(self):
        with patch.object(desktop, "_git") as git:
            git.side_effect = [" M tools/start_a4_acceptance.py"]
            with self.assertRaisesRegex(RuntimeError, "versionierten Quelldateien"):
                desktop.source_identity()
        git.assert_called_once_with("status", "--porcelain", "--untracked-files=no")

        with patch.object(desktop, "_git") as git:
            git.side_effect = ["", "commit123", "tree123"]
            self.assertEqual(desktop.source_identity(), ("commit123", "tree123"))

    def test_prior_failure_subgate_must_match_source_candidate_and_pass(self):
        candidate = "a" * 64
        evidence = "b" * 64
        base = {
            "schema_version": 1,
            "source_commit": "commit",
            "source_tree": "tree",
            "candidate_sha256": candidate,
            "gates": {
                "failure_containment_pro": {"status": "PASS", "evidence_sha256": evidence},
                "desktop_browser_e2e_pro": {"status": "NOT_RUN", "evidence_sha256": None},
            },
        }
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "SUBGATE_EVIDENCE.json"
            path.write_text(json.dumps(base), encoding="utf-8")
            loaded = desktop._load_prior_subgate(path, "commit", "tree", candidate)
            self.assertEqual(loaded["candidate_sha256"], candidate)

            bad = dict(base)
            bad["candidate_sha256"] = "c" * 64
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Release-Bytes"):
                desktop._load_prior_subgate(path, "commit", "tree", candidate)

    def _write_launcher_fixture(self, product: Path, *, desktop_exec: str, launcher_exec: str) -> None:
        tools = product / "tools"
        tools.mkdir()
        launcher = product / "START_BUNKERFREQUENZ.sh"
        launcher.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{launcher_exec}\n", encoding="utf-8")
        launcher.chmod(0o755)
        desktop_file = product / "BUNKERFREQUENZ.desktop"
        desktop_file.write_text(f"[Desktop Entry]\n{desktop_exec}\n", encoding="utf-8")
        desktop_file.chmod(0o755)
        (tools / "start_orchestrator.py").write_text("# canonical\n", encoding="utf-8")

    def test_desktop_contract_requires_exact_canonical_start_path(self):
        with tempfile.TemporaryDirectory() as root:
            product = Path(root)
            self._write_launcher_fixture(
                product,
                desktop_exec=desktop.EXPECTED_DESKTOP_EXEC,
                launcher_exec=desktop.EXPECTED_LAUNCHER_EXEC,
            )
            detail = desktop._scenario_desktop_launcher_contract(product)
            self.assertTrue(detail["single_orchestrator_path"])
            self.assertTrue(detail["exact_desktop_exec"])
            self.assertTrue(detail["exact_launcher_exec"])

    def test_launcher_substring_or_comment_cannot_fake_canonical_path(self):
        with tempfile.TemporaryDirectory() as root:
            product = Path(root)
            self._write_launcher_fixture(
                product,
                desktop_exec="Exec=./alternate.sh START_BUNKERFREQUENZ.sh",
                launcher_exec='exec python3 tools/alternate.py "$@" # tools/start_orchestrator.py',
            )
            with self.assertRaisesRegex(RuntimeError, "kanonischen Klickstartbefehl"):
                desktop._scenario_desktop_launcher_contract(product)

    def test_shutdown_claim_requires_health_endpoint_to_be_unreachable(self):
        with patch.object(desktop, "urlopen", side_effect=URLError("connection refused")) as probe:
            desktop._assert_server_stopped("http://127.0.0.1:8123/")
        probe.assert_called_once()

    def test_browser_acceptance_enforces_bounded_cold_start_floor(self):
        completed = unittest.mock.Mock(
            returncode=0,
            stdout="AVATAR_CONTEXT_E2E: PASS\n● BEREIT\nBUNKERFREQUENZ – Control Deck",
            stderr="",
        )
        with (
            patch.object(acceptance, "find_browser", return_value="/usr/bin/chromium"),
            patch.object(acceptance.subprocess, "run", return_value=completed) as run,
        ):
            acceptance.browser_dom("http://127.0.0.1:8044/", require_browser=True, timeout=15.0)
        self.assertEqual(run.call_args.kwargs["timeout"], acceptance.MIN_BROWSER_WALLCLOCK_TIMEOUT)
        self.assertEqual(acceptance.MIN_BROWSER_WALLCLOCK_TIMEOUT, 30.0)

    def test_evidence_serialization_is_canonical(self):
        payload = {"status": "PASS", "runs": [{"a": 1}], "schema_version": 1}
        first = desktop._canonical_json_bytes(payload)
        second = desktop._canonical_json_bytes(json.loads(first.decode("utf-8")))
        self.assertEqual(first, second)
        self.assertEqual(desktop._sha256_bytes(first), desktop._sha256_bytes(second))


if __name__ == "__main__":
    unittest.main()
