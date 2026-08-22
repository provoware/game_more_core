import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.application.recovery_service import CharacterRecoveryService, replay_character_event
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import FaultInjectedCrash, JournalContext, PersistenceError, PersistenceKernel

ACTION = {
    "action_id":"action.soundcheck","category":"event","risk_profile":"medium",
    "resource_effects":{"energy_delta":0,"stress_delta":0},
    "skill_weights":{"technik":0.5,"musik":0.3,"konzentration":0.2},
    "trait_evidence_weights":{"klangfokus":0.6,"detailmensch":0.4},"prerequisites":[]
}
ALLOWED = {
    "character.profile_updated","character.resources_changed","character.skill_xp_gained","character.skill_level_up",
    "character.trait_evidence_gained","character.trait_unlocked","character.trait_tier_up",
    "character.specialization_changed","character.level_up","system.recovery_performed",
}
CTX = JournalContext("2026-08-21T16:20:00+02:00", "s-r", "p-r", "character", "c-r", "cmd-r", "runtime", "0.5.1-alpha.1", "c-r")


def crash_at(target):
    def injector(point):
        if point == target:
            raise FaultInjectedCrash(point)
    return injector


class RecoveryTest(unittest.TestCase):
    def test_snapshot_writer_and_due_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({"character": CharacterState("c-r", "R").to_dict()})
            snapshot_id = kernel.create_snapshot("manual_test")
            path = Path(tmp) / "snapshots" / f"{snapshot_id}.json"
            self.assertTrue(path.exists())
            self.assertTrue((Path(tmp) / "snapshots" / "index.json").exists())
            self.assertFalse(kernel.snapshot_due(committed_events_since_snapshot=49, seconds_since_snapshot=299))
            self.assertTrue(kernel.snapshot_due(committed_events_since_snapshot=50, seconds_since_snapshot=1))
            self.assertTrue(kernel.snapshot_due(committed_events_since_snapshot=0, seconds_since_snapshot=300))

    def test_recover_after_journal_durable_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = CharacterState("c-r", "R")
            expected = ActionResolver().resolve(start, ACTION, action_instance_id="a-crash-j", world_seed="w").character_after.to_dict()
            kernel = PersistenceKernel(tmp, ALLOWED, fault_injector=crash_at("after_journal_durable"))
            service = CharacterActionService(ActionResolver(), kernel)
            with self.assertRaises(FaultInjectedCrash):
                service.execute(start, ACTION, action_instance_id="a-crash-j", world_seed="w", journal_context=CTX)
            with self.assertRaises(PersistenceError):
                PersistenceKernel(tmp, ALLOWED)
            recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
            receipt = CharacterRecoveryService(recovering).recover(context=CTX)
            self.assertEqual(receipt.status, "recovered")
            self.assertGreater(receipt.replayed_events, 0)
            self.assertEqual(recovering.load_state()["character"], expected)
            healthy = CharacterRecoveryService(recovering).recover(context=CTX)
            self.assertEqual(healthy.status, "healthy")

    def test_recover_after_state_applied_crash_without_double_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = CharacterState("c-r", "R")
            expected = ActionResolver().resolve(start, ACTION, action_instance_id="a-crash-s", world_seed="w").character_after.to_dict()
            kernel = PersistenceKernel(tmp, ALLOWED, fault_injector=crash_at("after_state_applied"))
            service = CharacterActionService(ActionResolver(), kernel)
            with self.assertRaises(FaultInjectedCrash):
                service.execute(start, ACTION, action_instance_id="a-crash-s", world_seed="w", journal_context=CTX)
            recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
            receipt = CharacterRecoveryService(recovering).recover(context=CTX)
            self.assertEqual(receipt.replayed_events, 0)
            self.assertEqual(recovering.load_state()["character"], expected)

    def test_corrupt_tail_is_quarantined_and_normal_open_works_after_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = CharacterState("c-r", "R")
            kernel = PersistenceKernel(tmp, ALLOWED)
            CharacterActionService(ActionResolver(), kernel).execute(
                start, ACTION, action_instance_id="a-ok", world_seed="w", journal_context=CTX
            )
            with (Path(tmp) / "journal" / "events.jsonl").open("ab") as handle:
                handle.write(b"{broken-tail\n")
            with self.assertRaises(PersistenceError):
                PersistenceKernel(tmp, ALLOWED)
            recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
            receipt = CharacterRecoveryService(recovering).recover(context=CTX)
            self.assertIsNotNone(receipt.quarantined_path)
            self.assertTrue((Path(tmp) / receipt.quarantined_path).exists())
            self.assertTrue((Path(tmp) / "recovery" / "RECOVERY_RECEIPT.json").exists())
            reopened = PersistenceKernel(tmp, ALLOWED)
            self.assertIsNotNone(reopened.load_state())

    def test_invalid_record_shapes_are_quarantined_for_recovery(self):
        invalid_records = {
            "JSON-Liste": [],
            "fehlendes Pflichtfeld": {"sequence": 1},
            "nichtnumerische Sequenz": {
                "sequence": "2", "event_id": "bad-sequence", "event_type": "character.profile_updated",
                "previous_event_hash": "GENESIS", "event_hash": "hash", "payload": {},
            },
            "Payload mit falschem Typ": {
                "sequence": 2, "event_id": "bad-payload", "event_type": "character.profile_updated",
                "previous_event_hash": "GENESIS", "event_hash": "hash", "payload": [],
            },
        }
        for label, invalid_record in invalid_records.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                kernel = PersistenceKernel(tmp, ALLOWED)
                kernel.initialize_state({"character": CharacterState("c-r", "R").to_dict()})
                invalid_tail = (json.dumps(invalid_record) + "\n" + '{"ungeprüfter_rest": true}\n').encode("utf-8")
                with kernel.journal_path.open("ab") as handle:
                    handle.write(invalid_tail)

                with self.assertRaisesRegex(PersistenceError, "Journal-Datensatz ungültig in Zeile 1"):
                    PersistenceKernel(tmp, ALLOWED)
                recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
                receipt = CharacterRecoveryService(recovering).recover(context=CTX)

                self.assertIsNotNone(receipt.quarantined_path)
                self.assertEqual((Path(tmp) / receipt.quarantined_path).read_bytes(), invalid_tail)

    def test_snapshot_plus_journal_replay_recovers_corrupt_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = CharacterState("c-r", "R")
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterActionService(ActionResolver(), kernel)
            first = service.execute(start, ACTION, action_instance_id="snap-a1", world_seed="w", journal_context=CTX).resolved.character_after
            snapshot_id = kernel.create_snapshot("checkpoint")
            second_expected = service.execute(first, ACTION, action_instance_id="snap-a2", world_seed="w", journal_context=CTX).resolved.character_after.to_dict()
            (Path(tmp) / "state" / "current.json").write_text("{broken-state", encoding="utf-8")
            with self.assertRaises(PersistenceError):
                PersistenceKernel(tmp, ALLOWED)
            recovering = PersistenceKernel.open_for_recovery(tmp, ALLOWED)
            receipt = CharacterRecoveryService(recovering).recover(context=CTX)
            self.assertEqual(receipt.checkpoint_kind, "snapshot")
            self.assertEqual(receipt.checkpoint_sequence, int(snapshot_id.split("-")[1]))
            self.assertGreater(receipt.replayed_events, 0)
            self.assertEqual(recovering.load_state()["character"], second_expected)

    def test_fault_after_meta_commit_is_already_consistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = CharacterState("c-r", "R")
            kernel = PersistenceKernel(tmp, ALLOWED, fault_injector=crash_at("after_meta_committed"))
            service = CharacterActionService(ActionResolver(), kernel)
            with self.assertRaises(FaultInjectedCrash):
                service.execute(start, ACTION, action_instance_id="a-meta", world_seed="w", journal_context=CTX)
            reopened = PersistenceKernel(tmp, ALLOWED)
            receipt = CharacterRecoveryService(reopened).recover(context=CTX)
            self.assertEqual(receipt.status, "healthy")

    def test_profile_update_has_one_step_compensating_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            profiles = CharacterProfileService(kernel)
            start = CharacterState("c-r", "R", alias="Alt")
            changed = profiles.update(
                start,
                {"alias": "Neu", "additional_nicknames": ["Echo", "Impuls"], "motto": "Bass"},
                event_id="profile-1",
                transaction_id="tx-profile-1",
                context=CTX,
            )
            self.assertEqual(changed.alias, "Neu")
            self.assertEqual(changed.additional_nicknames, ["Echo", "Impuls"])
            undone = profiles.undo_last_profile_update(event_id="undo-profile-1", transaction_id="tx-undo-profile-1", context=CTX)
            self.assertEqual(undone.alias, "Alt")
            self.assertEqual(undone.additional_nicknames, [])
            self.assertEqual(undone.motto, "")
            last = kernel.last_transaction_records()[0]
            self.assertEqual(last["compensation_for"], "profile-1")
            with self.assertRaises(PersistenceError):
                profiles.undo_last_profile_update(event_id="undo-again", transaction_id="tx-undo-again", context=CTX)

    def test_profile_replay_restores_additional_nicknames(self):
        state = {"character": CharacterState("c-r", "R").to_dict()}
        replayed = replay_character_event(
            state,
            {"event_type": "character.profile_updated", "payload": {"new": {"additional_nicknames": ["Echo"]}}},
        )
        self.assertEqual(replayed["character"]["additional_nicknames"], ["Echo"])


if __name__ == "__main__":
    unittest.main()
