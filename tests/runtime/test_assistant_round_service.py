import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.assistant_control_service import AssistantControlService
from bunkerfrequenz.application.assistant_round_service import (
    AssistantRoundExecutionService,
    ConfirmedRoundTrigger,
)
from bunkerfrequenz.application.scene_job_service import SceneJobService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, *, source: str = "confirmed-round-test") -> JournalContext:
    return JournalContext(
        "2026-08-23T20:30:00+02:00",
        "session-assistant-round",
        "player-local",
        "character",
        "char.local",
        command_id,
        source,
        "0.8.8-c3",
        "char.local",
    )


class AssistantRoundExecutionServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        character = CharacterState(character_id="char.local", display_name="Local")
        self.kernel.initialize_state({"character": character.to_dict()})
        self.control = AssistantControlService(self.kernel, JOBS)
        self.jobs = SceneJobService(self.kernel, JOBS)
        self.service = AssistantRoundExecutionService(self.kernel, self.jobs)

    def test_confirmed_round_executes_selected_scene_job_exactly_once(self):
        self.control.set_active_job("scene.flyer_shift", context=context("assistant-select"))
        trigger = ConfirmedRoundTrigger("round-001", "char.local")

        first = self.service.process(trigger, context=context("runtime-round-001"))
        records = self.kernel.read_records()
        retry = self.service.process(trigger, context=context("runtime-round-001-retry"))

        self.assertTrue(first.executed)
        self.assertFalse(first.idempotent_replay)
        self.assertEqual(first.job_id, "scene.flyer_shift")
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(self.kernel.read_records(), records)
        state = self.kernel.load_state()
        self.assertEqual(state["finance"]["cash_cents"], 3500)
        self.assertEqual(state["character"]["energy"], 94)
        self.assertEqual(state["character"]["stress"], 2)
        self.assertEqual(
            [r["event_type"] for r in records],
            [
                "assistant.control_changed",
                "character.resources_changed",
                "finance.job_completed",
                "assistant.round_processed",
            ],
        )

    def test_processed_round_does_not_change_meaning_after_job_switch(self):
        self.control.set_active_job("scene.flyer_shift", context=context("assistant-select-a"))
        trigger = ConfirmedRoundTrigger("round-002", "char.local")
        self.service.process(trigger, context=context("runtime-round-002"))
        self.control.set_active_job("scene.bar_support", context=context("assistant-select-b"))

        retry = self.service.process(trigger, context=context("runtime-round-002-retry"))

        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.job_id, "scene.flyer_shift")
        self.assertEqual(self.kernel.load_state()["finance"]["cash_cents"], 3500)

    def test_round_while_assistant_is_off_is_consumed_without_retroactive_job(self):
        trigger = ConfirmedRoundTrigger("round-off", "char.local")
        first = self.service.process(trigger, context=context("runtime-round-off"))
        self.control.set_active_job("scene.cable_repair", context=context("assistant-later"))
        retry = self.service.process(trigger, context=context("runtime-round-off-retry"))

        self.assertFalse(first.executed)
        self.assertTrue(retry.idempotent_replay)
        self.assertIsNone(retry.job_id)
        self.assertNotIn("finance", self.kernel.load_state())

    def test_durable_job_without_marker_recovers_original_choice_after_switch(self):
        self.control.set_active_job("scene.load_in_help", context=context("assistant-select-original"))
        child_context = context("assistant:char.local:round:round-crash")
        self.jobs.run("scene.load_in_help", context=child_context)
        self.control.set_active_job("scene.night_cleanup", context=context("assistant-switch-after-crash"))

        result = self.service.process(
            ConfirmedRoundTrigger("round-crash", "char.local"),
            context=context("runtime-round-crash-retry"),
        )

        self.assertTrue(result.executed)
        self.assertTrue(result.idempotent_replay)
        self.assertEqual(result.job_id, "scene.load_in_help")
        self.assertEqual(self.kernel.load_state()["finance"]["cash_cents"], 6000)
        processed = [r for r in self.kernel.read_records() if r["event_type"] == "assistant.round_processed"]
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0]["payload"]["job_id"], "scene.load_in_help")

    def test_trigger_requires_matching_character_and_is_not_a_browser_command(self):
        with self.assertRaisesRegex(ValueError, "passt nicht"):
            self.service.process(
                ConfirmedRoundTrigger("round-wrong", "char.other"),
                context=context("runtime-round-wrong"),
            )
        before = self.kernel.read_records()
        self.assertEqual(before, ())


if __name__ == "__main__":
    unittest.main()
