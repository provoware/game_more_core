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
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T20:00:00+02:00",
        "street-choice-session",
        "player-local",
        "character",
        "player-local",
        command_id,
        "a4-street-choice-test",
        "0.8.7-b1",
        "player-local",
    )


class GameClientStreetApproachTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            street_manifest=STREET,
            street_world_seed="street-choice-world",
        )
        self.session.bootstrap_character(CharacterState("player-local", "Choice Crew"))

    def dispatch(self, command: dict):
        return self.session.dispatch(command, context=context(command["command_id"]))

    def test_selected_approach_reaches_service_and_replay(self):
        command = {
            "type": "street.walk",
            "command_id": "choice-network-001",
            "approach_id": "network",
        }
        first = self.dispatch(command)
        second = self.dispatch(command)
        self.assertEqual(first.status, "confirmed")
        self.assertEqual(first.metadata["street_encounter"]["approach_id"], "network")
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.metadata, first.metadata)

    def test_missing_approach_keeps_balanced_legacy_behavior(self):
        result = self.dispatch({"type": "street.walk", "command_id": "choice-default-001"})
        self.assertEqual(result.status, "confirmed")
        self.assertEqual(result.metadata["street_encounter"]["approach_id"], "balanced")

    def test_unknown_approach_and_client_weight_effect_injection_fail_before_write(self):
        before = self.kernel.read_records()
        unknown = self.dispatch({
            "type": "street.walk",
            "command_id": "choice-bad-001",
            "approach_id": "guaranteed-win",
        })
        self.assertEqual((unknown.status, unknown.error_code), ("rejected", "validation_error"))
        self.assertEqual(self.kernel.read_records(), before)

        injected = self.dispatch({
            "type": "street.walk",
            "command_id": "choice-cheat-001",
            "approach_id": "network",
            "weights": {"street.friendly_face": 100},
            "effects": {"reputation_delta": 999},
        })
        self.assertEqual(
            (injected.status, injected.error_code),
            ("rejected", "unexpected_command_fields"),
        )
        self.assertEqual(self.kernel.read_records(), before)


if __name__ == "__main__":
    unittest.main()
