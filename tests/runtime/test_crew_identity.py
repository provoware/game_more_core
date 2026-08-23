import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.application.recovery_service import replay_character_event
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.crew_identity import default_crew_identity
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T17:00:00+02:00",
        "session-crew-identity",
        "player-local",
        "character",
        "char.local",
        command_id,
        "crew-identity-test",
        "0.8.8-a",
        "char.local",
    )


class CrewIdentityTests(unittest.TestCase):
    def test_legacy_character_gets_stable_neutral_identity_without_input_mutation(self):
        legacy = CharacterState(character_id="char.local", display_name="Local").to_dict()
        legacy.pop("crew_identity")
        loaded = CharacterState.from_dict(legacy)

        self.assertEqual(loaded.crew_identity, default_crew_identity())
        self.assertNotIn("crew_identity", legacy)

    def test_profile_update_journals_compact_identity_and_replay_restores_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterProfileService(kernel)
            character = CharacterState(character_id="char.local", display_name="Local")
            identity = {
                "mode": "logo",
                "style": "diagonal",
                "symbol": "bolt",
                "primary_color_id": "electric_blue",
                "secondary_color_id": "black",
                "accent_color_id": "warning_yellow",
                "mark": "BF+",
            }

            updated = service.update(
                character,
                {"crew_identity": identity},
                event_id="crew-profile:001",
                transaction_id="tx:crew-profile:001",
                context=context("crew-profile"),
            )
            record = kernel.read_records()[0]
            replayed = replay_character_event({"character": character.to_dict()}, record)

            self.assertEqual(updated.crew_identity, identity)
            self.assertEqual(record["event_type"], "character.profile_updated")
            self.assertEqual(record["payload"]["new"]["crew_identity"], identity)
            self.assertEqual(replayed["character"]["crew_identity"], identity)
            self.assertNotIn("image", record["payload"]["new"]["crew_identity"])
            self.assertNotIn("data", record["payload"]["new"]["crew_identity"])

    def test_unknown_ids_and_image_blob_fields_fail_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterProfileService(kernel)
            character = CharacterState(character_id="char.local", display_name="Local")
            bad_identity = default_crew_identity()
            bad_identity["image_data"] = "data:image/png;base64,AAAA"

            with self.assertRaisesRegex(ValueError, "Unbekannte Crew-Identitätsfelder"):
                service.update(
                    character,
                    {"crew_identity": bad_identity},
                    event_id="crew-profile:bad",
                    transaction_id="tx:crew-profile:bad",
                    context=context("crew-profile-bad"),
                )
            self.assertEqual(kernel.read_records(), ())
            self.assertIsNone(kernel.load_state())


if __name__ == "__main__":
    unittest.main()
