from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any, Mapping

from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.command_dispatcher import CommandResult, dispatch_command
from bunkerfrequenz.application.presentation_events import get_confirmed_events
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class SessionCommandResult:
    command_result: CommandResult
    confirmed_events: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class AutosaveResult:
    status: str
    committed_event_ids: tuple[str, ...]
    snapshot_id: str | None


class CharacterForgeSessionService:
    """Small application orchestrator for the playable Character Forge loop.

    Gameplay writes stay in the existing dispatcher/services. The session only keeps
    the confirmed character, tracks whether a periodic recovery checkpoint is due,
    exposes confirmed event records, and reloads persisted state.
    """

    def __init__(
        self,
        character: CharacterState,
        *,
        profile_service: CharacterProfileService,
        action_service: CharacterActionService,
        actions: Mapping[str, dict[str, Any]],
        world_seed: str,
    ) -> None:
        if profile_service.persistence is not action_service.persistence:
            raise ValueError("Session benötigt dieselbe Persistenz für Profil und Actions")
        if not isinstance(world_seed, str) or not world_seed.strip():
            raise ValueError("world_seed fehlt")
        character.validate()
        self.persistence: PersistenceKernel = profile_service.persistence
        self.profile_service = profile_service
        self.action_service = action_service
        self.actions = deepcopy(dict(actions))
        self.world_seed = world_seed
        self._character = CharacterState.from_dict(character.to_dict())
        self._dirty_since_periodic_autosave = False

    @property
    def character(self) -> CharacterState:
        return CharacterState.from_dict(self._character.to_dict())

    @property
    def dirty_since_periodic_autosave(self) -> bool:
        return self._dirty_since_periodic_autosave

    def dispatch(
        self,
        command: Mapping[str, Any],
        *,
        journal_context: JournalContext,
        server_sequence: int | None = None,
        action_context: dict[str, Any] | None = None,
    ) -> SessionCommandResult:
        result = dispatch_command(
            command,
            character=self._character,
            profile_service=self.profile_service,
            action_service=self.action_service,
            actions=self.actions,
            world_seed=self.world_seed,
            journal_context=journal_context,
            server_sequence=server_sequence,
            action_context=action_context,
        )
        if result.status != "confirmed" or result.confirmed_state is None:
            return SessionCommandResult(result, ())

        self._character = CharacterState.from_dict(result.confirmed_state.to_dict())
        confirmed_events = get_confirmed_events(result.committed_event_ids, self.persistence)
        if result.committed_event_ids:
            self._dirty_since_periodic_autosave = True
        return SessionCommandResult(result, confirmed_events)

    def autosave_if_due(
        self,
        *,
        seconds_since_last_save: float,
        autosave_id: str,
        journal_context: JournalContext,
    ) -> AutosaveResult:
        if not self.persistence.autosave_due(
            dirty=self._dirty_since_periodic_autosave,
            seconds_since_last_save=seconds_since_last_save,
        ):
            return AutosaveResult("not_due", (), None)

        autosave_id = _required_text(autosave_id, "autosave_id")
        state = self.persistence.load_state()
        if state is None or "character" not in state:
            raise PersistenceError("Kein bestätigter Zustand für Autosave vorhanden")

        event_id = f"autosave:{autosave_id}"
        transaction_id = f"tx:autosave:{autosave_id}"
        context = replace(
            journal_context,
            command_id=event_id,
            source="autosave",
        )
        receipt = self.persistence.commit(
            transaction_id=transaction_id,
            events=[{
                "event_id": event_id,
                "event_type": "system.autosave_committed",
                "payload": {
                    "interval_seconds": 60,
                    "reason": "dirty_periodic_recovery_checkpoint",
                },
            }],
            derived_state=deepcopy(state),
            context=context,
        )
        snapshot_id = self.persistence.create_snapshot("autosave_60s")
        self._dirty_since_periodic_autosave = False
        return AutosaveResult("committed", receipt.event_ids, snapshot_id)

    def reload(self) -> CharacterState:
        state = self.persistence.load_state()
        if state is None or "character" not in state:
            raise PersistenceError("Kein bestätigter Character-Zustand zum Neuladen vorhanden")
        self._character = CharacterState.from_dict(state["character"])
        return self.character


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss ein nicht-leerer Text sein")
    return value
