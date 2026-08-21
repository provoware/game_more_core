from __future__ import annotations

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.progression import add_trait_evidence, apply_skill_xp
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel, RecoveryReceipt


def replay_character_event(derived_state: dict, record: dict) -> dict:
    if "character" not in derived_state:
        return derived_state
    character = CharacterState.from_dict(derived_state["character"])
    event_type = record["event_type"]
    payload = record.get("payload", {})

    if event_type == "character.skill_xp_gained":
        apply_skill_xp(character, payload["skill_id"], int(payload["amount"]))
    elif event_type == "character.trait_evidence_gained":
        add_trait_evidence(character, payload["family"], float(payload["amount"]), payload["evidence_source"])
    elif event_type == "character.specialization_changed":
        character.specialization = payload.get("new")
    elif event_type == "character.profile_updated":
        for key, value in payload.get("new", {}).items():
            if key in {"display_name", "alias", "additional_nicknames", "motto"}:
                setattr(character, key, value)
    # Level-/trait-up events are consequences of the XP/evidence records above and
    # are intentionally informational during replay to avoid applying twice.
    derived_state = dict(derived_state)
    derived_state["character"] = character.to_dict()
    return derived_state


class CharacterRecoveryService:
    def __init__(self, persistence: PersistenceKernel):
        self.persistence = persistence

    def recover(self, *, context: JournalContext | None = None) -> RecoveryReceipt:
        return self.persistence.recover(replay_character_event, context=context)
