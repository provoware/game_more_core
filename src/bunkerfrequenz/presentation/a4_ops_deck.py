from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence

from bunkerfrequenz.presentation.components import build_components
from bunkerfrequenz.presentation.state import PresentationState


_DISPATCH_ROUTE = "application.command_dispatcher.dispatch_command"
_COMMAND_REQUIREMENTS = {
    "profile.update": ("character_id", "command_id", "event_id", "transaction_id", "changes"),
    "profile.undo_last": ("character_id", "command_id", "event_id", "transaction_id"),
    "action.execute": ("character_id", "command_id", "action_id", "action_instance_id"),
}
_COMMAND_CAPABILITIES = {
    "profile.update": "can_edit_profile",
    "profile.undo_last": "can_undo_profile",
    "action.execute": "can_execute_action",
}
_STEP_PRESENTATION = {
    "current_goal": ("target", "primary"),
    "next_action": ("play", "attention"),
    "result": ("check", "success"),
    "development": ("progress", "info"),
    "next_goal": ("arrow-right", "neutral"),
}
_VIEW_COMPONENTS = {
    "overview": ("ProfileEditor", "SpecializationCard"),
    "skills_traits": ("SkillList", "TraitList", "SpecializationCard"),
    "biography": ("BiographyTimeline",),
}


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} muss ein Mapping sein")
    return value


def _a4_variant(ui_manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    variants = ui_manifest.get("variants", ())
    if not isinstance(variants, Sequence) or isinstance(variants, (str, bytes)):
        raise ValueError("UI-Manifest enthält keine gültigen Varianten")
    for variant in variants:
        if isinstance(variant, Mapping) and variant.get("id") == "A4_OPS_DECK":
            return variant
    raise ValueError("UI-Manifest enthält A4_OPS_DECK nicht")


def _normalize_content_card(value: Any, field: str) -> dict[str, Any] | None:
    if value is None:
        return None
    card = _require_mapping(value, field)
    allowed = {"title_key", "detail_key", "placeholders", "status", "icon_id", "tone"}
    unknown = set(card) - allowed
    if unknown:
        raise ValueError(f"{field} enthält unbekannte Felder: {', '.join(sorted(unknown))}")
    title_key = card.get("title_key")
    if not isinstance(title_key, str) or not title_key.strip():
        raise ValueError(f"{field}.title_key fehlt")
    detail_key = card.get("detail_key")
    if detail_key is not None and (not isinstance(detail_key, str) or not detail_key.strip()):
        raise ValueError(f"{field}.detail_key ist ungültig")
    placeholders = card.get("placeholders", {})
    if not isinstance(placeholders, Mapping):
        raise ValueError(f"{field}.placeholders muss ein Mapping sein")
    normalized = {
        "title_key": title_key,
        "detail_key": detail_key,
        "placeholders": deepcopy(dict(placeholders)),
        "status": card.get("status"),
        "icon_id": card.get("icon_id"),
        "tone": card.get("tone"),
    }
    return normalized


def _normalize_primary_action(
    value: Any,
    *,
    order: int,
    character_id: str,
    capabilities: Mapping[str, Any],
    minimum_target_px: int,
    focus_ring_px: int,
) -> dict[str, Any]:
    action = _require_mapping(value, f"primary_actions[{order - 1}]")
    action_id = action.get("action_id")
    label_key = action.get("label_key")
    icon_id = action.get("icon_id")
    tone = action.get("tone", "primary")
    enabled = action.get("enabled", True)
    command = action.get("command")

    if not isinstance(action_id, str) or not action_id.strip():
        raise ValueError("Primäraktion benötigt action_id")
    if not isinstance(label_key, str) or not label_key.strip():
        raise ValueError(f"Primäraktion {action_id} benötigt label_key")
    if not isinstance(icon_id, str) or not icon_id.strip():
        raise ValueError(f"Primäraktion {action_id} benötigt icon_id")
    if not isinstance(tone, str) or not tone.strip():
        raise ValueError(f"Primäraktion {action_id} benötigt tone")
    if not isinstance(enabled, bool):
        raise ValueError(f"Primäraktion {action_id}.enabled muss bool sein")

    command_map = _require_mapping(command, f"Primäraktion {action_id}.command")
    command_type = command_map.get("type")
    if command_type not in _COMMAND_REQUIREMENTS:
        raise ValueError(f"Primäraktion {action_id} hat unbekannten Schreibcommand")
    missing = [field for field in _COMMAND_REQUIREMENTS[command_type] if field not in command_map]
    if missing:
        raise ValueError(
            f"Primäraktion {action_id} ist nicht dispatcher-fertig: {', '.join(missing)} fehlt"
        )
    if command_map.get("character_id") != character_id:
        raise ValueError(f"Primäraktion {action_id} gehört zu einem anderen Character")
    if command_type == "profile.update" and not isinstance(command_map.get("changes"), Mapping):
        raise ValueError(f"Primäraktion {action_id}.changes muss ein Mapping sein")

    capability = _COMMAND_CAPABILITIES[command_type]
    if enabled and not bool(capabilities.get(capability, False)):
        raise ValueError(f"Primäraktion {action_id} ist laut bestätigter Capability nicht verfügbar")

    return {
        "action_id": action_id,
        "label_key": label_key,
        "aria_label_key": label_key,
        "icon_id": icon_id,
        "tone": tone,
        "enabled": enabled,
        "keyboard_order": order,
        "target_px": minimum_target_px,
        "focus_ring_px": focus_ring_px,
        "dispatch": {
            "route": _DISPATCH_ROUTE,
            "command": deepcopy(dict(command_map)),
        },
    }


def _iter_text_keys(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for field, child in value.items():
            if isinstance(field, str) and field.endswith("_key") and isinstance(child, str):
                yield child
            else:
                yield from _iter_text_keys(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield from _iter_text_keys(child)


def _require_text_keys(value: Any, text_catalog: Mapping[str, str]) -> None:
    missing = sorted({key for key in _iter_text_keys(value) if key not in text_catalog})
    if missing:
        raise KeyError(f"Fehlende A4-Textschlüssel: {', '.join(missing)}")


def build_a4_ops_deck(
    projection: Mapping[str, Any],
    state: PresentationState,
    ui_manifest: Mapping[str, Any],
    text_catalog: Mapping[str, str],
    *,
    workflow: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose the A4 Ops Deck from shared components without adding gameplay state."""
    variant = _a4_variant(ui_manifest)
    focus_model = _require_mapping(ui_manifest.get("focus_model"), "UI focus_model")
    accessibility = _require_mapping(ui_manifest.get("accessibility"), "UI accessibility")
    contrast = _require_mapping(ui_manifest.get("contrast"), "UI contrast")

    workflow_order = tuple(focus_model.get("workflow", ()))
    if not workflow_order or any(step not in _STEP_PRESENTATION for step in workflow_order):
        raise ValueError("UI-Manifest enthält einen unbekannten oder leeren A4-Workflow")
    max_primary_actions = int(focus_model.get("max_primary_actions_visible", 0))
    if max_primary_actions < 1:
        raise ValueError("UI-Manifest benötigt max_primary_actions_visible >= 1")

    minimum_target_px = int(accessibility.get("minimum_target_px", 0))
    focus_ring_px = int(accessibility.get("focus_ring_px", 0))
    if minimum_target_px < 1 or focus_ring_px < 1:
        raise ValueError("UI-Manifest enthält ungültige Interaktionsmaße")

    source_workflow = deepcopy(dict(workflow or {}))
    allowed_workflow_fields = {"current_goal", "primary_actions", "result", "next_goal"}
    unknown_workflow_fields = set(source_workflow) - allowed_workflow_fields
    if unknown_workflow_fields:
        raise ValueError(
            f"A4-Workflow enthält unbekannte Felder: {', '.join(sorted(unknown_workflow_fields))}"
        )

    raw_actions = source_workflow.get("primary_actions", ())
    if not isinstance(raw_actions, Sequence) or isinstance(raw_actions, (str, bytes)):
        raise ValueError("primary_actions muss eine Sequenz sein")
    if len(raw_actions) > max_primary_actions:
        raise ValueError(
            f"A4 erlaubt maximal {max_primary_actions} Primäraktionen, erhalten: {len(raw_actions)}"
        )

    meta = _require_mapping(projection.get("meta"), "Projection meta")
    character_id = meta.get("character_id")
    if not isinstance(character_id, str) or not character_id.strip():
        raise ValueError("Projection benötigt character_id")
    capabilities = _require_mapping(projection.get("capabilities", {}), "Projection capabilities")

    primary_actions = [
        _normalize_primary_action(
            action,
            order=index,
            character_id=character_id,
            capabilities=capabilities,
            minimum_target_px=minimum_target_px,
            focus_ring_px=focus_ring_px,
        )
        for index, action in enumerate(raw_actions, start=1)
    ]

    components = build_components(projection, state)
    selected_components = _VIEW_COMPONENTS.get(state.selected_view)
    if selected_components is None:
        raise ValueError(f"A4 kennt View {state.selected_view} nicht")

    content_by_step = {
        "current_goal": _normalize_content_card(source_workflow.get("current_goal"), "current_goal"),
        "result": _normalize_content_card(source_workflow.get("result"), "result"),
        "next_goal": _normalize_content_card(source_workflow.get("next_goal"), "next_goal"),
    }
    component_refs_by_step = {
        "current_goal": ("CharacterHeader",),
        "next_action": ("ProfileEditor",),
        "result": ("ProgressFeedback",),
        "development": (
            "StatusSummary",
            "SkillList",
            "TraitList",
            "SpecializationCard",
            "BiographyTimeline",
        ),
        "next_goal": (),
    }

    workflow_steps = []
    for step_id in workflow_order:
        icon_id, tone = _STEP_PRESENTATION[step_id]
        step = {
            "step_id": step_id,
            "label_key": f"ui.workflow.{step_id}",
            "aria_label_key": f"ui.workflow.{step_id}",
            "icon_id": icon_id,
            "tone": tone,
            "component_refs": list(component_refs_by_step[step_id]),
            "content": content_by_step.get(step_id),
        }
        if step_id == "next_action":
            step["primary_action_ids"] = [action["action_id"] for action in primary_actions]
        workflow_steps.append(step)

    deck = {
        "view_model_version": "0.6.3",
        "layout": {
            "variant_id": "A4_OPS_DECK",
            "layout_token": variant.get("layout"),
            "density": variant.get("density"),
            "best_for": variant.get("best_for"),
        },
        "character_id": character_id,
        "selected_view": state.selected_view,
        "components": components,
        "workflow": workflow_steps,
        "zones": {
            "header": {"component_refs": ["CharacterHeader"]},
            "workflow_rail": {"step_ids": list(workflow_order)},
            "workspace": {
                "current_goal": deepcopy(content_by_step["current_goal"]),
                "primary_actions": primary_actions,
                "selected_view_component_refs": list(selected_components),
            },
            "live_status": {"component_refs": ["StatusSummary", "ProgressFeedback"]},
        },
        "keyboard_order": [action["action_id"] for action in primary_actions],
        "accessibility": {
            "minimum_body_px": accessibility.get("minimum_body_px"),
            "preferred_body_px": accessibility.get("preferred_body_px"),
            "minimum_target_px": minimum_target_px,
            "focus_ring_px": focus_ring_px,
            "keyboard_navigation": bool(accessibility.get("keyboard_navigation", False)),
            "screen_reader_labels": bool(accessibility.get("screen_reader_labels", False)),
            "high_contrast_mode": bool(accessibility.get("high_contrast_mode", False)),
            "reduced_motion": state.reduced_motion,
            "color_never_sole_information": contrast.get("rule") == "color_never_sole_information",
            "semantic_cues": ["text", "icon", "tone"],
        },
    }
    _require_text_keys(deck, text_catalog)
    return deck
