"""Check map redraw keyboard focus using the actual JavaScript renderer."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tests" / "presentation" / "map_focus_refresh_harness.cjs"


class MapFocusRefreshTests(unittest.TestCase):
    def test_keyboard_focus_survives_map_refresh(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node.js is required for the map focus gate")
        result = subprocess.run(
            [node, str(HARNESS)], cwd=ROOT, text=True,
            capture_output=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: 10/10 PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
