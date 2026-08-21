import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation import (
    VIEW_IDS,
    PresentationState,
    PresentationStateError,
    dismiss_feedback,
    filter_biography,
    select_view,
    visible_feedback,
)


ROOT = Path(__file__).resolve().parents[2]


def biography_categories() -> set[str]:
    manifest = json.loads((ROOT / "manifests/BIOGRAFIE_MANIFEST.json").read_text(encoding="utf-8"))
    return set(manifest["categories"])


class PresentationStateTest(unittest.TestCase):
    def test_view_catalog_matches_contract(self):
        self.assertEqual(VIEW_IDS, {"overview", "skills_traits", "biography"})

    def test_transitions_return_new_immutable_states(self):
        initial = PresentationState()
        viewed = select_view(initial, "biography")
        filtered = filter_biography(viewed, "major_success", allowed_categories=biography_categories())
        dismissed = dismiss_feedback(filtered, "feedback:abc")

        self.assertIsNot(initial, viewed)
        self.assertIsNot(viewed, filtered)
        self.assertIsNot(filtered, dismissed)
        self.assertEqual(initial, PresentationState())
        self.assertEqual(dismissed.selected_view, "biography")
        self.assertEqual(dismissed.biography_filter, "major_success")
        self.assertEqual(dismissed.dismissed_feedback_ids, {"feedback:abc"})
        with self.assertRaises((AttributeError, TypeError)):
            dismissed.selected_view = "overview"

    def test_biography_filter_uses_manifest_categories_not_private_copy(self):
        categories = biography_categories()
        self.assertIn("rare_random_event", categories)
        state = filter_biography(PresentationState(), "rare_random_event", allowed_categories=categories)
        self.assertEqual(state.biography_filter, "rare_random_event")
        with self.assertRaises(PresentationStateError) as caught:
            filter_biography(state, "made_up_category", allowed_categories=categories)
        self.assertEqual((caught.exception.code, caught.exception.field), ("invalid_biography_filter", "category"))

    def test_local_transitions_do_not_touch_character_or_source_feedback(self):
        character = CharacterState("char.pppoppi", "PPPOPPI")
        before = character.to_dict()
        feedback = [
            {"feedback_id": "feedback:keep", "kind": "level_up"},
            {"feedback_id": "feedback:hide", "kind": "trait_unlocked"},
        ]
        state = dismiss_feedback(PresentationState(), "feedback:hide")
        visible = visible_feedback(feedback, state)

        self.assertEqual(character.to_dict(), before)
        self.assertEqual([item["feedback_id"] for item in visible], ["feedback:keep"])
        visible[0]["kind"] = "changed"
        self.assertEqual(feedback[0]["kind"], "level_up")

    def test_invalid_local_ids_have_machine_readable_errors(self):
        cases = (
            (lambda: select_view(PresentationState(), "ranking"), "invalid_view_id", "view_id"),
            (lambda: filter_biography(PresentationState(), "unknown", allowed_categories=biography_categories()), "invalid_biography_filter", "category"),
            (lambda: dismiss_feedback(PresentationState(), ""), "invalid_feedback_id", "feedback_id"),
            (lambda: PresentationState(dismissed_feedback_ids="feedback:bad"), "invalid_feedback_id", "feedback_id"),
            (lambda: PresentationState(reduced_motion="yes"), "invalid_reduced_motion", "reduced_motion"),
        )
        for operation, code, field in cases:
            with self.subTest(code=code), self.assertRaises(PresentationStateError) as caught:
                operation()
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(caught.exception.field, field)


if __name__ == "__main__":
    unittest.main()
