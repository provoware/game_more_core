"""Fail-closed regression checks for malformed local checkpoint and save metadata.

Every fixture uses an isolated temporary save; no real player files are read.
"""
import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.infrastructure.persistence import PersistenceError, PersistenceKernel


class CheckpointShapeRecoveryTest(unittest.TestCase):
    @staticmethod
    def _ready_save(root: Path) -> PersistenceKernel:
        kernel = PersistenceKernel(root)
        kernel.initialize_state({"value": 7})
        kernel.create_snapshot("checkpoint_shape_regression")
        return kernel

    def test_invalid_state_shapes_use_valid_snapshot_without_losing_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = self._ready_save(root)
            valid = json.loads(kernel.state_path.read_text(encoding="utf-8"))
            variants = {
                "list": [],
                "null": None,
                "string": "bad",
                "non_object_data": {**valid, "data": []},
                "string_sequence": {**valid, "applied_sequence": "0"},
                "boolean_sequence": {**valid, "applied_sequence": True},
                "negative_sequence": {**valid, "applied_sequence": -1},
                "non_string_head": {**valid, "journal_head_hash": []},
                "empty_head": {**valid, "journal_head_hash": ""},
                "unknown_version": {**valid, "state_envelope_version": 99},
            }
            for label, malformed in variants.items():
                with self.subTest(label=label):
                    kernel.state_path.write_text(json.dumps(malformed), encoding="utf-8")
                    with self.assertRaises(PersistenceError):
                        PersistenceKernel(root)
                    recovery = PersistenceKernel.open_for_recovery(root)
                    receipt = recovery.recover(lambda state, record: state)
                    self.assertEqual(receipt.status, "recovered")
                    self.assertEqual(receipt.checkpoint_kind, "snapshot")
                    self.assertEqual(recovery.load_state(), {"value": 7})
                    self.assertEqual(PersistenceKernel(root).load_state(), {"value": 7})

    def test_invalid_metadata_shapes_recover_without_changing_game_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = self._ready_save(root)
            valid = json.loads(kernel.meta_path.read_text(encoding="utf-8"))
            variants = {
                "list": [],
                "null": None,
                "string": "bad",
                "missing_sequence": {"journal_head_hash": "GENESIS"},
                "string_sequence": {**valid, "last_sequence": "0"},
                "boolean_sequence": {**valid, "last_sequence": True},
                "negative_sequence": {**valid, "last_sequence": -1},
                "non_string_head": {**valid, "journal_head_hash": []},
                "empty_head": {**valid, "journal_head_hash": ""},
            }
            for label, malformed in variants.items():
                with self.subTest(label=label):
                    kernel.meta_path.write_text(json.dumps(malformed), encoding="utf-8")
                    with self.assertRaises(PersistenceError):
                        PersistenceKernel(root)
                    recovery = PersistenceKernel.open_for_recovery(root)
                    receipt = recovery.recover(lambda state, record: state)
                    self.assertEqual(receipt.status, "recovered")
                    self.assertEqual(recovery.load_state(), {"value": 7})
                    self.assertEqual(PersistenceKernel(root).load_state(), {"value": 7})

    def test_no_valid_checkpoint_refuses_recovery_without_overwriting_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = PersistenceKernel(root)
            kernel.initialize_state({"value": 7})
            kernel.state_path.write_text("[]", encoding="utf-8")
            kernel.meta_path.write_text("null", encoding="utf-8")
            before_state = kernel.state_path.read_bytes()
            before_meta = kernel.meta_path.read_bytes()
            recovery = PersistenceKernel.open_for_recovery(root)
            with self.assertRaisesRegex(PersistenceError, "Kein gültiger Recovery-Checkpoint"):
                recovery.recover(lambda state, record: state)
            self.assertEqual(kernel.state_path.read_bytes(), before_state)
            self.assertEqual(kernel.meta_path.read_bytes(), before_meta)


if __name__ == "__main__":
    unittest.main()
