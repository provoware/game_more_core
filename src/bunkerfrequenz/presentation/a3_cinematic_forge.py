from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.presentation.animation_cues import build_animation_cues
from bunkerfrequenz.presentation.components import build_components
from bunkerfrequenz.presentation.interaction_actions import (
    normalize_primary_actions,
    require_mapping,
    require_nonempty_text,
)
from bunkerfrequenz.presentation.state import PresentationState
from bunkerfrequenz.presentation.text_catalog import require_text_keys


_VIEW_DRAWER_COMPONENTS = {
    "overview": ("ProfileEditor", "SpecializationCard"),
    "skills_traits": ("SkillList", "TraitList", "SpecializationCard"),
    "biography": ("BiographyTimeline",),
}


def _a3_variant(ui_manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    variants = ui_manifest.get("variants", ())
    if not isinstance(variants, Sequence) or isinstance(variants, (str, bytes)):
        raise ValueError("UI-Manifest enthält keine gültigen Varianten")
    for variant in variants:
        if isinstance(variant, Mapping) and variant.get("id") == "A3_CINEMATIC_FORGE":
            return variant
    raise ValueError("UI-Manifest enthält A3_CINEMATIC_FORGE nicht")


def _radial_nodes(
    items: Sequence[Mapping[str, Any]],
    *,
    id_field: str,
    value_fields: Sequence[str],
) -> list[dict[str, Any]]:
    count = len(items)
    if count == 0:
        return []
    nodes: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        node_id = item.get(id_field)
        if not isinstance(node_id, str) or not node_id.strip():
            continue
        node = {
            "node_id": node_id,
            "label_key": item.get("label_key"),
            "angle_degrees": round((360.0 / count) * index, 3),
            "order": index + 1,
        }
        for field in value_fields:
            node[field] = deepcopy(item.get(field))
        nodes.append(node)
    return nodes


def _accessibility_projection(
    ui_manifest: Mapping[str, Any],
    state: PresentationState,
) -> dict[str, Any]:
    accessibility = require_mapping(ui_manifest.get("accessibility"), "UI accessibility")
    contrast = require_mapping(ui_manifest.get("contrast"), "UI contrast")
    minimum_target_px = int(accessibility.get("minimum_target_px", 0))
    focus_ring_px = int(accessibility.get("focus_ring_px", 0))
    if minimum_target_px < 1 or focus_ring_px < 1:
        raise ValueError("UI-Manifest enthält ungültige Interaktionsmaße")
    return {
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
    }


def build_a3_cinematic_forge(
    projection: Mapping[str, Any],
    state: PresentationState,
    ui_manifest: Mapping[str, Any],
    animation_manifest: Mapping[str, Any],
    text_catalog: Mapping[str, str],
    *,
    primary_actions: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Compose a cinematic A3 layout from exactly the shared Character Forge contracts."""
    variant = _a3_variant(ui_manifest)
    accessibility = _accessibility_projection(ui_manifest, state)
    focus_model = require_mapping(ui_manifest.get("focus_model"), "UI focus_model")
    max_primary_actions = int(focus_model.get("max_primary_actions_visible", 0))
    if max_primary_actions < 1:
        raise ValueError("UI-Manifest benötigt max_primary_actions_visible >= 1")

    meta = require_mapping(projection.get("meta"), "Projection meta")
    character_id = require_nonempty_text(meta.get("character_id"), "Projection character_id")
    capabilities = require_mapping(projection.get("capabilities", {}), "Projection capabilities")
    components = build_components(projection, state)

    actions = normalize_primary_actions(
        primary_actions,
        character_id=character_id,
        capabilities=capabilities,
        max_primary_actions=max_primary_actions,
        minimum_target_px=int(accessibility["minimum_target_px"]),
        focus_ring_px=int(accessibility["focus_ring_px"]),
    )
    drawer_components = _VIEW_DRAWER_COMPONENTS.get(state.selected_view)
    if drawer_components is None:
        raise ValueError(f"A3 kennt View {state.selected_view} nicht")

    skill_nodes = _radial_nodes(
        components["SkillList"]["data"],
        id_field="skill_id",
        value_fields=("value", "xp", "xp_to_next", "progress_percent", "trend"),
    )
    trait_nodes = _radial_nodes(
        components["TraitList"]["data"],
        id_field="trait_id",
        value_fields=("tier", "evidence", "next_tier", "progress_percent", "effect_key", "consequence_key"),
    )
    animation_cues = build_animation_cues(
        projection.get("feedback", ()),
        state,
        animation_manifest,
    )

    forge = {
        "view_model_version": "0.6.4",
        "layout": {
            "variant_id": "A3_CINEMATIC_FORGE",
            "layout_token": variant.get("layout"),
            "density": variant.get("density"),
            "best_for": variant.get("best_for"),
            "visual_family": ui_manifest.get("design_family"),
        },
        "character_id": character_id,
        "selected_view": state.selected_view,
        "components": components,
        "zones": {
            "character_stage": {
                "label_key": "ui.cinematic.character_stage",
                "aria_label_key": "ui.cinematic.character_stage",
                "component_refs": ["CharacterHeader", "StatusSummary"],
                "portrait_source": None,
                "presentation": {
                    "depth_layers": ["backdrop", "character", "status", "feedback"],
                    "camera_motion_allowed": not state.reduced_motion,
                    "input_blocked": False,
                },
            },
            "skill_web": {
                "label_key": "ui.cinematic.skill_web",
                "aria_label_key": "ui.cinematic.skill_web",
                "component_ref": "SkillList",
                "nodes": skill_nodes,
                "empty": not skill_nodes,
                "presentation": {"geometry": "radial", "center_component_ref": "CharacterHeader"},
            },
            "trait_orbit": {
                "label_key": "ui.cinematic.trait_orbit",
                "aria_label_key": "ui.cinematic.trait_orbit",
                "component_ref": "TraitList",
                "nodes": trait_nodes,
                "empty": not trait_nodes,
                "presentation": {"geometry": "orbit", "center_component_ref": "SpecializationCard"},
            },
            "specialization_focus": {
                "label_key": "ui.component.specialization_card",
                "aria_label_key": "ui.component.specialization_card",
                "component_ref": "SpecializationCard",
                "empty": components["SpecializationCard"]["empty"],
            },
            "context_drawer": {
                "label_key": "ui.cinematic.context_drawer",
                "aria_label_key": "ui.cinematic.context_drawer",
                "component_refs": list(drawer_components),
                "selected_view": state.selected_view,
            },
            "biography_rail": {
                "label_key": "ui.cinematic.biography_rail",
                "aria_label_key": "ui.cinematic.biography_rail",
                "component_ref": "BiographyTimeline",
                "empty": components["BiographyTimeline"]["empty"],
            },
            "progress_overlay": {
                "label_key": "ui.cinematic.progress_overlay",
                "aria_label_key": "ui.cinematic.progress_overlay",
                "component_ref": "ProgressFeedback",
                "animation_cues": animation_cues,
                "empty": components["ProgressFeedback"]["empty"],
                "presentation": {
                    "blocking": False,
                    "dismiss_command": "feedback.dismiss",
                    "motion_mode": "static" if state.reduced_motion else "animated",
                },
            },
            "action_dock": {
                "label_key": "ui.cinematic.action_dock",
                "aria_label_key": "ui.cinematic.action_dock",
                "primary_actions": actions,
                "empty": not actions,
            },
        },
        "keyboard_order": [action["action_id"] for action in actions],
        "accessibility": accessibility,
        "cinematic_contract": {
            "shared_component_names": list(components),
            "animation_never_blocks_gameplay": all(
                cue.get("max_blocking_ms") == 0 for cue in animation_cues
            ),
            "commands_use_shared_dispatcher": all(
                action["dispatch"]["route"] == "application.command_dispatcher.dispatch_command"
                for action in actions
            ),
            "portrait_data_invented": False,
        },
    }
    require_text_keys(forge, text_catalog, context="A3")
    return forge
