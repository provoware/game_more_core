import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.command_dispatcher import dispatch_command
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ACTION = {
    "action_id": "action.soundcheck",
    "category": "event",
    "risk_profile": "medium",
    "skill_weights": {"technik": 0.5, "musik": 0.3, "konzentration": 0.2},
    "trait_evidence_weights": {"klangfokus": 0.6, "detailmensch": 0.4},
    "prerequisites": [],
}
ALLOWED = {
    "character.profile_updated",
    "character.skill_xp_gained",
    "character.skill_level_up",
    "character.trait_evidence_gained",
    "character.trait_unlocked",
    "character.trait_tier_up",
    "character.specialization_changed",
    "character.level_up",
    "character.resonance_xp_gained",
    "character.resonance_rank_up",
}
CTX = JournalContext(
    "2026-08-21T19:50:00+02:00",
    "session-dispatch",
    "player-dispatch",
    "character",
    "char.pppoppi",
    "unused",
    "presentation",
    "0.5.2-alpha.1",
    "char.pppoppi",
)


class CommandDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.profile_service = CharacterProfileService(self.kernel)
        self.action_service = CharacterActionService(ActionResolver(), self.kernel)
        self.character = CharacterState("char.pppoppi", "PPPOPPI")

    def dispatch(self, command, *, character=None):
        return dispatch_command(
            command,
            character=character or self.character,
            profile_service=self.profile_service,
            action_service=self.action_service,
            actions={ACTION["action_id"]: ACTION},
            world_seed="world-fixed",
            journal_context=CTX,
        )

    def test_rejects_unknown_command_and_character_mismatch_without_write(self):
        unknown = self.dispatch({"type": "profile.delete"})
        self.assertEqual((unknown.status, unknown.error_code), ("rejected", "unknown_command"))

        mismatch = self.dispatch({
            "type": "profile.update",
            "character_id": "char.vicky",
            "command_id": "cmd-x",
            "event_id": "evt-x",
            "transaction_id": "tx-x",
            "changes": {"alias": "X"},
        })
        self.assertEqual(mismatch.error_code, "character_mismatch")
        self.assertEqual(self.kernel.read_records(), ())

    def test_profile_update_preserves_ids_and_is_idempotent(self):
        command = {
            "type": "profile.update",
            "character_id": "char.pppoppi",
            "command_id": "cmd-profile",
            "event_id": "evt-profile",
            "transaction_id": "tx-profile",
            "changes": {"alias": "Betonfunk"},
        }

        first = self.dispatch(command)
        second = self.dispatch(command)

        self.assertEqual(first.status, "confirmed")
        self.assertEqual(first.confirmed_state.alias, "Betonfunk")
        self.assertEqual(first.committed_event_ids, ("evt-profile",))
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.committed_event_ids, ())
        records = self.kernel.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(
            (records[0]["command_id"], records[0]["event_id"], records[0]["transaction_id"]),
            ("cmd-profile", "evt-profile", "tx-profile"),
        )

    def test_profile_undo_is_idempotent_for_repeated_same_command(self):
        update = self.dispatch({
            "type": "profile.update",
            "character_id": "char.pppoppi",
            "command_id": "cmd-update",
            "event_id": "evt-update",
            "transaction_id": "tx-update",
            "changes": {"motto": "Bass."},
        })
        undo_command = {
            "type": "profile.undo_last",
            "character_id": "char.pppoppi",
            "command_id": "cmd-undo",
            "event_id": "evt-undo",
            "transaction_id": "tx-undo",
        }

        first = self.dispatch(undo_command, character=update.confirmed_state)
        second = self.dispatch(undo_command, character=first.confirmed_state)

        self.assertEqual(first.status, "confirmed")
        self.assertEqual(first.confirmed_state.motto, "")
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.committed_event_ids, ())
        self.assertEqual(len(self.kernel.read_records()), 2)

    def test_action_execute_uses_action_instance_for_existing_runtime_idempotency(self):
        command = {
            "type": "action.execute",
            "character_id": "char.pppoppi",
            "command_id": "cmd-action",
            "action_id": ACTION["action_id"],
            "action_instance_id": "act-001",
        }

        first = self.dispatch(command)
        second = self.dispatch(command, character=first.confirmed_state)

        self.assertEqual(first.status, "confirmed")
        self.assertTrue(first.committed_event_ids)
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.committed_event_ids, ())
        self.assertEqual(self.kernel.read_records()[0]["command_id"], "cmd-action")

    def test_rejects_untrusted_or_invalid_ui_parameters(self):
        bad_profile = self.dispatch({
            "type": "profile.update",
            "character_id": "char.pppoppi",
            "command_id": "cmd-bad",
            "event_id": "evt-bad",
            "transaction_id": "tx-bad",
            "changes": {"level": 99},
        })
        self.assertEqual(bad_profile.error_code, "invalid_profile_fields")

        bad_selection = self.dispatch({
            "type": "action.execute",
            "character_id": "char.pppoppi",
            "command_id": "cmd-action-bad",
            "action_id": ACTION["action_id"],
            "action_instance_id": "act-bad",
            "selected_skill": " ",
        })
        self.assertEqual(bad_selection.error_code, "invalid_selected_skill")
        self.assertEqual(self.kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
