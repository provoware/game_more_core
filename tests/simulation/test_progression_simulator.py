import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM_PATH = ROOT / "tools" / "simulate_characters" / "progression_simulator.py"
SPEC = importlib.util.spec_from_file_location("progression_simulator", SIM_PATH)
SIM = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SIM)


class ProgressionSimulatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = json.loads((ROOT / "manifests" / "TRAIT_ENGINE_MANIFEST.json").read_text(encoding="utf-8"))
        cls.progression = json.loads((ROOT / "manifests" / "PROGRESSION_MANIFEST.json").read_text(encoding="utf-8"))

    def test_manifest_invariants(self):
        self.assertEqual([], SIM.validate_manifests(self.engine, self.progression))

    def test_deterministic_small_run(self):
        first = SIM.run_simulation(70, 180, 90409, self.engine, self.progression)
        second = SIM.run_simulation(70, 180, 90409, self.engine, self.progression)
        self.assertEqual(first, second)

    def test_full_balance_gate(self):
        report = SIM.run_simulation(350, 720, 90409, self.engine, self.progression)
        self.assertTrue(report["passed"], report)


if __name__ == "__main__":
    unittest.main()
