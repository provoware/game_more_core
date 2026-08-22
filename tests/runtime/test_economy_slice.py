from copy import deepcopy
import tempfile
import unittest

from bunkerfrequenz.application.economy_service import EconomyService, replay_economy_event
from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.domain.economy import EconomyState, market_price
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import (
    FaultInjectedCrash,
    JournalContext,
    PersistenceError,
    PersistenceKernel,
)


ALLOWED = {
    "event.created", "economy.catalog_initialized", "inventory.item_acquired",
    "inventory.item_removed", "economy.transaction_posted",
    "economy.transaction_compensated", "system.recovery_performed",
}


def context(command_id: str, *, entity_id: str = "event-1") -> JournalContext:
    return JournalContext(
        "2026-08-22T12:00:00+00:00", "session-0.8.2", "player-1", "event",
        entity_id, command_id, "runtime", "0.8.2-alpha.1",
    )


def event() -> EventState:
    return EventState(
        event_id="event-1", display_name="Testfrequenz", budget_cents=100_000,
        equipment=[
            {"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "required"},
            {"equipment_id": "equipment.tape", "label": "Tape", "quantity": 2, "status": "required"},
        ],
    )


def economy() -> EconomyState:
    return EconomyState(catalog={
        "equipment.pa": {
            "label": "PA", "base_price_cents": 50_000, "volatility_bps": 500, "consumable": False,
        },
        "equipment.tape": {
            "label": "Tape", "base_price_cents": 500, "volatility_bps": 100, "consumable": True,
        },
    })


def crash_after_journal(point: str) -> None:
    if point == "after_journal_durable":
        raise FaultInjectedCrash(point)


class EconomySliceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        EventStateService(self.kernel).create(event(), context=context("create-event"))
        EconomyService(self.kernel).initialize(economy(), context=context("init-catalog"))

    def test_vertical_slice_links_budget_inventory_reservation_and_requirements(self):
        service = EconomyService(self.kernel)
        with self.assertRaises(ValueError):
            EventStateService(self.kernel).update_planning(
                event(), {"budget_cents": 200_000}, context=context("direct-budget-change")
            )
        bought = service.transact("buy", "equipment.pa", 1, context=context("buy-pa"))
        self.assertEqual(bought.event.budget_cents, 55_000)
        self.assertEqual(bought.event.equipment[0]["status"], "missing")

        reserved = service.transact("reserve", "equipment.pa", 1, context=context("reserve-pa"))
        self.assertEqual(reserved.event.equipment[0]["status"], "ready")
        replay = service.transact("reserve", "equipment.pa", 1, context=context("reserve-pa"))
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.economy.inventory["equipment.pa"]["reserved"], 1)

        service.transact("buy", "equipment.tape", 3, context=context("buy-tape"))
        consumed = service.transact("consume", "equipment.tape", 1, context=context("consume-tape"))
        self.assertEqual(consumed.economy.inventory["equipment.tape"]["owned"], 2)
        with self.assertRaises(ValueError):
            service.transact("sell", "equipment.pa", 1, context=context("sell-reserved-pa"))

    def test_market_price_is_deterministic_and_compensation_uses_original_price(self):
        self.assertEqual(market_price(50_000, 0, 500), 45_000)
        self.assertEqual(market_price(50_000, 0, 500), market_price(50_000, 0, 500))
        service = EconomyService(self.kernel)
        bought = service.transact("buy", "equipment.pa", 1, context=context("buy-compensated"))
        compensated = service.compensate("buy-compensated", context=context("compensate-buy"))
        self.assertEqual(compensated.event.budget_cents, 100_000)
        self.assertEqual(compensated.economy.inventory["equipment.pa"]["owned"], 0)
        self.assertEqual(compensated.economy.ledger[-1]["unit_price_cents"], bought.economy.ledger[-1]["unit_price_cents"])

    def test_recovery_replays_atomic_economy_and_event_state(self):
        self.kernel.create_snapshot("economy_initialized")
        crashing = PersistenceKernel(self.tmp.name, ALLOWED, fault_injector=crash_after_journal)
        with self.assertRaises(FaultInjectedCrash):
            EconomyService(crashing).transact("buy", "equipment.pa", 1, context=context("buy-crash"))
        with self.assertRaises(PersistenceError):
            PersistenceKernel(self.tmp.name, ALLOWED)

        recovering = PersistenceKernel.open_for_recovery(self.tmp.name, ALLOWED)
        receipt = GameRecoveryService(recovering).recover(context=context("recover-economy"))
        self.assertEqual(receipt.status, "recovered")
        state = recovering.load_state()
        self.assertEqual(state["economy"]["inventory"]["equipment.pa"]["owned"], 1)
        self.assertEqual(state["event"]["budget_cents"], 55_000)

    def test_economy_commands_reject_context_for_another_event(self):
        service = EconomyService(self.kernel)
        wrong = context("wrong-event-buy", entity_id="event-2")
        with self.assertRaisesRegex(ValueError, "entity_id"):
            service.transact("buy", "equipment.pa", 1, context=wrong)

        service.transact("buy", "equipment.pa", 1, context=context("replay-guard"))
        with self.assertRaisesRegex(ValueError, "entity_id"):
            service.transact(
                "buy", "equipment.pa", 1,
                context=context("replay-guard", entity_id="event-2"),
            )

    def test_replay_rejects_conflicting_state_at_same_economy_revision(self):
        EconomyService(self.kernel).transact("buy", "equipment.pa", 1, context=context("buy-conflict"))
        state = self.kernel.load_state()
        conflicting_event = deepcopy(state["event"])
        conflicting_event["budget_cents"] += 1
        record = {
            "event_type": "economy.transaction_posted",
            "payload": {
                "economy": deepcopy(state["economy"]),
                "event": conflicting_event,
            },
        }
        with self.assertRaisesRegex(ValueError, "derselben Revision"):
            replay_economy_event(state, record)


if __name__ == "__main__":
    unittest.main()
