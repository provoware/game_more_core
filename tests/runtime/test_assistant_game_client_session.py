import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.assistant_game_client_session import AssistantGameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, character_id: str = "char.local") -> JournalContext:
    return JournalContext(
        "2026-08-23T20:45:00+02:00",
        "session-assistant-ui",
        "player-local",
        "character",
        character_id,
        command_id,
        "assistant-ui-test",
        "0.8.8-c4",
        character_id,
    )


class AssistantGameClientSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.character = CharacterState(character_id="char.local", display_name="Local")
        self.kernel.initialize_state({"character": self.character.to_dict()})
        self.session = AssistantGameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            scene_job_manifest=JOBS,
        )

    def test_start_switch_and_stop_delegate_to_canonical_control_service(self):
        start = self.session.dispatch(
            {"type": "assistant.control", "command_id": "ui-start", "job_id": "scene.flyer_shift"},
            context=context("ui-start"),
        )
        switch = self.session.dispatch(
            {"type": "assistant.control", "command_id": "ui-switch", "job_id": "scene.cable_repair"},
            context=context("ui-switch"),
        )
        stop = self.session.dispatch(
            {"type": "assistant.control", "command_id": "ui-stop", "job_id": None},
            context=context("ui-stop"),
        )

        self.assertEqual(start.status, "confirmed")
        self.assertEqual(start.committed_event_ids, ("ui-start:assistant-control",))
        self.assertEqual(start.metadata["assistant_control"]["active_job_id"], "scene.flyer_shift")
        self.assertEqual(switch.metadata["assistant_control"]["active_job_id"], "scene.cable_repair")
        self.assertIsNone(stop.metadata["assistant_control"]["active_job_id"])
        self.assertEqual(self.kernel.load_state()["assistant"]["revision"], 3)
        self.assertNotIn("finance", self.kernel.load_state())
        self.assertEqual(self.kernel.load_state()["character"], self.character.to_dict())

    def test_retry_is_idempotent_and_does_not_create_second_control_event(self):
        command = {"type": "assistant.control", "command_id": "ui-retry", "job_id": "scene.load_in_help"}
        first = self.session.dispatch(command, context=context("ui-retry"))
        records = self.kernel.read_records()
        retry = self.session.dispatch(command, context=context("ui-retry"))

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.committed_event_ids, ())
        self.assertEqual(self.kernel.read_records(), records)

    def test_unknown_job_extra_authority_and_wrong_character_fail_closed(self):
        unknown = self.session.dispatch(
            {"type": "assistant.control", "command_id": "ui-fake", "job_id": "scene.fake"},
            context=context("ui-fake"),
        )
        extra = self.session.dispatch(
            {
                "type": "assistant.control",
                "command_id": "ui-extra",
                "job_id": "scene.flyer_shift",
                "payout_cents": 999999,
            },
            context=context("ui-extra"),
        )
        wrong = self.session.dispatch(
            {"type": "assistant.control", "command_id": "ui-wrong", "job_id": "scene.flyer_shift"},
            context=context("ui-wrong", "char.other"),
        )

        self.assertEqual(unknown.status, "rejected")
        self.assertEqual(unknown.error_code, "validation_error")
        self.assertEqual(extra.error_code, "unexpected_command_fields")
        self.assertEqual(wrong.status, "rejected")
        self.assertEqual(self.kernel.read_records(), ())

    def test_recovery_command_delegates_to_canonical_service_and_rejects_client_deltas(self):
        low_energy = CharacterState.from_dict(self.character.to_dict())
        low_energy.energy = 40
        low_energy.stress = 30
        self.kernel.initialize_state({"character": low_energy.to_dict()})

        result = self.session.dispatch(
            {
                "type": "recovery.run",
                "command_id": "ui-recovery",
                "recovery_id": "recovery.koffein_kalte_luft",
            },
            context=context("ui-recovery"),
        )
        self.assertEqual(result.status, "confirmed")
        self.assertEqual(result.committed_event_ids, ("ui-recovery:recovery",))
        self.assertEqual(result.confirmed_state["character"]["energy"], 60)
        self.assertEqual(result.confirmed_state["character"]["stress"], 42)
        self.assertEqual(result.metadata["recovery_action"]["recovery_id"], "recovery.koffein_kalte_luft")

        before = self.kernel.read_records()
        injected = self.session.dispatch(
            {
                "type": "recovery.run",
                "command_id": "ui-recovery-inject",
                "recovery_id": "recovery.koffein_kalte_luft",
                "energy_delta": 100,
            },
            context=context("ui-recovery-inject"),
        )
        self.assertEqual(injected.status, "rejected")
        self.assertEqual(injected.error_code, "unexpected_command_fields")
        self.assertEqual(self.kernel.read_records(), before)


if __name__ == "__main__":
    unittest.main()
