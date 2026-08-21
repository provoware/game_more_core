from __future__ import annotations

from bunkerfrequenz.domain.character import CharacterState


def build_character_projection(
    character: CharacterState,
    capabilities: dict[str, bool],
) -> dict:
    """Build the capability-bearing base of the read-only character view."""
    character.validate()
    return {
        "meta": {"projection_version": "0.6", "character_id": character.character_id},
        "overview": {
            "display_name": character.display_name,
            "alias": character.alias,
            "additional_nicknames": list(character.additional_nicknames),
            "motto": character.motto,
            "level": character.level,
            "total_xp": character.total_xp,
            "resonance_xp": character.resonance_xp,
            "resonance_rank": character.resonance_rank,
            "energy": character.energy,
            "stress": character.stress,
            "reputation": character.reputation,
        },
        "capabilities": dict(capabilities),
    }
