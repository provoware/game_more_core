import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.economy_service import EconomyService
from bunkerfrequenz.application.event_execution_service import EventExecutionService
from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.application.incident_service import IncidentService, build_incident_catalog
from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import (
    FaultInjectedCrash,
    JournalContext,
    PersistenceError,
    PersistenceKernel,
)


ALLOWED = {
    "event.created",
    "event.phase_changed",
    "event.incident_started",
    "event.incident_resolved",
    "event.completed",
    "economy.catalog_initialized",
    "economy.transaction_posted",
    "inventory.item_acquired",
    "character.resources_changed",
    "character.reputation_changed",
    "character.biography_entry_added",
    "system.recovery_performed",
}


def context(command_id: str, *, entity_id: str = "event-1") -> JournalContext:
    return JournalContext(
        "2026-08-22T22:00:00+02:00",
        "session-0.8.3c",
        "player-1",
        "event",
        entity_id,
        command_id,
        "runtime",
        "0.8.3-c1",
    )


def character() -> CharacterState:
    return CharacterState(
        character_id="player-1",
        display_name="Testfigur",
        stress=95,
        reputation=10,
    )


def event() -> EventState:
    return EventState(
        event_id="event-1",
        display_name="Bunkerfrequenz Settlement Test",
        location={
            "location_id": "loc-test",
            "display_name": "Testort",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-1", "display_name": "Act 1", "status": "confirmed"}],
        crew=[{"character_id": "player-1", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "required"}],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


def economy() -> EconomyState:
    return EconomyState(catalog={
        "equipment.pa": {
            "label": "PA",
            "base_price_cents": 10_000,
            "volatility_bps": 0,
            "consumable": False,
        }
    })


def incident_catalog():
    manifest = json.loads(
        (Path(__file__).parents[2] / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8")
    )
    return manifest, build_incident_catalog(manifest)


def crash_after_journal(point: str) -> None:
    if point == "after_journal_durable":
        raise FaultInjectedCrash(point)


class SettlementServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.kernel.initialize_state({"character": character().to_dict()})
        created = EventStateService(self.kernel).create(event(), context=context("create-event"))
        EconomyService(self.kernel).initialize(economy(), context=context("init-economy"))
        execution = EventExecutionService(EventStateService(self.kernel))
        current = execution.execute(created.event, "begin_planning", context=context("begin-planning")).event
        current = execution.execute(current, "begin_procurement", context=context("begin-procurement")).event
        bought = EconomyService(self.kernel).transact("buy", "equipment.pa", 1, context=context("buy-pa"))
        reserved = EconomyService(self.kernel).transact("reserve", "equipment.pa", 1, context=context("reserve-pa"))
        current = reserved.event
        current = execution.execute(current, "start_transport", context=context("start-transport")).event
        current = execution.execute(current, "begin_setup", context=context("begin-setup")).event
        current = execution.execute(current, "confirm_soundcheck", context=context("soundcheck")).event
        current = execution.execute(current, "start_live", context=context("start-live")).event

        manifest, catalog = incident_catalog()
        incidents = IncidentService(self.kernel, catalog, contract_version=manifest["version"])
        opened = incidents.open("power_drop", context=context("open-power"), severity=3)
        resolved = incidents.resolve("power_drop.generator", context=context("resolve-power"))
        current = execution.execute(resolved.event, "finish_live", context=context("finish-live")).event
        self.settlement_event = execution.execute(
            current,
            "finish_teardown",
            context=context("finish-teardown"),
        ).event
        self.assertEqual(self.settlement_event.phase, "settlement")
        self.assertEqual(bought.event.budget_cents, 90_000)
        self.assertEqual(opened.event.phase, "crisis")

    def test_complete_applies_all_confirmed_consequences_once(self):
        before = self.kernel.load_state()
        pending = dict(before["incidents"]["pending_settlement"])
        market_tick_before = before["economy"]["market_tick"]

        result = SettlementService(self.kernel).complete(context=context("complete-settlement"))

        self.assertEqual(result.event.phase, "completed")
        self.assertEqual(result.event.budget_cents, 90_000 + pending["budget_delta_cents"])
        self.assertEqual(result.character.stress, 100)
        self.assertEqual(result.character.reputation, 10 + pending["reputation_delta"])
        self.assertEqual(result.economy.ledger[-1]["kind"], "settlement")
        self.assertEqual(result.economy.ledger[-1]["budget_delta_cents"], pending["budget_delta_cents"])
        self.assertEqual(result.economy.market_tick, market_tick_before)
        self.assertEqual(result.settlement.effects, pending)
        self.assertEqual(result.settlement.stress["new"], 100)
        self.assertTrue(result.settlement.incident_ids)
        self.assertFalse(any(result.incidents.pending_settlement.values()))

        records = self.kernel.read_records()
        self.assertEqual(
            [record["event_type"] for record in records[-6:]],
            [
                "economy.transaction_posted",
                "character.resources_changed",
                "character.reputation_changed",
                "character.biography_entry_added",
                "event.phase_changed",
                "event.completed",
            ],
        )

        ledger_count = len(result.economy.ledger)
        replay = SettlementService(self.kernel).complete(context=context("complete-settlement"))
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(len(replay.economy.ledger), ledger_count)
        self.assertEqual(replay.settlement.to_dict(), result.settlement.to_dict())

    def test_wrong_context_is_rejected_even_for_idempotent_replay(self):
        SettlementService(self.kernel).complete(context=context("context-guard"))
        with self.assertRaisesRegex(ValueError, "entity_id"):
            SettlementService(self.kernel).complete(
                context=context("context-guard", entity_id="event-2")
            )

    def test_settlement_requires_character_participation_and_settlement_phase(self):
        with self.assertRaisesRegex(ValueError, "completed|SettlementService"):
            EventStateService(self.kernel).transition_phase(
                self.settlement_event,
                "completed",
                context=context("illegal-direct-complete"),
                reason="test_should_not_use_generic_transition",
            )

        state = self.kernel.load_state()
        state["character"]["character_id"] = "not-in-crew"
        isolated = tempfile.TemporaryDirectory()
        self.addCleanup(isolated.cleanup)
        kernel = PersistenceKernel(isolated.name, ALLOWED)
        kernel.initialize_state(state)
        with self.assertRaisesRegex(ValueError, "Crew"):
            SettlementService(kernel).complete(context=context("wrong-character"))

    def test_recovery_replays_complete_settlement_after_durable_journal_crash(self):
        self.kernel.create_snapshot("before_settlement")
        crashing = PersistenceKernel(self.tmp.name, ALLOWED, fault_injector=crash_after_journal)
        with self.assertRaises(FaultInjectedCrash):
            SettlementService(crashing).complete(context=context("settlement-crash"))
        with self.assertRaises(PersistenceError):
            PersistenceKernel(self.tmp.name, ALLOWED)

        recovering = PersistenceKernel.open_for_recovery(self.tmp.name, ALLOWED)
        receipt = GameRecoveryService(recovering).recover(context=context("recover-settlement"))
        self.assertEqual(receipt.status, "recovered")
        state = recovering.load_state()
        self.assertEqual(state["event"]["phase"], "completed")
        self.assertEqual(state["settlement"]["status"], "completed")
        self.assertEqual(state["economy"]["ledger"][-1]["kind"], "settlement")
        self.assertEqual(state["character"]["stress"], 100)
        self.assertFalse(any(state["incidents"]["pending_settlement"].values()))


if __name__ == "__main__":
    unittest.main()
