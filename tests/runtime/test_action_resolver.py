import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.trait_effects import resolve_trait_modifiers

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

    def test_traits_change_resolution_and_respect_soft_conflict(self):
        resolver = ActionResolver()
        plain = CharacterState("p", "P")
        strong = CharacterState("s", "S", traits={"detailmensch": 4, "opportunist": 4})
        action = dict(ACTION, trait_evidence_weights={"detailmensch": 0.5, "opportunist": 0.5})
        resolved = resolver.resolve(strong, action, action_instance_id="trait", world_seed="world")
        self.assertEqual(resolved.trait_modifiers["error_detection_pct"], 15.3)
        self.assertEqual(resolved.trait_modifiers["action_speed_pct"], -6)
        self.assertNotEqual(
            resolver.resolve(plain, action, action_instance_id="trait", world_seed="world").character_after.to_dict(),
            resolved.character_after.to_dict(),
        )

    def test_trait_xp_modifier_is_applied_per_skill(self):
        resolver = ActionResolver()
        character = CharacterState("k", "K", traits={"klangfokus": 5})
        plain = CharacterState("p", "P")
        resolved = resolver.resolve(character, ACTION, action_instance_id="audio", world_seed="world", base_xp=100)
        self.assertEqual(resolved.trait_modifiers["audio_xp_pct"], 18)
        baseline = resolver.resolve(plain, ACTION, action_instance_id="audio", world_seed="world", base_xp=100)
        self.assertGreater(resolved.character_after.skill_xp["musik"], baseline.character_after.skill_xp["musik"])

    def test_combined_trait_targets_respect_stack_caps(self):
        families = ("krisenfest", "vernetzer", "klangfokus", "stromfokus", "planer", "scout", "improvisierer", "verhandler", "nachtmensch", "ausdauer", "kreativer", "risikospieler", "detailmensch", "crew_anker", "opportunist")
        character = CharacterState("c", "C", traits={family: 5 for family in families})
        action = dict(ACTION, trait_evidence_weights={family: 1 / len(families) for family in families})
        modifiers = resolve_trait_modifiers(character, action, ("logistik",))
        self.assertEqual(modifiers.quality_pct, 35)
        self.assertEqual(modifiers.outcome_pct, 35)
        self.assertEqual(modifiers.xp_pct_by_skill["logistik"], -20)


if __name__ == "__main__":
    unittest.main()
