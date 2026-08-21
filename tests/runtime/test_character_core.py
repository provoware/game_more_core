import unittest

from bunkerfrequenz.domain.character import CharacterState, START_SKILLS
from bunkerfrequenz.domain.progression import ProgressionRules, add_trait_evidence, apply_skill_xp, evaluate_specialization


class CharacterCoreTest(unittest.TestCase):
    def test_equal_start_and_progression(self):
        a = CharacterState("a", "A")
        b = CharacterState("b", "B")
        self.assertEqual(a.skills, b.skills)
        self.assertTrue(all(v == 10 for v in a.skills.values()))
        apply_skill_xp(a, "technik", ProgressionRules.xp_to_next_skill(10))
        self.assertEqual(a.skills["technik"], 11)
        self.assertEqual(b.skills["technik"], 10)

    def test_trait_unlock_requires_evidence_level_events_and_sources(self):
        state = CharacterState("t", "T")
        state.level = 3
        events = []
        for _ in range(12):
            events.extend(add_trait_evidence(state, "detailmensch", 20, "practice"))
        self.assertEqual(state.traits["detailmensch"], 1)
        self.assertTrue(any(e["event_type"] == "character.trait_unlocked" for e in events))

    def test_specialization_is_not_forced_at_start(self):
        state = CharacterState("s", "S")
        self.assertEqual(evaluate_specialization(state), [])
        self.assertIsNone(state.specialization)

    def test_invalid_skill_set_rejected(self):
        state = CharacterState("x", "X")
        state.skills.pop(next(iter(START_SKILLS)))
        with self.assertRaises(ValueError):
            state.validate()


if __name__ == "__main__":
    unittest.main()
