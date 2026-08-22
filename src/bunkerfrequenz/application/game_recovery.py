from __future__ import annotations

from bunkerfrequenz.application.economy_service import replay_economy_event
from bunkerfrequenz.application.event_state_service import replay_event_state_event
from bunkerfrequenz.application.recovery_service import replay_character_event
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel, RecoveryReceipt


def replay_game_event(derived_state: dict, record: dict) -> dict:
    state = replay_character_event(derived_state, record)
    state = replay_event_state_event(state, record)
    return replay_economy_event(state, record)


class GameRecoveryService:
    def __init__(self, persistence: PersistenceKernel):
        self.persistence = persistence

    def recover(self, *, context: JournalContext | None = None) -> RecoveryReceipt:
        return self.persistence.recover(replay_game_event, context=context)
