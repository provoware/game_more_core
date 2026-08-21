import unittest

from bunkerfrequenz.presentation.components import (
    BiographyTimeline,
    CharacterHeader,
    ProfileEditor,
    ProgressFeedback,
    SkillList,
    SpecializationCard,
    StatusSummary,
    TraitList,
)


OVERVIEW = {
    "display_name": "Mara",
    "alias": "Echo",
    "additional_nicknames": ["M"],
    "motto": "Weiter.",
    "level": 4,
    "total_xp": 250,
    "resonance_xp": 7,
    "resonance_rank": 1,
    "energy": 80,
    "stress": 12,
    "reputation": 3,
}


class RecordingAdapter:
    def __init__(self):
        self.commands = []

    def dispatch(self, command):
        self.commands.append(command)
        return "accepted"


class ComponentModelsTest(unittest.TestCase):
    def test_overview_components_map_only_their_fields(self):
        header = CharacterHeader().build(OVERVIEW, {"compact": True})
        status = StatusSummary().build(OVERVIEW)

        self.assertEqual(header["display_name"], "Mara")
        self.assertEqual(header["additional_nicknames"], ["M"])
        self.assertTrue(header["compact"])
        self.assertEqual(status["level"], 4)
        self.assertEqual(status["energy"], 80)
        self.assertNotIn("display_name", status)

    def test_list_components_keep_empty_lists_empty(self):
        self.assertEqual(SkillList().build([], {})["items"], [])
        self.assertEqual(TraitList().build([], {})["items"], [])
        self.assertEqual(BiographyTimeline().build([], {})["entries"], [])
        self.assertEqual(ProgressFeedback().build([], {})["items"], [])

    def test_missing_optional_specialization_stays_missing(self):
        model = SpecializationCard().build(None, {})
        self.assertIsNone(model["specialization"])

    def test_missing_text_key_remains_visible(self):
        skills = [{"skill_id": "technik", "label_key": "skill.technik", "value": 30}]
        model = SkillList().build(skills, {})
        self.assertEqual(model["items"][0]["label"], "skill.technik")

    def test_local_filter_and_dismissal_do_not_change_input(self):
        biography = [
            {"entry_id": "b1", "category": "work", "title_key": "bio.work"},
            {"entry_id": "b2", "category": "private", "title_key": "bio.private"},
        ]
        feedback = [
            {"feedback_id": "f1", "title_key": "feedback.one", "detail_keys": []},
            {"feedback_id": "f2", "title_key": "feedback.two", "detail_keys": []},
        ]

        timeline = BiographyTimeline().build(biography, {}, {"category": "work"})
        visible_feedback = ProgressFeedback().build(feedback, {}, {"dismissed_feedback_ids": ["f1"]})

        self.assertEqual([item["entry_id"] for item in timeline["entries"]], ["b1"])
        self.assertEqual([item["feedback_id"] for item in visible_feedback["items"]], ["f2"])
        self.assertNotIn("title", biography[0])
        self.assertNotIn("title", feedback[0])

    def test_profile_editor_maps_draft_and_dispatches_changed_fields(self):
        editor = ProfileEditor()
        adapter = RecordingAdapter()
        model = editor.build(
            OVERVIEW,
            {"can_edit_profile": True, "can_undo_profile": False},
            {"draft": {"alias": "Signal"}},
        )

        result = editor.submit(
            OVERVIEW,
            {"draft": {"alias": "Signal", "motto": "Weiter."}},
            adapter,
            character_id="c-1",
            command_id="cmd-1",
            event_id="evt-1",
            transaction_id="tx-1",
        )

        self.assertEqual(model["values"]["alias"], "Signal")
        self.assertTrue(model["can_submit"])
        self.assertEqual(result, "accepted")
        self.assertEqual(adapter.commands[0]["changes"], {"alias": "Signal"})

    def test_unchanged_profile_input_creates_no_command(self):
        adapter = RecordingAdapter()
        result = ProfileEditor().submit(
            OVERVIEW,
            {"draft": {"display_name": "Mara", "additional_nicknames": ["M"]}},
            adapter,
            character_id="c-1",
            command_id="cmd-1",
            event_id="evt-1",
            transaction_id="tx-1",
        )

        self.assertIsNone(result)
        self.assertEqual(adapter.commands, [])


if __name__ == "__main__":
    unittest.main()
