from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


DISPATCH_ROUTE = "application.command_dispatcher.dispatch_command"
PROFILE_CHANGE_FIELDS = frozenset({"display_name", "alias", "additional_nicknames", "motto"})
COMMAND_REQUIREMENTS = {
    "profile.update": ("character_id", "command_id", "event_id", "transaction_id", "changes"),
    "profile.undo_last": ("character_id", "command_id", "event_id", "transaction_id"),
    "action.execute": ("character_id", "command_id", "action_id", "action_instance_id"),
}
COMMAND_ALLOWED_FIELDS = {
    "profile.update": frozenset(
        {"type", "character_id", "command_id", "event_id", "transaction_id", "changes"}
    ),
    "profile.undo_last": frozenset(
        {"type", "character_id", "command_id", "event_id", "transaction_id"}
    ),
    "action.execute": frozenset(
        {
            "type",
            "character_id",
            "command_id",
            "action_id",
            "action_instance_id",
            "selected_skill",
            "selected_trait_family",
        }
    ),
}
COMMAND_CAPABILITIES = {
    "profile.update": "can_edit_profile",
    "profile.undo_last": "can_undo_profile",
    "action.execute": "can_execute_action",
}


def require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} muss ein Mapping sein")
    return value


def require_nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss ein nicht-leerer Text sein")
    return value


def validate_dispatcher_command(
    command_map: Mapping[str, Any],
    action_id: str,
    character_id: str,
) -> str:
    command_type = command_map.get("type")
    if command_type not in COMMAND_REQUIREMENTS:
        raise ValueError(f"Primäraktion {action_id} hat unbekannten Schreibcommand")

    unknown = set(command_map) - COMMAND_ALLOWED_FIELDS[command_type]
    if unknown:
        raise ValueError(
            f"Primäraktion {action_id} enthält nicht freigegebene Command-Felder: "
            f"{', '.join(sorted(unknown))}"
        )
    missing = [field for field in COMMAND_REQUIREMENTS[command_type] if field not in command_map]
    if missing:
        raise ValueError(
            f"Primäraktion {action_id} ist nicht dispatcher-fertig: {', '.join(missing)} fehlt"
        )

    if command_map.get("character_id") != character_id:
        raise ValueError(f"Primäraktion {action_id} gehört zu einem anderen Character")
    for field in COMMAND_REQUIREMENTS[command_type]:
        if field == "changes":
            continue
        require_nonempty_text(command_map.get(field), f"Primäraktion {action_id}.command.{field}")

    if command_type == "profile.update":
        changes = command_map.get("changes")
        if not isinstance(changes, Mapping) or not changes:
            raise ValueError(f"Primäraktion {action_id}.changes muss ein nicht-leeres Mapping sein")
        unknown_changes = set(changes) - PROFILE_CHANGE_FIELDS
        if unknown_changes:
            raise ValueError(
                f"Primäraktion {action_id} enthält nicht editierbare Profilfelder: "
                f"{', '.join(sorted(unknown_changes))}"
            )
    elif command_type == "action.execute":
        for field in ("selected_skill", "selected_trait_family"):
            if field in command_map:
                require_nonempty_text(
                    command_map[field],
                    f"Primäraktion {action_id}.command.{field}",
                )
    return command_type


def normalize_primary_action(
    value: Any,
    *,
    order: int,
    character_id: str,
    capabilities: Mapping[str, Any],
    minimum_target_px: int,
    focus_ring_px: int,
) -> dict[str, Any]:
    action = require_mapping(value, f"primary_actions[{order - 1}]")
    allowed_action_fields = {"action_id", "label_key", "icon_id", "tone", "enabled", "command"}
    unknown_action_fields = set(action) - allowed_action_fields
    if unknown_action_fields:
        raise ValueError(
            "Primäraktion enthält unbekannte Felder: "
            + ", ".join(sorted(unknown_action_fields))
        )

    action_id = require_nonempty_text(action.get("action_id"), "Primäraktion.action_id")
    label_key = require_nonempty_text(action.get("label_key"), f"Primäraktion {action_id}.label_key")
    icon_id = require_nonempty_text(action.get("icon_id"), f"Primäraktion {action_id}.icon_id")
    tone = require_nonempty_text(action.get("tone", "primary"), f"Primäraktion {action_id}.tone")
    enabled = action.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError(f"Primäraktion {action_id}.enabled muss bool sein")

    command_map = require_mapping(action.get("command"), f"Primäraktion {action_id}.command")
    command_type = validate_dispatcher_command(command_map, action_id, character_id)

    capability = COMMAND_CAPABILITIES[command_type]
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
            "route": DISPATCH_ROUTE,
            "command": deepcopy(dict(command_map)),
        },
    }


def normalize_primary_actions(
    raw_actions: Any,
    *,
    character_id: str,
    capabilities: Mapping[str, Any],
    max_primary_actions: int,
    minimum_target_px: int,
    focus_ring_px: int,
) -> list[dict[str, Any]]:
    if not isinstance(raw_actions, Sequence) or isinstance(raw_actions, (str, bytes)):
        raise ValueError("primary_actions muss eine Sequenz sein")
    if len(raw_actions) > max_primary_actions:
        raise ValueError(
            f"Presentation erlaubt maximal {max_primary_actions} Primäraktionen, "
            f"erhalten: {len(raw_actions)}"
        )

    normalized = [
        normalize_primary_action(
            action,
            order=index,
            character_id=character_id,
            capabilities=capabilities,
            minimum_target_px=minimum_target_px,
            focus_ring_px=focus_ring_px,
        )
        for index, action in enumerate(raw_actions, start=1)
    ]
    action_ids = [action["action_id"] for action in normalized]
    if len(set(action_ids)) != len(action_ids):
        raise ValueError("Primäraktions-IDs dürfen nicht doppelt vorkommen")
    return normalized
