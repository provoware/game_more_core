import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.application.property_service import PropertyService
from bunkerfrequenz.application.property_upgrade_service import PropertyUpgradeService
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
UPGRADES = json.loads((ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def event(*, budget_cents: int = 20_000_000) -> EventState:
    return EventState(
        event_id="event-upgrade",
        display_name="Upgrade Test",
        location={
            "location_id": "signalwerk",
            "display_name": "Signalwerk",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=budget_cents,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "char.upgrade", "role": "leitung", "status": "confirmed"}],
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
        "2026-08-22T19:45:00+02:00",
        "session-upgrade",
        "player-upgrade",
        "event",
        "event-upgrade",
        command_id,
        "property-upgrade-test",
        "0.8.6-b1",
        "char.upgrade",
    )


def initial_state(*, budget_cents: int = 20_000_000) -> dict:
    return {
        "character": CharacterState("char.upgrade", "Upgrade Crew").to_dict(),
        "event": event(budget_cents=budget_cents).to_dict(),
        "economy": economy().to_dict(),
    }


class PropertyUpgradeServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.kernel.initialize_state(initial_state())
        self.properties = PropertyService(self.kernel, PROPERTY, CITY_MAP)
        self.properties.purchase("signalwerk", context=context("buy-signalwerk"))
        self.service = PropertyUpgradeService(self.kernel, UPGRADES, PROPERTY, CITY_MAP)

    def test_three_levels_use_exact_cost_ladder_without_market_tick(self):
        before = self.kernel.load_state()
        market_tick = before["economy"]["market_tick"]
        expected_costs = [558_000, 837_000, 1_255_500]
        for level, expected_cost in enumerate(expected_costs, start=1):
            result = self.service.upgrade(
                "signalwerk", "stage", context=context(f"stage-l{level}")
            )
            self.assertEqual(result.new_level, level)
            self.assertEqual(result.upgrade_cost_cents, expected_cost)
            self.assertEqual(result.economy.market_tick, market_tick)
            self.assertEqual(result.economy.ledger[-1]["kind"], "property_upgrade")
            self.assertEqual(result.economy.ledger[-1]["unit_price_cents"], expected_cost)
            self.assertEqual(
                result.economy.ledger[-1]["item_id"],
                f"property_upgrade:signalwerk:stage:{level}",
            )
        state = self.kernel.load_state()
        stage = state["property_upgrades"]["properties"]["signalwerk"]["upgrades"]["stage"]
        self.assertEqual(stage["level"], 3)
        self.assertEqual(len(stage["economy_transaction_ids"]), 3)
        expected_budget = 20_000_000 - 6_200_000 - sum(expected_costs)
        self.assertEqual(state["event"]["budget_cents"], expected_budget)

    def test_max_level_and_unowned_or_invalid_slot_fail_without_write(self):
        for level in range(1, 4):
            self.service.upgrade("signalwerk", "power", context=context(f"power-l{level}"))
        records_before = self.kernel.read_records()
        state_before = self.kernel.load_state()
        with self.assertRaises(ValueError):
            self.service.upgrade("signalwerk", "power", context=context("power-l4"))
        self.assertEqual(self.kernel.read_records(), records_before)
        self.assertEqual(self.kernel.load_state(), state_before)

        with self.assertRaises(ValueError):
            self.service.upgrade("plattenstudio", "studio", context=context("not-owned"))
        with self.assertRaises(ValueError):
            self.service.upgrade("signalwerk", "office", context=context("wrong-slot"))
        self.assertEqual(self.kernel.read_records(), records_before)

    def test_same_command_is_idempotent(self):
        first = self.service.upgrade("signalwerk", "bar", context=context("bar-once"))
        replay = self.service.upgrade("signalwerk", "bar", context=context("bar-once"))
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.committed_event_ids, ())
        self.assertEqual(replay.new_level, 1)
        upgrade_records = [
            record for record in self.kernel.read_records()
            if record["event_type"] == "world.property_upgraded"
        ]
        self.assertEqual(len(upgrade_records), 1)

    def test_insufficient_budget_fails_before_write(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        kernel = PersistenceKernel(other.name, ALLOWED)
        # Enough for Signalwerk itself, but only 1 cent remains afterwards.
        kernel.initialize_state(initial_state(budget_cents=6_200_001))
        PropertyService(kernel, PROPERTY, CITY_MAP).purchase(
            "signalwerk", context=context("poor-buy")
        )
        service = PropertyUpgradeService(kernel, UPGRADES, PROPERTY, CITY_MAP)
        before_records = kernel.read_records()
        before_state = kernel.load_state()
        with self.assertRaises(ValueError):
            service.upgrade("signalwerk", "stage", context=context("poor-upgrade"))
        self.assertEqual(kernel.read_records(), before_records)
        self.assertEqual(kernel.load_state(), before_state)

    def test_crash_after_durable_journal_recovers_upgrade_and_economy_together(self):
        crash_root = tempfile.TemporaryDirectory()
        self.addCleanup(crash_root.cleanup)
        seed = PersistenceKernel(crash_root.name, ALLOWED)
        seed.initialize_state(initial_state())
        PropertyService(seed, PROPERTY, CITY_MAP).purchase(
            "signalwerk", context=context("crash-buy")
        )
        before = seed.load_state()

        def fault(point: str) -> None:
            if point == "after_journal_durable":
                raise FaultInjectedCrash("upgrade crash")

        fault_kernel = PersistenceKernel(crash_root.name, ALLOWED, fault_injector=fault)
        service = PropertyUpgradeService(fault_kernel, UPGRADES, PROPERTY, CITY_MAP)
        with self.assertRaises(FaultInjectedCrash):
            service.upgrade("signalwerk", "stage", context=context("crash-upgrade"))

        self.assertEqual(seed.load_state(), before)
        recovery_kernel = PersistenceKernel.open_for_recovery(crash_root.name, ALLOWED)
        receipt = GameRecoveryService(recovery_kernel).recover()
        self.assertEqual(receipt.status, "recovered")
        self.assertEqual(receipt.replayed_events, 2)
        recovered = recovery_kernel.load_state()
        self.assertEqual(recovered["economy"]["ledger"][-1]["kind"], "property_upgrade")
        self.assertEqual(recovered["economy"]["ledger"][-1]["unit_price_cents"], 558_000)
        self.assertEqual(
            recovered["property_upgrades"]["properties"]["signalwerk"]["upgrades"]["stage"]["level"],
            1,
        )
        self.assertEqual(
            recovered["event"]["budget_cents"],
            before["event"]["budget_cents"] - 558_000,
        )

    def test_manifest_mismatch_fails_closed(self):
        bad = json.loads(json.dumps(UPGRADES))
        bad["property_manifest_version"] = "wrong"
        with self.assertRaises(ValueError):
            PropertyUpgradeService(self.kernel, bad, PROPERTY, CITY_MAP)


if __name__ == "__main__":
    unittest.main()
