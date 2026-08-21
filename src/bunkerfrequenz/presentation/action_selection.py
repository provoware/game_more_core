from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


def build_action_selection(
    character_id: str,
    actions: Sequence[Mapping[str, Any]],
    *,
    can_execute_action: bool,
    prerequisite_status: Mapping[str, bool] | None = None,
) -> list[dict[str, Any]]:
    """Project manifest actions into a detached, fail-closed A4 selection list."""
    if not isinstance(character_id, str) or not character_id.strip():
        raise ValueError("character_id muss ein nicht-leerer Text sein")
    status = prerequisite_status or {}
    result = []
    seen: set[str] = set()
    for action in actions:
        action_id = _required_text(action.get("action_id"), "action_id")
        if action_id in seen:
            raise ValueError(f"Doppelte Action-ID: {action_id}")
        seen.add(action_id)
        prerequisites = _prerequisites(action.get("prerequisites", ()), status)
        duration = _duration(action.get("duration"))
        result.append({
            "action_id": action_id,
            "label_key": f"{action_id}.label",
            "category": _required_text(action.get("category"), f"{action_id}.category"),
            "enabled": can_execute_action and all(item["met"] for item in prerequisites),
            "prerequisites": prerequisites,
            "duration": duration,
            "resources": {
                "energy_delta": None,
                "stress_delta": None,
                "status": "not_defined",
                "status_key": "ui.action.resources.not_defined",
                "cost_model": action.get("cost_model"),
            },
            "expected_skill_effects": _skill_effects(action.get("skill_weights")),
            "selection_requirements": [
                field for field, weights_field in (
                    ("selected_skill", "skill_weights"),
                    ("selected_trait_family", "trait_evidence_weights"),
                )
                if field in action.get(weights_field, {})
            ],
            "command": {
                "type": "action.execute",
                "character_id": character_id,
                "action_id": action_id,
            },
        })
    return deepcopy(result)


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss ein nicht-leerer Text sein")
    return value


def _prerequisites(value: Any, status: Mapping[str, bool]) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("prerequisites muss eine Sequenz sein")
    return [
        {"rule_id": _required_text(rule, "prerequisite"), "met": status.get(rule) is True}
        for rule in value
    ]


def _duration(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("duration muss ein Mapping sein")
    mode = _required_text(value.get("mode"), "duration.mode")
    minutes = value.get("minutes")
    if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes < 0:
        raise ValueError("duration.minutes muss eine nicht-negative Ganzzahl sein")
    return {"mode": mode, "minutes": minutes}


def _skill_effects(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("skill_weights muss ein nicht-leeres Mapping sein")
    return [
        {
            "skill_id": skill_id,
            "label_key": f"skill.{skill_id}.label" if skill_id != "selected_skill" else None,
            "weight_percent": round(float(weight) * 100),
        }
        for skill_id, weight in value.items()
    ]
