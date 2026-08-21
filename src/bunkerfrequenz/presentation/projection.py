from __future__ import annotations

from typing import Iterable, Mapping

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.progression import ProgressionRules


def _require_key(text_catalog: Mapping[str, str], key: str) -> str:
    if key not in text_catalog:
        raise KeyError(f"Fehlender Textschlüssel: {key}")
    return key


def _skill_rows(character: CharacterState, text_catalog: Mapping[str, str]) -> list[dict]:
    rows = []
    for skill_id, value in character.skills.items():
        xp = character.skill_xp.get(skill_id, 0)
        required = ProgressionRules.xp_to_next_skill(value)
        rows.append({
            "skill_id": skill_id,
            "label_key": _require_key(text_catalog, f"skill.{skill_id}"),
            "value": value,
            "xp": xp,
            "xp_to_next": required,
            "progress_percent": min(100, round(100 * xp / required)),
            "trend": None,
        })
    return rows


def _trait_rows(character: CharacterState, text_catalog: Mapping[str, str]) -> list[dict]:
    rows = []
    for family, tier in sorted(character.traits.items()):
        progress = character.trait_progress.get(family, {})
        evidence = float(progress.get("evidence", character.trait_evidence.get(family, 0.0)))
        next_tier = tier + 1 if tier < len(ProgressionRules.trait_tiers) else None
        threshold = ProgressionRules.trait_tiers[tier][1] if next_tier else None
        rows.append({
            "trait_id": family,
            "label_key": _require_key(text_catalog, f"trait.{family}"),
            "tier": tier,
            "evidence": evidence,
            "next_tier": next_tier,
            "progress_percent": min(100, round(100 * evidence / threshold)) if threshold else 100,
            "effect_key": _require_key(text_catalog, f"trait.{family}.effect"),
            "consequence_key": _require_key(text_catalog, f"trait.{family}.consequence"),
        })
    return rows


def _biography(records: Iterable[dict], text_catalog: Mapping[str, str]) -> list[dict]:
    entries = []
    for record in records:
        if record.get("event_type") != "character.biography_entry_added":
            continue
        payload = record.get("payload", {})
        title_key = _require_key(text_catalog, payload["title_key"])
        body_key = _require_key(text_catalog, payload["body_key"])
        entries.append({
            "entry_id": payload["entry_id"],
            "event_id": record["event_id"],
            "category": payload["category"],
            "title_key": title_key,
            "body_key": body_key,
            "placeholders": dict(payload.get("placeholders", {})),
            "sequence": record["sequence"],
        })
    return sorted(entries, key=lambda row: (row["sequence"], row["event_id"]))


def build_character_projection(
    character: CharacterState,
    journal_records: Iterable[dict],
    text_catalog: Mapping[str, str],
    *,
    capabilities: Mapping[str, bool],
    feedback: Iterable[dict] = (),
) -> dict:
    """Return detached display data; never expose the mutable domain object."""
    character.validate()
    skills = _skill_rows(character, text_catalog)
    specialization = None
    if character.specialization:
        specialization_id = character.specialization["specialization_id"]
        stage = character.specialization["stage"]
        specialization = {
            "specialization_id": specialization_id,
            "label_key": _require_key(text_catalog, specialization_id),
            "stage": stage,
            "stage_label_key": _require_key(text_catalog, f"specialization.stage.{stage}"),
        }
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
        "top_skills": sorted(skills, key=lambda row: (-row["value"], row["skill_id"]))[:3],
        "skills": skills,
        "traits": _trait_rows(character, text_catalog),
        "specialization": specialization,
        "biography": _biography(journal_records, text_catalog),
        "capabilities": {key: bool(capabilities[key]) for key in (
            "can_edit_profile", "can_undo_profile", "can_execute_action"
        )},
        "feedback": [dict(item) for item in feedback],
    }
