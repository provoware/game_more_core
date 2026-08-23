from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import replay_game_event
from bunkerfrequenz.application.scene_job_service import SceneJobService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T18:00:00+02:00",
        "session-scene-job",
        "player-local",
        "character",
        "char.local",
        command_id,
        "scene-job-test",
        "0.8.8-c1",
        "char.local",
    )


class SceneJobServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.character = CharacterState(character_id="char.local", display_name="Local")
        self.kernel.initialize_state({"character": self.character.to_dict()})
        self.service = SceneJobService(self.kernel, JOBS)

    def test_job_is_available_without_event_and_applies_catalogued_payout_and_resources(self):
        result = self.service.run("scene.cable_repair", context=context("job-one"))

        self.assertEqual(result.finance.cash_cents, 5500)
        self.assertEqual(result.character.energy, 92)
        self.assertEqual(result.character.stress, 3)
        self.assertEqual(result.finance.ledger[-1]["kind"], "job_income")
        self.assertEqual(result.finance.ledger[-1]["source_id"], "scene.cable_repair")
        self.assertEqual(
            [record["event_type"] for record in self.kernel.read_records()],
            ["character.resources_changed", "finance.job_completed"],
        )
        self.assertNotIn("event", self.kernel.load_state())

    def test_retry_is_idempotent_and_does_not_pay_twice(self):
        first = self.service.run("scene.flyer_shift", context=context("job-retry"))
        records = self.kernel.read_records()
        retry = self.service.run("scene.flyer_shift", context=context("job-retry"))

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.finance.cash_cents, 3500)
        self.assertEqual(self.kernel.read_records(), records)

    def test_unknown_job_and_wrong_context_fail_before_write(self):
        before = self.kernel.read_records()
        with self.assertRaisesRegex(ValueError, "Unbekannter Scene Job"):
            self.service.run("scene.fake", context=context("job-fake"))
        with self.assertRaisesRegex(ValueError, "Character-Kontext"):
            self.service.run(
                "scene.flyer_shift",
                context=JournalContext(
                    "2026-08-23T18:00:00+02:00",
                    "session-scene-job",
                    "player-local",
                    "event",
                    "event-x",
                    "job-wrong-context",
                    "scene-job-test",
                    "0.8.8-c1",
                    "char.local",
                ),
            )
        self.assertEqual(self.kernel.read_records(), before)

    def test_recovery_reconstructs_finance_after_durable_records(self):
        result = self.service.run("scene.load_in_help", context=context("job-recovery"))
        state = {"character": self.character.to_dict()}
        for record in self.kernel.read_records():
            state = replay_game_event(state, record)

        self.assertEqual(state["finance"], result.finance.to_dict())
        self.assertEqual(state["character"], result.character.to_dict())

    def test_assistant_policy_reuses_jobs_and_fails_closed_on_unsafe_authority(self):
        policy = self.service.assistant_policy
        self.assertEqual(policy["task_source"], "scene_jobs")
        self.assertEqual(policy["max_active_tasks"], 1)
        self.assertTrue(policy["requires_confirmed_round"])
        self.assertFalse(policy["requires_system_time"])
        self.assertFalse(policy["client_can_supply_round_authority"])
        self.assertFalse(policy["client_can_supply_payout_or_effects"])
        self.assertTrue(policy["stop_and_switch_required"])

        unsafe = deepcopy(JOBS)
        unsafe["assistant_policy"]["client_can_supply_round_authority"] = True
        with self.assertRaisesRegex(ValueError, "Rundenautorität"):
            SceneJobService(self.kernel, unsafe)

        duplicate_catalog = deepcopy(JOBS)
        duplicate_catalog["assistant_policy"]["task_source"] = "assistant_jobs"
        with self.assertRaisesRegex(ValueError, "Scene-Job-Katalog"):
            SceneJobService(self.kernel, duplicate_catalog)


if __name__ == "__main__":
    unittest.main()
