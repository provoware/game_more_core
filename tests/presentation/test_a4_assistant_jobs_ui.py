import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.scene_jobs_projection import build_scene_jobs_projection


ROOT = Path(__file__).parents[2]
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
ASSISTANT_UI = (ROOT / "web" / "a4" / "assistant_jobs_ui.js").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "tools" / "start_a4_game_client.py").read_text(encoding="utf-8")


class A4AssistantJobsUiTests(unittest.TestCase):
    def test_projection_exposes_confirmed_control_state_and_catalog_label(self):
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "assistant": {"active_job_id": "scene.cable_repair", "revision": 4},
        }

        projection = build_scene_jobs_projection(state, JOBS["jobs"])

        self.assertTrue(projection["assistant"]["enabled"])
        self.assertEqual(projection["assistant"]["active_job_id"], "scene.cable_repair")
        self.assertEqual(projection["assistant"]["active_job_label"], "Kabel & Kleinkram reparieren")
        self.assertEqual(projection["assistant"]["revision"], 4)

    def test_projection_fails_closed_if_saved_assistant_job_is_not_in_catalog(self):
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "assistant": {"active_job_id": "scene.removed", "revision": 1},
        }
        with self.assertRaisesRegex(ValueError, "unbekannten Scene Job"):
            build_scene_jobs_projection(state, JOBS["jobs"])

    def test_ui_reuses_jobs_panel_and_sends_only_control_job_id(self):
        self.assertIn('src="assistant_jobs_ui.js"', INDEX)
        self.assertLess(INDEX.index('src="app.js"'), INDEX.index('src="assistant_jobs_ui.js"'))
        self.assertIn('document.getElementById("jobs-list")', ASSISTANT_UI)
        self.assertIn('control.id = "jobs-assistant-control"', ASSISTANT_UI)
        self.assertNotIn('assistant-panel', ASSISTANT_UI)

        start = ASSISTANT_UI.index('type: "assistant.control"')
        fragment = ASSISTANT_UI[start:start + 180]
        self.assertIn("job_id: jobId", fragment)
        self.assertNotIn("payout_cents", fragment)
        self.assertNotIn("energy_delta", fragment)
        self.assertNotIn("stress_delta", fragment)
        self.assertNotIn("round", fragment.lower())

    def test_ui_explains_round_authority_and_launcher_routes_control_as_character_command(self):
        self.assertIn("intern bestätigten Spielrunde", ASSISTANT_UI)
        self.assertIn("Browser und Rechnerzeit starten keine Runde", ASSISTANT_UI)
        self.assertIn("FREUND STARTEN", ASSISTANT_UI)
        self.assertIn("FREUND WECHSELN", ASSISTANT_UI)
        self.assertIn("FREUND STOPPEN", ASSISTANT_UI)
        self.assertIn("AssistantGameClientSession", LAUNCHER)
        self.assertIn('"assistant.control"', LAUNCHER)
        self.assertIn('"web/a4/assistant_jobs_ui.js"', LAUNCHER)


if __name__ == "__main__":
    unittest.main()
