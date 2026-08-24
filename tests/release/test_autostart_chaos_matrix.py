from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import start_orchestrator as orchestrator  # noqa: E402


class _DummyProcess:
    def wait(self) -> int:
        return 0


class _FakeServer:
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


class AutostartChaosMatrixTests(unittest.TestCase):
    @contextmanager
    def _state(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            state_dir = root_path / "status"
            save_dir = root_path / "save"
            with patch.dict(
                os.environ,
                {"BUNKERFREQUENZ_START_STATE_DIR": str(state_dir)},
                clear=False,
            ):
                yield state_dir, save_dir

    def _args(self, save_dir: Path, *, port: int = 8044, no_browser: bool = True):
        argv = [
            "--port",
            str(port),
            "--save-dir",
            str(save_dir),
            "--exit-after-ready",
            "--startup-timeout",
            "0.01",
        ]
        if no_browser:
            argv.append("--no-browser")
        return orchestrator.parse_args(argv)

    def _run_ready(self, args, *, browser_dom=object(), browser_command=(None, "none"), probe=None):
        if probe is None:
            probe = lambda address: None
        with (
            patch.object(orchestrator, "ServerProcess", _FakeServer),
            patch.object(orchestrator, "probe_http", side_effect=probe),
            patch.object(orchestrator, "browser_dom", return_value=browser_dom),
            patch.object(orchestrator, "_browser_command", return_value=browser_command),
            patch.object(orchestrator, "_ensure_start_permissions", return_value=None),
        ):
            return orchestrator.run(args)

    def test_occupied_port_is_auto_resolved_to_free_port_strategy(self):
        with self._state() as (state_dir, save_dir):
            _FakeServer.configure("http://127.0.0.1:19001/")
            args = self._args(save_dir, port=8044)
            with patch.object(orchestrator, "_port_available", return_value=False):
                result = self._run_ready(args)
            self.assertEqual(result, 0)
            self.assertEqual(_FakeServer.created_ports, [0])
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("Port 8044 war belegt", status)
            self.assertIn("automatisch gelöst", status)

    def test_read_only_save_path_fails_closed_with_permission_diagnosis(self):
        with self._state() as (state_dir, save_dir):
            args = self._args(save_dir)
            with patch.object(
                orchestrator,
                "_ensure_save_dir",
                side_effect=PermissionError("read-only test directory"),
            ):
                result = orchestrator.run(args)
            self.assertEqual(result, 1)
            diagnosis = (state_dir / "START_DIAGNOSE.txt").read_text(encoding="utf-8")
            self.assertIn("FEHLERKLASSE: filesystem_permissions", diagnosis)
            self.assertIn("JETZT BEHEBEN:", diagnosis)
            self.assertIn("read-only test directory", diagnosis)

    def test_missing_browser_is_yellow_not_false_red(self):
        with self._state() as (state_dir, save_dir):
            _FakeServer.configure("http://127.0.0.1:19002/")
            args = self._args(save_dir, no_browser=False)
            result = self._run_ready(
                args,
                browser_dom=None,
                browser_command=(None, "kein unterstützter Browserstarter"),
            )
            self.assertEqual(result, 0)
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("Kein unterstützter Browserstarter gefunden", status)
            self.assertIn("🟡 BEREIT", status)
            self.assertFalse((state_dir / "START_DIAGNOSE.txt").exists())

    def test_slow_first_server_attempt_times_out_then_recovers_once(self):
        with self._state() as (state_dir, save_dir):
            _FakeServer.configure(
                TimeoutError("Server lieferte innerhalb von 1s keine Adresse"),
                "http://127.0.0.1:19003/",
            )
            args = self._args(save_dir, port=8044)
            with patch.object(orchestrator, "_port_available", return_value=True):
                result = self._run_ready(args)
            self.assertEqual(result, 0)
            self.assertEqual(_FakeServer.created_ports, [8044, 0])
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("Recovery-Neustart mit automatisch freiem Port", status)

    def test_delayed_api_is_retried_and_then_post_validated(self):
        with self._state() as (state_dir, save_dir):
            _FakeServer.configure("http://127.0.0.1:19004/")
            args = self._args(save_dir)
            calls = iter((TimeoutError("API warming up"), None, None))

            def delayed_probe(address: str):
                outcome = next(calls)
                if isinstance(outcome, BaseException):
                    raise outcome
                return outcome

            with patch.object(orchestrator.time, "sleep", return_value=None):
                result = self._run_ready(args, probe=delayed_probe)
            self.assertEqual(result, 0)
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("API war noch nicht bereit", status)
            self.assertIn("NACHVALIDIERUNG", status)
            self.assertIn("[100%]", status)

    def test_aborted_first_start_recovers_on_exactly_one_second_attempt(self):
        with self._state() as (state_dir, save_dir):
            _FakeServer.configure(
                RuntimeError("Server wurde vor Bereitschaft beendet: injected abort"),
                "http://127.0.0.1:19005/",
            )
            args = self._args(save_dir)
            result = self._run_ready(args)
            self.assertEqual(result, 0)
            self.assertEqual(len(_FakeServer.created_ports), 2)
            self.assertGreaterEqual(_FakeServer.stopped, 2)
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("injected abort", status)
            self.assertIn("Versuch 2/2", status)

    def test_post_handoff_api_failure_triggers_controlled_server_recovery(self):
        with self._state() as (state_dir, save_dir):
            _FakeServer.configure(
                "http://127.0.0.1:19006/",
                "http://127.0.0.1:19007/",
            )
            args = self._args(save_dir)
            calls = iter((None, RuntimeError("post-handoff API lost"), None))

            def probe(address: str):
                outcome = next(calls)
                if isinstance(outcome, BaseException):
                    raise outcome
                return outcome

            with patch.object(orchestrator, "_port_available", return_value=True):
                result = self._run_ready(args, probe=probe)
            self.assertEqual(result, 0)
            self.assertEqual(_FakeServer.created_ports, [8044, 0])
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("Nachvalidierung erkannte einen Server-/API-Ausfall", status)
            self.assertIn("Server-/API-Recovery erfolgreich", status)


if __name__ == "__main__":
    unittest.main()