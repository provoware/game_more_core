from __future__ import annotations

import hashlib
from collections.abc import Iterable


_FEEDBACK_RULES = {
    "character.level_up": ("level_up", ("old", "new")),
    "character.skill_level_up": ("skill_level_up", ("skill_id", "old", "new")),
    "character.trait_unlocked": ("trait_unlocked", ("trait_id", "old_tier", "new_tier")),
    "character.trait_tier_up": ("trait_tier_up", ("trait_id", "old_tier", "new_tier")),
    "character.specialization_changed": ("specialization_changed", ("old", "new")),
    "character.resonance_rank_up": ("resonance_rank_up", ("old", "new")),
}


def _feedback_id(event_id: str) -> str:
    digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
    return f"feedback:{digest}"


def build_confirmed_feedback(
    events: Iterable[dict],
    confirmed_event_ids: Iterable[str],
    *,
    reduced_motion: bool = False,
) -> list[dict]:
    """Build feedback in event order for explicitly confirmed event IDs."""
    confirmed = set(confirmed_event_ids)
    feedback = []
    for event in events:
        event_id = event.get("event_id")
        rule = _FEEDBACK_RULES.get(event.get("event_type"))
        if not isinstance(event_id, str) or event_id not in confirmed or rule is None:
            continue
        kind, placeholder_names = rule
        payload = event.get("payload", {})
        placeholders = {name: payload[name] for name in placeholder_names if name in payload}
        feedback.append(
            {
                "feedback_id": _feedback_id(event_id),
                "kind": kind,
                "title_key": f"feedback.character.{kind}.title",
                "detail_keys": [
                    {
                        "text_key": f"feedback.character.{kind}.detail",
                        "placeholders": placeholders,
                    }
                ],
                "reduced_motion": bool(reduced_motion),
            }
        )
    return feedback
