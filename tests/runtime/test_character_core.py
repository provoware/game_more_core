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

    def test_level_50_continues_as_journaled_open_resonance(self):
        state = CharacterState("r", "R")
        state.total_xp = ProgressionRules.total_xp_for_level(50) - 1
        state.level = 49
        events = apply_skill_xp(state, "technik", ProgressionRules.resonance_xp_per_rank * 2)
        self.assertEqual(state.level, 50)
        self.assertGreaterEqual(state.resonance_rank, 1)
        self.assertTrue(any(event["event_type"] == "character.resonance_xp_gained" for event in events))
        self.assertTrue(any(event["event_type"] == "character.resonance_rank_up" for event in events))

    def test_legacy_state_loads_without_resonance_fields(self):
        data = CharacterState("l", "Legacy").to_dict()
        data.pop("resonance_xp")
        data.pop("resonance_rank")
        loaded = CharacterState.from_dict(data)
        self.assertEqual((loaded.resonance_xp, loaded.resonance_rank), (0, 0))

    def test_additional_nicknames_round_trip_without_shared_list(self):
        state = CharacterState("n", "Name", additional_nicknames=["Echo", "Impuls"])
        serialized = state.to_dict()
        loaded = CharacterState.from_dict(serialized)
        serialized["additional_nicknames"].append("Extern")
        self.assertEqual(loaded.additional_nicknames, ["Echo", "Impuls"])

        legacy = state.to_dict()
        legacy.pop("additional_nicknames")
        self.assertEqual(CharacterState.from_dict(legacy).additional_nicknames, [])

        with self.assertRaises(ValueError):
            CharacterState("invalid", "Name", additional_nicknames=[""]).validate()


if __name__ == "__main__":
    unittest.main()
