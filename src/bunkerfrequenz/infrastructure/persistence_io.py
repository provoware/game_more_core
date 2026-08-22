from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile


@dataclass(frozen=True, slots=True)
class JournalScan:
    records: tuple[dict, ...]
    error: str | None
    invalid_tail: bytes

    @property
    def sequence(self) -> int:
        return int(self.records[-1]["sequence"]) if self.records else 0

    @property
    def head_hash(self) -> str:
        return str(self.records[-1]["event_hash"]) if self.records else "GENESIS"


def canonical_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def payload_fingerprint(event_type: str, payload: dict) -> str:
    value = canonical_json({"event_type": event_type, "payload": payload})
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_data(data: dict) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def snapshot_path_is_safe(path: Path, snapshot_dir: Path) -> bool:
    try:
        path.resolve().relative_to(snapshot_dir.resolve())
    except (OSError, ValueError):
        return False
    return True


def validated_snapshot(data: object, entry: object, path: Path, snapshot_dir: Path) -> dict | None:
    if not isinstance(data, Mapping) or not isinstance(entry, Mapping):
        return None
    for field in ("snapshot_id", "journal_head_hash", "state_hash"):
        if not isinstance(data.get(field), str) or not data[field]:
            return None
    sequence = data.get("journal_sequence")
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        return None
    state = data.get("state")
    if not isinstance(state, dict) or data["state_hash"] != hash_data(state):
        return None
    for field in ("snapshot_id", "journal_head_hash", "path"):
        if not isinstance(entry.get(field), str) or not entry[field]:
            return None
    entry_sequence = entry.get("journal_sequence")
    if isinstance(entry_sequence, bool) or not isinstance(entry_sequence, int) or entry_sequence < 0:
        return None
    if not snapshot_path_is_safe(path, snapshot_dir):
        return None
    identity_fields = ("snapshot_id", "journal_sequence", "journal_head_hash")
    if path.name != entry["path"] or any(entry[field] != data[field] for field in identity_fields):
        return None
    return dict(data)


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _journal_record_shape_error(record: object) -> str | None:
    if not isinstance(record, dict):
        return "Datensatz ist kein Objekt"
    required = ("sequence", "event_id", "event_type", "previous_event_hash", "event_hash", "payload")
    missing = [field for field in required if field not in record]
    if missing:
        return f"Pflichtfeld fehlt: {missing[0]}"
    if isinstance(record["sequence"], bool) or not isinstance(record["sequence"], int) or record["sequence"] <= 0:
        return "Sequenz ist keine positive Ganzzahl"
    for field in ("event_id", "event_type", "previous_event_hash", "event_hash"):
        if not isinstance(record[field], str) or not record[field]:
            return f"Feld {field} ist keine nichtleere Zeichenkette"
    if not isinstance(record["payload"], dict):
        return "Payload ist kein Objekt"
    return None


def scan_journal(path: Path) -> JournalScan:
    if not path.exists():
        return JournalScan((), None, b"")
    raw_lines = path.read_bytes().splitlines(keepends=True)
    previous = "GENESIS"
    last_sequence = 0
    seen: dict[str, str] = {}
    records: list[dict] = []
    for index, raw_line in enumerate(raw_lines):
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return JournalScan(tuple(records), f"Journal beschädigt in Zeile {index + 1}: {exc}", b"".join(raw_lines[index:]))
        shape_error = _journal_record_shape_error(record)
        if shape_error:
            return JournalScan(tuple(records), f"Journal-Datensatz ungültig in Zeile {index + 1}: {shape_error}", b"".join(raw_lines[index:]))
        supplied_hash = record["event_hash"]
        unsigned = {key: value for key, value in record.items() if key != "event_hash"}
        expected = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
        if record["previous_event_hash"] != previous or supplied_hash != expected:
            return JournalScan(tuple(records), f"Journal-Hashkette ungültig in Zeile {index + 1}", b"".join(raw_lines[index:]))
        sequence = record["sequence"]
        if sequence <= last_sequence:
            return JournalScan(tuple(records), f"Journal-Sequenz ungültig in Zeile {index + 1}", b"".join(raw_lines[index:]))
        event_id = record["event_id"]
        fingerprint = payload_fingerprint(record["event_type"], record["payload"])
        if event_id in seen:
            return JournalScan(tuple(records), f"Doppelte Event-ID im Journal: {event_id}", b"".join(raw_lines[index:]))
        seen[event_id] = fingerprint
        records.append(record)
        last_sequence = sequence
        previous = supplied_hash
    return JournalScan(tuple(records), None, b"")


def head_for_sequence(records: tuple[dict, ...], sequence: int) -> str | None:
    if sequence == 0:
        return "GENESIS"
    for record in records:
        if int(record["sequence"]) == sequence:
            return str(record["event_hash"])
    return None
