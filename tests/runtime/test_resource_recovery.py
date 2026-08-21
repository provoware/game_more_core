import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.recovery_service import CharacterRecoveryService, replay_character_event
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ACTION = {
    "action_id": "action.soundcheck",
    "category": "event",
    "risk_profile": "medium",
    "resource_effects": {"energy_delta": -6, "stress_delta": 3},
    "skill_weights": {"technik": 0.5, "musik": 0.3, "konzentration": 0.2},
    "trait_evidence_weights": {"klangfokus": 0.6, "detailmensch": 0.4},
    "prerequisites": [],
}
ALLOWED = {
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
    "system.recovery_performed",
}
CTX = JournalContext(
    "2026-08-21T23:30:00+02:00",
    "session-resource-recovery",
    "player-resource-recovery",
    "character",
    "char.pppoppi",
    "cmd-resource-recovery",
    "runtime",
    "0.7.2-alpha.1",
    "char.pppoppi",
)


class ResourceRecoveryTest(unittest.TestCase):
    def test_replay_resource_event_requires_confirmed_old_value(self):
        state = CharacterState("char.pppoppi", "PPPOPPI", energy=80, stress=20)
        event = {
            "event_type": "character.resources_changed",
            "payload": {
                "source_action": "action.soundcheck",
                "energy": {"old": 80, "delta": -6, "new": 74},
                "stress": {"old": 20, "delta": 3, "new": 23},
            },
        }
        replayed = replay_character_event({"character": state.to_dict()}, event)
        character = CharacterState.from_dict(replayed["character"])
        self.assertEqual((character.energy, character.stress), (74, 23))

        event["payload"]["energy"]["old"] = 79
        with self.assertRaises(ValueError):
            replay_character_event({"character": state.to_dict()}, event)

    def test_recovery_from_pre_action_snapshot_replays_resource_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            start = CharacterState("char.pppoppi", "PPPOPPI", energy=80, stress=20)
            kernel.initialize_state({"character": start.to_dict()})
            kernel.create_snapshot("before_action")

            service = CharacterActionService(ActionResolver(), kernel)
            committed = service.execute(
                start,
                ACTION,
                action_instance_id="resource-recovery-action",
                world_seed="resource-recovery-world",
                journal_context=CTX,
            )
            expected = committed.resolved.character_after.to_dict()

            kernel.state_path.write_text("{broken", encoding="utf-8")
            recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
            receipt = CharacterRecoveryService(recovering).recover(context=CTX)
            recovered = CharacterState.from_dict(recovering.load_state()["character"])

            self.assertEqual(receipt.status, "recovered")
            self.assertEqual(recovered.to_dict(), expected)
            self.assertEqual((recovered.energy, recovered.stress), (74, 23))

    def test_character_resource_bounds_reject_invalid_loaded_state(self):
        with self.assertRaises(ValueError):
            CharacterState("x", "X", energy=-1).validate()
        with self.assertRaises(ValueError):
            CharacterState("x", "X", stress=101).validate()


if __name__ == "__main__":
    unittest.main()
