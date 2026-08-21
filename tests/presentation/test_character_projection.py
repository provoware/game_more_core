import tempfile
import unittest

from bunkerfrequenz.application.presentation_capabilities import get_presentation_capabilities
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel
from bunkerfrequenz.presentation.character_projection import build_character_projection


ALLOWED = {"character.profile_updated"}
CTX = JournalContext(
    "2026-08-21T16:20:00+02:00", "s-p", "p-p", "character", "c-p",
    "cmd-p", "runtime", "0.5.2-alpha.1", "c-p",
)


class CharacterProjectionCapabilitiesTest(unittest.TestCase):
    def test_fresh_loaded_state_allows_edit_and_action_but_not_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            character = CharacterState("c-p", "Pulse")
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({"character": character.to_dict()})

            capabilities = get_presentation_capabilities(character, kernel)
            projection = build_character_projection(character, capabilities)

            self.assertEqual(capabilities, {
                "can_edit_profile": True,
                "can_undo_profile": False,
                "can_execute_action": True,
            })
            self.assertEqual(projection["capabilities"], capabilities)
            self.assertIsNot(projection["capabilities"], capabilities)

    def test_last_profile_update_can_be_undone(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            changed = CharacterProfileService(kernel).update(
                CharacterState("c-p", "Pulse"), {"alias": "Echo"},
                event_id="profile-1", transaction_id="tx-profile-1", context=CTX,
            )

            self.assertTrue(get_presentation_capabilities(changed, kernel)["can_undo_profile"])

    def test_compensated_profile_update_cannot_be_undone_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            service = CharacterProfileService(kernel)
            service.update(
                CharacterState("c-p", "Pulse"), {"alias": "Echo"},
                event_id="profile-1", transaction_id="tx-profile-1", context=CTX,
            )
            restored = service.undo_last_profile_update(
                event_id="undo-profile-1", transaction_id="tx-undo-profile-1", context=CTX,
            )

            self.assertFalse(get_presentation_capabilities(restored, kernel)["can_undo_profile"])

    def test_missing_state_disables_all_capabilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            capabilities = get_presentation_capabilities(None, PersistenceKernel(tmp, ALLOWED))

            self.assertEqual(capabilities, {
                "can_edit_profile": False,
                "can_undo_profile": False,
                "can_execute_action": False,
            })


if __name__ == "__main__":
    unittest.main()
