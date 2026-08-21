from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Iterable, Mapping, Sequence


VIEW_IDS = frozenset({"overview", "skills_traits", "biography"})


class PresentationStateError(ValueError):
    """Machine-readable validation error for a local presentation transition."""

    def __init__(self, code: str, field: str, value: object):
        super().__init__(code)
        self.code = code
        self.field = field
        self.value = value


def _require_view(value: object) -> str:
    if not isinstance(value, str) or value not in VIEW_IDS:
        raise PresentationStateError("invalid_view_id", "view_id", value)
    return value


def _require_filter(value: object, allowed_categories: Iterable[str]) -> str:
    allowed = frozenset(allowed_categories) | {"all"}
    if not isinstance(value, str) or value not in allowed:
        raise PresentationStateError("invalid_biography_filter", "category", value)
    return value


def _require_feedback_id(value: object) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise PresentationStateError("invalid_feedback_id", "feedback_id", value)
    return value


@dataclass(frozen=True, slots=True)
class PresentationState:
    selected_view: str = "overview"
    biography_filter: str = "all"
    dismissed_feedback_ids: frozenset[str] = frozenset()
    reduced_motion: bool = False

    def __post_init__(self) -> None:
        _require_view(self.selected_view)
        if not isinstance(self.biography_filter, str) or not self.biography_filter or self.biography_filter.strip() != self.biography_filter:
            raise PresentationStateError("invalid_biography_filter", "category", self.biography_filter)
        if isinstance(self.dismissed_feedback_ids, str):
            raise PresentationStateError("invalid_feedback_id", "feedback_id", self.dismissed_feedback_ids)
        immutable_ids = frozenset(self.dismissed_feedback_ids)
        for feedback_id in immutable_ids:
            _require_feedback_id(feedback_id)
        if not isinstance(self.reduced_motion, bool):
            raise PresentationStateError("invalid_reduced_motion", "reduced_motion", self.reduced_motion)
        object.__setattr__(self, "dismissed_feedback_ids", immutable_ids)


def select_view(state: PresentationState, view_id: object) -> PresentationState:
    """Apply ``view.select`` locally without touching gameplay state."""
    return replace(state, selected_view=_require_view(view_id))


def filter_biography(
    state: PresentationState,
    category: object,
    *,
    allowed_categories: Iterable[str],
) -> PresentationState:
    """Apply ``biography.filter`` using categories supplied by the canonical manifest."""
    return replace(state, biography_filter=_require_filter(category, allowed_categories))


def dismiss_feedback(state: PresentationState, feedback_id: object) -> PresentationState:
    """Apply ``feedback.dismiss`` only to local presentation state."""
    validated = _require_feedback_id(feedback_id)
    return replace(state, dismissed_feedback_ids=state.dismissed_feedback_ids | {validated})


def visible_feedback(
    feedback: Sequence[Mapping[str, object]],
    state: PresentationState,
) -> list[dict[str, object]]:
    """Return detached feedback entries that have not been dismissed locally."""
    result: list[dict[str, object]] = []
    for entry in feedback:
        feedback_id = entry.get("feedback_id")
        if isinstance(feedback_id, str) and feedback_id in state.dismissed_feedback_ids:
            continue
        result.append(deepcopy(dict(entry)))
    return result
