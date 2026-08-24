from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from start_orchestrator import _ensure_save_dir, _port_available  # noqa: E402

ORCHESTRATOR = ROOT / "tools" / "start_orchestrator.py"
START = ROOT / "START_BUNKERFREQUENZ.sh"


class StartOrchestratorTests(unittest.TestCase):
    def test_dependency_resolution_creates_and_probes_save_dir(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "nested" / "save"
            resolved = _ensure_save_dir(target)
            self.assertEqual(resolved, target.resolve())
            self.assertTrue(resolved.is_dir())

    def test_port_probe_detects_occupied_port_and_accepts_auto_port(self):
        self.assertTrue(_port_available(0))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as blocker:
            blocker.bind(("127.0.0.1", 0))
            blocker.listen(1)
            port = blocker.getsockname()[1]
            self.assertFalse(_port_available(port))

    def test_help_is_informational_and_does_not_write_diagnosis(self):
        with tempfile.TemporaryDirectory() as state_dir:
            env = os.environ.copy()
            env["BUNKERFREQUENZ_START_STATE_DIR"] = state_dir
            completed = subprocess.run(
                [str(START), "--help"],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=8,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("vollautomatisch prüfen und lokal starten", completed.stdout)
            self.assertFalse((Path(state_dir) / "START_DIAGNOSE.txt").exists())

    def test_exit_after_ready_runs_full_orchestration_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            state_dir = root_path / "status"
            save_dir = root_path / "save"
            env = os.environ.copy()
            env["BUNKERFREQUENZ_START_STATE_DIR"] = str(state_dir)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ORCHESTRATOR),
                    "--port",
                    "0",
                    "--no-browser",
                    "--save-dir",
                    str(save_dir),
                    "--exit-after-ready",
                    "--startup-timeout",
                    "12",
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=35,
            )
            output = completed.stdout + completed.stderr
            self.assertEqual(completed.returncode, 0, output)
            self.assertIn("[100%]", output)
            self.assertIn("BEREIT", output)
            self.assertIn("API-PRÜFUNG", output)
            self.assertIn("NACHVALIDIERUNG", output)
            status = (state_dir / "START_STATUS.txt").read_text(encoding="utf-8")
            self.assertIn("[100%]", status)
            self.assertIn("BEREIT", status)
            self.assertFalse((state_dir / "START_DIAGNOSE.txt").exists())


if __name__ == "__main__":
    unittest.main()
