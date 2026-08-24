from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

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

    def test_desktop_contract_requires_single_canonical_start_path(self):
        with tempfile.TemporaryDirectory() as root:
            product = Path(root)
            tools = product / "tools"
            tools.mkdir()
            launcher = product / "START_BUNKERFREQUENZ.sh"
            launcher.write_text("#!/bin/sh\nexec python3 tools/start_orchestrator.py \"$@\"\n", encoding="utf-8")
            launcher.chmod(0o755)
            desktop_file = product / "BUNKERFREQUENZ.desktop"
            desktop_file.write_text("[Desktop Entry]\nExec=./START_BUNKERFREQUENZ.sh\n", encoding="utf-8")
            desktop_file.chmod(0o755)
            (tools / "start_orchestrator.py").write_text("# canonical\n", encoding="utf-8")
            detail = desktop._scenario_desktop_launcher_contract(product)
            self.assertTrue(detail["single_orchestrator_path"])

    def test_browser_acceptance_enforces_bounded_cold_start_floor(self):
        completed = unittest.mock.Mock(returncode=0, stdout="● BEREIT\nBUNKERFREQUENZ – Control Deck", stderr="")
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
