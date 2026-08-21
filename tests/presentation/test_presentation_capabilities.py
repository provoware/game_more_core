import tempfile
import unittest

from bunkerfrequenz.application.presentation_capabilities import get_presentation_capabilities
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ALLOWED = {"character.profile_updated"}
CTX = JournalContext(
    "2026-08-21T19:50:00+02:00",
    "session-cap",
    "player-cap",
    "character",
    "char.pppoppi",
    "command-cap",
    "presentation",
    "0.5.2-alpha.1",
    "char.pppoppi",
)


class PresentationCapabilitiesTest(unittest.TestCase):
    def test_fresh_confirmed_state_allows_edit_and_action_not_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            character = CharacterState("char.pppoppi", "PPPOPPI")
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({"character": character.to_dict()})

            self.assertEqual(
                get_presentation_capabilities(character, kernel),
                {
                    "can_edit_profile": True,
                    "can_undo_profile": False,
                    "can_execute_action": True,
                },
            )

    def test_profile_update_enables_one_safe_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            character = CharacterState("char.pppoppi", "PPPOPPI")
            kernel = PersistenceKernel(tmp, ALLOWED)
            changed = CharacterProfileService(kernel).update(
                character,
                {"alias": "Betonfunk"},
                event_id="profile-cap-1",
                transaction_id="tx-cap-1",
                context=CTX,
            )

            self.assertTrue(get_presentation_capabilities(changed, kernel)["can_undo_profile"])

    def test_compensation_disables_second_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            character = CharacterState("char.pppoppi", "PPPOPPI")
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterProfileService(kernel)
            service.update(
                character,
                {"motto": "Beton bleibt."},
                event_id="profile-cap-2",
                transaction_id="tx-cap-2",
                context=CTX,
            )
            restored = service.undo_last_profile_update(
                event_id="undo-cap-2",
                transaction_id="tx-undo-cap-2",
                context=CTX,
            )

            self.assertFalse(get_presentation_capabilities(restored, kernel)["can_undo_profile"])

    def test_missing_or_foreign_state_disables_all_capabilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            self.assertEqual(
                get_presentation_capabilities(None, kernel),
                {
                    "can_edit_profile": False,
                    "can_undo_profile": False,
                    "can_execute_action": False,
                },
            )
            confirmed = CharacterState("char.pppoppi", "PPPOPPI")
            kernel.initialize_state({"character": confirmed.to_dict()})
            foreign = CharacterState("char.vicky", "Vicky")
            self.assertFalse(any(get_presentation_capabilities(foreign, kernel).values()))


if __name__ == "__main__":
    unittest.main()
