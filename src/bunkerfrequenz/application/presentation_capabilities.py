from __future__ import annotations

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import PersistenceKernel


def get_presentation_capabilities(
    character: CharacterState | None,
    persistence: PersistenceKernel,
) -> dict[str, bool]:
    """Describe available character commands without changing persisted state."""
    state_data = persistence.load_state()
    if character is None or state_data is None or "character" not in state_data:
        return _capabilities(False, False)

    loaded = CharacterState.from_dict(state_data["character"])
    character.validate()
    state_available = loaded.character_id == character.character_id
    records = persistence.last_transaction_records()
    can_undo = (
        state_available
        and len(records) == 1
        and records[0]["event_type"] == "character.profile_updated"
        and not records[0].get("compensation_for")
    )
    return _capabilities(state_available, can_undo)


def _capabilities(state_available: bool, can_undo: bool) -> dict[str, bool]:
    return {
        "can_edit_profile": state_available,
        "can_undo_profile": can_undo,
        "can_execute_action": state_available,
    }
