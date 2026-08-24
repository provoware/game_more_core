from __future__ import annotations

import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen

from tools.start_a4_acceptance import _wait_for_address as acceptance_wait_for_address

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "tools" / "start_a4_game_client.py"


def _start(*args: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, "-u", str(LAUNCHER), *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def _wait_for_address(process: subprocess.Popen[str], timeout: float = 8.0) -> str:
    assert process.stdout is not None
    deadline = time.monotonic() + timeout
    lines: list[str] = []
    while time.monotonic() < deadline:
        line = process.stdout.readline()
        if line:
            lines.append(line.rstrip())
            if line.startswith("ADRESSE: "):
                return line.split("ADRESSE: ", 1)[1].strip()
        elif process.poll() is not None:
            break
    raise AssertionError("Launcher lieferte keine Adresse: " + " | ".join(lines))


class A4ReleaseAcceptanceTests(unittest.TestCase):
    def test_fresh_checkout_launcher_port_zero_health_state_and_clean_stop(self):
        with tempfile.TemporaryDirectory() as save_dir:
            process = _start("--port", "0", "--no-browser", "--save-dir", save_dir)
            try:
                address = _wait_for_address(process)
                with urlopen(address + "api/health", timeout=3) as response:
                    payload = json.load(response)
                self.assertEqual(payload["status"], "ready")
                self.assertEqual(Path(payload["save_dir"]).resolve(), Path(save_dir).resolve())
                self.assertIsNone(payload["startup_recovery"])

                with urlopen(address + "api/state", timeout=3) as response:
                    state_payload = json.load(response)
                self.assertEqual(state_payload["status"], "confirmed")
                self.assertIsInstance(state_payload["state"], dict)
                self.assertIn("scene_jobs", state_payload["state"])
                self.assertIn("event_timeline", state_payload["state"])
            finally:
                process.terminate()
                process.wait(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()
            self.assertIsNotNone(process.returncode)

    def test_acceptance_address_wait_times_out_for_silent_live_process(self):
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", "import time; time.sleep(2)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        started = time.monotonic()
        try:
            with self.assertRaisesRegex(RuntimeError, "Launcher lieferte keine Adresse"):
                acceptance_wait_for_address(process, timeout=0.2)
            self.assertLess(time.monotonic() - started, 1.0)
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=3)
            if process.stdout is not None:
                process.stdout.close()

    def test_occupied_port_has_beginner_friendly_error(self):
        with socket.socket() as blocker, tempfile.TemporaryDirectory() as save_dir:
            blocker.bind(("127.0.0.1", 0))
            blocker.listen(1)
            port = blocker.getsockname()[1]
            completed = subprocess.run(
                [sys.executable, str(LAUNCHER), "--port", str(port), "--no-browser", "--save-dir", save_dir],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=8,
            )
        output = completed.stdout + completed.stderr
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("START FEHLGESCHLAGEN", output)
        self.assertIn("Port", output)
        self.assertIn("--port 0", output)

    def test_unusable_save_path_fails_before_gameplay_write(self):
        with tempfile.TemporaryDirectory() as root:
            not_a_dir = Path(root) / "save-file"
            not_a_dir.write_text("kein Ordner", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(LAUNCHER), "--port", "0", "--no-browser", "--save-dir", str(not_a_dir)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=8,
            )
        output = completed.stdout + completed.stderr
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("START FEHLGESCHLAGEN", output)
        self.assertIn("Spielstandordner ist nicht beschreibbar", output)

    def test_missing_required_file_is_reported_explicitly(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import start_a4_game_client as launcher

        with tempfile.TemporaryDirectory() as root:
            fake = Path(root)
            with self.assertRaises(SystemExit) as raised:
                launcher.preflight(fake)
        message = str(raised.exception)
        self.assertIn("START FEHLGESCHLAGEN", message)
        self.assertIn("web/a4/index.html", message)
        self.assertIn("manifests/JOURNAL_MANIFEST.json", message)


if __name__ == "__main__":
    unittest.main()
