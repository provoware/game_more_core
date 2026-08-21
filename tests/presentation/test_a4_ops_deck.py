import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.a4_ops_deck import WORKFLOW, build_a4_ops_deck
from bunkerfrequenz.presentation.components import COMPONENT_NAMES
from bunkerfrequenz.presentation.projection import build_character_projection
from bunkerfrequenz.presentation.state import PresentationState


TEXTS = {f"skill.{skill}": skill for skill in CharacterState("c-1", "Test").skills}
CAPABILITIES = {
    "can_edit_profile": True,
    "can_undo_profile": True,
    "can_execute_action": True,
}


class A4OpsDeckTest(unittest.TestCase):
    def setUp(self):
        self.projection = build_character_projection(
            CharacterState("c-1", "Test"), (), TEXTS, capabilities=CAPABILITIES
        )

    def test_keyboard_order_follows_visible_primary_actions(self):
        deck = build_a4_ops_deck(self.projection, PresentationState(), ("action.soundcheck",))
        actions = deck["sections"]["next_action"]["actions"]
        self.assertEqual(deck["keyboard_order"], [item["command"] for item in actions])
        self.assertEqual([item["keyboard_order"] for item in actions], [1, 2, 3])
        self.assertEqual(actions[0]["command_args"], {"action_id": "action.soundcheck"})
        self.assertTrue(all(item["target_px"] >= 44 for item in actions))
        self.assertTrue(all(item["focus_ring_px"] >= 3 for item in actions))

    def test_current_goal_owns_primary_focus_and_manifest_workflow(self):
        deck = build_a4_ops_deck(self.projection, PresentationState())
        self.assertEqual(deck["workflow_order"], WORKFLOW)
        self.assertEqual(tuple(deck["sections"]), WORKFLOW)
        focused = [key for key, section in deck["sections"].items() if section.get("primary_focus")]
        self.assertEqual(focused, ["current_goal"])
        self.assertTrue(deck["accessibility"]["visible_focus"])
        self.assertTrue(deck["accessibility"]["high_contrast"])

    def test_primary_actions_are_limited_and_all_components_are_shared(self):
        deck = build_a4_ops_deck(
            self.projection, PresentationState(), ("a-1", "a-2", "a-3", "a-4")
        )
        self.assertLessEqual(len(deck["sections"]["next_action"]["actions"]), 3)
        self.assertEqual(tuple(deck["components"]), COMPONENT_NAMES)
        self.assertEqual(deck["accessibility"]["semantic_cues"], ("text", "icon", "color"))


if __name__ == "__main__":
    unittest.main()
