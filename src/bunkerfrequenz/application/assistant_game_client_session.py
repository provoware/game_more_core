from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Any, Mapping

from bunkerfrequenz.application.assistant_control_service import AssistantControlService
from bunkerfrequenz.application.game_client_session import GameClientCommandResult, GameClientSession
from bunkerfrequenz.application.personal_finance_service import PersonalFinanceService
from bunkerfrequenz.application.recovery_action_service import RecoveryActionService
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_ASSISTANT_FIELDS = frozenset({"type", "command_id", "job_id"})
_FINANCE_TRANSFER_FIELDS = frozenset({"type", "command_id", "direction", "amount_cents"})
_RECOVERY_FIELDS = frozenset({"type", "command_id", "recovery_id"})


class AssistantGameClientSession(GameClientSession):
    """Extend the existing A4 session with assistant, finance and recovery controls.

    Non-special commands remain owned by ``GameClientSession``. Assistant control
    delegates to ``AssistantControlService``. Personal wallet/bank transfers delegate
    to ``PersonalFinanceService``. Recovery delegates to ``RecoveryActionService``.
    None of these surfaces accepts round authority, payouts, resource deltas or
    client-supplied target balances.
    """

    def __init__(
        self,
        persistence: PersistenceKernel,
        *,
        scene_job_manifest: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            persistence,
            scene_job_manifest=scene_job_manifest,
            **kwargs,
        )
        self.assistant_control = (
            AssistantControlService(persistence, scene_job_manifest)
            if scene_job_manifest is not None
            else None
        )
        self.personal_finance = PersonalFinanceService(persistence)
        self.recovery_actions = RecoveryActionService(persistence)

    def dispatch(
        self,
        command: Mapping[str, Any],
        *,
        context: JournalContext,
    ) -> GameClientCommandResult:
        command_type = command.get("type")
        if command_type == "finance.transfer":
            return self._dispatch_finance_transfer(command, context=context)
        if command_type == "recovery.run":
            return self._dispatch_recovery(command, context=context)
        if command_type != "assistant.control":
            return super().dispatch(command, context=context)

        unknown_fields = set(command) - _ASSISTANT_FIELDS
        if unknown_fields:
            return self._rejected(
                "unexpected_command_fields",
                ", ".join(sorted(str(field) for field in unknown_fields)),
            )
        if "job_id" not in command:
            return self._rejected("invalid_job_id")

        command_id = command.get("command_id")
        if not isinstance(command_id, str) or not command_id.strip():
            return self._rejected("invalid_command_id")
        command_id = command_id.strip()
        if context.command_id != command_id:
            return self._rejected("command_context_mismatch")
        if context.entity_type != "character" or not context.entity_id:
            return self._rejected("invalid_character_context")
        if self.assistant_control is None:
            return self._rejected("assistant_not_configured")

        job_id = command.get("job_id")
        if job_id is not None and (not isinstance(job_id, str) or not job_id.strip()):
            return self._rejected("invalid_job_id")
        normalized_job_id = job_id.strip() if isinstance(job_id, str) else None

        try:
            result = self.assistant_control.set_active_job(normalized_job_id, context=context)
            committed = (f"{command_id}:assistant-control",) if result.changed else ()
            return GameClientCommandResult(
                "confirmed",
                self.read_state(),
                committed,
                result.idempotent_replay,
                None,
                None,
                {
                    "assistant_control": {
                        **deepcopy(result.assistant.to_dict()),
                        "changed": result.changed,
                    }
                },
            )
        except PersistenceError as exc:
            return self._rejected("persistence_error", str(exc))
        except (ValueError, KeyError, TypeError) as exc:
            return self._rejected("validation_error", str(exc))
        except RuntimeError as exc:
            return self._rejected("runtime_error", str(exc))

    def _dispatch_recovery(
        self,
        command: Mapping[str, Any],
        *,
        context: JournalContext,
    ) -> GameClientCommandResult:
        unknown_fields = set(command) - _RECOVERY_FIELDS
        if unknown_fields:
            return self._rejected(
                "unexpected_command_fields",
                ", ".join(sorted(str(field) for field in unknown_fields)),
            )
        command_id = command.get("command_id")
        if not isinstance(command_id, str) or not command_id.strip():
            return self._rejected("invalid_command_id")
        command_id = command_id.strip()
        if context.command_id != command_id:
            return self._rejected("command_context_mismatch")

        state = self.read_state()
        raw_character = state.get("character")
        if not isinstance(raw_character, dict):
            return self._rejected("character_missing")
        character_id = raw_character.get("character_id")
        if not isinstance(character_id, str) or not character_id:
            return self._rejected("character_missing")
        if context.character_id and context.character_id != character_id:
            return self._rejected("character_context_mismatch")
        recovery_context = replace(
            context,
            entity_type="character",
            entity_id=character_id,
            character_id=character_id,
        )

        recovery_id = command.get("recovery_id")
        if not isinstance(recovery_id, str) or not recovery_id.strip():
            return self._rejected("invalid_recovery_id")

        try:
            result = self.recovery_actions.run(recovery_id.strip(), context=recovery_context)
            return GameClientCommandResult(
                "confirmed",
                self.read_state(),
                result.committed_event_ids,
                result.idempotent_replay,
                None,
                None,
                {
                    "recovery_action": {
                        "recovery_id": result.action["recovery_id"],
                        "label": result.action["label"],
                        "resource_changes": deepcopy(result.resource_changes),
                    }
                },
            )
        except PersistenceError as exc:
            return self._rejected("persistence_error", str(exc))
        except (ValueError, KeyError, TypeError) as exc:
            return self._rejected("validation_error", str(exc))
        except RuntimeError as exc:
            return self._rejected("runtime_error", str(exc))

    def _dispatch_finance_transfer(
        self,
        command: Mapping[str, Any],
        *,
        context: JournalContext,
    ) -> GameClientCommandResult:
        unknown_fields = set(command) - _FINANCE_TRANSFER_FIELDS
        if unknown_fields:
            return self._rejected(
                "unexpected_command_fields",
                ", ".join(sorted(str(field) for field in unknown_fields)),
            )
        command_id = command.get("command_id")
        if not isinstance(command_id, str) or not command_id.strip():
            return self._rejected("invalid_command_id")
        command_id = command_id.strip()
        if context.command_id != command_id:
            return self._rejected("command_context_mismatch")

        state = self.read_state()
        raw_character = state.get("character")
        if not isinstance(raw_character, dict):
            return self._rejected("character_missing")
        character_id = raw_character.get("character_id")
        if not isinstance(character_id, str) or not character_id:
            return self._rejected("character_missing")
        if context.character_id and context.character_id != character_id:
            return self._rejected("character_context_mismatch")
        finance_context = replace(
            context,
            entity_type="character",
            entity_id=character_id,
            character_id=character_id,
        )

        direction = command.get("direction")
        amount_cents = command.get("amount_cents")
        if not isinstance(direction, str) or direction not in PersonalFinanceService.DIRECTIONS:
            return self._rejected("invalid_finance_direction")
        if isinstance(amount_cents, bool) or not isinstance(amount_cents, int) or amount_cents <= 0:
            return self._rejected("invalid_finance_amount")

        try:
            result = self.personal_finance.transfer(direction, amount_cents, context=finance_context)
            return GameClientCommandResult(
                "confirmed",
                self.read_state(),
                result.committed_event_ids,
                result.idempotent_replay,
                None,
                None,
                {
                    "personal_finance_transfer": {
                        "direction": result.direction,
                        "amount_cents": result.amount_cents,
                        "finance": result.finance.to_dict(),
                    }
                },
            )
        except PersistenceError as exc:
            return self._rejected("persistence_error", str(exc))
        except (ValueError, KeyError, TypeError) as exc:
            return self._rejected("validation_error", str(exc))
        except RuntimeError as exc:
            return self._rejected("runtime_error", str(exc))
