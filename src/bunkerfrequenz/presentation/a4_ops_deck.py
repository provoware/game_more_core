from __future__ import annotations

from collections.abc import Iterable

from .components import build_components
from .state import PresentationState


WORKFLOW = ("current_goal", "next_action", "result", "development", "next_goal")


def _action(command: str, label_key: str, icon: str, order: int, **command_args) -> dict:
    return {
        "command": command,
        "label_key": label_key,
        "icon": icon,
        "primary": True,
        "target_px": 44,
        "focus_ring_px": 3,
        "keyboard_order": order,
        "command_args": command_args,
    }


def build_a4_ops_deck(
    projection: dict,
    state: PresentationState,
    available_action_ids: Iterable[str] = (),
) -> dict:
    """Compose the A4 view model without introducing A3 or network data."""
    components = build_components(projection, state.biography_filter)
    capabilities = projection["capabilities"]
    actions = []
    if capabilities["can_execute_action"]:
        actions.extend(
            _action(
                "action.execute", "ui.action.execute", "play", len(actions) + 1,
                action_id=action_id,
            )
            for action_id in list(available_action_ids)[:1]
        )
    if capabilities["can_edit_profile"]:
        actions.append(_action("profile.update", "ui.profile.save", "save", len(actions) + 1))
    if capabilities["can_undo_profile"]:
        actions.append(_action("profile.undo_last", "ui.undo", "undo", len(actions) + 1))
    actions = actions[:3]
    feedback = [item for item in projection["feedback"] if item["feedback_id"] not in state.dismissed_feedback]
    sections = {
        "current_goal": {
            "heading_key": "ui.workflow.current_goal", "primary_focus": True,
            "components": [components["CharacterHeader"], components["ProfileEditor"]],
        },
        "next_action": {"heading_key": "ui.workflow.next_action", "actions": actions},
        "result": {
            "heading_key": "ui.workflow.result", "components": [components["ProgressFeedback"]],
            "feedback": feedback,
        },
        "development": {
            "heading_key": "ui.workflow.development",
            "components": [components[name] for name in (
                "StatusSummary", "SkillList", "TraitList", "SpecializationCard", "BiographyTimeline"
            )],
        },
        "next_goal": {"heading_key": "ui.workflow.next_goal", "components": []},
    }
    return {
        "layout": "A4_OPS_DECK",
        "selected_view": state.selected_view,
        "workflow_order": WORKFLOW,
        "sections": sections,
        "components": components,
        "keyboard_order": [item["command"] for item in actions],
        "accessibility": {
            "minimum_target_px": 44,
            "visible_focus": True,
            "semantic_cues": ("text", "icon", "color"),
            "high_contrast": True,
        },
    }
