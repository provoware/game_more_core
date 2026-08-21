from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.presentation.components import build_components
from bunkerfrequenz.presentation.interaction_actions import (
    normalize_primary_actions,
    require_mapping,
    require_nonempty_text,
)
from bunkerfrequenz.presentation.state import PresentationState
from bunkerfrequenz.presentation.text_catalog import require_text_keys


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
    card = require_mapping(value, field)
    allowed = {"title_key", "detail_key", "placeholders", "status", "icon_id", "tone"}
    unknown = set(card) - allowed
    if unknown:
        raise ValueError(f"{field} enthält unbekannte Felder: {', '.join(sorted(unknown))}")
    title_key = require_nonempty_text(card.get("title_key"), f"{field}.title_key")
    detail_key = card.get("detail_key")
    if detail_key is not None:
        require_nonempty_text(detail_key, f"{field}.detail_key")
    placeholders = card.get("placeholders", {})
    if not isinstance(placeholders, Mapping):
        raise ValueError(f"{field}.placeholders muss ein Mapping sein")
    return {
        "title_key": title_key,
        "detail_key": detail_key,
        "placeholders": deepcopy(dict(placeholders)),
        "status": card.get("status"),
        "icon_id": card.get("icon_id"),
        "tone": card.get("tone"),
    }


def build_a4_ops_deck(
    projection: Mapping[str, Any],
    state: PresentationState,
    ui_manifest: Mapping[str, Any],
    text_catalog: Mapping[str, str],
    *,
    workflow: Mapping[str, Any] | None = None,
    action_selection: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Compose the A4 Ops Deck from shared components without adding gameplay state."""
    variant = _a4_variant(ui_manifest)
    focus_model = require_mapping(ui_manifest.get("focus_model"), "UI focus_model")
    accessibility = require_mapping(ui_manifest.get("accessibility"), "UI accessibility")
    contrast = require_mapping(ui_manifest.get("contrast"), "UI contrast")

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

    meta = require_mapping(projection.get("meta"), "Projection meta")
    character_id = require_nonempty_text(meta.get("character_id"), "Projection character_id")
    capabilities = require_mapping(projection.get("capabilities", {}), "Projection capabilities")
    primary_actions = normalize_primary_actions(
        source_workflow.get("primary_actions", ()),
        character_id=character_id,
        capabilities=capabilities,
        max_primary_actions=max_primary_actions,
        minimum_target_px=minimum_target_px,
        focus_ring_px=focus_ring_px,
    )
    raw_actions = source_workflow.get("primary_actions", ())
    if not isinstance(raw_actions, Sequence) or isinstance(raw_actions, (str, bytes)):
        raise ValueError("primary_actions muss eine Sequenz sein")
    if len(raw_actions) > max_primary_actions:
        raise ValueError(
            f"A4 erlaubt maximal {max_primary_actions} Primäraktionen, erhalten: {len(raw_actions)}"
        )

    meta = _require_mapping(projection.get("meta"), "Projection meta")
    character_id = _require_nonempty_text(meta.get("character_id"), "Projection character_id")
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
    selectable_actions = deepcopy(list(action_selection))
    for action in selectable_actions:
        if not isinstance(action, Mapping) or action.get("command", {}).get("character_id") != character_id:
            raise ValueError("Action-Auswahl gehört zu einem anderen Character")

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
                "action_selection": selectable_actions,
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
    require_text_keys(deck, text_catalog, context="A4")
    return deck
