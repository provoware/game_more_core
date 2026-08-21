"""Read-only presentation projections and local Character Forge view state."""

from bunkerfrequenz.presentation.biography_projection import build_biography_projection
from bunkerfrequenz.presentation.character_projection import build_character_projection
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
    "VIEW_IDS",
    "PresentationState",
    "PresentationStateError",
    "build_biography_projection",
    "build_character_projection",
    "build_confirmed_feedback",
    "dismiss_feedback",
    "filter_biography",
    "select_view",
    "visible_feedback",
]
