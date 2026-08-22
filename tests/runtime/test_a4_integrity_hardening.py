import json
from pathlib import Path
import sys
import tempfile
import unittest

from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.application.world_service import WorldCommitResult
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.world import WorldState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel

ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def character_context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T17:00:00+02:00",
        "a4-integrity-hardening",
        "player-local",
        "character",
        "player-local",
        command_id,
        "a4-integrity-hardening-test",
        "0.8.5-d1",
        "player-local",
    )


class ProfileReplayHardeningTests(unittest.TestCase):
    def test_same_profile_command_id_cannot_be_reused_with_other_changes(self):
        with tempfile.TemporaryDirectory() as save_dir:
            kernel = PersistenceKernel(save_dir, ALLOWED)
            session = GameClientSession(
                kernel,
                incident_catalog=build_incident_catalog(INCIDENTS),
                incident_contract_version=INCIDENTS["version"],
            )
            session.bootstrap_character(CharacterState("player-local", "Ria"))
            first_command = {
                "type": "profile.update",
                "command_id": "profile-fixed-id",
                "changes": {"display_name": "Ria Eins", "motto": "Erstes Motto"},
            }
            first = session.dispatch(first_command, context=character_context("profile-fixed-id"))
            retry = session.dispatch(first_command, context=character_context("profile-fixed-id"))
            altered = session.dispatch(
                {
                    "type": "profile.update",
                    "command_id": "profile-fixed-id",
                    "changes": {"display_name": "Ria Zwei", "motto": "Anderes Motto"},
                },
                context=character_context("profile-fixed-id"),
            )

            self.assertEqual(first.status, "confirmed")
            self.assertTrue(retry.idempotent_replay)
            self.assertEqual((altered.status, altered.error_code), ("rejected", "persistence_error"))
            self.assertIn("anderem Profilupdate", altered.error_detail)
            self.assertEqual(session.read_state()["character"]["display_name"], "Ria Eins")
            self.assertEqual(
                len([record for record in kernel.read_records() if record["event_id"] == "profile-fixed-id:profile"]),
                1,
            )


class _FakeWorldService:
    def __init__(self) -> None:
        self.contexts = []

    def apply_confirmed_settlement(self, *, context: JournalContext) -> WorldCommitResult:
        self.contexts.append(context)
        world = WorldState(world_id="living_city")
        return WorldCommitResult(world, ("startup-world-settlement",), False)


class _FakeSession:
    def __init__(self, state: dict) -> None:
        self._state = state
        self.world = _FakeWorldService()

    def read_state(self) -> dict:
        return json.loads(json.dumps(self._state))


class StartupWorldReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tools = str(ROOT / "tools")
        if tools not in sys.path:
            sys.path.insert(0, tools)
        import start_a4_game_client as launcher

        cls.Runtime = launcher.A4ClientRuntime

    def runtime(self, applied: list[str]):
        instance = self.Runtime.__new__(self.Runtime)
        instance.session_id = "startup-reconcile-test"
        instance.game_version = "0.8.5-d1"
        instance.session = _FakeSession({
            "character": {"character_id": "player-local"},
            "event": {"event_id": "event-1", "phase": "completed"},
            "settlement": {"settlement_id": "settlement:done"},
            "world": {"applied_settlements": list(applied)},
        })
        return instance

    def test_missing_world_followup_is_reconciled_once_from_confirmed_settlement(self):
        runtime = self.runtime([])
        runtime._reconcile_completed_world_settlement()
        self.assertEqual(len(runtime.session.world.contexts), 1)
        context = runtime.session.world.contexts[0]
        self.assertEqual(context.entity_type, "event")
        self.assertEqual(context.entity_id, "event-1")
        self.assertEqual(context.character_id, "player-local")
        self.assertEqual(context.command_id, "startup-world-settlement:settlement:done")

    def test_already_applied_world_settlement_does_not_write_again(self):
        runtime = self.runtime(["settlement:done"])
        runtime._reconcile_completed_world_settlement()
        self.assertEqual(runtime.session.world.contexts, [])


if __name__ == "__main__":
    unittest.main()
