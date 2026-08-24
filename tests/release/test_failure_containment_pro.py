from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import failure_containment_pro as containment  # noqa: E402
import start_orchestrator as orchestrator  # noqa: E402

from bunkerfrequenz.infrastructure.persistence import PersistenceKernel  # noqa: E402


class _DummyProcess:
    def wait(self) -> int:
        return 0


class _RaceServer:
    outcomes: list[object] = []
    created_ports: list[int] = []
    stopped = 0

    def __init__(self, save_dir: Path, port: int) -> None:
        self.save_dir = save_dir
        self.port = port
        self.process = _DummyProcess()
        type(self).created_ports.append(port)
        self._outcome = type(self).outcomes.pop(0)

    @classmethod
    def configure(cls, *outcomes: object) -> None:
        cls.outcomes = list(outcomes)
        cls.created_ports = []
        cls.stopped = 0

    def start(self) -> None:
        pass

    def wait_for_address(self, timeout: float) -> str:
        if isinstance(self._outcome, BaseException):
            raise self._outcome
        return str(self._outcome)

    def alive(self) -> bool:
        return True

    def stop(self) -> None:
        type(self).stopped += 1


class FailureContainmentContractTests(unittest.TestCase):
    def _args(self, save_dir: Path):
        return orchestrator.parse_args(
            [
                "--port",
                "18777",
                "--save-dir",
                str(save_dir),
                "--no-browser",
                "--exit-after-ready",
                "--startup-timeout",
                "0.01",
            ]
        )

    def test_bind_race_after_free_port_probe_recovers_exactly_once(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            state_dir = root_path / "state"
            _RaceServer.configure(
                RuntimeError("[Errno 98] Address already in use"),
                "http://127.0.0.1:19077/",
            )
            with (
                patch.dict(os.environ, {"BUNKERFREQUENZ_START_STATE_DIR": str(state_dir)}, clear=False),
                patch.object(orchestrator, "ServerProcess", _RaceServer),
                patch.object(orchestrator, "_port_available", return_value=True),
                patch.object(orchestrator, "probe_http", return_value=None),
                patch.object(orchestrator, "browser_dom", return_value=None),
                patch.object(orchestrator, "_browser_command", return_value=(None, "none")),
                patch.object(orchestrator, "_ensure_start_permissions", return_value=None),
            ):
                result = orchestrator.run(self._args(root_path / "save"))
            self.assertEqual(result, 0)
            self.assertEqual(_RaceServer.created_ports, [18777, 0])
            self.assertEqual(_RaceServer.stopped, 2)
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("Address already in use", status)
            self.assertIn("einmaliger Recovery-Neustart mit freiem Port", status)

    def test_enospc_save_failure_is_fail_closed_and_classified_as_filesystem(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            state_dir = root_path / "state"
            disk_full = OSError(errno.ENOSPC, "No space left on device")
            with (
                patch.dict(os.environ, {"BUNKERFREQUENZ_START_STATE_DIR": str(state_dir)}, clear=False),
                patch.object(orchestrator, "_ensure_save_dir", side_effect=disk_full),
            ):
                result = orchestrator.run(self._args(root_path / "save"))
            self.assertEqual(result, 1)
            diagnosis = (state_dir / "START_DIAGNOSE.txt").read_text(encoding="utf-8")
            self.assertIn("FEHLERKLASSE: filesystem_permissions", diagnosis)
            self.assertIn("No space left on device", diagnosis)
            self.assertIn("JETZT BEHEBEN:", diagnosis)

    def test_dirty_worktree_is_rejected_before_source_identity_is_recorded(self):
        with patch.object(containment, "_git") as git:
            git.side_effect = [" M tools/failure_containment_pro.py"]
            with self.assertRaisesRegex(RuntimeError, "sauberen Git-Working-Tree"):
                containment.source_identity()
        git.assert_called_once_with("status", "--porcelain", "--untracked-files=all")

    def test_clean_worktree_source_identity_uses_exact_head_and_tree(self):
        with patch.object(containment, "_git") as git:
            git.side_effect = ["", "abc123", "tree456"]
            self.assertEqual(containment.source_identity(), ("abc123", "tree456"))
        self.assertEqual(
            git.call_args_list,
            [
                unittest.mock.call("status", "--porcelain", "--untracked-files=all"),
                unittest.mock.call("rev-parse", "HEAD"),
                unittest.mock.call("rev-parse", "HEAD^{tree}"),
            ],
        )

    def test_anti_flake_mismatch_can_never_be_pass(self):
        first = {name: {"status": "PASS"} for name in containment.REQUIRED_SCENARIOS}
        second = {name: {"status": "PASS"} for name in containment.REQUIRED_SCENARIOS}
        second["resource_stress"] = {"status": "FAIL"}
        self.assertEqual(containment.evaluate_runs(first, second), "FLAKY")
        self.assertEqual(containment.evaluate_runs(first, first), "PASS")
        failed = {name: {"status": "FAIL"} for name in containment.REQUIRED_SCENARIOS}
        self.assertEqual(containment.evaluate_runs(failed, failed), "FAIL")

    def test_subgate_receipt_hash_is_canonical_and_stable(self):
        payload = {"schema_version": 1, "status": "PASS", "cases": ["a", "b"]}
        first = containment._canonical_json_bytes(payload)
        second = containment._canonical_json_bytes(json.loads(first.decode("utf-8")))
        self.assertEqual(first, second)
        self.assertEqual(containment._sha256_bytes(first), containment._sha256_bytes(second))

    def test_evidence_detail_contract_avoids_volatile_pid_and_port_fields(self):
        process_detail = {"foreign_process_survived": True, "owned_processes_remaining": 0}
        port_detail = {"fail_closed": True, "diagnostic": "occupied_loopback_port_rejected"}
        payload = containment._canonical_json_bytes(
            {"process_ownership": process_detail, "port_collision": port_detail}
        ).decode("utf-8")
        self.assertNotIn("server_pid", payload)
        self.assertNotIn("occupied_port", payload)
        self.assertNotRegex(payload, r"Port \\d+")


class LegacyUpgradeRecoveryTests(unittest.TestCase):
    def test_legacy_050_state_is_read_as_current_envelope_without_data_loss(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            state_dir = root_path / "state"
            state_dir.mkdir(parents=True)
            legacy_state = {"character": {"character_id": "legacy-c", "name": "Legacy"}, "legacy_marker": True}
            (state_dir / "current.json").write_text(json.dumps(legacy_state), encoding="utf-8")
            (root_path / "save_meta.json").write_text(
                json.dumps({"schema_version": 1, "last_sequence": 0, "journal_head_hash": "GENESIS"}),
                encoding="utf-8",
            )
            kernel = PersistenceKernel(root_path, set())
            self.assertEqual(kernel.load_state(), legacy_state)
            self.assertEqual(json.loads((state_dir / "current.json").read_text(encoding="utf-8")), legacy_state)


if __name__ == "__main__":
    unittest.main()