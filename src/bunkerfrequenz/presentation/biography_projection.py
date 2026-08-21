from __future__ import annotations

from copy import deepcopy
from typing import Iterable


_BIOGRAPHY_EVENT_TYPES = frozenset({"character.biography_entry_added"})
_PAYLOAD_FIELDS = ("entry_id", "category", "title_key", "body_key", "placeholders")


def build_biography_projection(character_id: str, journal_records: Iterable[dict]) -> list[dict]:
    """Return display-ready biography entries without changing journal records."""
    entries = []
    for record in journal_records:
        if not _is_valid_record(record, character_id):
            continue
        payload = record["payload"]
        entries.append(
            {
                "entry_id": payload["entry_id"],
                "event_id": record["event_id"],
                "category": payload["category"],
                "title_key": payload["title_key"],
                "body_key": payload["body_key"],
                "placeholders": deepcopy(payload["placeholders"]),
                "sequence": record["sequence"],
            }
        )
    return sorted(entries, key=lambda entry: (entry["sequence"], entry["event_id"]))


def _is_valid_record(record: object, character_id: str) -> bool:
    if not isinstance(record, dict) or record.get("event_type") not in _BIOGRAPHY_EVENT_TYPES:
        return False
    if not _nonempty_string(character_id) or record.get("character_id") != character_id:
        return False
    if not _nonempty_string(record.get("event_id")):
        return False
    sequence = record.get("sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
        return False
    payload = record.get("payload")
    if not isinstance(payload, dict) or any(field not in payload for field in _PAYLOAD_FIELDS):
        return False
    return (
        all(_nonempty_string(payload[field]) for field in _PAYLOAD_FIELDS[:-1])
        and isinstance(payload["placeholders"], dict)
    )


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())
