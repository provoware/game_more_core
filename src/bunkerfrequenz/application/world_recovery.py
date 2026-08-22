from __future__ import annotations

from copy import deepcopy
from typing import Any

from bunkerfrequenz.domain.world import WorldState


def replay_world_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Replay only the world block.

    Character effects that happen in the same transaction are deliberately
    reconstructed by the canonical character replay events, never by a
    world event payload. This keeps replay order deterministic.
    """
    if not str(record.get("event_type", "")).startswith("world."):
        return derived_state
    payload = record.get("payload", {})
    raw_world = payload.get("world")
    if not isinstance(raw_world, dict):
        return derived_state
    target = WorldState.from_dict(raw_world)
    state = deepcopy(derived_state)
    current_raw = state.get("world")
    if isinstance(current_raw, dict):
        current = WorldState.from_dict(current_raw)
        if current.revision > target.revision:
            return state
        if current.revision == target.revision:
            if current.to_dict() != target.to_dict():
                raise ValueError("World-Replay kollidiert mit Zustand derselben Revision")
            return state
    state["world"] = target.to_dict()
    return state
