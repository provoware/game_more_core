from __future__ import annotations

from typing import Any, Mapping, Sequence

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.progression import (
    ProgressionRules,
    SPECIALIZATIONS,
    SPECIALIZATION_XP_EFFECTS,
)
from bunkerfrequenz.presentation.biography_projection import build_biography_projection


TRAIT_FAMILIES = frozenset(
    {
        "krisenfest",
        "vernetzer",
        "klangfokus",
        "stromfokus",
        "planer",
        "scout",
        "improvisierer",
        "verhandler",
        "nachtmensch",
        "ausdauer",
        "kreativer",
        "risikospieler",
        "detailmensch",
        "crew_anker",
        "opportunist",
    }
)
CAPABILITY_KEYS = (
    "can_edit_profile",
    "can_undo_profile",
    "can_execute_action",
)


def _skill_projection(skill_name: str, value: int, xp: int) -> dict[str, Any]:
    skill_id = f"skill.{skill_name}"
    safe_xp = max(0, int(xp))
    if value >= ProgressionRules.skill_max:
        required = 0
        remaining = 0
        percent = 100
    else:
        required = ProgressionRules.xp_to_next_skill(value)
        remaining = max(0, required - safe_xp)
        percent = max(0, min(100, round(safe_xp / required * 100)))
    return {
        "skill_id": skill_id,
        "label_key": f"{skill_id}.label",
        "value": value,
        "xp": safe_xp,
        "xp_to_next": remaining,
        "progress_percent": percent,
        "trend": None,
    }


def _trait_projection(character: CharacterState, family: str) -> dict[str, Any] | None:
    if family not in TRAIT_FAMILIES:
        return None
    if not character.character_id.startswith("char."):
        raise ValueError(f"Ungültige Character-ID für Trait-Projektion: {character.character_id}")

    tier = int(character.traits.get(family, 0))
    trait_id = f"trait.{character.character_id.removeprefix('char.')}.{family}"
    next_tier = tier + 1 if tier < len(ProgressionRules.trait_tiers) else None

    if tier <= 0:
        evidence: float | None = None
        percent: int | None = None
    else:
        progress = character.trait_progress.get(family, {})
        evidence = float(progress.get("evidence", character.trait_evidence.get(family, 0.0)))
        if next_tier is None:
            percent = 100
        else:
            current_threshold = ProgressionRules.trait_tiers[tier - 1][1]
            next_threshold = ProgressionRules.trait_tiers[tier][1]
            percent = max(
                0,
                min(
                    100,
                    round((evidence - current_threshold) / (next_threshold - current_threshold) * 100),
                ),
            )

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
        keys.extend(
            (
                projection["specialization"]["label_key"],
                projection["specialization"]["stage_label_key"],
            )
        )
    missing = sorted(key for key in keys if key not in text_catalog)
    if missing:
        raise KeyError(f"Fehlende Textschlüssel: {', '.join(missing)}")


def _top_skill(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {key: entry[key] for key in ("skill_id", "label_key", "value", "xp", "trend")}


def _capability_projection(capabilities: Mapping[str, Any] | None) -> dict[str, bool]:
    values = capabilities or {}
    return {key: bool(values.get(key, False)) for key in CAPABILITY_KEYS}


def build_character_projection(
    character: CharacterState,
    journal_records: Sequence[Mapping[str, Any]],
    text_catalog: Mapping[str, str],
    capabilities: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a detached, deterministic, text-key-only character projection."""
    character.validate()
    skills = [
        _skill_projection(skill_name, value, character.skill_xp.get(skill_name, 0))
        for skill_name, value in sorted(character.skills.items())
    ]

    trait_families = sorted(
        (set(character.traits) | set(character.trait_progress) | set(character.trait_evidence))
        & TRAIT_FAMILIES
    )
    traits = [entry for family in trait_families if (entry := _trait_projection(character, family))]
    specialization = _specialization_projection(character.specialization)

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
        "top_skills": [
            _top_skill(entry)
            for entry in sorted(skills, key=lambda item: (-item["value"], item["skill_id"]))[:3]
        ],
        "skills": skills,
        "traits": traits,
        "specialization": specialization,
        "biography": build_biography_projection(character.character_id, journal_records),
        "capabilities": _capability_projection(capabilities),
        "feedback": [],
    }
    _require_catalog_keys(projection, text_catalog)
    return projection
