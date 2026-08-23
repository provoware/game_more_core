import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
ASSISTANT = json.loads((ROOT / "manifests" / "ASSISTANT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T20:00:00+02:00",
        "assistant-client-session",
        "player-local",
        "character",
        "player-local",
        command_id,
        "a4-assistant-client-test",
        "0.8.8-c1",
        "player-local",
    )


class GameClientAssistantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            street_manifest=STREET,
            street_world_seed="assistant-street-world",
            scene_job_manifest=JOBS,
            assistant_manifest=ASSISTANT,
        )
        self.session.bootstrap_character(CharacterState("player-local", "Assistant Crew"))

    def dispatch(self, command: dict):
        return self.session.dispatch(command, context=context(command["command_id"]))

    def test_assign_then_confirmed_street_round_executes_same_scene_job_once(self):
        assigned = self.dispatch({
            "type": "assistant.assign",
            "command_id": "assistant-assign-001",
            "task_id": "scene.flyer_shift",
        })
        self.assertEqual(assigned.status, "confirmed")
        self.assertEqual(assigned.confirmed_state["assistant"]["active_task_id"], "scene.flyer_shift")

        command = {
            "type": "street.walk",
            "command_id": "assistant-street-001",
            "approach_id": "balanced",
        }
        first = self.dispatch(command)
        records_after_first = self.kernel.read_records()
        cash_after_first = first.confirmed_state["finance"]["cash_cents"]
        retry = self.dispatch(command)

        self.assertEqual(first.status, "confirmed")
        self.assertTrue(first.metadata["assistant"]["executed"])
        self.assertEqual(first.metadata["assistant"]["task_id"], "scene.flyer_shift")
        self.assertEqual(first.metadata["assistant"]["payout_cents"], 3500)
        self.assertEqual(first.confirmed_state["assistant"]["completed_rounds"], 1)
        self.assertEqual(first.confirmed_state["assistant"]["last_completed_round_id"], "assistant-street-001")
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.confirmed_state["finance"]["cash_cents"], cash_after_first)
        self.assertEqual(self.kernel.read_records(), records_after_first)

    def test_deactivate_stops_execution_on_next_confirmed_round(self):
        self.dispatch({
            "type": "assistant.assign",
            "command_id": "assistant-assign-002",
            "task_id": "scene.cable_repair",
        })
        stopped = self.dispatch({
            "type": "assistant.deactivate",
            "command_id": "assistant-stop-002",
        })
        self.assertIsNone(stopped.confirmed_state["assistant"]["active_task_id"])

        round_result = self.dispatch({
            "type": "street.walk",
            "command_id": "assistant-street-002",
        })
        self.assertEqual(round_result.status, "confirmed")
        self.assertNotIn("assistant", round_result.metadata)
        self.assertNotIn("finance", round_result.confirmed_state)

    def test_browser_cannot_inject_assistant_payout_effects_or_round_authority(self):
        before = self.kernel.read_records()
        injected = self.dispatch({
            "type": "assistant.assign",
            "command_id": "assistant-cheat-001",
            "task_id": "scene.bar_support",
            "payout_cents": 99999999,
            "energy_delta": 100,
            "round_id": "fake-round",
        })
        self.assertEqual(
            (injected.status, injected.error_code),
            ("rejected", "unexpected_command_fields"),
        )
        self.assertEqual(self.kernel.read_records(), before)
        self.assertNotIn("assistant", self.session.read_state())


if __name__ == "__main__":
    unittest.main()
