import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.event import EventState, PHASES, PHASE_TRANSITIONS
from bunkerfrequenz.infrastructure.persistence import FaultInjectedCrash, JournalContext, PersistenceError, PersistenceKernel


ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "event.created",
    "event.planning_updated",
    "event.phase_changed",
    "character.profile_updated",
    "character.resources_changed",
    "character.skill_xp_gained",
    "character.skill_level_up",
    "character.trait_evidence_gained",
    "character.trait_unlocked",
    "character.trait_tier_up",
    "character.specialization_changed",
    "character.level_up",
    "character.resonance_xp_gained",
    "character.resonance_rank_up",
    "character.biography_entry_added",
    "system.recovery_performed",
}
ACTION = {
    "action_id": "action.soundcheck",
    "category": "event",
    "risk_profile": "medium",
    "resource_effects": {"energy_delta": -6, "stress_delta": 3},
    "skill_weights": {"technik": 0.5, "musik": 0.3, "konzentration": 0.2},
    "trait_evidence_weights": {"klangfokus": 0.6, "detailmensch": 0.4},
    "prerequisites": [],
}


def context(
    command_id: str,
    *,
    event_id: str = "event-1",
    entity_type: str = "event",
    character_id: str | None = None,
) -> JournalContext:
    return JournalContext(
        "2026-08-22T01:00:00+02:00",
        "session-0.8.1",
        "player-0.8.1",
        entity_type,
        event_id,
        command_id,
        "runtime",
        "0.8.1-alpha.1",
        character_id,
    )


def planned_event(*, phase: str = "draft", revision: int = 0) -> EventState:
    return EventState(
        event_id="event-1",
        display_name="Testfrequenz",
        location={
            "location_id": "location.testbunker",
            "display_name": "Testbunker",
            "region": "Brandenburg",
            "access_status": "fictionalized",
        },
        budget_cents=250_000,
        acts=[{"act_id": "act.test", "display_name": "Test Act", "status": "confirmed"}],
        crew=[{"character_id": "char.pppoppi", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "ready"}],
        time_window={
            "start_local": "2026-09-05T20:00:00+02:00",
            "end_local": "2026-09-06T08:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
        phase=phase,
        revision=revision,
    )


def crash_at(target: str):
    def injector(point: str) -> None:
        if point == target:
            raise FaultInjectedCrash(point)

    return injector


class EventStateContractTest(unittest.TestCase):
    def test_defaults_and_roundtrip_are_strict(self):
        state = EventState("event-x", "Rohentwurf")
        self.assertEqual(state.phase, "draft")
        self.assertEqual(state.safety_status, "unreviewed")
        self.assertEqual(state.budget_cents, 0)
        self.assertEqual(state.revision, 0)
        self.assertEqual(EventState.from_dict(state.to_dict()).to_dict(), state.to_dict())

    def test_duplicate_crew_and_invalid_time_window_are_rejected(self):
        duplicate = planned_event()
        duplicate.crew.append(dict(duplicate.crew[0]))
        with self.assertRaises(ValueError):
            duplicate.validate()

        invalid_time = planned_event()
        invalid_time.time_window = {
            "start_local": "2026-09-06T08:00:00+02:00",
            "end_local": "2026-09-05T20:00:00+02:00",
            "timezone": "Europe/Berlin",
        }
        with self.assertRaises(ValueError):
            invalid_time.validate()

        naive_time = planned_event()
        naive_time.time_window = {
            "start_local": "2026-09-05T20:00:00",
            "end_local": "2026-09-06T08:00:00",
            "timezone": "Europe/Berlin",
        }
        with self.assertRaises(ValueError):
            naive_time.validate()

    def test_physical_phase_gate_requires_location_time_and_clearance(self):
        state = planned_event(phase="procurement", revision=2)
        self.assertEqual(state.transition_to("transport").phase, "transport")

        for mutate in (
            lambda value: setattr(value, "location", None),
            lambda value: value.location.__setitem__("access_status", "unverified"),
            lambda value: setattr(value, "time_window", None),
            lambda value: setattr(value, "safety_status", "restricted"),
        ):
            candidate = planned_event(phase="procurement", revision=2)
            mutate(candidate)
            with self.assertRaises(ValueError):
                candidate.transition_to("transport")

    def test_illegal_and_terminal_phase_transitions_are_rejected(self):
        with self.assertRaises(ValueError):
            planned_event().transition_to("live")
        with self.assertRaises(ValueError):
            planned_event(phase="completed").transition_to("planning")
        with self.assertRaises(ValueError):
            planned_event(phase="cancelled").transition_to("planning")

    def test_manifest_phase_contract_matches_domain(self):
        manifest = json.loads((ROOT / "manifests/EVENT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
        journal = json.loads((ROOT / "manifests/JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(tuple(manifest["fields"]["phase"]["values"]), PHASES)
        normalized = {key: set(value) for key, value in manifest["phase_transitions"].items()}
        self.assertEqual(normalized, {key: set(value) for key, value in PHASE_TRANSITIONS.items()})
        for event_type in ("event.created", "event.planning_updated", "event.phase_changed"):
            self.assertIn(event_type, journal["event_types"])


class EventStateServiceTest(unittest.TestCase):
    def test_create_update_phase_and_idempotency(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = EventStateService(kernel)
            event = planned_event()

            created = service.create(event, context=context("cmd-create"))
            self.assertFalse(created.idempotent_replay)
            self.assertEqual(len(created.committed_event_ids), 1)
            replay = service.create(event, context=context("cmd-create"))
            self.assertTrue(replay.idempotent_replay)
            self.assertEqual(replay.committed_event_ids, ())

            updated = service.update_planning(
                created.event,
                {"budget_cents": 300_000, "display_name": "Neue Frequenz"},
                context=context("cmd-plan"),
            )
            self.assertEqual(updated.event.budget_cents, 300_000)
            self.assertEqual(updated.event.display_name, "Neue Frequenz")
            self.assertEqual(updated.event.revision, 1)
            update_replay = service.update_planning(
                created.event,
                {"budget_cents": 300_000, "display_name": "Neue Frequenz"},
                context=context("cmd-plan"),
            )
            self.assertTrue(update_replay.idempotent_replay)
            self.assertEqual(update_replay.event.revision, 1)

            planning = service.transition_phase(
                updated.event,
                "planning",
                context=context("cmd-phase"),
                reason="Planung freigegeben",
            )
            self.assertEqual(planning.event.phase, "planning")
            self.assertEqual(planning.event.revision, 2)
            phase_replay = service.transition_phase(
                updated.event,
                "planning",
                context=context("cmd-phase"),
                reason="Planung freigegeben",
            )
            self.assertTrue(phase_replay.idempotent_replay)

            with self.assertRaises(PersistenceError):
                service.transition_phase(
                    updated.event,
                    "cancelled",
                    context=context("cmd-phase"),
                    reason="anderer Inhalt",
                )

    def test_stale_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = EventStateService(kernel)
            created = service.create(planned_event(), context=context("cmd-create"))
            updated = service.update_planning(
                created.event,
                {"budget_cents": 275_000},
                context=context("cmd-update-1"),
            )
            self.assertEqual(updated.event.revision, 1)
            with self.assertRaises(PersistenceError):
                service.update_planning(
                    created.event,
                    {"budget_cents": 280_000},
                    context=context("cmd-update-stale"),
                )

    def test_character_and_event_blocks_survive_each_other(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            event_service = EventStateService(kernel)
            created = event_service.create(planned_event(), context=context("cmd-event-create"))

            character = CharacterState("char.pppoppi", "PPPOPPI")
            profile = CharacterProfileService(kernel)
            changed_character = profile.update(
                character,
                {"alias": "Basskopf"},
                event_id="profile-event-1",
                transaction_id="tx-profile-event-1",
                context=context(
                    "cmd-profile",
                    event_id="char.pppoppi",
                    entity_type="character",
                    character_id="char.pppoppi",
                ),
            )
            after_profile = kernel.load_state()
            self.assertEqual(EventState.from_dict(after_profile["event"]).to_dict(), created.event.to_dict())
            self.assertEqual(after_profile["character"]["alias"], "Basskopf")

            action = CharacterActionService(ActionResolver(), kernel)
            action.execute(
                changed_character,
                ACTION,
                action_instance_id="action-with-event",
                world_seed="event-world",
                journal_context=context(
                    "cmd-action",
                    event_id="char.pppoppi",
                    entity_type="character",
                    character_id="char.pppoppi",
                ),
            )
            after_action = kernel.load_state()
            self.assertEqual(EventState.from_dict(after_action["event"]).to_dict(), created.event.to_dict())
            self.assertLess(after_action["character"]["energy"], 100)

            event_service.update_planning(
                created.event,
                {"budget_cents": 260_000},
                context=context("cmd-event-plan"),
            )
            after_event_update = kernel.load_state()
            self.assertIn("character", after_event_update)
            self.assertEqual(after_event_update["character"]["alias"], "Basskopf")
            self.assertEqual(after_event_update["event"]["budget_cents"], 260_000)

    def test_game_recovery_replays_durable_event_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = EventStateService(kernel)
            created = service.create(planned_event(), context=context("cmd-create"))
            kernel.create_snapshot("event_created")

            crashing = PersistenceKernel(tmp, ALLOWED, fault_injector=crash_at("after_journal_durable"))
            crashing_service = EventStateService(crashing)
            with self.assertRaises(FaultInjectedCrash):
                crashing_service.update_planning(
                    created.event,
                    {"budget_cents": 77_700},
                    context=context("cmd-crash-update"),
                )

            with self.assertRaises(PersistenceError):
                PersistenceKernel(tmp, ALLOWED)

            recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
            receipt = GameRecoveryService(recovering).recover(
                context=context("cmd-recovery", event_id="event-1")
            )
            self.assertEqual(receipt.status, "recovered")
            recovered = EventState.from_dict(recovering.load_state()["event"])
            self.assertEqual(recovered.budget_cents, 77_700)
            self.assertEqual(recovered.revision, 1)


if __name__ == "__main__":
    unittest.main()
