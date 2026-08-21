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
    "character.profile_updated", "character.skill_xp_gained", "character.skill_level_up",
    "character.trait_evidence_gained", "character.trait_unlocked", "character.trait_tier_up",
    "character.specialization_changed", "character.level_up", "character.resonance_xp_gained",
    "character.resonance_rank_up",
}
CTX = JournalContext(
    "2026-08-21T16:00:00+02:00", "s-1", "p-1", "character", "c-1",
    "unused", "presentation", "0.5.2-alpha.1", "c-1",
)


class CommandDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.profiles = CharacterProfileService(self.kernel)
        self.actions = CharacterActionService(ActionResolver(), self.kernel)
        self.character = CharacterState("c-1", "Test")

    def dispatch(self, command):
        return dispatch_command(
            command,
            character=self.character,
            profile_service=self.profiles,
            action_service=self.actions,
            actions={ACTION["action_id"]: ACTION},
            world_seed="world-fixed",
            journal_context=CTX,
        )

    def test_rejects_unknown_command(self):
        result = self.dispatch({"type": "profile.delete"})
        self.assertEqual((result.status, result.error_code), ("rejected", "unknown_command"))
        self.assertEqual(self.kernel.read_records(), ())

    def test_rejects_disallowed_profile_field(self):
        result = self.dispatch({
            "type": "profile.update", "character_id": "c-1", "command_id": "cmd-1",
            "event_id": "event-1", "transaction_id": "tx-1", "changes": {"level": 2},
        })
        self.assertEqual(result.error_code, "invalid_profile_fields")
        self.assertEqual(self.kernel.read_records(), ())

    def test_rejects_empty_required_ids(self):
        base = {"type": "profile.update", "character_id": "c-1", "command_id": "cmd-1",
                "event_id": "event-1", "transaction_id": "tx-1", "changes": {"alias": "Echo"}}
        for field in ("character_id", "command_id", "event_id", "transaction_id"):
            command = dict(base)
            command[field] = " "
            with self.subTest(field=field):
                self.assertTrue(self.dispatch(command).error_code.startswith("invalid_"))
        action = {"type": "action.execute", "character_id": "c-1", "command_id": "cmd-a",
                  "action_id": ACTION["action_id"], "action_instance_id": ""}
        self.assertEqual(self.dispatch(action).error_code, "invalid_action_instance_id")
        self.assertEqual(self.kernel.read_records(), ())

    def test_dispatches_profile_update_and_action(self):
        profile = self.dispatch({
            "type": "profile.update", "character_id": "c-1", "command_id": "cmd-profile",
            "event_id": "event-profile", "transaction_id": "tx-profile", "changes": {"alias": "Echo"},
        })
        self.assertEqual(profile.status, "confirmed")
        self.assertEqual(profile.projection["alias"], "Echo")
        current = CharacterState.from_dict(profile.projection)
        action = dispatch_command(
            {"type": "action.execute", "character_id": "c-1", "command_id": "cmd-action",
             "action_id": ACTION["action_id"], "action_instance_id": "action-1"},
            character=current, profile_service=self.profiles, action_service=self.actions,
            actions={ACTION["action_id"]: ACTION}, world_seed="world-fixed", journal_context=CTX,
        )
        self.assertEqual(action.status, "confirmed")
        self.assertTrue(action.feedback)
        self.assertEqual(self.kernel.read_records()[-1]["command_id"], "cmd-action")

    def test_repeated_command_keeps_ids_and_projection(self):
        command = {
            "type": "profile.update", "character_id": "c-1", "command_id": "cmd-repeat",
            "event_id": "event-repeat", "transaction_id": "tx-repeat", "changes": {"motto": "Bass"},
        }
        first = self.dispatch(command)
        second = self.dispatch(command)
        self.assertEqual(second, first)
        records = self.kernel.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(
            (records[0]["command_id"], records[0]["event_id"], records[0]["transaction_id"]),
            ("cmd-repeat", "event-repeat", "tx-repeat"),
        )


if __name__ == "__main__":
    unittest.main()
