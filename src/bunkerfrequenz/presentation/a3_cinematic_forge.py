from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.presentation.a4_ops_deck import build_a4_ops_deck
from bunkerfrequenz.presentation.state import PresentationState


_FEEDBACK_ANIMATIONS = {
    "level_up": "anim.level_up",
    "skill_level_up": "anim.skill_up",
    "trait_unlocked": "anim.trait_unlock",
    "trait_tier_up": "anim.trait_tier_up",
    "specialization_changed": "anim.specialization",
    "resonance_rank_up": "anim.resonance_up",
}


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} muss ein Mapping sein")
    return value


def _variant(ui_manifest: Mapping[str, Any], variant_id: str) -> Mapping[str, Any]:
    variants = ui_manifest.get("variants", ())
    if not isinstance(variants, Sequence) or isinstance(variants, (str, bytes)):
        raise ValueError("UI-Manifest enthält keine gültigen Varianten")
    for variant in variants:
        if isinstance(variant, Mapping) and variant.get("id") == variant_id:
            return variant
    raise ValueError(f"UI-Manifest enthält {variant_id} nicht")


def _animation_index(animation_manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    animations = animation_manifest.get("animations", ())
    if not isinstance(animations, Sequence) or isinstance(animations, (str, bytes)):
        raise ValueError("Animationsmanifest enthält keine gültige Animationsliste")
    index: dict[str, dict[str, Any]] = {}
    for item in animations:
        if not isinstance(item, Mapping):
            continue
        animation_id = item.get("id")
        if isinstance(animation_id, str) and animation_id:
            index[animation_id] = deepcopy(dict(item))
    return index


def _cinematic_feedback(
    feedback: Sequence[Mapping[str, Any]],
    *,
    animation_manifest: Mapping[str, Any],
    reduced_motion: bool,
) -> list[dict[str, Any]]:
    animations = _animation_index(animation_manifest)
    cues: list[dict[str, Any]] = []
    for item in feedback:
        feedback_id = item.get("feedback_id")
        kind = item.get("kind")
        if not isinstance(feedback_id, str) or not isinstance(kind, str):
            continue
        animation_id = _FEEDBACK_ANIMATIONS.get(kind)
        spec = animations.get(animation_id) if animation_id else None
        fallback = "static_feedback_card"
        if spec is not None and isinstance(spec.get("fallback"), str):
            fallback = spec["fallback"]
        animated = spec is not None and not reduced_motion
        cues.append(
            {
                "feedback_id": feedback_id,
                "kind": kind,
                "mode": "animated" if animated else "static",
                "animation_id": animation_id if animated else None,
                "fallback": fallback,
                "duration_ms": int(spec.get("duration_ms", 0)) if animated else 0,
                "max_blocking_ms": 0,
                "skippable": True,
                "input_blocked": False,
                "title_key": item.get("title_key"),
                "subject_label_key": item.get("subject_label_key"),
                "detail_keys": deepcopy(item.get("detail_keys", [])),
            }
        )
    return cues


def build_a3_cinematic_forge(
    projection: Mapping[str, Any],
    state: PresentationState,
    ui_manifest: Mapping[str, Any],
    animation_manifest: Mapping[str, Any],
    text_catalog: Mapping[str, str],
    *,
    workflow: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose A3 from the already validated A4 interaction/component contract."""
    a4 = build_a4_ops_deck(
        projection,
        state,
        ui_manifest,
        text_catalog,
        workflow=workflow,
    )
    a3_variant = _variant(ui_manifest, "A3_CINEMATIC_FORGE")
    animations = _require_mapping(animation_manifest, "Animationsmanifest")

    components = deepcopy(a4["components"])
    primary_actions = deepcopy(a4["zones"]["workspace"]["primary_actions"])
    selected_refs = deepcopy(a4["zones"]["workspace"]["selected_view_component_refs"])
    visible_feedback = components["ProgressFeedback"]["data"]
    cinematic_feedback = _cinematic_feedback(
        visible_feedback,
        animation_manifest=animations,
        reduced_motion=state.reduced_motion,
    )

    return {
        "view_model_version": "0.6.4",
        "layout": {
            "variant_id": "A3_CINEMATIC_FORGE",
            "layout_token": a3_variant.get("layout"),
            "density": a3_variant.get("density"),
            "best_for": a3_variant.get("best_for"),
        },
        "character_id": a4["character_id"],
        "selected_view": state.selected_view,
        "components": components,
        "zones": {
            "hero_stage": {
                "label_key": "ui.cinematic.hero_stage",
                "component_refs": ["CharacterHeader", "SpecializationCard"],
            },
            "vital_ribbon": {
                "label_key": "ui.cinematic.vital_ribbon",
                "component_refs": ["StatusSummary"],
            },
            "growth_web": {
                "label_key": "ui.cinematic.growth_web",
                "component_refs": ["SkillList", "TraitList"],
                "presentation": "radial_skill_trait_web",
            },
            "context_drawer": {
                "label_key": "ui.cinematic.context_drawer",
                "component_refs": selected_refs,
            },
            "profile_drawer": {
                "label_key": "ui.cinematic.profile_drawer",
                "component_refs": ["ProfileEditor"],
            },
            "story_drawer": {
                "label_key": "ui.cinematic.story_drawer",
                "component_refs": ["BiographyTimeline"],
            },
            "action_dock": {
                "label_key": "ui.cinematic.action_dock",
                "primary_actions": primary_actions,
            },
            "development_overlay": {
                "label_key": "ui.cinematic.development_overlay",
                "component_refs": ["ProgressFeedback"],
                "cues": cinematic_feedback,
                "dismiss_command": "feedback.dismiss",
            },
        },
        "keyboard_order": deepcopy(a4["keyboard_order"]),
        "accessibility": {
            **deepcopy(a4["accessibility"]),
            "animation_never_blocks_input": True,
            "development_overlay_skippable": True,
        },
        "interaction_contract": {
            "source": "A4_OPS_DECK",
            "shared_component_names": list(components),
            "command_routes": sorted(
                {
                    action["dispatch"]["route"]
                    for action in primary_actions
                    if isinstance(action, Mapping) and isinstance(action.get("dispatch"), Mapping)
                }
            ),
            "command_types": [
                action["dispatch"]["command"]["type"]
                for action in primary_actions
            ],
        },
    }
