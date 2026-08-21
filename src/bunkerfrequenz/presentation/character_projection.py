from __future__ import annotations

from copy import deepcopy
from typing import Any

from bunkerfrequenz.domain.progression import ProgressionRules


def _percent(current: float, target: float) -> float:
    if target <= 0:
        return 100.0
    return min(100.0, max(0.0, round(current / target * 100, 2)))


def _skill_entries(character: Any, catalog: dict) -> list[dict]:
    entries = []
    skill_catalog = catalog.get("skills", {})
    for skill_id in sorted(character.skills):
        value = int(character.skills[skill_id])
        xp = int(character.skill_xp.get(skill_id, 0))
        required = ProgressionRules.xp_to_next_skill(value)
        at_maximum = value >= ProgressionRules.skill_max
        entries.append({
            "skill_id": skill_id,
            "label_key": skill_catalog.get(skill_id, {}).get(
                "label_key", f"skill.{skill_id}.label"
            ),
            "value": value,
            "xp": xp,
            "xp_to_next": 0 if at_maximum else max(0, required - xp),
            "progress_percent": 100.0 if at_maximum else _percent(xp, required),
            "trend": None,
        })
    return entries


def _trait_entry(family: str, character: Any, config: dict) -> dict:
    tier = int(character.traits.get(family, 0))
    progress = character.trait_progress.get(family, {})
    evidence = float(progress.get("evidence", character.trait_evidence.get(family, 0.0)))
    next_tier = tier + 1 if tier < len(ProgressionRules.trait_tiers) else None
    target = ProgressionRules.trait_tiers[tier][1] if next_tier is not None else 0.0
    hidden = tier == 0
    return {
        "trait_id": config["trait_id"],
        "label_key": config["label_key"],
        "tier": tier,
        "evidence": None if hidden else evidence,
        "next_tier": next_tier,
        "progress_percent": None if hidden else _percent(evidence, target),
        "effect_key": config["effect_key"],
        "consequence_key": config["consequence_key"],
    }


def _traits(character: Any, catalog: dict) -> list[dict]:
    trait_catalog = catalog.get("traits", {})
    families = set(character.traits) | set(character.trait_progress)
    entries = []
    for family in sorted(families):
        config = trait_catalog.get(family)
        required = {"trait_id", "label_key", "effect_key", "consequence_key"}
        if isinstance(config, dict) and required <= config.keys():
            entries.append(_trait_entry(family, character, config))
    return entries


def _specialization(character: Any, catalog: dict) -> dict | None:
    source = character.specialization
    if not isinstance(source, dict):
        return None
    specialization_id = source.get("specialization_id")
    stage = source.get("stage")
    config = catalog.get("specializations", {}).get(specialization_id)
    if not isinstance(config, dict) or not config.get("label_key"):
        return None
    return {
        "specialization_id": specialization_id,
        "label_key": config["label_key"],
        "stage": stage,
        "stage_label_key": config.get("stage_label_keys", {}).get(stage),
    }


def _biography(records: list[dict], catalog: dict) -> list[dict]:
    event_catalog = catalog.get("journal_events", {})
    entries = []
    for record in records:
        config = event_catalog.get(record.get("event_type"))
        payload = record.get("payload", {})
        if not isinstance(config, dict) or not isinstance(payload, dict):
            continue
        if not record.get("event_id") or not isinstance(record.get("sequence"), int):
            continue
        entries.append({
            "entry_id": payload.get("entry_id", record["event_id"]),
            "event_id": record["event_id"],
            "category": config.get("category"),
            "title_key": config.get("title_key"),
            "body_key": config.get("body_key"),
            "placeholders": deepcopy(payload.get("placeholders", {})),
            "sequence": record["sequence"],
        })
    return sorted(entries, key=lambda entry: (entry["sequence"], entry["event_id"]))


def build_character_projection(
    character: Any, journal_records: list[dict], text_catalog: dict
) -> dict:
    """Build a detached, deterministic display projection for a character."""
    skills = _skill_entries(character, text_catalog)
    top_skills = [
        {key: entry[key] for key in ("skill_id", "label_key", "value", "xp", "trend")}
        for entry in sorted(skills, key=lambda item: (-item["value"], item["skill_id"]))[:3]
    ]
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
        "top_skills": top_skills,
        "skills": skills,
        "traits": _traits(character, text_catalog),
        "specialization": _specialization(character, text_catalog),
        "biography": _biography(journal_records, text_catalog),
        "capabilities": {
            "can_edit_profile": False,
            "can_undo_profile": False,
            "can_execute_action": False,
        },
        "feedback": [],
    }
