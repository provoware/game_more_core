from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any, Mapping

from bunkerfrequenz.application.action_biography import build_action_biography_event
from bunkerfrequenz.application.action_resolver import ActionResolver, ResolvedAction
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


@dataclass(frozen=True, slots=True)
class ActionCommitResult:
    resolved: ResolvedAction
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class CharacterActionService:
    def __init__(
        self,
        resolver: ActionResolver,
        persistence: PersistenceKernel,
        *,
        biography_policy: Mapping[str, Any] | None = None,
    ):
        self.resolver = resolver
        self.persistence = persistence
        self.biography_policy = deepcopy(dict(biography_policy)) if biography_policy is not None else None

    def execute(
        self,
        character: CharacterState,
        action: dict,
        *,
        action_instance_id: str,
        world_seed: str,
        journal_context: JournalContext,
        **resolver_kwargs,
    ) -> ActionCommitResult:
        self.persistence.initialize_state({"character": character.to_dict()})
        first_event_id = f"{action_instance_id}:001"
        if self.persistence.has_event(first_event_id):
            persisted = self.persistence.load_state()
            if persisted is None:
                raise RuntimeError("Journal enthält Aktion, aber abgeleiteter Zustand fehlt")
            replay_state = CharacterState.from_dict(persisted["character"])
            replay = ResolvedAction(
                action["action_id"],
                action_instance_id,
                "idempotent_replay",
                1.0,
                1.0,
                {},
                (),
                replay_state,
            )
            return ActionCommitResult(replay, (), True)

        resolved = self.resolver.resolve(
            character,
            action,
            action_instance_id=action_instance_id,
            world_seed=world_seed,
            **resolver_kwargs,
        )
        biography_event = build_action_biography_event(action, resolved, self.biography_policy)
        if biography_event is not None:
            resolved = replace(
                resolved,
                journal_events=resolved.journal_events + (biography_event,),
            )

        events = [
            {
                "event_id": f"{action_instance_id}:{index:03d}",
                "event_type": event["event_type"],
                "payload": event["payload"],
            }
            for index, event in enumerate(resolved.journal_events, 1)
        ]
        receipt = self.persistence.commit(
            transaction_id=f"tx:{action_instance_id}",
            events=events,
            derived_state={"character": resolved.character_after.to_dict()},
            context=journal_context,
        )
        return ActionCommitResult(resolved, receipt.event_ids, False)
