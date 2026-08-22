import json
from pathlib import Path
import socket
import stat
import subprocess
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tools.start_a4_game_client import A4ClientRuntime, create_server, parse_args, preflight


ROOT = Path(__file__).parents[2]


def _json_get(url: str) -> dict:
    with urlopen(url, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def _json_post(base: str, path: str, payload: dict, *, origin: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if origin is not None:
        headers["Origin"] = origin
    request = Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


class _ServerHarness:
    def __init__(self, runtime: A4ClientRuntime):
        self.server = create_server(0, runtime)
        self.port = int(self.server.server_address[1])
        self.base = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)


class A4ReleaseAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

    def test_fresh_http_first_run_full_loop_restart_and_recovery(self):
        save_dir = self.tmp_path / "fresh-save"
        runtime = A4ClientRuntime(save_dir)
        http = _ServerHarness(runtime)
        self.addCleanup(http.close)

        health = _json_get(http.base + "/api/health")
        self.assertEqual(health["status"], "ready")
        self.assertIsNone(health["startup_recovery"])

        with urlopen(http.base + "/", timeout=3) as response:
            html = response.read().decode("utf-8")
        self.assertIn("BUNKERFREQUENZ", html)

        # Static serving is rooted in web/a4 and must not expose repository files.
        with self.assertRaises(HTTPError) as escaped:
            urlopen(http.base + "/../README.md", timeout=3)
        self.assertEqual(escaped.exception.code, 404)

        # A foreign browser Origin must never be allowed to create a save.
        with self.assertRaises(HTTPError) as forbidden:
            _json_post(
                http.base,
                "/api/new-game",
                {"command_id": "release:foreign", "character_name": "X", "event_name": "Y"},
                origin="https://example.invalid",
            )
        self.assertEqual(forbidden.exception.code, 403)
        self.assertEqual(runtime.session.read_state(), {})

        first = _json_post(
            http.base,
            "/api/new-game",
            {
                "command_id": "release:first-run",
                "character_name": "Release Crew",
                "event_name": "Release Event",
            },
        )
        self.assertEqual(first["status"], "confirmed", first)

        commands = (
            {"type": "event.execute", "command_id": "release:planning", "action_id": "begin_planning"},
            {"type": "event.execute", "command_id": "release:procurement", "action_id": "begin_procurement"},
            {
                "type": "economy.transact",
                "command_id": "release:buy",
                "kind": "buy",
                "item_id": "equipment.pa",
                "quantity": 1,
            },
            {
                "type": "economy.transact",
                "command_id": "release:reserve",
                "kind": "reserve",
                "item_id": "equipment.pa",
                "quantity": 1,
            },
            {"type": "event.execute", "command_id": "release:transport", "action_id": "start_transport"},
            {"type": "event.execute", "command_id": "release:setup", "action_id": "begin_setup"},
            {"type": "event.execute", "command_id": "release:soundcheck", "action_id": "confirm_soundcheck"},
            {"type": "event.execute", "command_id": "release:live", "action_id": "start_live"},
            {
                "type": "incident.open",
                "command_id": "release:incident-open",
                "incident_type": "power_drop",
                "severity": 3,
            },
            {
                "type": "incident.resolve",
                "command_id": "release:incident-resolve",
                "response_id": "power_drop.generator",
            },
            {"type": "event.execute", "command_id": "release:finish-live", "action_id": "finish_live"},
            {
                "type": "event.execute",
                "command_id": "release:finish-teardown",
                "action_id": "finish_teardown",
            },
            {"type": "settlement.complete", "command_id": "release:settlement"},
        )
        for command in commands:
            result = _json_post(http.base, "/api/command", command)
            self.assertEqual(result["status"], "confirmed", (command, result))

        checkpoint = _json_post(http.base, "/api/checkpoint", {})
        self.assertEqual(checkpoint["status"], "confirmed")
        expected = _json_get(http.base + "/api/state")["state"]
        self.assertEqual(expected["event"]["phase"], "completed")
        http.close()

        restarted = A4ClientRuntime(save_dir)
        self.assertIsNone(restarted.startup_recovery)
        self.assertEqual(restarted.projection(), expected)

        restarted.kernel.state_path.unlink()
        recovered = A4ClientRuntime(save_dir)
        self.assertIsNotNone(recovered.startup_recovery)
        self.assertEqual(recovered.startup_recovery.status, "recovered")
        self.assertEqual(recovered.projection(), expected)

        final_restart = A4ClientRuntime(save_dir)
        self.assertIsNone(final_restart.startup_recovery)
        self.assertEqual(final_restart.projection(), expected)

    def test_release_start_failures_are_clear_and_port_zero_is_supported(self):
        args = parse_args([
            "--port",
            "0",
            "--no-browser",
            "--save-dir",
            str(self.tmp_path / "save"),
        ])
        self.assertEqual(args.port, 0)
        self.assertTrue(args.no_browser)

        with self.assertRaisesRegex(SystemExit, "START FEHLGESCHLAGEN.*fehlt"):
            preflight(self.tmp_path / "empty-checkout")

        unusable_parent = self.tmp_path / "not-a-directory"
        unusable_parent.write_text("file", encoding="utf-8")
        with self.assertRaisesRegex(SystemExit, "Spielstandordner ist nicht beschreibbar"):
            A4ClientRuntime(unusable_parent / "save")

        runtime = A4ClientRuntime(self.tmp_path / "port-test-save")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            port = int(occupied.getsockname()[1])
            with self.assertRaisesRegex(SystemExit, rf"Port {port} ist belegt.*--port 0"):
                create_server(port, runtime)

    def test_clickstart_script_is_executable_and_launches_real_server(self):
        launcher = ROOT / "START_BUNKERFREQUENZ.sh"
        self.assertTrue(launcher.is_file())
        self.assertTrue(launcher.stat().st_mode & stat.S_IXUSR, "Klickstart-Script ist nicht ausführbar")

        save_dir = self.tmp_path / "process-save"
        process = subprocess.Popen(
            [
                str(launcher),
                "--port",
                "0",
                "--no-browser",
                "--save-dir",
                str(save_dir),
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.assertIsNotNone(process.stdout)

        address = None
        output = []
        for _ in range(8):
            line = process.stdout.readline()
            if not line:
                break
            output.append(line.rstrip())
            if line.startswith("ADRESSE: "):
                address = line.split("ADRESSE: ", 1)[1].strip().rstrip("/")
                break
        self.assertIsNotNone(address, "Launcher lieferte keine Adresse: " + " | ".join(output))
        health = _json_get(address + "/api/health")
        self.assertEqual(health["status"], "ready")

        process.terminate()
        process.wait(timeout=3)
        self.assertIsNotNone(process.returncode)


if __name__ == "__main__":
    unittest.main()
