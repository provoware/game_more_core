from dataclasses import dataclass
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.command_adapter import PresentationCommandAdapter
from bunkerfrequenz.presentation.state import PresentationState


TEXTS = {f"skill.{skill}": skill for skill in CharacterState("c-1", "Test").skills}
CAPABILITIES = {
    "can_edit_profile": True,
    "can_undo_profile": False,
    "can_execute_action": True,
}


@dataclass
class Resolved:
    character_after: CharacterState
    action_instance_id: str = "run-1"
    outcome: str = "success"


@dataclass
class ConfirmedResult:
    resolved: Resolved
    committed_event_ids: tuple[str, ...] = ("run-1:001",)
    idempotent_replay: bool = False


class ActionServiceSpy:
    def __init__(self):
        self.calls = []

    def execute(self, character, action, **service_args):
        self.calls.append((character, action, service_args))
        updated = CharacterState.from_dict(character.to_dict())
        updated.skill_xp["technik"] = 12
        return ConfirmedResult(Resolved(updated))


class ProfileServiceForbidden:
    def update(self, *args, **kwargs):
        raise AssertionError("Profilservice war für eine Spielaktion nicht zuständig")

    def undo_last_profile_update(self, **kwargs):
        raise AssertionError("Profilservice war für eine Spielaktion nicht zuständig")


class CommandAdapterTest(unittest.TestCase):
    def test_confirmed_action_result_builds_feedback_and_new_projection(self):
        actions = ActionServiceSpy()
        adapter = PresentationCommandAdapter(
            ProfileServiceForbidden(), actions, journal_records=lambda: (),
            text_catalog=TEXTS, capabilities=CAPABILITIES,
        )
        original = CharacterState("c-1", "Test")
        projection = adapter.dispatch({
            "type": "action.execute",
            "action": {"action_id": "action.soundcheck"},
            "service_args": {"action_instance_id": "run-1", "world_seed": "fixed"},
        }, original, PresentationState())

        self.assertEqual(len(actions.calls), 1)
        self.assertEqual(original.skill_xp, {})
        technique = next(row for row in projection["skills"] if row["skill_id"] == "technik")
        self.assertEqual(technique["xp"], 12)
        self.assertEqual(projection["feedback"][0]["feedback_id"], "run-1")
        self.assertEqual(projection["feedback"][0]["title_key"], "ui.feedback.action_confirmed")

    def test_local_view_command_does_not_call_application_services(self):
        actions = ActionServiceSpy()
        adapter = PresentationCommandAdapter(
            ProfileServiceForbidden(), actions, journal_records=lambda: (),
            text_catalog=TEXTS, capabilities=CAPABILITIES,
        )
        state = PresentationState()
        adapter.dispatch({"type": "view.select", "view_id": "biography"}, CharacterState("c-1", "Test"), state)
        self.assertEqual(state.selected_view, "biography")
        self.assertEqual(actions.calls, [])


if __name__ == "__main__":
    unittest.main()
