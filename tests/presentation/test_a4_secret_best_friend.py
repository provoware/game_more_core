import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.assistant import AssistantState
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.assistant_projection import build_assistant_projection


ROOT = Path(__file__).parents[2]
ASSISTANT = json.loads((ROOT / "manifests" / "ASSISTANT_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
UI = (ROOT / "web" / "a4" / "assistant_ui.js").read_text(encoding="utf-8")
TIMELINE = (ROOT / "web" / "a4" / "event_timeline.js").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "tools" / "start_a4_game_client.py").read_text(encoding="utf-8")


class A4SecretBestFriendTests(unittest.TestCase):
    def test_projection_is_legacy_safe_and_resolves_active_task_from_scene_jobs(self):
        legacy = {"character": CharacterState("char.local", "Local").to_dict()}
        inactive = build_assistant_projection(legacy, manifest=ASSISTANT, scene_jobs=JOBS["jobs"])
        self.assertTrue(inactive["available"])
        self.assertIsNone(inactive["active_task_id"])
        self.assertEqual(inactive["completed_rounds"], 0)

        active_state = dict(legacy)
        active_state["assistant"] = AssistantState(
            active_task_id="scene.cable_repair",
            last_completed_round_id="street-7",
            completed_rounds=3,
            revision=5,
        ).to_dict()
        active = build_assistant_projection(active_state, manifest=ASSISTANT, scene_jobs=JOBS["jobs"])
        self.assertEqual(active["active_task"]["job_id"], "scene.cable_repair")
        self.assertEqual(active["active_task"]["label"], "Kabel & Kleinkram reparieren")
        self.assertEqual(active["trigger_label"], "nach jeder bestätigten Straßenrunde")

    def test_browser_assigns_only_task_id_and_deactivate_has_no_effect_fields(self):
        assign = UI[UI.index('type: "assistant.assign"'):]
        assign = assign[:assign.index("});", assign.index('task_id: job.job_id')) + 3]
        self.assertIn("task_id: job.job_id", assign)
        self.assertNotIn("payout_cents", assign)
        self.assertNotIn("energy_delta", assign)
        self.assertNotIn("round_id", assign)

        stop = UI[UI.index('type: "assistant.deactivate"'):]
        stop = stop[:stop.index("});") + 3]
        self.assertNotIn("task_id", stop)
        self.assertNotIn("payout", stop)
        self.assertNotIn("effect", stop)

    def test_assistant_reuses_jobs_panel_and_existing_state_refresh(self):
        self.assertIn('document.getElementById("jobs-panel")', UI)
        self.assertIn('document.getElementById("jobs-list")', UI)
        self.assertNotIn('id = "assistant-panel"', UI)
        self.assertNotIn('fetch("/api/state"', UI)
        self.assertIn("window.BunkerAssistantUI?.render(gameState)", TIMELINE)
        self.assertIn('script.src = "assistant_ui.js"', TIMELINE)

    def test_launcher_loads_same_assistant_and_scene_job_contracts(self):
        self.assertIn('"manifests/ASSISTANT_MANIFEST.json"', LAUNCHER)
        self.assertIn('self.assistant_manifest = _load_json', LAUNCHER)
        self.assertIn('assistant_manifest=self.assistant_manifest', LAUNCHER)
        self.assertIn('build_assistant_projection(', LAUNCHER)
        self.assertIn('"assistant.assign", "assistant.deactivate"', LAUNCHER)


if __name__ == "__main__":
    unittest.main()
