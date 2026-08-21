from __future__ import annotations

from dataclasses import dataclass, field


VIEWS = ("overview", "skills_traits", "biography")


@dataclass(slots=True)
class PresentationState:
    selected_view: str = "overview"
    biography_filter: str = "all"
    dismissed_feedback: set[str] = field(default_factory=set)

    def select_view(self, view_id: str) -> None:
        if view_id not in VIEWS:
            raise ValueError(f"Unbekannte Ansicht: {view_id}")
        self.selected_view = view_id

    def filter_biography(self, category: str) -> None:
        if not category:
            raise ValueError("Biografie-Filter fehlt")
        self.biography_filter = category

    def dismiss_feedback(self, feedback_id: str) -> None:
        if not feedback_id:
            raise ValueError("Feedback-ID fehlt")
        self.dismissed_feedback.add(feedback_id)
