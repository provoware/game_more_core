from __future__ import annotations

from copy import deepcopy
from typing import Iterable

from bunkerfrequenz.infrastructure.persistence import PersistenceError, PersistenceKernel


def get_confirmed_events(
    event_ids: Iterable[str],
    persistence: PersistenceKernel,
) -> tuple[dict, ...]:
    """Return detached persisted records for exactly the confirmed event IDs in requested order."""
    requested = tuple(event_ids)
    if any(not isinstance(event_id, str) or not event_id.strip() for event_id in requested):
        raise ValueError("Bestätigte Event-IDs müssen nicht-leere Texte sein")
    if len(set(requested)) != len(requested):
        raise ValueError("Bestätigte Event-IDs dürfen nicht doppelt vorkommen")
    if not requested:
        return ()

    records = {record["event_id"]: record for record in persistence.read_records()}
    missing = [event_id for event_id in requested if event_id not in records]
    if missing:
        raise PersistenceError(f"Bestätigte Journal-Ereignisse fehlen: {', '.join(missing)}")
    return tuple(deepcopy(records[event_id]) for event_id in requested)
