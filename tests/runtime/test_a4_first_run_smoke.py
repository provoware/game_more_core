from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.infrastructure.persistence import PersistenceKernel
from tools.start_a4_game_client import A4ClientRuntime


def cid(name: str) -> str:
    return f"smoke:{name}"


class A4FirstRunSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.save_dir = Path(self.tmp.name)

    def send(self, runtime: A4ClientRuntime, command: dict) -> dict:
        result = runtime.command(command)
        self.assertEqual(result["status"], "confirmed", (command, result))
        return result

    def test_new_game_full_loop_restart_and_automatic_recovery(self):
        runtime = A4ClientRuntime(self.save_dir)
        first_run = runtime.bootstrap({
            "command_id": cid("first-run"),
            "character_name": "Smoke Crew",
            "event_name": "Smoke Event",
        })
        self.assertEqual(first_run["status"], "confirmed", first_run)

        for command in (
            {"type": "event.execute", "command_id": cid("planning"), "action_id": "begin_planning"},
            {"type": "event.execute", "command_id": cid("procurement"), "action_id": "begin_procurement"},
            {"type": "economy.transact", "command_id": cid("buy"), "kind": "buy", "item_id": "equipment.pa", "quantity": 1},
            {"type": "economy.transact", "command_id": cid("reserve"), "kind": "reserve", "item_id": "equipment.pa", "quantity": 1},
            {"type": "event.execute", "command_id": cid("transport"), "action_id": "start_transport"},
            {"type": "event.execute", "command_id": cid("setup"), "action_id": "begin_setup"},
            {"type": "event.execute", "command_id": cid("soundcheck"), "action_id": "confirm_soundcheck"},
            {"type": "event.execute", "command_id": cid("live"), "action_id": "start_live"},
            {"type": "incident.open", "command_id": cid("incident-open"), "incident_type": "power_drop", "severity": 3},
            {"type": "incident.resolve", "command_id": cid("incident-resolve"), "response_id": "power_drop.generator"},
            {"type": "event.execute", "command_id": cid("finish-live"), "action_id": "finish_live"},
            {"type": "event.execute", "command_id": cid("finish-teardown"), "action_id": "finish_teardown"},
            {"type": "settlement.complete", "command_id": cid("settlement")},
        ):
            self.send(runtime, command)

        checkpoint = runtime.checkpoint()
        self.assertEqual(checkpoint["status"], "confirmed")
        expected = runtime.session.read_state()
        self.assertEqual(expected["event"]["phase"], "completed")

        restarted = A4ClientRuntime(self.save_dir)
        self.assertIsNone(restarted.startup_recovery)
        self.assertEqual(restarted.session.read_state(), expected)

        # Simulate a missing current checkpoint. The snapshot+journal are intact;
        # a normal kernel must fail closed, while A4 startup performs canonical recovery.
        restarted.kernel.state_path.unlink()
        with self.assertRaises(RuntimeError):
            PersistenceKernel(self.save_dir, restarted.kernel.allowed_event_types)

        recovered = A4ClientRuntime(self.save_dir)
        self.assertIsNotNone(recovered.startup_recovery)
        self.assertEqual(recovered.startup_recovery.status, "recovered")
        self.assertEqual(recovered.session.read_state(), expected)

        final_restart = A4ClientRuntime(self.save_dir)
        self.assertIsNone(final_restart.startup_recovery)
        self.assertEqual(final_restart.session.read_state(), expected)

    def test_invalid_first_run_id_does_not_seed_partial_save(self):
        runtime = A4ClientRuntime(self.save_dir)
        result = runtime.bootstrap({"command_id": "", "character_name": "X", "event_name": "Y"})
        self.assertEqual((result["status"], result["error_code"]), ("rejected", "invalid_command_id"))
        self.assertEqual(runtime.session.read_state(), {})
        self.assertEqual(runtime.kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
