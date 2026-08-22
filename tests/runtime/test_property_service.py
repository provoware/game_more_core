import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.application.property_service import PropertyService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import (
    FaultInjectedCrash,
    JournalContext,
    PersistenceKernel,
)


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
PROPERTY = json.loads((ROOT / "manifests" / "PROPERTY_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def event(*, budget_cents: int = 10_000_000) -> EventState:
    return EventState(
        event_id="event-property",
        display_name="Property Test",
        location={
            "location_id": "signalwerk",
            "display_name": "Signalwerk",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=budget_cents,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "char.property", "role": "leitung", "status": "confirmed"}],
        equipment=[],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T04:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


def economy() -> EconomyState:
    return EconomyState(catalog={
        "equipment.pa": {
            "label": "PA",
            "base_price_cents": 10_000,
            "volatility_bps": 100,
            "consumable": False,
        }
    })


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T19:30:00+02:00",
        "session-property",
        "player-property",
        "event",
        "event-property",
        command_id,
        "property-test",
        "0.8.6-a1",
        "char.property",
    )


def initial_state(*, budget_cents: int = 10_000_000) -> dict:
    return {
        "character": CharacterState("char.property", "Property Crew").to_dict(),
        "event": event(budget_cents=budget_cents).to_dict(),
        "economy": economy().to_dict(),
    }


class PropertyServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.kernel.initialize_state(initial_state())
        self.service = PropertyService(self.kernel, PROPERTY, CITY_MAP)

    def test_successful_purchase_is_one_atomic_economy_property_transaction(self):
        before = self.kernel.load_state()
        result = self.service.purchase("signalwerk", context=context("buy-signalwerk"))
        self.assertFalse(result.idempotent_replay)
        self.assertEqual(result.committed_event_ids, ("buy-signalwerk:economy", "buy-signalwerk:property"))
        self.assertEqual(result.event.budget_cents, before["event"]["budget_cents"] - 6_200_000)
        self.assertEqual(result.economy.market_tick, before["economy"]["market_tick"])
        self.assertEqual(result.economy.revision, before["economy"]["revision"] + 1)
        ledger = result.economy.ledger[-1]
        self.assertEqual(ledger["kind"], "property_purchase")
        self.assertEqual(ledger["item_id"], "property:signalwerk")
        self.assertEqual(ledger["quantity"], 1)
        self.assertEqual(ledger["unit_price_cents"], 6_200_000)
        self.assertEqual(ledger["budget_delta_cents"], -6_200_000)
        ownership = result.properties.owned["signalwerk"]
        self.assertEqual(ownership["owner_character_id"], "char.property")
        self.assertEqual(ownership["purchase_price_cents"], 6_200_000)
        self.assertEqual(ownership["economy_transaction_id"], "property:buy-signalwerk")
        records = self.kernel.read_records()
        self.assertEqual([record["event_type"] for record in records], [
            "economy.transaction_posted",
            "world.property_purchased",
        ])
        self.assertEqual({record["transaction_id"] for record in records}, {"tx:buy-signalwerk"})

    def test_same_command_is_idempotent_and_different_second_purchase_is_rejected(self):
        first = self.service.purchase("signalwerk", context=context("buy-once"))
        replay = self.service.purchase("signalwerk", context=context("buy-once"))
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.committed_event_ids, ())
        self.assertEqual(len(self.kernel.read_records()), 2)
        with self.assertRaises(ValueError):
            self.service.purchase("signalwerk", context=context("buy-twice"))
        self.assertEqual(len(self.kernel.read_records()), 2)

    def test_non_purchasable_location_and_insufficient_budget_fail_without_write(self):
        before = self.kernel.load_state()
        with self.assertRaises(ValueError):
            self.service.purchase("hall_of_tribute", context=context("buy-hall"))
        self.assertEqual(self.kernel.read_records(), ())
        self.assertEqual(self.kernel.load_state(), before)

        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        poor_kernel = PersistenceKernel(other.name, ALLOWED)
        poor_kernel.initialize_state(initial_state(budget_cents=6_199_999))
        poor_service = PropertyService(poor_kernel, PROPERTY, CITY_MAP)
        poor_before = poor_kernel.load_state()
        with self.assertRaises(ValueError):
            poor_service.purchase("signalwerk", context=context("too-poor"))
        self.assertEqual(poor_kernel.read_records(), ())
        self.assertEqual(poor_kernel.load_state(), poor_before)

    def test_price_is_taken_exactly_from_city_map(self):
        expected = {
            item["location_id"]: item["purchase_price_cents"]
            for item in CITY_MAP["locations"]
            if item.get("purchasable") is True
        }
        self.assertEqual(len(expected), 7)
        self.service.purchase("sublevel_44", context=context("buy-sublevel"))
        state = self.kernel.load_state()
        self.assertEqual(state["properties"]["owned"]["sublevel_44"]["purchase_price_cents"], expected["sublevel_44"])
        self.assertEqual(state["economy"]["ledger"][-1]["unit_price_cents"], expected["sublevel_44"])

    def test_crash_after_durable_journal_recovers_economy_event_and_property_together(self):
        crash_root = tempfile.TemporaryDirectory()
        self.addCleanup(crash_root.cleanup)
        seed_kernel = PersistenceKernel(crash_root.name, ALLOWED)
        seed_kernel.initialize_state(initial_state())
        before = seed_kernel.load_state()

        def fault(point: str) -> None:
            if point == "after_journal_durable":
                raise FaultInjectedCrash("property crash")

        fault_kernel = PersistenceKernel(crash_root.name, ALLOWED, fault_injector=fault)
        service = PropertyService(fault_kernel, PROPERTY, CITY_MAP)
        with self.assertRaises(FaultInjectedCrash):
            service.purchase("signalwerk", context=context("crash-buy"))

        self.assertEqual(seed_kernel.load_state(), before)
        recovery_kernel = PersistenceKernel.open_for_recovery(crash_root.name, ALLOWED)
        receipt = GameRecoveryService(recovery_kernel).recover()
        self.assertEqual(receipt.status, "recovered")
        self.assertEqual(receipt.replayed_events, 2)
        recovered = recovery_kernel.load_state()
        self.assertEqual(recovered["event"]["budget_cents"], before["event"]["budget_cents"] - 6_200_000)
        self.assertEqual(recovered["economy"]["ledger"][-1]["kind"], "property_purchase")
        self.assertEqual(recovered["properties"]["owned"]["signalwerk"]["purchase_price_cents"], 6_200_000)

    def test_property_manifest_and_persisted_state_fail_closed(self):
        bad = json.loads(json.dumps(PROPERTY))
        bad["city_map_manifest_version"] = "wrong"
        with self.assertRaises(ValueError):
            PropertyService(self.kernel, bad, CITY_MAP)

        invalid_state = initial_state()
        invalid_state["properties"] = {
            "contract_version": PROPERTY["version"],
            "revision": 1,
            "owned": {
                "hall_of_tribute": {
                    "location_id": "hall_of_tribute",
                    "owner_character_id": "char.property",
                    "purchase_price_cents": 1,
                    "economy_transaction_id": "property:invalid",
                    "event_id": "event-property",
                }
            },
        }
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        invalid_kernel = PersistenceKernel(other.name, ALLOWED)
        invalid_kernel.initialize_state(invalid_state)
        with self.assertRaises(Exception):
            PropertyService(invalid_kernel, PROPERTY, CITY_MAP).current_state()


if __name__ == "__main__":
    unittest.main()
