from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError


_COMMANDS = {"profile.update", "profile.undo_last", "action.execute"}
_PROFILE_FIELDS = {"display_name", "alias", "additional_nicknames", "motto"}


@dataclass(frozen=True, slots=True)
class CommandResult:
    status: str
    projection: dict[str, Any] | None
    feedback: tuple[dict[str, Any], ...]
    error_code: str | None


def _rejected(code: str) -> CommandResult:
    return CommandResult("rejected", None, (), code)


def _required_id(command: Mapping[str, Any], name: str) -> bool:
    value = command.get(name)
    return isinstance(value, str) and bool(value.strip())


def _confirmed_projection(service: Any, fallback: CharacterState) -> dict[str, Any]:
    persisted = service.persistence.load_state()
    if persisted is not None:
        return CharacterState.from_dict(persisted["character"]).to_dict()
    return fallback.to_dict()


def dispatch_command(
    command: Mapping[str, Any],
    *,
    character: CharacterState,
    profile_service: CharacterProfileService,
    action_service: CharacterActionService,
    actions: Mapping[str, dict[str, Any]],
    world_seed: str,
    journal_context: JournalContext,
) -> CommandResult:
    """Validate and route one presentation command to its application service."""
    command_type = command.get("type")
    if not isinstance(command_type, str) or command_type not in _COMMANDS:
        return _rejected("unknown_command")
    if not _required_id(command, "character_id"):
        return _rejected("invalid_character_id")
    if command["character_id"] != character.character_id:
        return _rejected("character_mismatch")
    if not _required_id(command, "command_id"):
        return _rejected("invalid_command_id")

    context = replace(journal_context, command_id=command["command_id"])
    try:
        if command_type == "profile.update":
            changes = command.get("changes")
            if not isinstance(changes, dict) or set(changes) - _PROFILE_FIELDS:
                return _rejected("invalid_profile_fields")
            if not _required_id(command, "event_id"):
                return _rejected("invalid_event_id")
            if not _required_id(command, "transaction_id"):
                return _rejected("invalid_transaction_id")
            updated = profile_service.update(
                character,
                changes,
                event_id=command["event_id"],
                transaction_id=command["transaction_id"],
                context=context,
            )
            projection = _confirmed_projection(profile_service, updated)
            return CommandResult("confirmed", projection, (), None)

        if command_type == "profile.undo_last":
            if not _required_id(command, "event_id"):
                return _rejected("invalid_event_id")
            if not _required_id(command, "transaction_id"):
                return _rejected("invalid_transaction_id")
            updated = profile_service.undo_last_profile_update(
                event_id=command["event_id"],
                transaction_id=command["transaction_id"],
                context=context,
            )
            projection = _confirmed_projection(profile_service, updated)
            return CommandResult("confirmed", projection, (), None)

        if not _required_id(command, "action_instance_id"):
            return _rejected("invalid_action_instance_id")
        if not _required_id(command, "action_id") or command["action_id"] not in actions:
            return _rejected("invalid_action_id")
        committed = action_service.execute(
            character,
            actions[command["action_id"]],
            action_instance_id=command["action_instance_id"],
            world_seed=world_seed,
            journal_context=context,
        )
        projection = _confirmed_projection(action_service, committed.resolved.character_after)
        feedback = tuple(committed.resolved.journal_events)
        return CommandResult("confirmed", projection, feedback, None)
    except (ValueError, KeyError, PersistenceError, RuntimeError):
        return _rejected("service_error")
