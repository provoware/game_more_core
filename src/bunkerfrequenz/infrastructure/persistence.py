from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable


class TransactionState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    PREPARED = "PREPARED"
    JOURNAL_DURABLE = "JOURNAL_DURABLE"
    STATE_APPLIED = "STATE_APPLIED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class PersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class JournalContext:
    timestamp_local: str
    session_id: str
    player_id: str
    entity_type: str
    entity_id: str
    command_id: str
    source: str
    game_version: str
    character_id: str | None = None


@dataclass(frozen=True, slots=True)
class CommitReceipt:
    transaction_id: str
    state: TransactionState
    event_ids: tuple[str, ...]
    journal_head_hash: str


def _canonical_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _payload_fingerprint(event_type: str, payload: dict) -> str:
    return hashlib.sha256(_canonical_json({"event_type": event_type, "payload": payload}).encode("utf-8")).hexdigest()


def _atomic_write_json(path: Path, data: dict) -> None:
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


class PersistenceKernel:
    def __init__(self, root: str | Path, allowed_event_types: set[str] | None = None):
        self.root = Path(root)
        self.journal_path = self.root / "journal" / "events.jsonl"
        self.state_path = self.root / "state" / "current.json"
        self.meta_path = self.root / "save_meta.json"
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        self.allowed_event_types = allowed_event_types
        self._seen: dict[str, str] = {}
        self._head_hash = "GENESIS"
        self._last_sequence = 0
        if self.journal_path.exists():
            self._load_and_verify()

    @property
    def head_hash(self) -> str:
        return self._head_hash

    def has_event(self, event_id: str) -> bool:
        return event_id in self._seen

    def load_state(self) -> dict | None:
        if not self.state_path.exists():
            return None
        with self.state_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _load_and_verify(self) -> None:
        previous = "GENESIS"
        last_sequence = 0
        seen: dict[str, str] = {}
        with self.journal_path.open("r", encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise PersistenceError(f"Journal beschädigt in Zeile {number}") from exc
                supplied_hash = record.get("event_hash")
                unsigned = {k: v for k, v in record.items() if k != "event_hash"}
                expected = hashlib.sha256(_canonical_json(unsigned).encode("utf-8")).hexdigest()
                if record.get("previous_event_hash") != previous or supplied_hash != expected:
                    raise PersistenceError(f"Journal-Hashkette ungültig in Zeile {number}")
                sequence = int(record.get("sequence", 0))
                if sequence <= last_sequence:
                    raise PersistenceError(f"Journal-Sequenz ungültig in Zeile {number}")
                event_id = record["event_id"]
                fingerprint = _payload_fingerprint(record["event_type"], record["payload"])
                if event_id in seen and seen[event_id] != fingerprint:
                    raise PersistenceError(f"Event-ID mit abweichendem Payload: {event_id}")
                seen[event_id] = fingerprint
                last_sequence = sequence
                previous = supplied_hash
        self._seen = seen
        self._head_hash = previous
        self._last_sequence = last_sequence

    def _prepare_records(self, transaction_id: str, events: Iterable[dict], context: JournalContext) -> list[dict]:
        prepared = []
        previous = self._head_hash
        next_sequence = self._last_sequence
        pending: dict[str, str] = {}
        for event in events:
            event_id = event["event_id"]
            event_type = event["event_type"]
            payload = event.get("payload", {})
            if self.allowed_event_types is not None and event_type not in self.allowed_event_types:
                raise PersistenceError(f"Nicht katalogisierter Journal-Eventtyp: {event_type}")
            fingerprint = _payload_fingerprint(event_type, payload)
            if event_id in self._seen:
                if self._seen[event_id] != fingerprint:
                    raise PersistenceError(f"Doppeltes Event mit anderem Inhalt: {event_id}")
                continue
            if event_id in pending:
                if pending[event_id] != fingerprint:
                    raise PersistenceError(f"Doppeltes Event im selben Commit mit anderem Inhalt: {event_id}")
                continue
            pending[event_id] = fingerprint
            next_sequence += 1
            record = {
                "schema_version": 2,
                "event_id": event_id,
                "event_type": event_type,
                "sequence": next_sequence,
                "transaction_id": transaction_id,
                "timestamp_local": context.timestamp_local,
                "session_id": context.session_id,
                "player_id": context.player_id,
                "entity_type": context.entity_type,
                "entity_id": context.entity_id,
                "command_id": context.command_id,
                "source": context.source,
                "game_version": context.game_version,
                "payload": payload,
                "previous_event_hash": previous,
            }
            if context.character_id is not None:
                record["character_id"] = context.character_id
            record["event_hash"] = hashlib.sha256(_canonical_json(record).encode("utf-8")).hexdigest()
            previous = record["event_hash"]
            prepared.append(record)
        return prepared

    def commit(self, transaction_id: str, events: Iterable[dict], derived_state: dict, context: JournalContext) -> CommitReceipt:
        records = self._prepare_records(transaction_id, events, context)
        if not records:
            return CommitReceipt(transaction_id, TransactionState.COMMITTED, (), self._head_hash)

        with self.journal_path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(_canonical_json(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

        for record in records:
            self._seen[record["event_id"]] = _payload_fingerprint(record["event_type"], record["payload"])
            self._head_hash = record["event_hash"]
            self._last_sequence = record["sequence"]

        _atomic_write_json(self.state_path, derived_state)
        _atomic_write_json(self.meta_path, {
            "schema_version": 2,
            "journal_head_hash": self._head_hash,
            "last_sequence": self._last_sequence,
            "last_transaction_id": transaction_id,
        })
        return CommitReceipt(transaction_id, TransactionState.COMMITTED, tuple(r["event_id"] for r in records), self._head_hash)

    @staticmethod
    def autosave_due(*, dirty: bool, seconds_since_last_save: float) -> bool:
        return dirty and seconds_since_last_save >= 60.0
