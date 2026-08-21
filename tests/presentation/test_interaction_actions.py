import unittest

from bunkerfrequenz.presentation.interaction_actions import normalize_primary_actions


CAPABILITIES = {
    "can_edit_profile": True,
    "can_undo_profile": True,
    "can_execute_action": True,
}


def profile_action(action_id: str, command_id: str) -> dict:
    return {
        "action_id": action_id,
        "label_key": "ui.profile.save",
        "icon_id": "save",
        "tone": "primary",
        "enabled": True,
        "command": {
            "type": "profile.update",
            "character_id": "char.pppoppi",
            "command_id": command_id,
            "event_id": f"evt-{command_id}",
            "transaction_id": f"tx-{command_id}",
            "changes": {"alias": "Betonfunk"},
        },
    }


class InteractionActionsTest(unittest.TestCase):
    def normalize(self, actions):
        return normalize_primary_actions(
            actions,
            character_id="char.pppoppi",
            capabilities=CAPABILITIES,
            max_primary_actions=3,
            minimum_target_px=44,
            focus_ring_px=3,
        )

    def test_duplicate_action_ids_are_rejected_even_when_commands_are_distinct(self):
        with self.assertRaises(ValueError):
            self.normalize(
                [
                    profile_action("same", "one"),
                    profile_action("same", "two"),
                ]
            )

    def test_normalized_actions_remain_detached_and_dispatcher_ready(self):
        source = [profile_action("save", "one")]
        normalized = self.normalize(source)
        normalized[0]["dispatch"]["command"]["changes"]["alias"] = "changed"

        self.assertEqual(source[0]["command"]["changes"]["alias"], "Betonfunk")
        self.assertEqual(normalized[0]["dispatch"]["route"], "application.command_dispatcher.dispatch_command")
        self.assertEqual(normalized[0]["target_px"], 44)
        self.assertEqual(normalized[0]["focus_ring_px"], 3)


if __name__ == "__main__":
    unittest.main()
