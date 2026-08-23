import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.presentation.scene_jobs_projection import build_scene_jobs_projection


ROOT = Path(__file__).parents[2]
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
APP = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "tools" / "start_a4_game_client.py").read_text(encoding="utf-8")


class A4SceneJobsControlDeckTests(unittest.TestCase):
    def test_projection_exposes_confirmed_wallet_and_catalogued_display_consequences(self):
        finance = PlayerFinanceState(cash_cents=12_300, revision=2)
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "finance": finance.to_dict(),
        }

        projected = build_scene_jobs_projection(state, JOBS["jobs"])

        self.assertTrue(projected["available"])
        self.assertEqual(projected["cash_cents"], 12_300)
        self.assertEqual(projected["finance_revision"], 2)
        self.assertEqual(len(projected["jobs"]), 5)
        cable = next(item for item in projected["jobs"] if item["job_id"] == "scene.cable_repair")
        self.assertEqual(cable["payout_cents"], 5500)
        self.assertEqual(cable["energy_delta"], -8)
        self.assertEqual(cable["stress_delta"], 3)

    def test_legacy_state_without_finance_projects_zero_cash_without_write(self):
        state = {"character": CharacterState("char.local", "Local").to_dict()}
        original = json.loads(json.dumps(state))

        projected = build_scene_jobs_projection(state, JOBS["jobs"])

        self.assertEqual(projected["cash_cents"], 0)
        self.assertEqual(projected["ledger_entries"], 0)
        self.assertEqual(state, original)

    def test_browser_job_command_sends_only_job_id_not_payout_or_effects(self):
        start = APP.index('type: "job.run"')
        fragment = APP[start:start + 220]
        self.assertIn("job_id: job.job_id", fragment)
        self.assertNotIn("payout_cents", fragment)
        self.assertNotIn("energy_delta", fragment)
        self.assertNotIn("stress_delta", fragment)
        for marker in ("jobs-panel", "hud-cash", "jobs-list", "jobs-last-result"):
            self.assertIn(marker, APP)

    def test_launcher_uses_same_manifest_service_and_character_context(self):
        self.assertIn('"manifests/SCENE_JOB_MANIFEST.json"', LAUNCHER)
        self.assertIn('self.scene_job_manifest = _load_json', LAUNCHER)
        self.assertIn('scene_job_manifest=self.scene_job_manifest', LAUNCHER)
        self.assertIn('build_scene_jobs_projection(', LAUNCHER)
        self.assertIn('{"profile.update", "street.walk", "job.run"}', LAUNCHER)


if __name__ == "__main__":
    unittest.main()
