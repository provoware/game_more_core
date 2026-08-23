import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])
INCIDENT = {
    "power_drop": {
        "responses": {
            "power_drop.generator": {
                "target_phase": "live",
                "effects": {
                    "budget_delta_cents": 0,
                    "reputation_delta": 0,
                    "crew_stress_delta": 0,
                    "stability_delta": 0,
                    "heat_delta": 0,
                },
            }
        }
    }
}


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T18:30:00+02:00",
        "session-client-job",
        "player-local",
        "character",
        "char.local",
        command_id,
        "game-client-scene-job-test",
        "0.8.8-b1",
        "char.local",
    )


class GameClientSceneJobTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=INCIDENT,
            incident_contract_version="test",
            scene_job_manifest=JOBS,
        )
        self.session.bootstrap_character(CharacterState("char.local", "Local"))

    def test_client_sends_only_job_id_and_service_owns_payout_and_effects(self):
        result = self.session.dispatch(
            {"type": "job.run", "command_id": "job-client", "job_id": "scene.night_cleanup"},
            context=context("job-client"),
        )

        self.assertEqual(result.status, "confirmed")
        self.assertEqual(result.metadata["scene_job"]["payout_cents"], 5000)
        self.assertEqual(result.confirmed_state["finance"]["cash_cents"], 5000)
        self.assertEqual(result.confirmed_state["character"]["energy"], 91)
        self.assertEqual(result.confirmed_state["character"]["stress"], 2)

    def test_client_cannot_inject_job_payout_or_resource_effects(self):
        before = self.kernel.read_records()
        result = self.session.dispatch(
            {
                "type": "job.run",
                "command_id": "job-inject",
                "job_id": "scene.flyer_shift",
                "payout_cents": 99999999,
                "energy_delta": 100,
            },
            context=context("job-inject"),
        )

        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.error_code, "unexpected_command_fields")
        self.assertEqual(self.kernel.read_records(), before)
        self.assertNotIn("finance", self.session.read_state())


if __name__ == "__main__":
    unittest.main()
