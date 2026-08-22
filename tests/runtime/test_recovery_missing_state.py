import tempfile
import unittest

from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel

ALLOWED = {"character.profile_updated"}
CTX = JournalContext(
    "2026-08-22T14:00:00+02:00",
    "session-recovery-missing-state",
    "player-local",
    "character",
    "player-local",
    "cmd-recovery",
    "test",
    "0.8.4-a1",
    "player-local",
)


class MissingStateRecoveryTest(unittest.TestCase):
    def test_snapshot_at_head_restores_missing_current_state_instead_of_reporting_healthy(self):
        with tempfile.TemporaryDirectory() as root:
            kernel = PersistenceKernel(root, ALLOWED)
            initial = {"character": {"display_name": "A"}}
            kernel.initialize_state(initial)
            state = {"character": {"display_name": "B"}}
            kernel.commit(
                "tx-profile",
                [{
                    "event_id": "evt-profile",
                    "event_type": "character.profile_updated",
                    "payload": {"changes": {"display_name": "B"}},
                }],
                state,
                CTX,
            )
            kernel.create_snapshot("head")
            kernel.state_path.unlink()

            with self.assertRaises(PersistenceError):
                PersistenceKernel(root, ALLOWED)

            recovery = PersistenceKernel.open_for_recovery(root, ALLOWED)
            receipt = recovery.recover(lambda current, record: state)
            self.assertEqual(receipt.status, "recovered")
            self.assertEqual(recovery.load_state(), state)

            healthy = PersistenceKernel(root, ALLOWED)
            self.assertEqual(healthy.load_state(), state)


if __name__ == "__main__":
    unittest.main()
