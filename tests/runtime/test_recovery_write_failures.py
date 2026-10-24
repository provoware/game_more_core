"""Recovery write failures must not destroy confirmed journal events.

Faults are injected only into temporary, synthetic save directories.
"""
import errno
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bunkerfrequenz.infrastructure import persistence as persistence_module
from bunkerfrequenz.infrastructure.persistence import (
    JournalContext, PersistenceError, PersistenceKernel,
)

ALLOWED = {"character.profile_updated"}
CTX = JournalContext(
    "2026-10-24T18:30:00+02:00", "session-test", "player-test",
    "character", "player-test", "cmd-test", "test", "0.8.4-a1",
)


def interrupted_save(root: Path) -> PersistenceKernel:
    kernel = PersistenceKernel(root, ALLOWED)
    kernel.initialize_state({"value": 0})
    kernel.create_snapshot("before_confirmed_event")
    kernel.commit(
        "tx-one",
        [{"event_id": "evt-one", "event_type": "character.profile_updated",
          "payload": {"new": {"value": 1}}}],
        {"value": 1},
        CTX,
    )
    kernel.state_path.write_text("[]", encoding="utf-8")
    with kernel.journal_path.open("ab") as handle:
        handle.write(b"{broken-tail\n")
    return kernel


def replay(state: dict, record: dict) -> dict:
    return {"value": record["payload"]["new"]["value"]}


class RecoveryWriteFailureTest(unittest.TestCase):
    def assert_retry_recovers(self, root: Path, recovery: PersistenceKernel) -> None:
        with self.assertRaises(PersistenceError):
            PersistenceKernel(root, ALLOWED)
        receipt = recovery.recover(replay)
        self.assertEqual(receipt.status, "recovered")
        self.assertEqual(PersistenceKernel(root, ALLOWED).load_state(), {"value": 1})
        records = PersistenceKernel(root, ALLOWED).read_records()
        self.assertEqual([record["event_id"] for record in records], ["evt-one"])

    def test_enospc_state_or_meta_keeps_original_journal_and_recovery_guard(self):
        for target_name in ("state_path", "meta_path"):
            with self.subTest(target=target_name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                kernel = interrupted_save(root)
                before = kernel.journal_path.read_bytes()
                recovery = PersistenceKernel.open_for_recovery(root, ALLOWED)
                target = getattr(recovery, target_name)
                original_write = persistence_module._atomic_write_json

                def fail_target(path, data):
                    if path == target:
                        raise OSError(errno.ENOSPC, "synthetic full disk")
                    return original_write(path, data)

                with patch.object(persistence_module, "_atomic_write_json", side_effect=fail_target):
                    with self.assertRaises(OSError) as caught:
                        recovery.recover(replay)
                self.assertEqual(caught.exception.errno, errno.ENOSPC)
                self.assertEqual(kernel.journal_path.read_bytes(), before)
                self.assertTrue(recovery._recovery_required)
                with self.assertRaises(PersistenceError):
                    recovery.commit("tx-forbidden", [], {}, CTX)
                self.assert_retry_recovers(root, recovery)

    def test_enospc_journal_replacement_keeps_original_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = interrupted_save(root)
            before = kernel.journal_path.read_bytes()
            recovery = PersistenceKernel.open_for_recovery(root, ALLOWED)
            original_write = persistence_module._atomic_write_bytes

            def fail_journal(path, data):
                if path == recovery.journal_path:
                    raise OSError(errno.ENOSPC, "synthetic journal replacement failure")
                return original_write(path, data)

            with patch.object(persistence_module, "_atomic_write_bytes", side_effect=fail_journal):
                with self.assertRaises(OSError):
                    recovery.recover(replay)
            self.assertEqual(kernel.journal_path.read_bytes(), before)
            self.assertTrue(recovery._recovery_required)
            self.assert_retry_recovers(root, recovery)

    def test_enospc_snapshot_after_recovery_leaves_playable_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            interrupted_save(root)
            recovery = PersistenceKernel.open_for_recovery(root, ALLOWED)
            original_write = persistence_module._atomic_write_json

            def fail_snapshot(path, data):
                if path.parent == recovery.snapshot_dir and path.name.startswith("snap-"):
                    raise OSError(errno.ENOSPC, "synthetic snapshot failure")
                return original_write(path, data)

            with patch.object(persistence_module, "_atomic_write_json", side_effect=fail_snapshot):
                with self.assertRaises(OSError):
                    recovery.recover(replay)
            reopened = PersistenceKernel(root, ALLOWED)
            self.assertEqual(reopened.load_state(), {"value": 1})
            self.assertEqual([r["event_id"] for r in reopened.read_records()], ["evt-one"])
            self.assertEqual(reopened.recover(replay).status, "healthy")


if __name__ == "__main__":
    unittest.main()
