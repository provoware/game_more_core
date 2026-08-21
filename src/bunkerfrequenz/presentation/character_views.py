from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

COMPONENTS = (
    "CharacterHeader", "StatusSummary", "SkillList", "TraitList",
    "SpecializationCard", "BiographyTimeline", "ProfileEditor", "ProgressFeedback",
)
COMMANDS = (
    "profile.update", "profile.undo_last", "action.execute", "view.select",
    "biography.filter", "feedback.dismiss",
)
LAYOUTS = {
    "A3_CINEMATIC_FORGE": ("large_character_stage", "radial_skill_web", "context_drawer"),
    "A4_OPS_DECK": ("vertical_workflow_rail", "center_action_workspace", "right_live_status"),
}


def build_character_view(
    variant_id: str, projection: Mapping[str, Any], *, reduced_motion: bool = False
) -> dict[str, Any]:
    """Arrange the shared contract without adding variant-specific game logic."""
    if variant_id not in LAYOUTS:
        raise ValueError(f"Unbekannte UI-Variante: {variant_id}")
    feedback = deepcopy(projection["feedback"])
    for item in feedback:
        item["presentation"] = "static" if reduced_motion else "non_blocking_animation"
    return {
        "variant_id": variant_id,
        "projection": deepcopy(dict(projection)),
        "component_interface": COMPONENTS,
        "command_interface": COMMANDS,
        "layout_regions": LAYOUTS[variant_id],
        "progress_feedback": feedback,
        "empty_states": {
            "ranking": {"status": "not_connected", "items": []},
            "network": {"status": "not_connected", "items": []},
            "sync": {"status": "not_connected", "items": []},
        },
        "input_blocked_by_feedback": False,
    }
