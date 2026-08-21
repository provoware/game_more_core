from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


_SELECTION_FIELDS = frozenset({"selected_skill", "selected_trait_family"})
_TEMPLATE_FIELDS = frozenset({"type", "character_id", "action_id"})
_RESOURCE_FIELDS = frozenset({"energy_delta", "stress_delta"})


def build_action_selection(
    character_id: str,
    actions: Sequence[Mapping[str, Any]],
    *,
    can_execute_action: bool,
    prerequisite_status: Mapping[str, bool] | None = None,
) -> list[dict[str, Any]]:
    """Project manifest actions into a detached, fail-closed A4 selection list."""
    character_id = _required_text(character_id, "character_id")
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
        resources = _resources(action.get("resource_effects"), action.get("cost_model"))
        result.append({
            "action_id": action_id,
            "label_key": f"{action_id}.label",
            "category": _required_text(action.get("category"), f"{action_id}.category"),
            "enabled": can_execute_action and all(item["met"] for item in prerequisites),
            "prerequisites": prerequisites,
            "duration": duration,
            "resources": resources,
            "expected_skill_effects": _skill_effects(action.get("skill_weights")),
            "selection_requirements": [
                field for field, weights_field in (
                    ("selected_skill", "skill_weights"),
                    ("selected_trait_family", "trait_evidence_weights"),
                )
                if field in action.get(weights_field, {})
            ],
            "command_template": {
                "type": "action.execute",
                "character_id": character_id,
                "action_id": action_id,
            },
            "required_runtime_ids": ["command_id", "action_instance_id"],
        })
    return deepcopy(result)


def build_action_execute_command(
    selection: Mapping[str, Any],
    *,
    command_id: str,
    action_instance_id: str,
    selected_skill: str | None = None,
    selected_trait_family: str | None = None,
) -> dict[str, Any]:
    """Turn one enabled selection into a complete existing-dispatcher command."""
    if not isinstance(selection, Mapping):
        raise ValueError("selection muss ein Mapping sein")
    if selection.get("enabled") is not True:
        raise ValueError("Action-Auswahl ist nicht bestätigt ausführbar")

    template = selection.get("command_template")
    if not isinstance(template, Mapping) or set(template) != _TEMPLATE_FIELDS:
        raise ValueError("command_template ist ungültig")
    if template.get("type") != "action.execute":
        raise ValueError("command_template besitzt einen unbekannten Commandtyp")

    command = {
        "type": "action.execute",
        "character_id": _required_text(template.get("character_id"), "command_template.character_id"),
        "command_id": _required_text(command_id, "command_id"),
        "action_id": _required_text(template.get("action_id"), "command_template.action_id"),
        "action_instance_id": _required_text(action_instance_id, "action_instance_id"),
    }

    requirements = selection.get("selection_requirements", ())
    if not isinstance(requirements, Sequence) or isinstance(requirements, (str, bytes)):
        raise ValueError("selection_requirements muss eine Sequenz sein")
    requirement_set = set(requirements)
    if not requirement_set.issubset(_SELECTION_FIELDS):
        raise ValueError("selection_requirements enthält unbekannte Felder")

    supplied = {
        "selected_skill": selected_skill,
        "selected_trait_family": selected_trait_family,
    }
    for field, value in supplied.items():
        if field in requirement_set:
            command[field] = _required_text(value, field)
        elif value is not None:
            raise ValueError(f"{field} ist für diese Action nicht zulässig")

    return command


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


def _resources(value: Any, cost_model: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _RESOURCE_FIELDS:
        raise ValueError("resource_effects benötigt exakt energy_delta und stress_delta")
    energy_delta = value["energy_delta"]
    stress_delta = value["stress_delta"]
    if any(
        isinstance(item, bool) or not isinstance(item, int) or not -100 <= item <= 100
        for item in (energy_delta, stress_delta)
    ):
        raise ValueError("resource_effects benötigt Ganzzahlen zwischen -100 und 100")
    return {
        "energy_delta": energy_delta,
        "stress_delta": stress_delta,
        "status": "defined",
        "status_key": "ui.action.resources.defined",
        "cost_model": cost_model,
    }


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
