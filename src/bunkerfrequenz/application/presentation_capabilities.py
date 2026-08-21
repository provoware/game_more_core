from __future__ import annotations

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import PersistenceError, PersistenceKernel


_CAPABILITY_KEYS = (
    "can_edit_profile",
    "can_undo_profile",
    "can_execute_action",
)


def _capabilities(enabled: bool = False, *, can_undo: bool = False) -> dict[str, bool]:
    return {
        "can_edit_profile": enabled,
        "can_undo_profile": enabled and can_undo,
        "can_execute_action": enabled,
    }


def get_presentation_capabilities(
    character: CharacterState | None,
    persistence: PersistenceKernel,
) -> dict[str, bool]:
    """Return UI capabilities from confirmed application/persistence state without mutation."""
    if character is None:
        return _capabilities()

    try:
        character.validate()
        state_data = persistence.load_state()
        records = persistence.last_transaction_records()
    except (PersistenceError, ValueError, KeyError, TypeError):
        return _capabilities()

    if state_data is None or "character" not in state_data:
        return _capabilities()

    try:
        persisted = CharacterState.from_dict(state_data["character"])
    except (ValueError, KeyError, TypeError):
        return _capabilities()

    state_available = persisted.character_id == character.character_id
    can_undo = bool(
        state_available
        and len(records) == 1
        and records[0].get("event_type") == "character.profile_updated"
        and not records[0].get("compensation_for")
    )
    return _capabilities(state_available, can_undo=can_undo)


def normalize_presentation_capabilities(values: dict[str, bool] | None) -> dict[str, bool]:
    """Return the stable public capability shape as a detached copy."""
    values = values or {}
    return {key: bool(values.get(key, False)) for key in _CAPABILITY_KEYS}
