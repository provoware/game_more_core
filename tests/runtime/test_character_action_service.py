import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel

ACTION = {
    "action_id":"action.soundcheck","category":"event","risk_profile":"medium",
    "skill_weights":{"technik":0.5,"musik":0.3,"konzentration":0.2},
    "trait_evidence_weights":{"klangfokus":0.6,"detailmensch":0.4},"prerequisites":[]
}
ALLOWED = {"character.skill_xp_gained","character.skill_level_up","character.trait_evidence_gained","character.trait_unlocked","character.trait_tier_up","character.specialization_changed","character.level_up"}
CTX = JournalContext("2026-08-21T16:00:00+02:00", "s-1", "p-1", "character", "c-1", "cmd-1", "runtime", "0.5.0-alpha.1", "c-1")


class CharacterActionServiceTest(unittest.TestCase):
    def test_action_to_journal_to_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterActionService(ActionResolver(), kernel)
            start = CharacterState("c-1", "Test")
            result = service.execute(start, ACTION, action_instance_id="act-1", world_seed="w", journal_context=CTX)
            self.assertTrue(result.committed_event_ids)
            reloaded = CharacterState.from_dict(PersistenceKernel(tmp, ALLOWED).load_state()["character"])
            self.assertGreater(sum(reloaded.skill_xp.values()), 0)
            replay = service.execute(start, ACTION, action_instance_id="act-1", world_seed="w", journal_context=CTX)
            self.assertTrue(replay.idempotent_replay)
            self.assertEqual(replay.committed_event_ids, ())


if __name__ == "__main__":
    unittest.main()
