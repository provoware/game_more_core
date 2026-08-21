from __future__ import annotations

from typing import Any, Mapping

from bunkerfrequenz.presentation.adapter import PresentationAdapter

from ._shared import copied


EDITABLE_FIELDS = ("display_name", "alias", "additional_nicknames", "motto")


class ProfileEditor:
    def build(
        self,
        overview: Mapping[str, Any],
        capabilities: Mapping[str, Any],
        local_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        draft = (local_state or {}).get("draft", {})
        return {
            "values": {field: copied(draft.get(field, overview.get(field))) for field in EDITABLE_FIELDS},
            "can_submit": bool(capabilities.get("can_edit_profile", False)),
            "can_undo": bool(capabilities.get("can_undo_profile", False)),
        }

    def submit(
        self,
        overview: Mapping[str, Any],
        local_state: Mapping[str, Any],
        adapter: PresentationAdapter,
        *,
        character_id: str,
        command_id: str,
        event_id: str,
        transaction_id: str,
    ) -> Any | None:
        draft = local_state.get("draft", {})
        changes = {
            field: copied(draft[field])
            for field in EDITABLE_FIELDS
            if field in draft and draft[field] != overview.get(field)
        }
        if not changes:
            return None
        return adapter.dispatch({
            "type": "profile.update",
            "character_id": character_id,
            "changes": changes,
            "command_id": command_id,
            "event_id": event_id,
            "transaction_id": transaction_id,
        })
