from __future__ import annotations

from bunkerfrequenz.domain.character import CharacterState, RESOURCE_MAX, RESOURCE_MIN
from bunkerfrequenz.domain.progression import add_trait_evidence, apply_skill_xp
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel, RecoveryReceipt


def _replay_resource_change(character: CharacterState, payload: dict) -> None:
    energy = payload.get("energy")
    stress = payload.get("stress")
    if not isinstance(energy, dict) or not isinstance(stress, dict):
        raise ValueError("Ressourcen-Replay benötigt energy und stress")
    for name, block, current in (
        ("energy", energy, character.energy),
        ("stress", stress, character.stress),
    ):
        if set(block) != {"old", "delta", "new"}:
            raise ValueError(f"Ressourcen-Replay {name} besitzt ungültige Felder")
        old = block["old"]
        delta = block["delta"]
        new = block["new"]
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (old, delta, new)):
            raise ValueError(f"Ressourcen-Replay {name} benötigt Ganzzahlen")
        if current != old:
            raise ValueError(f"Ressourcen-Replay {name} passt nicht zum bestätigten Ausgangszustand")
        expected = min(RESOURCE_MAX, max(RESOURCE_MIN, old + delta))
        if new != expected or not RESOURCE_MIN <= new <= RESOURCE_MAX:
            raise ValueError(f"Ressourcen-Replay {name} besitzt inkonsistenten Zielwert")
    character.energy = energy["new"]
    character.stress = stress["new"]


def _replay_reputation_change(character: CharacterState, payload: dict) -> None:
    if set(payload) != {"old", "delta", "new", "reason"}:
        raise ValueError("Reputation-Replay benötigt old/delta/new/reason")
    old = payload["old"]
    delta = payload["delta"]
    new = payload["new"]
    reason = payload["reason"]
    if any(isinstance(value, bool) or not isinstance(value, int) for value in (old, delta, new)):
        raise ValueError("Reputation-Replay benötigt Ganzzahlen")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Reputation-Replay benötigt reason")
    if character.reputation != old:
        raise ValueError("Reputation-Replay passt nicht zum bestätigten Ausgangswert")
    if new != old + delta:
        raise ValueError("Reputation-Replay besitzt inkonsistenten Zielwert")
    character.reputation = new


def replay_character_event(derived_state: dict, record: dict) -> dict:
    if "character" not in derived_state:
        return derived_state
    character = CharacterState.from_dict(derived_state["character"])
    event_type = record["event_type"]
    payload = record.get("payload", {})

    if event_type == "character.resources_changed":
        _replay_resource_change(character, payload)
    elif event_type == "character.reputation_changed":
        _replay_reputation_change(character, payload)
    elif event_type == "character.skill_xp_gained":
        apply_skill_xp(character, payload["skill_id"], int(payload["amount"]))
    elif event_type == "character.trait_evidence_gained":
        add_trait_evidence(character, payload["family"], float(payload["amount"]), payload["evidence_source"])
    elif event_type == "character.specialization_changed":
        character.specialization = payload.get("new")
    elif event_type == "character.profile_updated":
        for key, value in payload.get("new", {}).items():
            if key in {"display_name", "alias", "additional_nicknames", "motto"}:
                setattr(character, key, value)
    # Level-/trait-up and biography events are consequences/information and are
    # intentionally not applied a second time during replay.
    derived_state = dict(derived_state)
    derived_state["character"] = character.to_dict()
    return derived_state


class CharacterRecoveryService:
    def __init__(self, persistence: PersistenceKernel):
        self.persistence = persistence

    def recover(self, *, context: JournalContext | None = None) -> RecoveryReceipt:
        return self.persistence.recover(replay_character_event, context=context)
