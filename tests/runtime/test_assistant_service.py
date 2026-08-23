import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.assistant_service import AssistantService
from bunkerfrequenz.application.game_recovery import replay_game_event
from bunkerfrequenz.application.scene_job_service import SceneJobService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
ASSISTANT = json.loads((ROOT / "manifests" / "ASSISTANT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T19:00:00+02:00",
        "session-assistant",
        "player-local",
        "character",
        "char.local",
        command_id,
        "assistant-test",
        "0.8.8-c1",
        "char.local",
    )


class AssistantServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.character = CharacterState(character_id="char.local", display_name="Local")
        self.kernel.initialize_state({"character": self.character.to_dict()})
        self.jobs = SceneJobService(self.kernel, JOBS)
        self.service = AssistantService(self.kernel, self.jobs, ASSISTANT)

    def test_assigns_exactly_one_existing_scene_job_and_can_switch(self):
        first = self.service.assign("scene.flyer_shift", context=context("assist-a"))
        second = self.service.assign("scene.cable_repair", context=context("assist-b"))

        self.assertEqual(first.assistant.active_task_id, "scene.flyer_shift")
        self.assertEqual(second.assistant.active_task_id, "scene.cable_repair")
        self.assertEqual(second.assistant.revision, 2)
        self.assertEqual(
            [record["event_type"] for record in self.kernel.read_records()],
            ["assistant.task_assigned", "assistant.task_assigned"],
        )

    def test_confirmed_round_runs_active_job_once_and_retry_cannot_double_pay(self):
        self.service.assign("scene.flyer_shift", context=context("assist-assign"))
        first = self.service.run_confirmed_round("street-round-1", context=context("assist-round-1"))
        records = self.kernel.read_records()
        retry = self.service.run_confirmed_round("street-round-1", context=context("assist-round-1-retry"))

        self.assertTrue(first.executed)
        self.assertEqual(first.assistant.completed_rounds, 1)
        self.assertEqual(first.assistant.last_completed_round_id, "street-round-1")
        self.assertFalse(retry.executed)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(self.kernel.read_records(), records)
        self.assertEqual(self.kernel.load_state()["finance"]["cash_cents"], 3500)
        self.assertEqual(self.kernel.load_state()["character"]["energy"], 94)

    def test_deactivate_stops_future_round_execution(self):
        self.service.assign("scene.load_in_help", context=context("assist-assign"))
        self.service.deactivate(context=context("assist-stop"))
        before = self.kernel.read_records()
        result = self.service.run_confirmed_round("street-round-2", context=context("assist-round-2"))

        self.assertFalse(result.executed)
        self.assertIsNone(result.assistant.active_task_id)
        self.assertEqual(self.kernel.read_records(), before)
        self.assertNotIn("finance", self.kernel.load_state())

    def test_unknown_task_fails_before_write_and_recovery_restores_assistant(self):
        before = self.kernel.read_records()
        with self.assertRaisesRegex(ValueError, "katalogisierte Scene Jobs"):
            self.service.assign("scene.fake", context=context("assist-fake"))
        self.assertEqual(self.kernel.read_records(), before)

        self.service.assign("scene.night_cleanup", context=context("assist-real"))
        self.service.run_confirmed_round("street-round-3", context=context("assist-round-3"))
        replayed = {"character": self.character.to_dict()}
        for record in self.kernel.read_records():
            replayed = replay_game_event(replayed, record)

        current = self.kernel.load_state()
        self.assertEqual(replayed["assistant"], current["assistant"])
        self.assertEqual(replayed["finance"], current["finance"])
        self.assertEqual(replayed["character"], current["character"])


if __name__ == "__main__":
    unittest.main()
