"""Read-only projections, shared components and local Character Forge view state."""

from bunkerfrequenz.presentation.a4_ops_deck import build_a4_ops_deck
from bunkerfrequenz.presentation.biography_projection import build_biography_projection
from bunkerfrequenz.presentation.character_projection import build_character_projection
from bunkerfrequenz.presentation.components import (
    COMPONENT_NAMES,
    build_biography_timeline,
    build_character_header,
    build_components,
    build_profile_editor,
    build_progress_feedback,
    build_skill_list,
    build_specialization_card,
    build_status_summary,
    build_trait_list,
)
from bunkerfrequenz.presentation.feedback import build_confirmed_feedback
from bunkerfrequenz.presentation.state import (
    VIEW_IDS,
    PresentationState,
    PresentationStateError,
    dismiss_feedback,
    filter_biography,
    select_view,
    visible_feedback,
)

__all__ = [
    "COMPONENT_NAMES",
    "VIEW_IDS",
    "PresentationState",
    "PresentationStateError",
    "build_a4_ops_deck",
    "build_biography_projection",
    "build_biography_timeline",
    "build_character_header",
    "build_character_projection",
    "build_components",
    "build_confirmed_feedback",
    "build_profile_editor",
    "build_progress_feedback",
    "build_skill_list",
    "build_specialization_card",
    "build_status_summary",
    "build_trait_list",
    "dismiss_feedback",
    "filter_biography",
    "select_view",
    "visible_feedback",
]
