import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel

ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, *, event_id: str = "event-a4") -> JournalContext:
    return JournalContext(
        "2026-08-22T14:00:00+02:00",
        "session-a4",
        "player-local",
        "event",
        event_id,
        command_id,
        "a4-test",
        "0.8.4-a1",
        "player-local",
    )


def starter_event() -> EventState:
    return EventState(
        event_id="event-a4",
        display_name="A4 Smoke Event",
        location={
            "location_id": "loc-a4",
            "display_name": "A4 Testort",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-a4", "display_name": "Act A4", "status": "confirmed"}],
        crew=[{"character_id": "player-local", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "required"}],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


def starter_economy() -> EconomyState:
    return EconomyState(catalog={
        "equipment.pa": {
            "label": "PA",
            "base_price_cents": 10_000,
            "volatility_bps": 0,
            "consumable": False,
        }
    })


class GameClientSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
        )
        self.character = CharacterState("player-local", "Lokale Crew")
        self.session.bootstrap_character(self.character)

    def dispatch(self, command):
        return self.session.dispatch(command, context=context(command["command_id"]))

    def create_base(self):
        created = self.dispatch({
            "type": "event.create",
            "command_id": "create-event",
            "event": starter_event().to_dict(),
        })
        initialized = self.dispatch({
            "type": "economy.initialize",
            "command_id": "init-economy",
            "economy": starter_economy().to_dict(),
        })
        self.assertEqual(created.status, "confirmed")
        self.assertEqual(initialized.status, "confirmed")

    def test_dispatch_rejects_unknown_fields_before_any_write(self):
        result = self.dispatch({
            "type": "event.create",
            "command_id": "bad-extra",
            "event": starter_event().to_dict(),
            "target_phase": "completed",
        })
        self.assertEqual((result.status, result.error_code), ("rejected", "unexpected_command_fields"))
        self.assertEqual(self.kernel.read_records(), ())

    def test_full_client_command_path_uses_canonical_services(self):
        self.create_base()
        commands = [
            {"type": "event.execute", "command_id": "planning", "action_id": "begin_planning"},
            {"type": "event.execute", "command_id": "procurement", "action_id": "begin_procurement"},
            {"type": "economy.transact", "command_id": "buy-pa", "kind": "buy", "item_id": "equipment.pa", "quantity": 1},
            {"type": "economy.transact", "command_id": "reserve-pa", "kind": "reserve", "item_id": "equipment.pa", "quantity": 1},
            {"type": "event.execute", "command_id": "transport", "action_id": "start_transport"},
            {"type": "event.execute", "command_id": "setup", "action_id": "begin_setup"},
            {"type": "event.execute", "command_id": "soundcheck", "action_id": "confirm_soundcheck"},
            {"type": "event.execute", "command_id": "live", "action_id": "start_live"},
            {"type": "incident.open", "command_id": "incident-open", "incident_type": "power_drop", "severity": 3},
            {"type": "incident.resolve", "command_id": "incident-resolve", "response_id": "power_drop.generator"},
            {"type": "event.execute", "command_id": "teardown", "action_id": "finish_live"},
            {"type": "event.execute", "command_id": "settlement-phase", "action_id": "finish_teardown"},
            {"type": "settlement.complete", "command_id": "settlement-complete"},
        ]
        for command in commands:
            result = self.dispatch(command)
            self.assertEqual(result.status, "confirmed", (command, result.error_code, result.error_detail))

        confirmed = self.session.read_state()
        self.assertEqual(confirmed["event"]["phase"], "completed")
        self.assertEqual(confirmed["settlement"]["status"], "completed")
        self.assertEqual(confirmed["economy"]["ledger"][-1]["kind"], "settlement")
        self.assertFalse(any(confirmed["incidents"]["pending_settlement"].values()))

    def test_event_action_retry_is_idempotent_after_phase_advanced(self):
        self.create_base()
        command = {"type": "event.execute", "command_id": "planning-once", "action_id": "begin_planning"}
        first = self.dispatch(command)
        second = self.dispatch(command)
        self.assertEqual(first.status, "confirmed")
        self.assertEqual(second.status, "confirmed")
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.committed_event_ids, ())
        self.assertEqual(self.session.read_state()["event"]["phase"], "planning")

    def test_bootstrap_never_overwrites_an_existing_character(self):
        other = CharacterState("player-local", "Andere Crew")
        with self.assertRaisesRegex(RuntimeError, "anderen Character"):
            self.session.bootstrap_character(other)


if __name__ == "__main__":
    unittest.main()
