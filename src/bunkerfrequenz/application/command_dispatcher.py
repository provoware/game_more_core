from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_COMMANDS = {"profile.update", "profile.undo_last", "action.execute"}
_PROFILE_FIELDS = {"display_name", "alias", "additional_nicknames", "motto"}
_SELECTION_FIELDS = {"selected_skill", "selected_trait_family"}


@dataclass(frozen=True, slots=True)
class CommandResult:
    status: str
    confirmed_state: CharacterState | None
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool
    error_code: str | None


def _rejected(code: str) -> CommandResult:
    return CommandResult("rejected", None, (), False, code)


def _required_id(command: Mapping[str, Any], name: str) -> bool:
    value = command.get(name)
    return isinstance(value, str) and bool(value.strip())


def _confirmed_character(persistence: PersistenceKernel, fallback: CharacterState) -> CharacterState:
    persisted = persistence.load_state()
    if persisted is None or "character" not in persisted:
        return CharacterState.from_dict(fallback.to_dict())
    return CharacterState.from_dict(persisted["character"])


def _existing_record(persistence: PersistenceKernel, event_id: str) -> dict[str, Any] | None:
    for record in persistence.read_records():
        if record.get("event_id") == event_id:
            return record
    return None


def dispatch_command(
    command: Mapping[str, Any],
    *,
    character: CharacterState,
    profile_service: CharacterProfileService,
    action_service: CharacterActionService,
    actions: Mapping[str, dict[str, Any]],
    world_seed: str,
    journal_context: JournalContext,
    server_sequence: int | None = None,
    action_context: dict[str, Any] | None = None,
) -> CommandResult:
    """Validate one UI write command and route it through the existing application services."""
    if profile_service.persistence is not action_service.persistence:
        return _rejected("service_persistence_mismatch")

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
    persistence = profile_service.persistence

    try:
        if command_type == "profile.update":
            changes = command.get("changes")
            if not isinstance(changes, dict) or not changes or set(changes) - _PROFILE_FIELDS:
                return _rejected("invalid_profile_fields")
            if not _required_id(command, "event_id"):
                return _rejected("invalid_event_id")
            if not _required_id(command, "transaction_id"):
                return _rejected("invalid_transaction_id")

            replay = persistence.has_event(command["event_id"])
            updated = profile_service.update(
                character,
                changes,
                event_id=command["event_id"],
                transaction_id=command["transaction_id"],
                context=context,
            )
            confirmed = _confirmed_character(persistence, updated)
            return CommandResult(
                "confirmed",
                confirmed,
                () if replay else (command["event_id"],),
                replay,
                None,
            )

        if command_type == "profile.undo_last":
            if not _required_id(command, "event_id"):
                return _rejected("invalid_event_id")
            if not _required_id(command, "transaction_id"):
                return _rejected("invalid_transaction_id")

            existing = _existing_record(persistence, command["event_id"])
            if existing is not None:
                if (
                    existing.get("command_id") == command["command_id"]
                    and existing.get("transaction_id") == command["transaction_id"]
                    and existing.get("compensation_for")
                ):
                    confirmed = _confirmed_character(persistence, character)
                    return CommandResult("confirmed", confirmed, (), True, None)
                return _rejected("duplicate_event_conflict")

            updated = profile_service.undo_last_profile_update(
                event_id=command["event_id"],
                transaction_id=command["transaction_id"],
                context=context,
            )
            confirmed = _confirmed_character(persistence, updated)
            return CommandResult("confirmed", confirmed, (command["event_id"],), False, None)

        if not _required_id(command, "action_id") or command["action_id"] not in actions:
            return _rejected("invalid_action_id")
        if not _required_id(command, "action_instance_id"):
            return _rejected("invalid_action_instance_id")

        resolver_kwargs: dict[str, Any] = {
            "server_sequence": server_sequence,
            "context": action_context or {},
        }
        for field in _SELECTION_FIELDS:
            if field in command:
                value = command[field]
                if not isinstance(value, str) or not value.strip():
                    return _rejected(f"invalid_{field}")
                resolver_kwargs[field] = value

        committed = action_service.execute(
            character,
            actions[command["action_id"]],
            action_instance_id=command["action_instance_id"],
            world_seed=world_seed,
            journal_context=context,
            **resolver_kwargs,
        )
        confirmed = _confirmed_character(persistence, committed.resolved.character_after)
        return CommandResult(
            "confirmed",
            confirmed,
            committed.committed_event_ids,
            committed.idempotent_replay,
            None,
        )
    except PersistenceError:
        return _rejected("persistence_error")
    except (ValueError, KeyError, TypeError):
        return _rejected("validation_error")
    except RuntimeError:
        return _rejected("runtime_error")
