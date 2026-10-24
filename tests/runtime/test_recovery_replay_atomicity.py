"""Recovery darf das Originaljournal nicht verändern, wenn Replay fehlschlägt.

Nur künstliche Spielstände in temporären Verzeichnissen.
"""
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.infrastructure.persistence import (
    JournalContext, PersistenceError, PersistenceKernel,
)

ALLOWED = {"character.profile_updated"}
CTX = JournalContext(
    "2026-10-24T13:00:00+02:00", "session-test", "player-test",
    "character", "player-test", "cmd-test", "test", "0.8.4-a1",
)


def prepare_interrupted_save(root: Path):
    kernel = PersistenceKernel(root, ALLOWED)
    kernel.initialize_state({"value": 0})
    kernel.create_snapshot("pre_event")
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


class ReplayAtomicityTest(unittest.TestCase):
    def test_failed_replay_preserves_original_journal_and_checkpoints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = prepare_interrupted_save(root)
            before = {
                path: path.read_bytes()
                for path in (kernel.journal_path, kernel.state_path, kernel.meta_path)
            }
            recovery = PersistenceKernel.open_for_recovery(root, ALLOWED)

            def replay_fails(state, record):
                raise ValueError("Replay absichtlich fehlgeschlagen")

            with self.assertRaisesRegex(ValueError, "Replay absichtlich"):
                recovery.recover(replay_fails)

            for path, original in before.items():
                self.assertEqual(path.read_bytes(), original, f"Quelle verändert: {path.name}")
            with self.assertRaises(PersistenceError):
                PersistenceKernel(root, ALLOWED)

    def test_successful_replay_quarantines_tail_and_restores_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = prepare_interrupted_save(root)
            recovery = PersistenceKernel.open_for_recovery(root, ALLOWED)

            def replay(state, record):
                self.assertEqual(record["event_id"], "evt-one")
                return {"value": record["payload"]["new"]["value"]}

            receipt = recovery.recover(replay)
            self.assertEqual(receipt.status, "recovered")
            self.assertEqual(receipt.checkpoint_kind, "snapshot")
            self.assertEqual(receipt.replayed_events, 1)
            self.assertIsNotNone(receipt.quarantined_path)
            self.assertEqual((root / receipt.quarantined_path).read_bytes(), b"{broken-tail\n")
            self.assertEqual(PersistenceKernel(root, ALLOWED).load_state(), {"value": 1})
            self.assertEqual(len(PersistenceKernel(root, ALLOWED).read_records()), 1)


if __name__ == "__main__":
    unittest.main()
