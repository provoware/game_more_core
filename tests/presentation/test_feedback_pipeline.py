import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.command_dispatcher import dispatch_command
from bunkerfrequenz.application.presentation_events import get_confirmed_events
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel
from bunkerfrequenz.presentation import build_character_projection, build_confirmed_feedback


ROOT = Path(__file__).resolve().parents[2]
ACTION = {
    "action_id": "action.feedback_test",
    "category": "event",
    "risk_profile": "low",
    "skill_weights": {"technik": 1.0},
    "trait_evidence_weights": {"klangfokus": 1.0},
    "prerequisites": [],
}


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for name in (
        "skills.json",
        "traits.json",
        "trait_effects.json",
        "trait_consequences.json",
        "specializations.json",
        "stages.json",
        "feedback.json",
    ):
        catalog.update(load_json(f"content/de/ui/{name}"))
    return catalog


class ConfirmedFeedbackPipelineTest(unittest.TestCase):
    def test_confirmed_action_events_flow_to_feedback_and_projection_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal_types = set(load_json("manifests/JOURNAL_MANIFEST.json")["event_types"])
            kernel = PersistenceKernel(tmp, journal_types)
            action_service = CharacterActionService(ActionResolver(), kernel)
            profile_service = CharacterProfileService(kernel)
            character = CharacterState("char.pppoppi", "PPPOPPI")
            character.skill_xp["technik"] = 69
            context = JournalContext(
                "2026-08-21T19:50:00+02:00",
                "session-pipeline",
                "player-pipeline",
                "character",
                "char.pppoppi",
                "unused",
                "presentation",
                "0.5.2-alpha.1",
                "char.pppoppi",
            )
            command = {
                "type": "action.execute",
                "character_id": "char.pppoppi",
                "command_id": "cmd-pipeline",
                "action_id": ACTION["action_id"],
                "action_instance_id": "action-pipeline-1",
            }

            result = dispatch_command(
                command,
                character=character,
                profile_service=profile_service,
                action_service=action_service,
                actions={ACTION["action_id"]: ACTION},
                world_seed="pipeline-world",
                journal_context=context,
            )
            self.assertEqual(result.status, "confirmed")
            self.assertTrue(result.committed_event_ids)

            confirmed_records = get_confirmed_events(result.committed_event_ids, kernel)
            feedback = build_confirmed_feedback(
                confirmed_records,
                result.committed_event_ids,
                journal_event_types=journal_types,
                text_catalog=load_catalog(),
            )
            self.assertIn("skill_level_up", [item["kind"] for item in feedback])

            projection = build_character_projection(
                result.confirmed_state,
                confirmed_records,
                load_catalog(),
                feedback=feedback,
            )
            self.assertEqual(projection["feedback"], feedback)

            replay = dispatch_command(
                command,
                character=result.confirmed_state,
                profile_service=profile_service,
                action_service=action_service,
                actions={ACTION["action_id"]: ACTION},
                world_seed="pipeline-world",
                journal_context=context,
            )
            self.assertTrue(replay.idempotent_replay)
            self.assertEqual(replay.committed_event_ids, ())
            self.assertEqual(len(kernel.read_records()), len(confirmed_records))


if __name__ == "__main__":
    unittest.main()
