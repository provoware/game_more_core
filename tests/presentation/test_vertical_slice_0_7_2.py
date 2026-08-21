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
from bunkerfrequenz.presentation import (
    PresentationState,
    build_a3_cinematic_forge,
    build_a4_ops_deck,
    build_character_projection,
    build_confirmed_feedback,
)


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for path in sorted((ROOT / "content/de/ui").glob("*.json")):
        catalog.update(json.loads(path.read_text(encoding="utf-8")))
    return catalog


class VerticalSlice072Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.action_manifest = load_json("manifests/ACTION_MANIFEST.json")
        cls.biography_manifest = load_json("manifests/BIOGRAFIE_MANIFEST.json")
        cls.journal_manifest = load_json("manifests/JOURNAL_MANIFEST.json")
        cls.ui_manifest = load_json("manifests/UI_MANIFEST.json")
        cls.animation_manifest = load_json("manifests/ANIMATION_MANIFEST.json")
        cls.catalog = load_catalog()
        cls.actions = {item["action_id"]: item for item in cls.action_manifest["actions"]}
        cls.allowed_events = set(cls.journal_manifest["event_types"])

    def context(self) -> JournalContext:
        return JournalContext(
            "2026-08-21T23:40:00+02:00",
            "session-vertical-0.7.2",
            "player-vertical-0.7.2",
            "character",
            "char.pppoppi",
            "unused",
            "character_forge",
            "0.7.2-alpha.1",
            "char.pppoppi",
        )

    def test_complete_character_forge_vertical_slice(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, self.allowed_events)
            profile_service = CharacterProfileService(kernel)
            action_service = CharacterActionService(
                ActionResolver(),
                kernel,
                biography_policy=self.biography_manifest["action_candidate"],
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

            action = session.dispatch(
                {
                    "type": "action.execute",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-vertical-action",
                    "action_id": "action.run_event",
                    "action_instance_id": "flow-action",
                },
                journal_context=self.context(),
                action_context={"event_plan_valid": True, "safety_requirements_met": True},
            )
            self.assertEqual(action.command_result.status, "confirmed")
            action_types = [event["event_type"] for event in action.confirmed_events]
            self.assertEqual(action_types[0], "character.resources_changed")
            self.assertIn("character.skill_level_up", action_types)
            self.assertIn("character.level_up", action_types)
            self.assertIn("character.biography_entry_added", action_types)
            self.assertEqual((session.character.energy, session.character.stress), (72, 18))

            feedback = build_confirmed_feedback(
                action.confirmed_events,
                action.command_result.committed_event_ids,
                journal_event_types=self.allowed_events,
                text_catalog=self.catalog,
            )
            feedback_kinds = {item["kind"] for item in feedback}
            self.assertIn("skill_level_up", feedback_kinds)
            self.assertIn("level_up", feedback_kinds)

            autosave = session.autosave_if_due(
                seconds_since_last_save=60,
                autosave_id="vertical-1",
                journal_context=self.context(),
            )
            self.assertEqual(autosave.status, "committed")
            self.assertIsNotNone(autosave.snapshot_id)

            profile = session.dispatch(
                {
                    "type": "profile.update",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-vertical-profile",
                    "event_id": "evt-vertical-profile",
                    "transaction_id": "tx-vertical-profile",
                    "changes": {"motto": "Beton hört mit."},
                },
                journal_context=self.context(),
            )
            self.assertEqual(profile.command_result.status, "confirmed")
            self.assertTrue(get_presentation_capabilities(session.character, kernel)["can_undo_profile"])

            undo = session.dispatch(
                {
                    "type": "profile.undo_last",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-vertical-undo",
                    "event_id": "evt-vertical-undo",
                    "transaction_id": "tx-vertical-undo",
                },
                journal_context=self.context(),
            )
            self.assertEqual(undo.command_result.status, "confirmed")
            self.assertEqual(session.character.motto, "")

            reloaded = session.reload()
            self.assertEqual(reloaded.motto, "")
            self.assertEqual((reloaded.energy, reloaded.stress), (72, 18))

            records = kernel.read_records()
            capabilities = get_presentation_capabilities(reloaded, kernel)
            projection = build_character_projection(
                reloaded,
                records,
                self.catalog,
                capabilities=capabilities,
                feedback=feedback,
            )
            state = PresentationState()
            a4 = build_a4_ops_deck(
                projection,
                state,
                self.ui_manifest,
                self.catalog,
            )
            a3 = build_a3_cinematic_forge(
                projection,
                state,
                self.ui_manifest,
                self.animation_manifest,
                self.catalog,
            )

            for component in ("StatusSummary", "BiographyTimeline", "ProgressFeedback"):
                self.assertEqual(a4["components"][component], a3["components"][component])
            self.assertEqual(a4["components"]["StatusSummary"]["data"]["energy"], 72)
            self.assertEqual(a4["components"]["StatusSummary"]["data"]["stress"], 18)
            self.assertEqual(len(a4["components"]["BiographyTimeline"]["data"]), 1)
            self.assertGreaterEqual(len(a4["components"]["ProgressFeedback"]["data"]), 2)


if __name__ == "__main__":
    unittest.main()
