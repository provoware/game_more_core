import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation import build_character_projection, build_character_view


class CharacterLayoutContractTest(unittest.TestCase):
    def test_a3_and_a4_share_projection_components_and_commands(self):
        character = CharacterState(
            "char-1", "Alex", level=50, resonance_xp=5100, resonance_rank=1,
            traits={"planer": 2}, trait_evidence={"planer": 500},
            specialization={"specialization_id": "spec.einsatzleitung", "stage": "profil"},
        )
        records = [
            {"event_id": "evt-level", "event_type": "character.level_up", "sequence": 1, "payload": {"new": 50}},
            {"event_id": "evt-skill", "event_type": "character.skill_level_up", "sequence": 2, "payload": {"skill_id": "technik"}},
            {"event_id": "evt-trait", "event_type": "character.trait_tier_up", "sequence": 3, "payload": {"family": "planer"}},
            {"event_id": "evt-spec", "event_type": "character.specialization_changed", "sequence": 4, "payload": {"new": character.specialization}},
            {"event_id": "evt-resonance", "event_type": "character.resonance_rank_up", "sequence": 5, "payload": {"new": 1}},
        ]
        projection = build_character_projection(character, records, {})

        a3 = build_character_view("A3_CINEMATIC_FORGE", projection, reduced_motion=True)
        a4 = build_character_view("A4_OPS_DECK", projection, reduced_motion=True)

        self.assertEqual(a3["projection"], a4["projection"])
        self.assertEqual(a3["component_interface"], a4["component_interface"])
        self.assertEqual(a3["command_interface"], a4["command_interface"])
        self.assertEqual(a3["layout_regions"], ("large_character_stage", "radial_skill_web", "context_drawer"))
        self.assertEqual({item["kind"] for item in a3["progress_feedback"]}, {"level", "skill", "trait", "specialization", "resonance"})
        self.assertTrue(all(item["presentation"] == "static" for item in a3["progress_feedback"]))
        self.assertFalse(a3["input_blocked_by_feedback"])
        self.assertTrue(all(not state["items"] for state in a3["empty_states"].values()))
        a3["projection"]["overview"]["display_name"] = "Geänderte Ansicht"
        self.assertEqual(projection["overview"]["display_name"], "Alex")


if __name__ == "__main__":
    unittest.main()
