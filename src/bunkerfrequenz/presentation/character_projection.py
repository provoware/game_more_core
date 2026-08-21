from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping

from bunkerfrequenz.domain.character import CharacterState, START_SKILLS
from bunkerfrequenz.domain.progression import ProgressionRules

PROJECTION_VERSION = "0.6"
TRAIT_FAMILIES = frozenset(
    (
        "krisenfest", "vernetzer", "klangfokus", "stromfokus", "planer",
        "scout", "improvisierer", "verhandler", "nachtmensch", "ausdauer",
        "kreativer", "risikospieler", "detailmensch", "crew_anker", "opportunist",
    )
)
FEEDBACK_TITLES = {
    "character.level_up": ("level", "ui.level_up"),
    "character.skill_level_up": ("skill", "ui.skill_up"),
    "character.trait_unlocked": ("trait", "ui.trait_unlock"),
    "character.trait_tier_up": ("trait", "ui.trait_unlock"),
    "character.specialization_changed": ("specialization", "ui.specialization"),
    "character.resonance_xp_gained": ("resonance", "ui.resonance_up"),
    "character.resonance_rank_up": ("resonance", "ui.resonance_up"),
}


def _skills(character: CharacterState) -> list[dict[str, Any]]:
    result = []
    for skill_id in START_SKILLS:
        value = character.skills[skill_id]
        xp = character.skill_xp.get(skill_id, 0)
        needed = ProgressionRules.xp_to_next_skill(value)
        progress = 100 if value >= ProgressionRules.skill_max else round(100 * xp / needed)
        result.append({
            "skill_id": skill_id, "label_key": f"skill.{skill_id}.name",
            "value": value, "xp": xp, "xp_to_next": needed,
            "progress_percent": max(0, min(100, progress)), "trend": None,
        })
    return result


def _traits(character: CharacterState) -> list[dict[str, Any]]:
    result = []
    for family, tier in sorted(character.traits.items()):
        if family not in TRAIT_FAMILIES:
            continue
        evidence = float(character.trait_evidence.get(family, 0.0))
        next_tier = tier + 1 if tier < len(ProgressionRules.trait_tiers) else None
        threshold = ProgressionRules.trait_tiers[tier][1] if next_tier else evidence
        progress = 100 if next_tier is None else round(100 * evidence / threshold)
        result.append({
            "trait_id": family, "label_key": f"trait.{family}.name", "tier": tier,
            "evidence": evidence, "next_tier": next_tier,
            "progress_percent": max(0, min(100, progress)),
            "effect_key": f"trait.{family}.effect",
            "consequence_key": f"trait.{family}.consequence",
        })
    return result


def _biography(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    entries = []
    for record in records:
        if record.get("event_type") != "character.biography_entry_added":
            continue
        payload = record.get("payload", {})
        entries.append({
            "entry_id": payload.get("entry_id"), "event_id": record.get("event_id"),
            "category": payload.get("category"), "title_key": payload.get("title_key"),
            "body_key": payload.get("body_key"),
            "placeholders": deepcopy(payload.get("placeholders", {})),
            "sequence": int(record.get("sequence", 0)),
        })
    return sorted(entries, key=lambda entry: (entry["sequence"], entry["event_id"] or ""))


def _feedback(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    feedback = []
    for record in records:
        definition = FEEDBACK_TITLES.get(record.get("event_type"))
        if not definition or not record.get("event_id"):
            continue
        kind, title_key = definition
        feedback.append({
            "feedback_id": record["event_id"], "kind": kind, "title_key": title_key,
            "detail_keys": [f"feedback.{record['event_type']}.detail"],
            "reduced_motion": "static", "payload": deepcopy(record.get("payload", {})),
        })
    return feedback


def build_character_projection(
    character: CharacterState,
    journal_records: Iterable[Mapping[str, Any]],
    text_catalog: Mapping[str, str],
    capabilities: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Create a detached display projection without changing domain or journal data."""
    del text_catalog  # Resolution remains a rendering concern; only keys cross this boundary.
    records = tuple(journal_records)
    skills = _skills(character)
    top_skills = sorted(skills, key=lambda item: (-item["value"], item["skill_id"]))[:3]
    specialization = deepcopy(character.specialization)
    if specialization:
        specialization = {
            **specialization,
            "label_key": f"specialization.{specialization['specialization_id']}.name",
            "stage_label_key": f"specialization.stage.{specialization['stage']}",
        }
    allowed = capabilities or {}
    return {
        "meta": {"projection_version": PROJECTION_VERSION, "character_id": character.character_id},
        "overview": {
            key: deepcopy(getattr(character, key)) for key in (
                "display_name", "alias", "additional_nicknames", "motto", "level",
                "total_xp", "resonance_xp", "resonance_rank", "energy", "stress", "reputation",
            )
        },
        "top_skills": [{key: item[key] for key in ("skill_id", "label_key", "value", "xp", "trend")} for item in top_skills],
        "skills": skills, "traits": _traits(character), "specialization": specialization,
        "biography": _biography(records),
        "capabilities": {key: bool(allowed.get(key, False)) for key in (
            "can_edit_profile", "can_undo_profile", "can_execute_action",
        )},
        "feedback": _feedback(records),
    }
