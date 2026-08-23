import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.assistant_control_service import AssistantControlService
from bunkerfrequenz.application.game_recovery import replay_game_event
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T19:30:00+02:00",
        "session-assistant-control",
        "player-local",
        "character",
        "char.local",
        command_id,
        "assistant-control-test",
        "0.8.8-c2",
        "char.local",
    )


class AssistantControlServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        character = CharacterState(character_id="char.local", display_name="Local")
        self.initial = {"character": character.to_dict()}
        self.kernel.initialize_state(self.initial)
        self.service = AssistantControlService(self.kernel, JOBS)

    def test_start_switch_and_stop_persist_exactly_one_job_choice(self):
        start = self.service.set_active_job("scene.flyer_shift", context=context("assistant-start"))
        switch = self.service.set_active_job("scene.cable_repair", context=context("assistant-switch"))
        stop = self.service.set_active_job(None, context=context("assistant-stop"))

        self.assertTrue(start.changed)
        self.assertEqual(start.assistant.active_job_id, "scene.flyer_shift")
        self.assertEqual(switch.assistant.active_job_id, "scene.cable_repair")
        self.assertIsNone(stop.assistant.active_job_id)
        self.assertEqual(stop.assistant.revision, 3)
        self.assertEqual(
            [record["event_type"] for record in self.kernel.read_records()],
            ["assistant.control_changed"] * 3,
        )
        state = self.kernel.load_state()
        self.assertEqual(state["character"], self.initial["character"])
        self.assertNotIn("finance", state)

    def test_unknown_job_and_wrong_character_fail_before_write(self):
        with self.assertRaisesRegex(ValueError, "Unbekannter Scene Job"):
            self.service.set_active_job("scene.fake", context=context("assistant-fake"))
        wrong = JournalContext(
            "2026-08-23T19:30:00+02:00", "session-assistant-control", "player-local",
            "character", "char.other", "assistant-wrong", "assistant-control-test", "0.8.8-c2", "char.other",
        )
        with self.assertRaisesRegex(ValueError, "passt nicht"):
            self.service.set_active_job("scene.flyer_shift", context=wrong)
        self.assertEqual(self.kernel.read_records(), [])

    def test_retry_is_idempotent_and_command_id_cannot_change_meaning(self):
        first = self.service.set_active_job("scene.load_in_help", context=context("assistant-retry"))
        records = self.kernel.read_records()
        retry = self.service.set_active_job("scene.load_in_help", context=context("assistant-retry"))
        self.assertTrue(first.changed)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(self.kernel.read_records(), records)
        with self.assertRaises(PersistenceError):
            self.service.set_active_job("scene.bar_support", context=context("assistant-retry"))

    def test_same_selection_is_write_free_and_recovery_reconstructs_control_state(self):
        self.service.set_active_job("scene.night_cleanup", context=context("assistant-one"))
        records = self.kernel.read_records()
        noop = self.service.set_active_job("scene.night_cleanup", context=context("assistant-two"))
        self.assertFalse(noop.changed)
        self.assertEqual(self.kernel.read_records(), records)

        recovered = dict(self.initial)
        for record in records:
            recovered = replay_game_event(recovered, record)
        self.assertEqual(recovered["assistant"], self.kernel.load_state()["assistant"])


if __name__ == "__main__":
    unittest.main()
