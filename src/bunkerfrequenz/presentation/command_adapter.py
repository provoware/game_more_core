from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping

from bunkerfrequenz.domain.character import CharacterState

from .projection import build_character_projection
from .state import PresentationState


class PresentationCommandAdapter:
    """Single boundary for local UI commands and confirmed application writes."""

    def __init__(
        self,
        profile_service,
        action_service,
        *,
        journal_records: Callable[[], Iterable[dict]],
        text_catalog: Mapping[str, str],
        capabilities: Mapping[str, bool],
    ):
        self.profile_service = profile_service
        self.action_service = action_service
        self.journal_records = journal_records
        self.text_catalog = text_catalog
        self.capabilities = capabilities

    def dispatch(self, command: dict, character: CharacterState, state: PresentationState) -> dict:
        command_type = command.get("type")
        if command_type == "view.select":
            state.select_view(command["view_id"])
            return self._project(character)
        if command_type == "biography.filter":
            state.filter_biography(command["category"])
            return self._project(character)
        if command_type == "feedback.dismiss":
            state.dismiss_feedback(command["feedback_id"])
            return self._project(character)
        if command_type == "profile.update":
            updated = self.profile_service.update(character, command["changes"], **command["service_args"])
            return self._project(updated)
        if command_type == "profile.undo_last":
            updated = self.profile_service.undo_last_profile_update(**command["service_args"])
            return self._project(updated)
        if command_type == "action.execute":
            result = self.action_service.execute(character, command["action"], **command["service_args"])
            feedback = self._confirmed_feedback(result)
            return self._project(result.resolved.character_after, feedback)
        raise ValueError(f"Unbekannter Presentation-Command: {command_type}")

    def _project(self, character: CharacterState, feedback: Iterable[dict] = ()) -> dict:
        return build_character_projection(
            character,
            self.journal_records(),
            self.text_catalog,
            capabilities=self.capabilities,
            feedback=feedback,
        )

    def _confirmed_feedback(self, result) -> list[dict]:
        if not result.committed_event_ids and not result.idempotent_replay:
            return []
        return [{
            "feedback_id": result.resolved.action_instance_id,
            "kind": result.resolved.outcome,
            "title_key": "ui.feedback.action_confirmed",
            "detail_keys": ["ui.feedback.projection_updated"],
            "reduced_motion": True,
        }]
