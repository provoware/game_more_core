from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
from typing import Callable, Iterable

from bunkerfrequenz.infrastructure.persistence_io import (
    JournalScan as _JournalScan,
    atomic_write_bytes as _atomic_write_bytes,
    atomic_write_json as _atomic_write_json,
    canonical_json as _canonical_json,
    hash_data as _hash_data,
    head_for_sequence as _head_for_sequence,
    payload_fingerprint as _payload_fingerprint,
    scan_journal as _scan_journal,
    snapshot_path_is_safe as _snapshot_path_is_safe,
    validated_snapshot as _validated_snapshot,
)


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


class FaultInjectedCrash(RuntimeError):
    """Test-only crash marker raised by an injected transaction fault."""


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


@dataclass(frozen=True, slots=True)
class RecoveryReceipt:
    status: str
    recovery_id: str | None
    checkpoint_kind: str | None
    checkpoint_sequence: int
    replayed_events: int
    quarantined_path: str | None
    recovered_sequence: int
    recovered_head_hash: str
    snapshot_id: str | None


class PersistenceKernel:
    def __init__(
        self,
        root: str | Path,
        allowed_event_types: set[str] | None = None,
        *,
        fault_injector: Callable[[str], None] | None = None,
        recovery_mode: bool = False,
    ):
        self.root = Path(root)
        self.journal_path = self.root / "journal" / "events.jsonl"
        self.state_path = self.root / "state" / "current.json"
        self.meta_path = self.root / "save_meta.json"
        self.snapshot_dir = self.root / "snapshots"
        self.snapshot_index_path = self.snapshot_dir / "index.json"
        self.quarantine_dir = self.root / "recovery" / "quarantine"
        self.recovery_receipt_path = self.root / "recovery" / "RECOVERY_RECEIPT.json"
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        self.allowed_event_types = allowed_event_types
        self._fault_injector = fault_injector
        self._recovery_mode = recovery_mode
        self._recovery_required = False
        self._seen: dict[str, str] = {}
        self._head_hash = "GENESIS"
        self._last_sequence = 0
        if self.journal_path.exists():
            scan = _scan_journal(self.journal_path)
            if scan.error:
                if not recovery_mode:
                    raise PersistenceError(scan.error)
                self._recovery_required = True
            self._accept_scan(scan)
        self._verify_checkpoint_consistency()

    @classmethod
    def open_for_recovery(cls, root: str | Path, allowed_event_types: set[str] | None = None) -> "PersistenceKernel":
        return cls(root, allowed_event_types, recovery_mode=True)

    @property
    def head_hash(self) -> str:
        return self._head_hash

    @property
    def last_sequence(self) -> int:
        return self._last_sequence

    def has_event(self, event_id: str) -> bool:
        return event_id in self._seen

    def _trip_fault(self, point: str) -> None:
        if self._fault_injector is not None:
            self._fault_injector(point)

    @staticmethod
    def _state_envelope(data: dict, sequence: int, head_hash: str) -> dict:
        return {
            "state_envelope_version": 1,
            "applied_sequence": sequence,
            "journal_head_hash": head_hash,
            "data": data,
            "data_hash": _hash_data(data),
        }

    def _read_state_envelope(self) -> dict | None:
        if not self.state_path.exists():
            return None
        try:
            with self.state_path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise PersistenceError("State-Checkpoint ist beschädigt") from exc
        if raw.get("state_envelope_version") == 1:
            if raw.get("data_hash") != _hash_data(raw.get("data", {})):
                raise PersistenceError("State-Checkpoint besitzt ungültige Prüfsumme")
            return raw
        # 0.5.0-alpha.1 legacy state: pair with meta if possible.
        meta = self._read_meta()
        sequence = int(meta.get("last_sequence", 0)) if meta else 0
        head_hash = str(meta.get("journal_head_hash", "GENESIS")) if meta else "GENESIS"
        return self._state_envelope(raw, sequence, head_hash)

    def _read_meta(self) -> dict | None:
        if not self.meta_path.exists():
            return None
        try:
            with self.meta_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise PersistenceError("Save-Metadaten sind beschädigt") from exc

    def load_state(self) -> dict | None:
        envelope = self._read_state_envelope()
        return None if envelope is None else envelope["data"]

    def initialize_state(self, derived_state: dict) -> None:
        """Create a GENESIS checkpoint before the first journaled action."""
        if self.state_path.exists():
            return
        if self._last_sequence != 0:
            raise PersistenceError("Initialzustand fehlt trotz bestehendem Journal; Recovery erforderlich")
        _atomic_write_json(self.state_path, self._state_envelope(derived_state, 0, "GENESIS"))
        _atomic_write_json(self.meta_path, {
            "schema_version": 2,
            "state_envelope_version": 1,
            "journal_head_hash": "GENESIS",
            "last_sequence": 0,
            "last_transaction_id": None,
        })

    def _load_and_verify(self) -> None:
        scan = _scan_journal(self.journal_path)
        if scan.error:
            raise PersistenceError(scan.error)
        self._accept_scan(scan)

    def _verify_checkpoint_consistency(self) -> None:
        if self._last_sequence == 0 and not self.state_path.exists():
            return
        try:
            envelope = self._read_state_envelope()
            meta = self._read_meta()
        except PersistenceError:
            if self._recovery_mode:
                self._recovery_required = True
                return
            raise
        consistent = bool(
            envelope
            and meta
            and int(envelope.get("applied_sequence", -1)) == self._last_sequence
            and envelope.get("journal_head_hash") == self._head_hash
            and int(meta.get("last_sequence", -1)) == self._last_sequence
            and meta.get("journal_head_hash") == self._head_hash
        )
        if not consistent:
            self._recovery_required = True
            if not self._recovery_mode:
                raise PersistenceError("Zustand und Journal sind nicht auf demselben bestätigten Stand; Recovery erforderlich")

    def _accept_scan(self, scan: _JournalScan) -> None:
        self._seen = {
            record["event_id"]: _payload_fingerprint(record["event_type"], record["payload"])
            for record in scan.records
        }
        self._head_hash = scan.head_hash
        self._last_sequence = scan.sequence

    def read_records(self) -> tuple[dict, ...]:
        scan = _scan_journal(self.journal_path)
        if scan.error:
            raise PersistenceError(scan.error)
        return scan.records

    def last_transaction_records(self) -> tuple[dict, ...]:
        records = self.read_records()
        if not records:
            return ()
        transaction_id = records[-1]["transaction_id"]
        selected: list[dict] = []
        for record in reversed(records):
            if record["transaction_id"] != transaction_id:
                break
            selected.append(record)
        return tuple(reversed(selected))

    def _prepare_records(self, transaction_id: str, events: Iterable[dict], context: JournalContext) -> list[dict]:
        prepared = []
        previous = self._head_hash
        next_sequence = self._last_sequence
        pending: dict[str, str] = {}
        optional_top_level = ("causation_id", "correlation_id", "reason", "compensation_for")
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
            for key in optional_top_level:
                if key in event:
                    record[key] = event[key]
            record["event_hash"] = hashlib.sha256(_canonical_json(record).encode("utf-8")).hexdigest()
            previous = record["event_hash"]
            prepared.append(record)
        return prepared

    def commit(self, transaction_id: str, events: Iterable[dict], derived_state: dict, context: JournalContext) -> CommitReceipt:
        if self._recovery_required:
            raise PersistenceError("Persistenz ist im Recovery-Zustand; zuerst Wiederherstellung ausführen")
        records = self._prepare_records(transaction_id, events, context)
        if not records:
            return CommitReceipt(transaction_id, TransactionState.COMMITTED, (), self._head_hash)

        with self.journal_path.open("a", encoding="utf-8") as handle:
            for record in records:
                handle.write(_canonical_json(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._trip_fault("after_journal_durable")

        new_head = records[-1]["event_hash"]
        new_sequence = int(records[-1]["sequence"])
        _atomic_write_json(self.state_path, self._state_envelope(derived_state, new_sequence, new_head))
        self._trip_fault("after_state_applied")

        _atomic_write_json(self.meta_path, {
            "schema_version": 2,
            "state_envelope_version": 1,
            "journal_head_hash": new_head,
            "last_sequence": new_sequence,
            "last_transaction_id": transaction_id,
        })
        self._trip_fault("after_meta_committed")

        for record in records:
            self._seen[record["event_id"]] = _payload_fingerprint(record["event_type"], record["payload"])
        self._head_hash = new_head
        self._last_sequence = new_sequence
        return CommitReceipt(transaction_id, TransactionState.COMMITTED, tuple(r["event_id"] for r in records), self._head_hash)

    def create_snapshot(self, reason: str, *, state: dict | None = None) -> str:
        if not reason:
            raise ValueError("Snapshot benötigt einen Grund")
        envelope = self._read_state_envelope()
        if state is None:
            if envelope is None:
                raise PersistenceError("Kein Zustand für Snapshot vorhanden")
            state = envelope["data"]
            sequence = int(envelope["applied_sequence"])
            head_hash = str(envelope["journal_head_hash"])
        else:
            sequence = self._last_sequence
            head_hash = self._head_hash
        if _head_for_sequence(self.read_records(), sequence) != head_hash:
            raise PersistenceError("Snapshot-Checkpoint passt nicht zum Journal")
        snapshot_id = f"snap-{sequence:012d}-{head_hash[:12]}"
        payload = {
            "snapshot_schema_version": 1,
            "snapshot_id": snapshot_id,
            "reason": reason,
            "journal_sequence": sequence,
            "journal_head_hash": head_hash,
            "state": state,
            "state_hash": _hash_data(state),
        }
        _atomic_write_json(self.snapshot_dir / f"{snapshot_id}.json", payload)
        self._rebuild_snapshot_index()
        return snapshot_id

    def _rebuild_snapshot_index(self) -> None:
        entries = []
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(self.snapshot_dir.glob("snap-*.json")):
            if not _snapshot_path_is_safe(path, self.snapshot_dir):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            entry = {
                "snapshot_id": data.get("snapshot_id") if isinstance(data, Mapping) else None,
                "journal_sequence": data.get("journal_sequence") if isinstance(data, Mapping) else None,
                "journal_head_hash": data.get("journal_head_hash") if isinstance(data, Mapping) else None,
                "path": path.name,
            }
            if _validated_snapshot(data, entry, path, self.snapshot_dir) is None:
                continue
            entries.append(entry)
        entries.sort(key=lambda entry: (entry["journal_sequence"], entry["snapshot_id"]))
        _atomic_write_json(self.snapshot_index_path, {"schema_version": 1, "snapshots": entries})

    def _valid_snapshots(self, records: tuple[dict, ...]) -> list[dict]:
        self._rebuild_snapshot_index()
        try:
            index = json.loads(self.snapshot_index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        valid = []
        if not isinstance(index, Mapping) or not isinstance(index.get("snapshots"), list):
            return valid
        for entry in index["snapshots"]:
            if not isinstance(entry, Mapping):
                continue
            path_value = entry.get("path")
            if not isinstance(path_value, str) or not path_value:
                continue
            path = self.snapshot_dir / path_value
            if not _snapshot_path_is_safe(path, self.snapshot_dir):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            data = _validated_snapshot(data, entry, path, self.snapshot_dir)
            if data is None:
                continue
            expected_head = _head_for_sequence(records, entry["journal_sequence"])
            if expected_head != entry["journal_head_hash"]:
                continue
            valid.append(data)
        return valid

    def _checkpoint_from_state(self, records: tuple[dict, ...]) -> dict | None:
        try:
            envelope = self._read_state_envelope()
        except PersistenceError:
            return None
        if envelope is None:
            return None
        sequence = int(envelope["applied_sequence"])
        head_hash = str(envelope["journal_head_hash"])
        if _head_for_sequence(records, sequence) != head_hash:
            return None
        return {"kind": "state", "sequence": sequence, "head_hash": head_hash, "state": envelope["data"]}

    def _checkpoint_from_snapshot(self, records: tuple[dict, ...]) -> dict | None:
        snapshots = self._valid_snapshots(records)
        if not snapshots:
            return None
        latest = max(snapshots, key=lambda data: int(data["journal_sequence"]))
        return {
            "kind": "snapshot",
            "sequence": int(latest["journal_sequence"]),
            "head_hash": latest["journal_head_hash"],
            "state": latest["state"],
            "snapshot_id": latest["snapshot_id"],
        }

    def recover(
        self,
        replay_event: Callable[[dict, dict], dict],
        *,
        context: JournalContext | None = None,
    ) -> RecoveryReceipt:
        scan = _scan_journal(self.journal_path)
        records = scan.records
        valid_sequence = scan.sequence
        valid_head = scan.head_hash

        state_checkpoint = self._checkpoint_from_state(records)
        snapshot_checkpoint = self._checkpoint_from_snapshot(records)
        checkpoints = [item for item in (state_checkpoint, snapshot_checkpoint) if item is not None]
        if not checkpoints:
            raise PersistenceError("Kein gültiger Recovery-Checkpoint vorhanden")
        checkpoint = max(checkpoints, key=lambda item: int(item["sequence"]))

        meta_ok = False
        try:
            meta = self._read_meta()
            meta_ok = bool(meta and int(meta.get("last_sequence", -1)) == valid_sequence and meta.get("journal_head_hash") == valid_head)
        except PersistenceError:
            meta_ok = False
        state_at_head = int(checkpoint["sequence"]) == valid_sequence and checkpoint["head_hash"] == valid_head
        if scan.error is None and state_at_head and meta_ok:
            self._accept_scan(scan)
            return RecoveryReceipt("healthy", None, checkpoint["kind"], int(checkpoint["sequence"]), 0, None, valid_sequence, valid_head, checkpoint.get("snapshot_id"))

        quarantine_path = None
        if scan.invalid_tail:
            tail_hash = hashlib.sha256(scan.invalid_tail).hexdigest()
            quarantine_path = self.quarantine_dir / f"events-tail-{tail_hash[:16]}.jsonl"
            if not quarantine_path.exists():
                _atomic_write_bytes(quarantine_path, scan.invalid_tail)
            _atomic_write_json(quarantine_path.with_suffix(".json"), {
                "schema_version": 1,
                "error": scan.error,
                "valid_sequence": valid_sequence,
                "valid_head_hash": valid_head,
                "tail_sha256": tail_hash,
            })
            repaired = b"".join((_canonical_json(record) + "\n").encode("utf-8") for record in records)
            _atomic_write_bytes(self.journal_path, repaired)

        state = json.loads(json.dumps(checkpoint["state"]))
        replayed = 0
        for record in records:
            if int(record["sequence"]) <= int(checkpoint["sequence"]):
                continue
            state = replay_event(state, record)
            replayed += 1

        self._accept_scan(_JournalScan(records, None, b""))
        self._recovery_required = False
        _atomic_write_json(self.state_path, self._state_envelope(state, valid_sequence, valid_head))
        _atomic_write_json(self.meta_path, {
            "schema_version": 2,
            "state_envelope_version": 1,
            "journal_head_hash": valid_head,
            "last_sequence": valid_sequence,
            "last_transaction_id": records[-1]["transaction_id"] if records else None,
        })

        recovery_basis = {
            "checkpoint_kind": checkpoint["kind"],
            "checkpoint_sequence": int(checkpoint["sequence"]),
            "valid_sequence": valid_sequence,
            "valid_head": valid_head,
            "quarantine": str(quarantine_path.relative_to(self.root)) if quarantine_path else None,
        }
        recovery_id = "rec-" + hashlib.sha256(_canonical_json(recovery_basis).encode("utf-8")).hexdigest()[:20]

        if context is not None and (self.allowed_event_types is None or "system.recovery_performed" in self.allowed_event_types):
            recovery_event = {
                "event_id": f"recovery:{recovery_id}",
                "event_type": "system.recovery_performed",
                "payload": {
                    "recovery_id": recovery_id,
                    "checkpoint_sequence": int(checkpoint["sequence"]),
                    "replayed_events": replayed,
                    "corrupt_tail_quarantined": quarantine_path is not None,
                },
            }
            self.commit(f"tx:{recovery_id}", [recovery_event], state, context)
            valid_sequence = self._last_sequence
            valid_head = self._head_hash

        snapshot_id = self.create_snapshot("post_recovery")
        receipt_data = {
            "schema_version": 1,
            "recovery_id": recovery_id,
            "status": "recovered",
            "checkpoint_kind": checkpoint["kind"],
            "checkpoint_sequence": int(checkpoint["sequence"]),
            "replayed_events": replayed,
            "quarantined_path": str(quarantine_path.relative_to(self.root)) if quarantine_path else None,
            "recovered_sequence": valid_sequence,
            "recovered_head_hash": valid_head,
            "snapshot_id": snapshot_id,
            "state_hash": _hash_data(state),
        }
        _atomic_write_json(self.recovery_receipt_path, receipt_data)
        return RecoveryReceipt(
            "recovered", recovery_id, checkpoint["kind"], int(checkpoint["sequence"]), replayed,
            receipt_data["quarantined_path"], valid_sequence, valid_head, snapshot_id,
        )

    @staticmethod
    def autosave_due(*, dirty: bool, seconds_since_last_save: float) -> bool:
        return dirty and seconds_since_last_save >= 60.0

    @staticmethod
    def snapshot_due(*, committed_events_since_snapshot: int, seconds_since_snapshot: float) -> bool:
        return committed_events_since_snapshot >= 50 or seconds_since_snapshot >= 300.0
