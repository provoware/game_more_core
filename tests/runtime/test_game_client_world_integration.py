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
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
WORLD = json.loads((ROOT / "manifests" / "WORLD_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def ctx(command_id: str, *, entity_type: str = "event", event_id: str = "event-world") -> JournalContext:
    entity_id = "player-local" if entity_type == "character" else event_id
    return JournalContext(
        "2026-08-22T17:00:00+02:00",
        "world-client-session",
        "player-local",
        entity_type,
        entity_id,
        command_id,
        "world-client-test",
        "0.8.5-d1",
        "player-local",
    )


def event_state() -> EventState:
    return EventState(
        event_id="event-world",
        display_name="World Client Event",
        location={
            "location_id": "loc-a4-demo",
            "display_name": "A4 Testlocation",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-world", "display_name": "World Act", "status": "confirmed"}],
        crew=[{"character_id": "player-local", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "required"}],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


def economy_state() -> EconomyState:
    return EconomyState(catalog={
        "equipment.pa": {
            "label": "PA",
            "base_price_cents": 10_000,
            "volatility_bps": 0,
            "consumable": False,
        }
    })


class GameClientWorldIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            street_manifest=STREET,
            street_world_seed="world-client-street",
            world_manifest=WORLD,
        )
        self.character = CharacterState("player-local", "Ria")
        self.session.bootstrap_character(self.character)
        registered = self.session.ensure_world_player(
            self.character,
            context=ctx("world-register", entity_type="character"),
        )
        self.assertEqual(registered.status, "confirmed")
        self._event({
            "type": "event.create",
            "command_id": "create-world-event",
            "event": event_state().to_dict(),
        })
        self._event({
            "type": "economy.initialize",
            "command_id": "init-world-economy",
            "economy": economy_state().to_dict(),
        })

    def _event(self, command):
        return self.session.dispatch(command, context=ctx(command["command_id"]))

    def _character(self, command):
        return self.session.dispatch(
            command,
            context=ctx(command["command_id"], entity_type="character"),
        )

    def test_city_multiplier_is_server_derived_and_client_cannot_override_it(self):
        move = self._character({
            "type": "world.move",
            "command_id": "move-hamburg",
            "city_id": "hamburg",
            "district_id": "wilhelmsburg",
            "location_id": "wilhelmsburg_halle",
        })
        self.assertEqual(move.status, "confirmed")
        self.assertEqual(move.metadata["city_price_multiplier_bps"], 11500)

        rejected = self._event({
            "type": "economy.transact",
            "command_id": "fake-cheap-price",
            "kind": "buy",
            "item_id": "equipment.pa",
            "quantity": 1,
            "price_multiplier_bps": 1,
        })
        self.assertEqual((rejected.status, rejected.error_code), ("rejected", "unexpected_command_fields"))

        bought = self._event({
            "type": "economy.transact",
            "command_id": "hamburg-buy",
            "kind": "buy",
            "item_id": "equipment.pa",
            "quantity": 1,
        })
        self.assertEqual(bought.status, "confirmed")
        self.assertEqual(bought.metadata["city_price_multiplier_bps"], 11500)
        state = self.session.read_state()
        self.assertEqual(state["economy"]["ledger"][-1]["unit_price_cents"], 11_500)
        self.assertEqual(state["event"]["budget_cents"], 88_500)
        record = next(r for r in self.kernel.read_records() if r["event_id"] == "hamburg-buy:economy")
        self.assertEqual(record["payload"]["market_context"]["price_multiplier_bps"], 11500)

    def test_browser_has_no_direct_trust_violation_command(self):
        result = self._character({
            "type": "world.trust_violation",
            "command_id": "browser-trust-cheat",
            "target_id": "someone",
            "violation_type": "fraud",
        })
        self.assertEqual((result.status, result.error_code), ("rejected", "unknown_command"))

    def test_settlement_automatically_applies_world_consequences_exactly_once(self):
        commands = [
            {"type": "event.execute", "command_id": "w-planning", "action_id": "begin_planning"},
            {"type": "event.execute", "command_id": "w-procurement", "action_id": "begin_procurement"},
            {"type": "economy.transact", "command_id": "w-buy", "kind": "buy", "item_id": "equipment.pa", "quantity": 1},
            {"type": "economy.transact", "command_id": "w-reserve", "kind": "reserve", "item_id": "equipment.pa", "quantity": 1},
            {"type": "event.execute", "command_id": "w-transport", "action_id": "start_transport"},
            {"type": "event.execute", "command_id": "w-setup", "action_id": "begin_setup"},
            {"type": "event.execute", "command_id": "w-soundcheck", "action_id": "confirm_soundcheck"},
            {"type": "event.execute", "command_id": "w-live", "action_id": "start_live"},
            {"type": "event.execute", "command_id": "w-finish-live", "action_id": "finish_live"},
            {"type": "event.execute", "command_id": "w-finish-teardown", "action_id": "finish_teardown"},
        ]
        for command in commands:
            result = self._event(command)
            self.assertEqual(result.status, "confirmed", (command, result.error_code, result.error_detail))

        command = {"type": "settlement.complete", "command_id": "w-settlement"}
        first = self._event(command)
        record_count = len(self.kernel.read_records())
        second = self._event(command)
        state = self.session.read_state()

        self.assertEqual(first.status, "confirmed")
        self.assertTrue(first.metadata["world_settlement_applied"])
        self.assertEqual(state["event"]["phase"], "completed")
        self.assertEqual(len(state["world"]["applied_settlements"]), 1)
        self.assertIn("betonstarter", state["world"]["honors"]["player-local"])
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(len(self.kernel.read_records()), record_count)
        world_records = [r for r in self.kernel.read_records() if r["event_type"] == "world.settlement_applied"]
        self.assertEqual(len(world_records), 1)


if __name__ == "__main__":
    unittest.main()
