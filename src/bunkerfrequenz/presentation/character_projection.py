from __future__ import annotations

from typing import Any, Mapping, Sequence

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.progression import ProgressionRules, SPECIALIZATIONS, SPECIALIZATION_XP_EFFECTS


TRAIT_FAMILIES = frozenset(
    {
        "krisenfest", "vernetzer", "klangfokus", "stromfokus", "planer",
        "scout", "improvisierer", "verhandler", "nachtmensch", "ausdauer",
        "kreativer", "risikospieler", "detailmensch", "crew_anker", "opportunist",
    }
)


def _skill_projection(skill_id: str, value: int, xp: int) -> dict[str, Any]:
    required = 0 if value >= ProgressionRules.skill_max else ProgressionRules.xp_to_next_skill(value)
    percent = 100 if required == 0 else min(100, round(xp / required * 100))
    return {
        "skill_id": f"skill.{skill_id}",
        "label_key": f"skill.{skill_id}.label",
        "value": value,
        "xp": xp,
        "xp_to_next": required,
        "progress_percent": percent,
        "trend": None,
    }


def _trait_projection(character: CharacterState, family: str, tier: int) -> dict[str, Any]:
    if family not in TRAIT_FAMILIES or not character.character_id.startswith("char."):
        raise ValueError(f"Unbekannte Trait-Zuordnung: {character.character_id}/{family}")
    trait_id = f"trait.{character.character_id.removeprefix('char.')}.{family}"
    progress = character.trait_progress.get(family, {})
    evidence = float(progress.get("evidence", character.trait_evidence.get(family, 0.0)))
    next_tier = tier + 1 if tier < len(ProgressionRules.trait_tiers) else None
    if next_tier is None:
        percent = 100
    else:
        previous = 0 if tier == 0 else ProgressionRules.trait_tiers[tier - 1][1]
        target = ProgressionRules.trait_tiers[tier][1]
        percent = max(0, min(100, round((evidence - previous) / (target - previous) * 100)))
    return {
        "trait_id": trait_id,
        "label_key": f"{trait_id}.label",
        "tier": tier,
        "evidence": evidence,
        "next_tier": next_tier,
        "progress_percent": percent,
        "effect_key": f"trait.effect.{family}",
        "consequence_key": f"trait.consequence.{family}",
    }


def _specialization_projection(value: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    specialization_id = value.get("specialization_id")
    stage = value.get("stage")
    if specialization_id not in SPECIALIZATIONS or stage not in SPECIALIZATION_XP_EFFECTS:
        raise ValueError("Unbekannte Spezialisierungszuordnung")
    short_id = specialization_id.removeprefix("spec.")
    return {
        "specialization_id": specialization_id,
        "label_key": f"specialization.{short_id}.label",
        "stage": stage,
        "stage_label_key": f"stage.{stage}.label",
    }


def _require_catalog_keys(projection: Mapping[str, Any], text_catalog: Mapping[str, str]) -> None:
    keys = [entry["label_key"] for entry in projection["skills"]]
    for entry in projection["traits"]:
        keys.extend((entry["label_key"], entry["effect_key"], entry["consequence_key"]))
    if projection["specialization"]:
        keys.extend((projection["specialization"]["label_key"], projection["specialization"]["stage_label_key"]))
    missing = sorted(key for key in keys if key not in text_catalog)
    if missing:
        raise KeyError(f"Fehlende Textschlüssel: {', '.join(missing)}")


def _top_skill(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {key: entry[key] for key in ("skill_id", "label_key", "value", "xp", "trend")}


def build_character_projection(
    character: CharacterState,
    journal_records: Sequence[Mapping[str, Any]],
    text_catalog: Mapping[str, str],
) -> dict[str, Any]:
    """Build a detached, text-key-only view of current character progression."""
    del journal_records  # Biography projection is a separate planned iteration.
    skills = [
        _skill_projection(skill_id, value, character.skill_xp.get(skill_id, 0))
        for skill_id, value in sorted(character.skills.items())
    ]
    traits = [
        _trait_projection(character, family, tier)
        for family, tier in sorted(character.traits.items())
    ]
    projection = {
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
        "top_skills": [_top_skill(entry) for entry in sorted(skills, key=lambda item: (-item["value"], item["skill_id"]))[:3]],
        "skills": skills,
        "traits": traits,
        "specialization": _specialization_projection(character.specialization),
        "biography": [],
        "capabilities": {"can_edit_profile": False, "can_undo_profile": False, "can_execute_action": False},
        "feedback": [],
    }
    _require_catalog_keys(projection, text_catalog)
    return projection
