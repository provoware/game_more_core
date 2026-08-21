from __future__ import annotations

from dataclasses import dataclass, replace

VIEW_IDS = frozenset({"overview", "skills_traits", "biography"})
BIOGRAPHY_CATEGORIES = frozenset({
    "first_time",
    "major_success",
    "major_failure",
    "level_milestone",
    "trait",
    "specialization",
    "relationship",
    "major_find",
    "event",
    "club",
    "economy",
    "personal_mission",
    "rare_random_event",
})
BIOGRAPHY_FILTERS = BIOGRAPHY_CATEGORIES | {"all"}


class PresentationStateError(ValueError):
    """A machine-readable validation error for a local presentation command."""

    def __init__(self, code: str, field: str, value: object):
        super().__init__(code)
        self.code = code
        self.field = field
        self.value = value


def _require_catalog_value(value: object, allowed: frozenset[str], field: str) -> None:
    if not isinstance(value, str) or value not in allowed:
        raise PresentationStateError(f"invalid_{field}", field, value)


def _require_feedback_id(feedback_id: object) -> None:
    if not isinstance(feedback_id, str) or not feedback_id or feedback_id.strip() != feedback_id:
        raise PresentationStateError("invalid_feedback_id", "feedback_id", feedback_id)


@dataclass(frozen=True, slots=True)
class PresentationState:
    selected_view: str = "overview"
    biography_filter: str = "all"
    dismissed_feedback_ids: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        _require_catalog_value(self.selected_view, VIEW_IDS, "view_id")
        _require_catalog_value(self.biography_filter, BIOGRAPHY_FILTERS, "category")
        if isinstance(self.dismissed_feedback_ids, str):
            raise PresentationStateError(
                "invalid_feedback_id", "feedback_id", self.dismissed_feedback_ids
            )
        immutable_ids = frozenset(self.dismissed_feedback_ids)
        for feedback_id in immutable_ids:
            _require_feedback_id(feedback_id)
        object.__setattr__(self, "dismissed_feedback_ids", immutable_ids)


def select_view(state: PresentationState, view_id: object) -> PresentationState:
    """Apply ``view.select`` without writing domain or persistent state."""
    _require_catalog_value(view_id, VIEW_IDS, "view_id")
    return replace(state, selected_view=view_id)


def filter_biography(state: PresentationState, category: object) -> PresentationState:
    """Apply ``biography.filter`` to local presentation state."""
    _require_catalog_value(category, BIOGRAPHY_FILTERS, "category")
    return replace(state, biography_filter=category)


def dismiss_feedback(state: PresentationState, feedback_id: object) -> PresentationState:
    """Apply ``feedback.dismiss`` without changing gameplay state."""
    _require_feedback_id(feedback_id)
    return replace(state, dismissed_feedback_ids=state.dismissed_feedback_ids | {feedback_id})
