from __future__ import annotations

import hashlib
from typing import Any, Iterable, Mapping, Sequence


_FEEDBACK_RULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "character.level_up": ("level_up", ("old", "new")),
    "character.skill_level_up": ("skill_level_up", ("skill_id", "old", "new")),
    "character.trait_unlocked": ("trait_unlocked", ("family", "old_tier", "new_tier")),
    "character.trait_tier_up": ("trait_tier_up", ("family", "old_tier", "new_tier")),
    "character.specialization_changed": ("specialization_changed", ("old", "new")),
    "character.resonance_rank_up": ("resonance_rank_up", ("old", "new")),
}


def _feedback_id(event_id: str) -> str:
    return f"feedback:{hashlib.sha256(event_id.encode('utf-8')).hexdigest()}"


def _subject_label_key(event: Mapping[str, Any]) -> str | None:
    event_type = event.get("event_type")
    payload = event.get("payload", {})
    if event_type == "character.skill_level_up":
        skill_id = payload.get("skill_id")
        return f"skill.{skill_id}.label" if isinstance(skill_id, str) and skill_id else None
    if event_type in {"character.trait_unlocked", "character.trait_tier_up"}:
        family = payload.get("family")
        character_id = event.get("character_id")
        if (
            isinstance(family, str)
            and family
            and isinstance(character_id, str)
            and character_id.startswith("char.")
        ):
            return f"trait.{character_id.removeprefix('char.')}.{family}.label"
        return None
    if event_type == "character.specialization_changed":
        new_value = payload.get("new")
        if isinstance(new_value, Mapping):
            specialization_id = new_value.get("specialization_id")
            if isinstance(specialization_id, str) and specialization_id.startswith("spec."):
                return f"specialization.{specialization_id.removeprefix('spec.')}.label"
    return None


def _detail_placeholders(kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    if kind in {"level_up", "resonance_rank_up", "skill_level_up"}:
        return {key: payload[key] for key in ("old", "new") if key in payload}
    if kind in {"trait_unlocked", "trait_tier_up"}:
        return {key: payload[key] for key in ("old_tier", "new_tier") if key in payload}
    return {}


def build_confirmed_feedback(
    events: Sequence[Mapping[str, Any]],
    confirmed_event_ids: Iterable[str],
    *,
    journal_event_types: Iterable[str],
    text_catalog: Mapping[str, str],
    dismissed_feedback_ids: Iterable[str] = (),
    reduced_motion: bool = False,
) -> list[dict[str, Any]]:
    """Project only confirmed, catalogued progression events into deterministic UI feedback."""
    confirmed = frozenset(confirmed_event_ids)
    allowed_events = frozenset(journal_event_types)
    dismissed = frozenset(dismissed_feedback_ids)
    feedback: list[dict[str, Any]] = []

    for event in events:
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        if not isinstance(event_id, str) or event_id not in confirmed:
            continue
        if not isinstance(event_type, str) or event_type not in allowed_events:
            continue
        rule = _FEEDBACK_RULES.get(event_type)
        if rule is None:
            continue
        kind, required_payload = rule
        payload = event.get("payload")
        if not isinstance(payload, Mapping) or any(field not in payload for field in required_payload):
            continue

        feedback_id = _feedback_id(event_id)
        if feedback_id in dismissed:
            continue
        title_key = f"feedback.character.{kind}.title"
        detail_key = f"feedback.character.{kind}.detail"
        subject_label_key = _subject_label_key(event)
        required_text_keys = [title_key, detail_key]
        if subject_label_key is not None:
            required_text_keys.append(subject_label_key)
        missing = [key for key in required_text_keys if key not in text_catalog]
        if missing:
            raise KeyError(f"Fehlende Feedback-Textschlüssel: {', '.join(sorted(missing))}")

        feedback.append(
            {
                "feedback_id": feedback_id,
                "source_event_id": event_id,
                "kind": kind,
                "title_key": title_key,
                "subject_label_key": subject_label_key,
                "detail_keys": [
                    {
                        "text_key": detail_key,
                        "placeholders": _detail_placeholders(kind, payload),
                    }
                ],
                "reduced_motion": bool(reduced_motion),
            }
        )
    return feedback
