from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.presentation.state import PresentationState, visible_feedback


_FEEDBACK_ANIMATIONS = {
    "level_up": "anim.level_up",
    "skill_level_up": "anim.skill_up",
    "trait_unlocked": "anim.trait_unlock",
    "trait_tier_up": "anim.trait_unlock",
    "specialization_changed": "anim.specialization",
    "resonance_rank_up": "anim.resonance_up",
}


def _animation_index(animation_manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    animations = animation_manifest.get("animations", ())
    if not isinstance(animations, Sequence) or isinstance(animations, (str, bytes)):
        raise ValueError("Animation-Manifest enthält keine gültige animations-Liste")
    result: dict[str, Mapping[str, Any]] = {}
    for entry in animations:
        if not isinstance(entry, Mapping):
            raise ValueError("Animation-Manifest enthält einen ungültigen Eintrag")
        animation_id = entry.get("id")
        if not isinstance(animation_id, str) or not animation_id.strip():
            raise ValueError("Animation benötigt eine nicht-leere id")
        if animation_id in result:
            raise ValueError(f"Doppelte Animation-ID: {animation_id}")
        result[animation_id] = entry
    return result


def build_animation_cues(
    feedback: Sequence[Mapping[str, Any]],
    state: PresentationState,
    animation_manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Translate visible confirmed feedback into non-blocking renderer instructions."""
    index = _animation_index(animation_manifest)
    failure_policy = animation_manifest.get("failure_policy")
    if failure_policy != "missing_animation_never_blocks_or_changes_game_state":
        raise ValueError("Unbekannte Animation-Failure-Policy")

    cues: list[dict[str, Any]] = []
    for entry in visible_feedback(feedback, state):
        feedback_id = entry.get("feedback_id")
        kind = entry.get("kind")
        if not isinstance(feedback_id, str) or not feedback_id.strip():
            continue
        animation_id = _FEEDBACK_ANIMATIONS.get(kind)
        animation = index.get(animation_id) if animation_id else None

        if animation is None:
            cues.append(
                {
                    "cue_id": f"cue:{feedback_id}",
                    "source_feedback_id": feedback_id,
                    "kind": kind,
                    "mode": "static",
                    "animation_id": None,
                    "duration_ms": 0,
                    "max_blocking_ms": 0,
                    "skippable": True,
                    "fallback": "static_feedback_card",
                    "motif": None,
                    "reason": "missing_animation",
                }
            )
            continue

        max_blocking_ms = animation.get("max_blocking_ms")
        if max_blocking_ms != 0:
            raise ValueError(f"Animation {animation_id} darf Gameplay nicht blockieren")
        duration_ms = animation.get("duration_ms")
        if isinstance(duration_ms, bool) or not isinstance(duration_ms, int) or duration_ms < 0:
            raise ValueError(f"Animation {animation_id} hat ungültige Dauer")
        skippable = animation.get("skippable")
        if skippable is not True:
            raise ValueError(f"Animation {animation_id} muss überspringbar sein")
        fallback = animation.get("fallback")
        if not isinstance(fallback, str) or not fallback.strip():
            raise ValueError(f"Animation {animation_id} benötigt statischen Fallback")

        reduced_motion = state.reduced_motion
        cues.append(
            {
                "cue_id": f"cue:{feedback_id}",
                "source_feedback_id": feedback_id,
                "kind": kind,
                "mode": "static" if reduced_motion else "animated",
                "animation_id": animation_id,
                "duration_ms": 0 if reduced_motion else duration_ms,
                "max_blocking_ms": 0,
                "skippable": True,
                "fallback": fallback,
                "motif": animation.get("motif"),
                "reason": "reduced_motion" if reduced_motion else None,
            }
        )
    return deepcopy(cues)
