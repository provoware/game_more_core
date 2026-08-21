import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.domain.character import CharacterState

ACTION = {
    "action_id": "action.soundcheck",
    "category": "event",
    "risk_profile": "medium",
    "skill_weights": {"technik": 0.5, "musik": 0.3, "konzentration": 0.2},
    "trait_evidence_weights": {"klangfokus": 0.6, "detailmensch": 0.4},
    "prerequisites": [],
}


class ActionResolverTest(unittest.TestCase):
    def test_same_seed_is_deterministic(self):
        resolver = ActionResolver()
        character = CharacterState("x", "X")
        first = resolver.resolve(character, ACTION, action_instance_id="a-1", world_seed="world")
        second = resolver.resolve(character, ACTION, action_instance_id="a-1", world_seed="world")
        self.assertEqual(first.outcome, second.outcome)
        self.assertEqual(first.character_after.to_dict(), second.character_after.to_dict())
        self.assertEqual(first.journal_events, second.journal_events)

    def test_better_skills_improve_same_seed_outcome_or_hold(self):
        resolver = ActionResolver()
        low = CharacterState("l", "L")
        high = CharacterState("h", "H")
        high.skills["technik"] = high.skills["musik"] = high.skills["konzentration"] = 100
        order = {"failed":0,"partial":1,"success":2,"excellent":3,"legendary":4}
        a = resolver.resolve(low, ACTION, action_instance_id="same", world_seed="world")
        b = resolver.resolve(high, ACTION, action_instance_id="same", world_seed="world")
        self.assertGreaterEqual(order[b.outcome], order[a.outcome])

    def test_prerequisite_failure_stops_before_mutation(self):
        resolver = ActionResolver(lambda _rule, _ctx: False)
        action = dict(ACTION, prerequisites=["authorized"])
        character = CharacterState("x", "X")
        before = character.to_dict()
        with self.assertRaises(ValueError):
            resolver.resolve(character, action, action_instance_id="a-2", world_seed="world")
        self.assertEqual(character.to_dict(), before)


if __name__ == "__main__":
    unittest.main()
