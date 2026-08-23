from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.application.assistant_control_service import AssistantControlService
from bunkerfrequenz.application.game_client_session import GameClientCommandResult, GameClientSession
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_ASSISTANT_FIELDS = frozenset({"type", "command_id", "job_id"})


class AssistantGameClientSession(GameClientSession):
    """Add only assistant start/switch/stop to the existing A4 session boundary.

    All non-assistant commands remain owned by ``GameClientSession``. Assistant
    control delegates directly to ``AssistantControlService`` and therefore
    cannot provide round authority, payout values or resource effects.
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

    def dispatch(
        self,
        command: Mapping[str, Any],
        *,
        context: JournalContext,
    ) -> GameClientCommandResult:
        if command.get("type") != "assistant.control":
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
