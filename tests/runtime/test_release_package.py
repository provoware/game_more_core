import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.request import Request, urlopen
import zipfile

from tools.build_release import build


ROOT = Path(__file__).parents[2]


def _post(base: str, path: str, payload: dict) -> dict:
    request = Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


class ReleasePackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

    def test_release_zip_is_reproducible_and_runs_after_unpack(self):
        zip_a, sha_a, summary_a = build(self.tmp_path / "a")
        zip_b, sha_b, summary_b = build(self.tmp_path / "b")
        self.assertEqual(zip_a.read_bytes(), zip_b.read_bytes())
        self.assertEqual(sha_a.read_text(encoding="utf-8"), sha_b.read_text(encoding="utf-8"))
        self.assertEqual(summary_a["sha256"], hashlib.sha256(zip_a.read_bytes()).hexdigest())
        self.assertEqual(summary_a, summary_b)

        version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))["version"]
        package_root = f"BUNKERFREQUENZ-{version}"
        with zipfile.ZipFile(zip_a) as archive:
            names = archive.namelist()
            self.assertTrue(all(name.startswith(package_root + "/") for name in names))
            self.assertNotIn(package_root + "/.git", names)
            self.assertFalse(any("/.github/" in name for name in names))
            self.assertFalse(any("/tests/" in name for name in names))
            self.assertIn(package_root + "/START_BUNKERFREQUENZ.sh", names)
            self.assertIn(package_root + "/RELEASE_INFO.json", names)
            info = json.loads(archive.read(package_root + "/RELEASE_INFO.json"))
            self.assertEqual(info["version"], version)
            expected_head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
            ).stdout.strip()
            self.assertEqual(info["source_commit"], expected_head)
            launcher_info = archive.getinfo(package_root + "/START_BUNKERFREQUENZ.sh")
            self.assertTrue((launcher_info.external_attr >> 16) & 0o100)
            archive.extractall(self.tmp_path / "unpacked")

        extracted = self.tmp_path / "unpacked" / package_root
        launcher = extracted / "START_BUNKERFREQUENZ.sh"
        launcher.chmod(0o755)
        save_dir = self.tmp_path / "package-save"
        process = subprocess.Popen(
            [str(launcher), "--port", "0", "--no-browser", "--save-dir", str(save_dir)],
            cwd=extracted,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.addCleanup(lambda: process.poll() is None and process.kill())
        self.assertIsNotNone(process.stdout)
        address = None
        output = []
        for _ in range(10):
            line = process.stdout.readline()
            if not line:
                break
            output.append(line.rstrip())
            if line.startswith("ADRESSE: "):
                address = line.split("ADRESSE: ", 1)[1].strip().rstrip("/")
                break
        self.assertIsNotNone(address, "Paketstart lieferte keine Adresse: " + " | ".join(output))
        with urlopen(address + "/api/health", timeout=3) as response:
            health = json.loads(response.read().decode("utf-8"))
        self.assertEqual(health["status"], "ready")

        first = _post(address, "/api/new-game", {
            "command_id": "package:first-run",
            "character_name": "Package Crew",
            "event_name": "Package Event",
        })
        self.assertEqual(first["status"], "confirmed", first)
        commands = (
            {"type": "event.execute", "command_id": "package:planning", "action_id": "begin_planning"},
            {"type": "event.execute", "command_id": "package:procurement", "action_id": "begin_procurement"},
            {"type": "economy.transact", "command_id": "package:buy", "kind": "buy", "item_id": "equipment.pa", "quantity": 1},
            {"type": "economy.transact", "command_id": "package:reserve", "kind": "reserve", "item_id": "equipment.pa", "quantity": 1},
            {"type": "event.execute", "command_id": "package:transport", "action_id": "start_transport"},
            {"type": "event.execute", "command_id": "package:setup", "action_id": "begin_setup"},
            {"type": "event.execute", "command_id": "package:soundcheck", "action_id": "confirm_soundcheck"},
            {"type": "event.execute", "command_id": "package:live", "action_id": "start_live"},
            {"type": "event.execute", "command_id": "package:finish-live", "action_id": "finish_live"},
            {"type": "event.execute", "command_id": "package:teardown", "action_id": "finish_teardown"},
            {"type": "settlement.complete", "command_id": "package:settlement"},
        )
        result = first
        for command in commands:
            result = _post(address, "/api/command", command)
            self.assertEqual(result["status"], "confirmed", (command, result))
        self.assertEqual(result["state"]["event"]["phase"], "completed")
        checkpoint = _post(address, "/api/checkpoint", {})
        self.assertEqual(checkpoint["status"], "confirmed")

        process.terminate()
        process.wait(timeout=3)
        if process.stdout is not None:
            process.stdout.close()


if __name__ == "__main__":
    unittest.main()
