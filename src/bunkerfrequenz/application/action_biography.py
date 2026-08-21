from __future__ import annotations

from typing import Any, Mapping

from bunkerfrequenz.application.action_resolver import ResolvedAction


_OUTCOMES = frozenset({"failed", "partial", "success", "excellent", "legendary"})


def build_action_biography_event(
    action: Mapping[str, Any],
    resolved: ResolvedAction,
    policy: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Create one deterministic biography journal event or None from manifest policy."""
    if policy is None:
        return None
    if not isinstance(policy, Mapping) or policy.get("enabled") is not True:
        return None

    threshold = _bounded_int(policy.get("importance_threshold"), "importance_threshold", 0, 100)
    bounds = policy.get("importance_bounds")
    if bounds != [0, 100]:
        raise ValueError("Biografie importance_bounds muss [0, 100] sein")

    adjustments = policy.get("outcome_adjustments")
    if not isinstance(adjustments, Mapping) or set(adjustments) != _OUTCOMES:
        raise ValueError("Biografie outcome_adjustments ist unvollständig")
    if resolved.outcome not in _OUTCOMES:
        raise ValueError(f"Unbekanntes Action-Ergebnis für Biografie: {resolved.outcome}")

    base = _bounded_int(action.get("biography_importance_base"), "biography_importance_base", 0, 100)
    adjustment = adjustments[resolved.outcome]
    if isinstance(adjustment, bool) or not isinstance(adjustment, int):
        raise ValueError("Biografie outcome adjustment muss Ganzzahl sein")
    importance = min(100, max(0, base + adjustment))
    if importance < threshold:
        return None

    category = _category_for(action, resolved.outcome, policy)
    text_keys = policy.get("text_keys")
    if not isinstance(text_keys, Mapping) or category not in text_keys:
        raise ValueError(f"Biografie-Textvertrag fehlt für Kategorie {category}")
    text = text_keys[category]
    if not isinstance(text, Mapping):
        raise ValueError(f"Biografie-Textvertrag für {category} ist ungültig")
    title_key = _required_text(text.get("title_key"), f"{category}.title_key")
    body_key = _required_text(text.get("body_key"), f"{category}.body_key")

    return {
        "event_type": "character.biography_entry_added",
        "payload": {
            "entry_id": f"bio:{resolved.action_instance_id}",
            "category": category,
            "title_key": title_key,
            "body_key": body_key,
            "placeholders": {
                "action_id": resolved.action_id,
                "outcome": resolved.outcome,
                "importance": importance,
            },
        },
    }


def _category_for(action: Mapping[str, Any], outcome: str, policy: Mapping[str, Any]) -> str:
    if outcome == "failed":
        return _required_text(policy.get("failed_category"), "failed_category")
    mapping = policy.get("category_by_action_category")
    if not isinstance(mapping, Mapping):
        raise ValueError("Biografie category_by_action_category muss ein Mapping sein")
    category = action.get("category")
    if isinstance(category, str) and category in mapping:
        return _required_text(mapping[category], f"category_by_action_category.{category}")
    return _required_text(policy.get("fallback_category"), "fallback_category")


def _bounded_int(value: Any, field: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{field} muss Ganzzahl zwischen {minimum} und {maximum} sein")
    return value


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss ein nicht-leerer Text sein")
    return value
