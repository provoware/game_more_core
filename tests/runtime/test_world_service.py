import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.application.world_service import WorldService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.domain.world import WorldState
from bunkerfrequenz.infrastructure.persistence import (
    FaultInjectedCrash,
    JournalContext,
    PersistenceKernel,
)

ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
WORLD = json.loads((ROOT / "manifests" / "WORLD_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def character_context(command_id: str, character_id: str = "player-1") -> JournalContext:
    return JournalContext(
        "2026-08-22T16:00:00+02:00",
        "world-test-session",
        character_id,
        "character",
        character_id,
        command_id,
        "world-test",
        "0.8.5-d1",
        character_id,
    )


def event_context(command_id: str, event_id: str, character_id: str = "player-1") -> JournalContext:
    return JournalContext(
        "2026-08-22T16:00:00+02:00",
        "world-test-session",
        character_id,
        "event",
        event_id,
        command_id,
        "world-test",
        "0.8.5-d1",
        character_id,
    )


def event_state(event_id: str, *, phase: str = "draft", revision: int = 0) -> EventState:
    return EventState(
        event_id=event_id,
        display_name="Living City Testnacht",
        location={
            "location_id": "loc-a4-demo",
            "display_name": "A4 Testlocation",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-1", "role": "leitung", "status": "confirmed"}],
        equipment=[],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
        phase=phase,
        revision=revision,
    )


class WorldServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.player1 = CharacterState("player-1", "Ria")
        self.kernel.initialize_state({"character": self.player1.to_dict()})
        self.service = WorldService(self.kernel, WORLD)
        self.service.ensure_player(self.player1, context=character_context("register-1"))

    def register(self, character_id: str, name: str):
        character = CharacterState(character_id, name)
        return self.service.ensure_player(
            character,
            context=character_context(f"register-{character_id}", character_id),
        )

    def test_booking_ids_never_duplicate_and_exactly_one_home_is_missing(self):
        self.register("player-2", "Mika")
        self.register("player-3", "Nox")
        world = WorldState.from_dict(self.kernel.load_state()["world"])

        booking_ids = [entry["booking_id"] for entry in world.players.values()]
        self.assertEqual(booking_ids, ["BF-000001", "BF-000002", "BF-000003"])
        self.assertEqual(len(booking_ids), len(set(booking_ids)))
        self.assertEqual(
            sum(home["status"] != "independent" for home in world.housing.values()),
            1,
        )
        self.assertEqual(world.housing["player-3"]["status"], "homeless")
        self.assertEqual(world.housing["player-1"]["status"], "independent")
        self.assertEqual(world.housing["player-2"]["status"], "independent")

        corrupt = world.to_dict()
        corrupt["players"]["player-3"]["booking_id"] = corrupt["players"]["player-1"]["booking_id"]
        with self.assertRaisesRegex(ValueError, "Einbuchungs-ID.*doppelt"):
            WorldState.from_dict(corrupt)

    def test_shortage_player_can_be_guest_but_shortage_remains_exactly_one(self):
        self.register("player-2", "Mika")
        result = self.service.set_guest_housing(
            "player-2",
            "player-1",
            context=character_context("guest-2-at-1", "player-2"),
        )
        self.assertFalse(result.idempotent_replay)
        world = result.world
        self.assertEqual(
            world.housing["player-2"],
            {"status": "guest", "host_character_id": "player-1"},
        )
        self.assertEqual(
            sum(home["status"] != "independent" for home in world.housing.values()),
            1,
        )
        with self.assertRaisesRegex(ValueError, "Nur die Person ohne"):
            self.service.set_guest_housing(
                "player-1",
                "player-2",
                context=character_context("wrong-guest", "player-1"),
            )

    def test_trust_block_is_directed_for_exactly_twelve_effect_cycles(self):
        self.register("player-2", "Mika")
        recorded = self.service.record_trust_violation(
            "player-1",
            "player-2",
            "fraud",
            context=character_context("fraud-1-to-2", "player-1"),
        )
        self.assertEqual(recorded.world.trust_blocks[0]["remaining_cycles"], 12)
        self.assertEqual(self.service.effectiveness_bps("player-1", "player-2"), 0)
        self.assertEqual(self.service.effectiveness_bps("player-2", "player-1"), 10000)

        for cycle in range(1, 13):
            result = self.service.consume_trust_cycle(
                "player-1",
                "player-2",
                context=character_context(f"trust-cycle-{cycle}", "player-1"),
            )
            self.assertEqual(result.metadata["effectiveness_bps"], 0)
            if cycle < 12:
                self.assertEqual(self.service.effectiveness_bps("player-1", "player-2"), 0)
        self.assertEqual(self.service.effectiveness_bps("player-1", "player-2"), 10000)
        self.assertEqual(self.service.effectiveness_bps("player-2", "player-1"), 10000)

    def test_movement_changes_server_price_context_by_city(self):
        self.assertEqual(self.service.city_price_multiplier_bps("player-1"), 10000)
        moved = self.service.move(
            "player-1",
            city_id="leipzig",
            district_id="plagwitz",
            location_id="plagwitz_werk",
            context=character_context("move-leipzig"),
        )
        self.assertEqual(moved.world.positions["player-1"]["city_id"], "leipzig")
        self.assertEqual(self.service.city_price_multiplier_bps("player-1"), 9200)
        self.service.move(
            "player-1",
            city_id="hamburg",
            district_id="wilhelmsburg",
            location_id="wilhelmsburg_halle",
            context=character_context("move-hamburg"),
        )
        self.assertEqual(self.service.city_price_multiplier_bps("player-1"), 11500)
        with self.assertRaisesRegex(ValueError, "Unbekannte Stadt-/Bezirk"):
            self.service.move(
                "player-1",
                city_id="berlin",
                district_id="plagwitz",
                location_id=None,
                context=character_context("bad-move"),
            )

    def test_storefront_notes_are_returned_as_flat_unclassified_sequence(self):
        self.service.move(
            "player-1",
            city_id="berlin",
            district_id="neukoelln",
            location_id="tape_kiosk",
            context=character_context("move-tape"),
        )
        first = self.service.inspect_storefront(
            "player-1",
            context=character_context("read-window"),
        )
        second = self.service.inspect_storefront(
            "player-1",
            context=character_context("read-window"),
        )
        self.assertEqual(len(first.metadata["note_keys"]), 4)
        self.assertNotIn("secret_index", first.metadata)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.metadata, first.metadata)

    def test_poker_slot_and_xoxo_are_deterministic_score_only_games(self):
        self.service.move(
            "player-1",
            city_id="berlin",
            district_id="neukoelln",
            location_id="tape_kiosk",
            context=character_context("move-games"),
        )
        slot_first = self.service.play_minigame(
            "player-1", "slot", cell=None, context=character_context("slot-001")
        )
        slot_replay = self.service.play_minigame(
            "player-1", "slot", cell=None, context=character_context("slot-001")
        )
        self.assertEqual(slot_first.metadata, slot_replay.metadata)
        self.assertTrue(slot_replay.idempotent_replay)
        self.assertNotIn("money", slot_first.metadata)
        self.assertNotIn("stake", slot_first.metadata)

        xoxo = self.service.play_minigame(
            "player-1", "xoxo", cell=4, context=character_context("xoxo-001")
        )
        self.assertEqual(xoxo.metadata["game_id"], "xoxo")
        self.assertEqual(xoxo.metadata["board"][4], "X")
        self.assertIn("O", xoxo.metadata["board"])

        self.service.move(
            "player-1",
            city_id="berlin",
            district_id="mitte",
            location_id="plattenstudio",
            context=character_context("move-poker"),
        )
        poker = self.service.play_minigame(
            "player-1", "poker", cell=None, context=character_context("poker-001")
        )
        self.assertEqual(len(poker.metadata["player_hand"]), 5)
        self.assertEqual(len(poker.metadata["house_hand"]), 5)
        self.assertIn(poker.metadata["outcome"], {"win", "draw", "loss"})
        self.assertNotIn("wager", poker.metadata)

    def test_unofficial_party_check_is_stable_and_has_exactly_three_safe_choices(self):
        threshold = 40
        event_id = next(
            f"event-party-{index}"
            for index in range(1, 500)
            if self.service._percent("party-check", f"event-party-{index}", "concrete_orbit") < threshold
        )
        event_service = EventStateService(self.kernel)
        event = event_state(event_id)
        event_service.create(event, context=event_context("party-create", event_id))
        self.service.set_party_mode(
            event_id,
            "unofficial",
            context=event_context("party-mode", event_id),
        )
        current = event
        for index, phase in enumerate(("planning", "procurement", "transport", "setup", "soundcheck", "live"), start=1):
            result = event_service.transition_phase(
                current,
                phase,
                context=event_context(f"party-phase-{index}", event_id),
                reason="world_test",
            )
            current = result.event

        checked = self.service.check_party_encounter(
            event_id,
            context=event_context("party-check", event_id),
        )
        self.assertTrue(checked.metadata["triggered"])
        self.assertEqual(len(checked.metadata["choices"]), 3)
        self.assertEqual(
            {item["choice_id"] for item in checked.metadata["choices"]},
            {"cooperate_and_end", "accept_conditions_reduce", "cancel_and_take_consequences"},
        )
        replay = self.service.check_party_encounter(
            event_id,
            context=event_context("party-check-other-command", event_id),
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertTrue(replay.metadata["triggered"])

        before = self.kernel.load_state()
        resolved = self.service.resolve_party_encounter(
            event_id,
            "accept_conditions_reduce",
            context=event_context("party-resolve", event_id),
        )
        after = self.kernel.load_state()
        self.assertEqual(resolved.metadata["choice_id"], "accept_conditions_reduce")
        self.assertGreater(after["character"]["stress"], before["character"]["stress"])
        self.assertTrue(after["world"]["party_checks"][event_id]["resolved"])

    def test_confirmed_settlement_updates_district_once_and_awards_good_and_bad_legacy(self):
        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED)
            character = CharacterState("player-1", "Ria", stress=4, reputation=6)
            event = event_state("event-settle", phase="completed", revision=2)
            settlement = SettlementState(
                event_id=event.event_id,
                settlement_id="settlement:world-1",
                contract_version="0.8.3-c1",
                incident_ids=["incident-1"],
                effects={
                    "budget_delta_cents": 0,
                    "reputation_delta": 6,
                    "crew_stress_delta": 4,
                    "stability_delta": 6,
                    "heat_delta": 10,
                },
                budget={"old": 100_000, "delta": 0, "new": 100_000},
                character_id="player-1",
                stress={"old": 0, "delta": 4, "new": 4},
                reputation={"old": 0, "delta": 6, "new": 6},
                event_revision={"old": 0, "new": 2},
                economy_revision={"old": 0, "new": 1},
                incident_revision={"old": 0, "new": 1},
            )
            kernel.initialize_state({
                "character": character.to_dict(),
                "event": event.to_dict(),
                "settlement": settlement.to_dict(),
            })
            service = WorldService(kernel, WORLD)
            first = service.apply_confirmed_settlement(
                context=event_context("world-settlement", event.event_id)
            )
            second = service.apply_confirmed_settlement(
                context=event_context("world-settlement-retry", event.event_id)
            )
            metrics = first.world.districts["berlin"]["lichtenberg"]
            self.assertEqual(metrics, {
                "heat": 30,
                "prestige": 23,
                "police_pressure": 18,
                "scene_activity": 33,
            })
            self.assertTrue(second.idempotent_replay)
            self.assertEqual(first.world.applied_settlements, ["settlement:world-1"])
            self.assertEqual(
                set(first.world.honors["player-1"]),
                {"betonstarter", "krisenlotse", "pegelphantom", "nachtminister"},
            )
            self.assertEqual(len(first.world.great_deeds), 4)
            self.assertIn("negative", {deed["valence"] for deed in first.world.great_deeds})

    def test_world_move_recovers_after_journal_durable_crash(self):
        armed = {"value": False}

        def fault(point: str) -> None:
            if armed["value"] and point == "after_journal_durable":
                raise FaultInjectedCrash("world crash")

        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED, fault_injector=fault)
            character = CharacterState("player-1", "Ria")
            kernel.initialize_state({"character": character.to_dict()})
            service = WorldService(kernel, WORLD)
            service.ensure_player(character, context=character_context("recover-register"))
            before = kernel.load_state()["world"]
            armed["value"] = True
            with self.assertRaises(FaultInjectedCrash):
                service.move(
                    "player-1",
                    city_id="leipzig",
                    district_id="plagwitz",
                    location_id="plagwitz_werk",
                    context=character_context("recover-move"),
                )
            self.assertEqual(kernel.load_state()["world"], before)

            recovering = PersistenceKernel.open_for_recovery(root, ALLOWED)
            receipt = GameRecoveryService(recovering).recover()
            self.assertEqual(receipt.status, "recovered")
            recovered = WorldState.from_dict(recovering.load_state()["world"])
            self.assertEqual(recovered.positions["player-1"]["city_id"], "leipzig")
            self.assertEqual(recovered.positions["player-1"]["location_id"], "plagwitz_werk")


if __name__ == "__main__":
    unittest.main()
