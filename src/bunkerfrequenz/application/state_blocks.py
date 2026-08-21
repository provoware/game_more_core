from __future__ import annotations

from copy import deepcopy
from typing import Any

from bunkerfrequenz.infrastructure.persistence import PersistenceKernel


def merge_state_block(
    persistence: PersistenceKernel,
    block_name: str,
    block_value: dict[str, Any],
    *,
    genesis_fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return current derived state with exactly one named block replaced."""
    current = persistence.load_state()
    if current is None:
        merged = deepcopy(genesis_fallback or {})
    else:
        merged = deepcopy(current)
    merged[block_name] = deepcopy(block_value)
    return merged
