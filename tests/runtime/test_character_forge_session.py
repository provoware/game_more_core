import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.character_forge_session import CharacterForgeSessionService
from bunkerfrequenz.application.presentation_capabilities import get_presentation_capabilities
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).resolve().parents[2]


class CharacterForgeSessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        action_manifest = json.loads((ROOT / "manifests/ACTION_MANIFEST.json").read_text(encoding="utf-8"))
        biography_manifest = json.loads((ROOT / "manifests/BIOGRAFIE_MANIFEST.json").read_text(encoding="utf-8"))
        journal_manifest = json.loads((ROOT / "manifests/JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
        cls.actions = {item["action_id"]: item for item in action_manifest["actions"]}
        cls.biography_policy = biography_manifest["action_candidate"]
        cls.allowed_events = set(journal_manifest["event_types"])

    def context(self, command_id: str = "unused") -> JournalContext:
        return JournalContext(
            "2026-08-21T23:35:00+02:00",
            "session-0.7.2",
            "player-0.7.2",
            "character",
            "char.pppoppi",
            command_id,
            "character_forge",
            "0.7.2-alpha.1",
            "char.pppoppi",
        )

    def test_action_autosave_safe_profile_undo_and_reload_form_one_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, self.allowed_events)
            profile_service = CharacterProfileService(kernel)
            action_service = CharacterActionService(
                ActionResolver(),
                kernel,
                biography_policy=self.biography_policy,
            )
            start = CharacterState(
                "char.pppoppi",
                "PPPOPPI",
                total_xp=195,
                skill_xp={"organisation": 68},
            )
            session = CharacterForgeSessionService(
                start,
                profile_service=profile_service,
                action_service=action_service,
                actions=self.actions,
                world_seed="world",
            )

            action_result = session.dispatch(
                {
                    "type": "action.execute",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-flow-action",
                    "action_id": "action.run_event",
                    "action_instance_id": "flow-action",
                },
                journal_context=self.context(),
                action_context={"event_plan_valid": True, "safety_requirements_met": True},
            )
            self.assertEqual(action_result.command_result.status, "confirmed")
            self.assertEqual((session.character.energy, session.character.stress), (72, 18))
            event_types = [event["event_type"] for event in action_result.confirmed_events]
            self.assertEqual(event_types[0], "character.resources_changed")
            self.assertIn("character.biography_entry_added", event_types)
            self.assertTrue(session.dirty_since_periodic_autosave)
            self.assertFalse(get_presentation_capabilities(session.character, kernel)["can_undo_profile"])

            not_due = session.autosave_if_due(
                seconds_since_last_save=59.9,
                autosave_id="flow-1",
                journal_context=self.context(),
            )
            self.assertEqual(not_due.status, "not_due")
            self.assertTrue(session.dirty_since_periodic_autosave)

            autosave = session.autosave_if_due(
                seconds_since_last_save=60.0,
                autosave_id="flow-1",
                journal_context=self.context(),
            )
            self.assertEqual(autosave.status, "committed")
            self.assertEqual(autosave.committed_event_ids, ("autosave:flow-1",))
            self.assertIsNotNone(autosave.snapshot_id)
            self.assertFalse(session.dirty_since_periodic_autosave)
            self.assertTrue((kernel.snapshot_dir / f"{autosave.snapshot_id}.json").is_file())

            profile_result = session.dispatch(
                {
                    "type": "profile.update",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-profile-after-action",
                    "event_id": "evt-profile-after-action",
                    "transaction_id": "tx-profile-after-action",
                    "changes": {"alias": "Betonfunk"},
                },
                journal_context=self.context(),
            )
            self.assertEqual(profile_result.command_result.status, "confirmed")
            self.assertEqual(session.character.alias, "Betonfunk")
            self.assertTrue(get_presentation_capabilities(session.character, kernel)["can_undo_profile"])

            undo_result = session.dispatch(
                {
                    "type": "profile.undo_last",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-undo-after-action",
                    "event_id": "evt-undo-after-action",
                    "transaction_id": "tx-undo-after-action",
                },
                journal_context=self.context(),
            )
            self.assertEqual(undo_result.command_result.status, "confirmed")
            self.assertEqual(session.character.alias, "")
            self.assertFalse(get_presentation_capabilities(session.character, kernel)["can_undo_profile"])

            before_reload = session.character.to_dict()
            reloaded = session.reload()
            self.assertEqual(reloaded.to_dict(), before_reload)
            self.assertEqual((reloaded.energy, reloaded.stress), (72, 18))


if __name__ == "__main__":
    unittest.main()
