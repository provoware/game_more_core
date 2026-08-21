from __future__ import annotations

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_EDITABLE = {"display_name", "alias", "motto"}


class CharacterProfileService:
    def __init__(self, persistence: PersistenceKernel):
        self.persistence = persistence

    def update(
        self,
        character: CharacterState,
        changes: dict[str, str],
        *,
        event_id: str,
        transaction_id: str,
        context: JournalContext,
    ) -> CharacterState:
        unknown = set(changes) - _EDITABLE
        if unknown:
            raise ValueError(f"Nicht editierbare Profilfelder: {', '.join(sorted(unknown))}")
        updated = CharacterState.from_dict(character.to_dict())
        old: dict[str, str] = {}
        new: dict[str, str] = {}
        for key, value in changes.items():
            if key == "display_name" and not value.strip():
                raise ValueError("Anzeigename darf nicht leer sein")
            old[key] = getattr(updated, key)
            setattr(updated, key, value)
            new[key] = value
        updated.validate()
        self.persistence.initialize_state({"character": character.to_dict()})
        self.persistence.commit(
            transaction_id,
            [{"event_id": event_id, "event_type": "character.profile_updated", "payload": {"old": old, "new": new}}],
            {"character": updated.to_dict()},
            context,
        )
        return updated

    def undo_last_profile_update(self, *, event_id: str, transaction_id: str, context: JournalContext) -> CharacterState:
        records = self.persistence.last_transaction_records()
        if len(records) != 1 or records[0]["event_type"] != "character.profile_updated":
            raise PersistenceError("Die letzte Aktion ist keine sicher rückgängig machbare Profiländerung")
        original = records[0]
        if original.get("compensation_for"):
            raise PersistenceError("Die letzte Aktion ist bereits ein Undo")
        state_data = self.persistence.load_state()
        if state_data is None:
            raise PersistenceError("Kein Zustand für Undo vorhanden")
        character = CharacterState.from_dict(state_data["character"])
        reverse = dict(original["payload"].get("old", {}))
        current = {key: getattr(character, key) for key in reverse}
        for key, value in reverse.items():
            setattr(character, key, value)
        character.validate()
        self.persistence.commit(
            transaction_id,
            [{
                "event_id": event_id,
                "event_type": "character.profile_updated",
                "payload": {"old": current, "new": reverse, "undo_of": original["event_id"]},
                "compensation_for": original["event_id"],
            }],
            {"character": character.to_dict()},
            context,
        )
        return character
