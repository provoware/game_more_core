from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.presentation.state import PresentationState, visible_feedback


COMPONENT_NAMES = (
    "CharacterHeader",
    "StatusSummary",
    "SkillList",
    "TraitList",
    "SpecializationCard",
    "BiographyTimeline",
    "ProfileEditor",
    "ProgressFeedback",
)

_PROFILE_FIELDS = (
    ("display_name", "ui.profile.display_name", "text"),
    ("alias", "ui.profile.alias", "text"),
    ("additional_nicknames", "ui.profile.additional_nicknames", "text_list"),
    ("motto", "ui.profile.motto", "text"),
)


def _component(
    name: str,
    label_key: str,
    data: Any,
    *,
    empty: bool = False,
    actions: Sequence[Mapping[str, Any]] = (),
    presentation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if name not in COMPONENT_NAMES:
        raise ValueError(f"Unbekannte Character-Forge-Komponente: {name}")
    return {
        "component": name,
        "label_key": label_key,
        "aria_label_key": label_key,
        "data": deepcopy(data),
        "empty": bool(empty),
        "actions": deepcopy(list(actions)),
        "presentation": deepcopy(dict(presentation or {})),
    }


def build_character_header(overview: Mapping[str, Any]) -> dict[str, Any]:
    data = {
        "display_name": overview.get("display_name"),
        "alias": overview.get("alias"),
        "additional_nicknames": deepcopy(list(overview.get("additional_nicknames") or ())),
        "motto": overview.get("motto"),
        "level": overview.get("level"),
        "resonance_rank": overview.get("resonance_rank"),
    }
    return _component("CharacterHeader", "ui.component.character_header", data)


def build_status_summary(overview: Mapping[str, Any]) -> dict[str, Any]:
    data = {
        "energy": overview.get("energy"),
        "stress": overview.get("stress"),
        "reputation": overview.get("reputation"),
        "total_xp": overview.get("total_xp"),
        "resonance_xp": overview.get("resonance_xp"),
        "resonance_rank": overview.get("resonance_rank"),
    }
    return _component("StatusSummary", "ui.component.status_summary", data)


def build_skill_list(skills: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    items = deepcopy([dict(item) for item in skills])
    return _component("SkillList", "ui.component.skill_list", items, empty=not items)


def build_trait_list(traits: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    items = deepcopy([dict(item) for item in traits])
    return _component("TraitList", "ui.component.trait_list", items, empty=not items)


def build_specialization_card(specialization: Mapping[str, Any] | None) -> dict[str, Any]:
    data = deepcopy(dict(specialization)) if specialization is not None else None
    return _component(
        "SpecializationCard",
        "ui.component.specialization_card",
        data,
        empty=data is None,
    )


def build_biography_timeline(
    biography: Sequence[Mapping[str, Any]],
    state: PresentationState,
) -> dict[str, Any]:
    items = [deepcopy(dict(item)) for item in biography]
    if state.biography_filter != "all":
        items = [item for item in items if item.get("category") == state.biography_filter]
    return _component(
        "BiographyTimeline",
        "ui.component.biography_timeline",
        items,
        empty=not items,
        presentation={"active_filter": state.biography_filter},
    )


def build_profile_editor(
    overview: Mapping[str, Any],
    capabilities: Mapping[str, Any],
) -> dict[str, Any]:
    can_edit = bool(capabilities.get("can_edit_profile", False))
    can_undo = bool(capabilities.get("can_undo_profile", False))
    fields = [
        {
            "field": field,
            "label_key": label_key,
            "control": control,
            "value": deepcopy(overview.get(field)),
            "editable": can_edit,
        }
        for field, label_key, control in _PROFILE_FIELDS
    ]
    actions = [
        {
            "action_id": "profile.save",
            "label_key": "ui.profile.save",
            "aria_label_key": "ui.profile.save",
            "icon_id": "save",
            "tone": "primary",
            "enabled": can_edit,
            "command_route": "application.command_dispatcher.dispatch_command",
            "command_type": "profile.update",
            "required_command_fields": [
                "character_id",
                "command_id",
                "event_id",
                "transaction_id",
                "changes",
            ],
            "allowed_change_fields": [field for field, _, _ in _PROFILE_FIELDS],
        },
        {
            "action_id": "profile.undo",
            "label_key": "ui.undo",
            "aria_label_key": "ui.undo",
            "icon_id": "undo",
            "tone": "attention",
            "enabled": can_undo,
            "command_route": "application.command_dispatcher.dispatch_command",
            "command_type": "profile.undo_last",
            "required_command_fields": [
                "character_id",
                "command_id",
                "event_id",
                "transaction_id",
            ],
        },
    ]
    return _component(
        "ProfileEditor",
        "ui.component.profile_editor",
        {"fields": fields},
        actions=actions,
        presentation={"editable": can_edit},
    )


def build_progress_feedback(
    feedback: Sequence[Mapping[str, Any]],
    state: PresentationState,
) -> dict[str, Any]:
    items = visible_feedback(feedback, state)
    return _component(
        "ProgressFeedback",
        "ui.component.progress_feedback",
        items,
        empty=not items,
        presentation={
            "motion_mode": "static" if state.reduced_motion else "animated",
            "dismiss_command": "feedback.dismiss",
        },
    )


def build_components(
    projection: Mapping[str, Any],
    state: PresentationState,
) -> dict[str, dict[str, Any]]:
    """Build the eight shared components from projection blocks plus local presentation state."""
    components = {
        "CharacterHeader": build_character_header(projection.get("overview", {})),
        "StatusSummary": build_status_summary(projection.get("overview", {})),
        "SkillList": build_skill_list(projection.get("skills", ())),
        "TraitList": build_trait_list(projection.get("traits", ())),
        "SpecializationCard": build_specialization_card(projection.get("specialization")),
        "BiographyTimeline": build_biography_timeline(projection.get("biography", ()), state),
        "ProfileEditor": build_profile_editor(
            projection.get("overview", {}),
            projection.get("capabilities", {}),
        ),
        "ProgressFeedback": build_progress_feedback(projection.get("feedback", ()), state),
    }
    if tuple(components) != COMPONENT_NAMES:
        raise RuntimeError("Character-Forge-Komponentenreihenfolge verletzt")
    return components
