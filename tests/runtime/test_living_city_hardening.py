import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.economy_service import EconomyService
from bunkerfrequenz.application.world_service import WorldService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.world import WorldState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel

ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
WORLD = json.loads((ROOT / "manifests" / "WORLD_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def character_context(command_id: str, character_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T17:00:00+02:00",
        "living-city-hardening",
        character_id,
        "character",
        character_id,
        command_id,
        "living-city-hardening-test",
        "0.8.5-d1",
        character_id,
    )


def event_context(command_id: str, event_id: str, character_id: str = "player-1") -> JournalContext:
    return JournalContext(
        "2026-08-22T17:00:00+02:00",
        "living-city-hardening",
        character_id,
        "event",
        event_id,
        command_id,
        "living-city-hardening-test",
        "0.8.5-d1",
        character_id,
    )


def event_state(event_id: str = "event-hardening") -> EventState:
    return EventState(
        event_id=event_id,
        display_name="Hardening Event",
        location={
            "location_id": "loc-a4-demo",
            "display_name": "A4 Testlocation",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=500_000,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-1", "role": "leitung", "status": "confirmed"}],
        equipment=[],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


class WorldStateHardeningTests(unittest.TestCase):
    def test_booking_counter_cannot_move_back_behind_issued_ids(self):
        world = WorldState.empty_from_manifest(WORLD)
        data = world.to_dict()
        data["players"]["player-1"] = {
            "booking_id": "BF-000007",
            "display_name": "Ria",
            "intro_acknowledged": False,
        }
        data["positions"]["player-1"] = {
            "city_id": "berlin",
            "district_id": "lichtenberg",
            "location_id": "concrete_orbit",
        }
        data["housing"]["player-1"] = {"status": "homeless", "host_character_id": None}
        data["honors"]["player-1"] = []
        data["storefront_reads"]["player-1"] = []
        data["mini_games"]["player-1"] = WorldState.default_minigames()
        data["next_booking_number"] = 7
        with self.assertRaisesRegex(ValueError, "next_booking_number"):
            WorldState.from_dict(data)
        data["next_booking_number"] = 8
        self.assertEqual(WorldState.from_dict(data).next_booking_number, 8)

    def test_booking_id_format_is_fail_closed(self):
        world = WorldState.empty_from_manifest(WORLD)
        data = world.to_dict()
        data["players"]["player-1"] = {
            "booking_id": "BF-7",
            "display_name": "Ria",
            "intro_acknowledged": False,
        }
        data["positions"]["player-1"] = {
            "city_id": "berlin",
            "district_id": "lichtenberg",
            "location_id": "concrete_orbit",
        }
        data["housing"]["player-1"] = {"status": "homeless", "host_character_id": None}
        data["honors"]["player-1"] = []
        data["storefront_reads"]["player-1"] = []
        data["mini_games"]["player-1"] = WorldState.default_minigames()
        with self.assertRaisesRegex(ValueError, "Format"):
            WorldState.from_dict(data)

    def test_impossible_xoxo_board_is_rejected(self):
        world = WorldState.empty_from_manifest(WORLD)
        data = world.to_dict()
        data["players"]["player-1"] = {
            "booking_id": "BF-000001",
            "display_name": "Ria",
            "intro_acknowledged": False,
        }
        data["positions"]["player-1"] = {
            "city_id": "berlin",
            "district_id": "lichtenberg",
            "location_id": "concrete_orbit",
        }
        data["housing"]["player-1"] = {"status": "homeless", "host_character_id": None}
        data["honors"]["player-1"] = []
        data["storefront_reads"]["player-1"] = []
        data["mini_games"]["player-1"] = WorldState.default_minigames()
        data["next_booking_number"] = 2
        data["mini_games"]["player-1"]["xoxo"].update(
            board=["O", "O", "O", "", "", "", "", "", ""],
            status="lost",
            round=1,
        )
        with self.assertRaisesRegex(ValueError, "Zuganzahl"):
            WorldState.from_dict(data)

    def test_party_check_flags_cannot_contradict_each_other(self):
        world = WorldState.empty_from_manifest(WORLD)
        data = world.to_dict()
        data["party_checks"]["event-1"] = {
            "triggered": False,
            "resolved": False,
            "choice_id": None,
        }
        with self.assertRaisesRegex(ValueError, "Nicht ausgelöste"):
            WorldState.from_dict(data)


class WorldCommandHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.player1 = CharacterState("player-1", "Ria")
        self.kernel.initialize_state({"character": self.player1.to_dict()})
        self.service = WorldService(self.kernel, WORLD)
        self.service.ensure_player(self.player1, context=character_context("register-1", "player-1"))
        self.player2 = CharacterState("player-2", "Mika")
        self.player3 = CharacterState("player-3", "Nox")
        self.service.ensure_player(self.player2, context=character_context("register-2", "player-2"))
        self.service.ensure_player(self.player3, context=character_context("register-3", "player-3"))

    def test_housing_command_id_is_bound_to_original_host(self):
        first = self.service.set_guest_housing(
            "player-3", "player-1", context=character_context("housing-same", "player-3")
        )
        replay = self.service.set_guest_housing(
            "player-3", "player-1", context=character_context("housing-same", "player-3")
        )
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        with self.assertRaisesRegex(PersistenceError, "anderem World-Request"):
            self.service.set_guest_housing(
                "player-3", "player-2", context=character_context("housing-same", "player-3")
            )

    def test_trust_command_id_cannot_change_violation(self):
        self.service.record_trust_violation(
            "player-1",
            "player-2",
            "fraud",
            context=character_context("trust-same", "player-1"),
        )
        with self.assertRaisesRegex(PersistenceError, "anderem World-Request"):
            self.service.record_trust_violation(
                "player-1",
                "player-2",
                "betrayal",
                context=character_context("trust-same", "player-1"),
            )

    def test_final_trust_cycle_retry_stays_idempotently_blocked_for_that_action(self):
        self.service.record_trust_violation(
            "player-1",
            "player-2",
            "fraud",
            context=character_context("trust-start", "player-1"),
        )
        final_context = None
        final_result = None
        for cycle in range(1, 13):
            final_context = character_context(f"trust-cycle-{cycle}", "player-1")
            final_result = self.service.consume_trust_cycle(
                "player-1", "player-2", context=final_context
            )
        self.assertEqual(final_result.metadata["effectiveness_bps"], 0)
        retry = self.service.consume_trust_cycle(
            "player-1", "player-2", context=final_context
        )
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.metadata["effectiveness_bps"], 0)
        self.assertEqual(self.service.effectiveness_bps("player-1", "player-2"), 10000)

    def test_poker_rank_covers_real_five_card_categories(self):
        rank = self.service._poker_rank
        self.assertGreater(rank(["9H", "TH", "JH", "QH", "KH"]), rank(["9C", "9D", "9H", "9S", "2D"]))
        self.assertGreater(rank(["2H", "5H", "7H", "9H", "KH"]), rank(["5C", "6D", "7H", "8S", "9D"]))
        self.assertGreater(rank(["AC", "2D", "3H", "4S", "5D"]), rank(["KC", "KD", "7H", "5S", "2D"]))
        self.assertEqual(rank(["AC", "2D", "3H", "4S", "5D"]), (4, [5]))


class EconomyCityContextHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        event = event_state()
        economy = EconomyState(catalog={
            "equipment.pa": {
                "label": "PA",
                "base_price_cents": 10_000,
                "volatility_bps": 0,
                "consumable": False,
            }
        })
        self.kernel.initialize_state({"event": event.to_dict()})
        self.service = EconomyService(self.kernel)
        self.service.initialize(economy, context=event_context("economy-init", event.event_id))
        self.event_id = event.event_id

    def test_transaction_command_id_is_bound_to_city_price_context(self):
        ctx = event_context("city-buy", self.event_id)
        first = self.service.transact(
            "buy", "equipment.pa", 1, context=ctx, price_multiplier_bps=9200
        )
        replay = self.service.transact(
            "buy", "equipment.pa", 1, context=ctx, price_multiplier_bps=9200
        )
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        with self.assertRaisesRegex(PersistenceError, "Stadt-Preisfaktor"):
            self.service.transact(
                "buy", "equipment.pa", 1, context=ctx, price_multiplier_bps=11500
            )


if __name__ == "__main__":
    unittest.main()
