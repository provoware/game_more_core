from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel

CTX = JournalContext("2026-08-21T16:00:00+02:00", "s-1", "p-1", "character", "c-1", "cmd-1", "runtime", "0.5.0-alpha.1", "c-1")
ALLOWED = {"character.skill_xp_gained"}


class PersistenceKernelTest(unittest.TestCase):
    def test_commit_reload_and_idempotent_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = PersistenceKernel(root, ALLOWED)
            event = {"event_id": "evt-1", "event_type": "character.skill_xp_gained", "payload": {"amount": 5}}
            receipt = kernel.commit("tx-1", [event], {"value": 1}, CTX)
            self.assertEqual(receipt.state.value, "COMMITTED")
            reloaded = PersistenceKernel(root, ALLOWED)
            self.assertEqual(reloaded.head_hash, receipt.journal_head_hash)
            duplicate = reloaded.commit("tx-2", [event], {"value": 999}, CTX)
            self.assertEqual(duplicate.event_ids, ())
            self.assertEqual(reloaded.load_state(), {"value": 1})

    def test_duplicate_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.commit("tx-1", [{"event_id":"evt-1","event_type":"character.skill_xp_gained","payload":{"v":1}}], {"v":1}, CTX)
            with self.assertRaises(PersistenceError):
                kernel.commit("tx-2", [{"event_id":"evt-1","event_type":"character.skill_xp_gained","payload":{"v":2}}], {"v":2}, CTX)

    def test_duplicate_inside_same_commit_is_collapsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            event = {"event_id":"evt-1","event_type":"character.skill_xp_gained","payload":{"v":1}}
            receipt = kernel.commit("tx-1", [event, event], {"v":1}, CTX)
            self.assertEqual(receipt.event_ids, ("evt-1",))

    def test_unknown_event_type_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            with self.assertRaises(PersistenceError):
                kernel.commit("tx-1", [{"event_id":"evt-1","event_type":"not.catalogued","payload":{}}], {}, CTX)

    def test_corrupt_tail_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = PersistenceKernel(root, ALLOWED)
            kernel.commit("tx-1", [{"event_id":"evt-1","event_type":"character.skill_xp_gained","payload":{"v":1}}], {"v":1}, CTX)
            with (root / "journal" / "events.jsonl").open("a", encoding="utf-8") as handle:
                handle.write("{broken\n")
            with self.assertRaises(PersistenceError):
                PersistenceKernel(root, ALLOWED)

    def test_autosave_contract(self):
        self.assertFalse(PersistenceKernel.autosave_due(dirty=False, seconds_since_last_save=100))
        self.assertFalse(PersistenceKernel.autosave_due(dirty=True, seconds_since_last_save=59.9))
        self.assertTrue(PersistenceKernel.autosave_due(dirty=True, seconds_since_last_save=60.0))


if __name__ == "__main__":
    unittest.main()
