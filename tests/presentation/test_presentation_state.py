import json
from pathlib import Path
import unittest
from unittest.mock import Mock

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation import (
    BIOGRAPHY_FILTERS,
    VIEW_IDS,
    PresentationState,
    PresentationStateError,
    dismiss_feedback,
    filter_biography,
    select_view,
)


class PresentationStateTest(unittest.TestCase):
    def test_catalogs_match_contracts(self):
        manifest = json.loads(Path("manifests/BIOGRAFIE_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(VIEW_IDS, {"overview", "skills_traits", "biography"})
        self.assertEqual(BIOGRAPHY_FILTERS, set(manifest["categories"]) | {"all"})

    def test_transitions_return_new_immutable_states(self):
        initial = PresentationState()
        viewed = select_view(initial, "biography")
        filtered = filter_biography(viewed, "major_success")
        dismissed = dismiss_feedback(filtered, "feedback.action-1")

        self.assertIsNot(initial, viewed)
        self.assertIsNot(viewed, filtered)
        self.assertIsNot(filtered, dismissed)
        self.assertEqual(initial, PresentationState())
        self.assertEqual(dismissed.selected_view, "biography")
        self.assertEqual(dismissed.biography_filter, "major_success")
        self.assertEqual(dismissed.dismissed_feedback_ids, {"feedback.action-1"})
        with self.assertRaises((AttributeError, TypeError)):
            dismissed.selected_view = "overview"

    def test_transitions_do_not_touch_character_journal_or_kernel(self):
        character = CharacterState("c-1", "Test")
        character_before = character.to_dict()
        journal = [{"event_id": "event-1"}]
        journal_before = [dict(record) for record in journal]
        kernel = Mock()

        state = select_view(PresentationState(), "skills_traits")
        state = filter_biography(state, "trait")
        dismiss_feedback(state, "feedback-1")

        self.assertEqual(character.to_dict(), character_before)
        self.assertEqual(journal, journal_before)
        kernel.assert_not_called()
        self.assertEqual(kernel.method_calls, [])

    def test_invalid_ids_have_machine_readable_errors(self):
        cases = (
            (lambda: select_view(PresentationState(), "ranking"), "invalid_view_id", "view_id"),
            (lambda: filter_biography(PresentationState(), "unknown"), "invalid_category", "category"),
            (lambda: dismiss_feedback(PresentationState(), ""), "invalid_feedback_id", "feedback_id"),
            (lambda: PresentationState(dismissed_feedback_ids="feedback-1"), "invalid_feedback_id", "feedback_id"),
        )
        for operation, code, field in cases:
            with self.subTest(code=code), self.assertRaises(PresentationStateError) as caught:
                operation()
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(caught.exception.field, field)
            self.assertEqual(str(caught.exception), code)


if __name__ == "__main__":
    unittest.main()
