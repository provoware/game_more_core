import unittest

from bunkerfrequenz.presentation import (
    COMPONENT_NAMES,
    PresentationState,
    build_components,
    build_profile_editor,
    build_progress_feedback,
)


def projection() -> dict:
    return {
        "meta": {"projection_version": "0.6", "character_id": "char.pppoppi"},
        "overview": {
            "display_name": "PPPOPPI",
            "alias": "Betonfunk",
            "additional_nicknames": ["P"],
            "motto": "Bass bleibt.",
            "level": 12,
            "total_xp": 1234,
            "resonance_xp": 0,
            "resonance_rank": 0,
            "energy": 73,
            "stress": 21,
            "reputation": 9,
        },
        "top_skills": [],
        "skills": [
            {
                "skill_id": "skill.technik",
                "label_key": "skill.technik.label",
                "value": 24,
                "xp": 12,
                "xp_to_next": 100,
                "progress_percent": 12,
                "trend": None,
            }
        ],
        "traits": [
            {
                "trait_id": "trait.pppoppi.krisenfest",
                "label_key": "trait.pppoppi.krisenfest.label",
                "tier": 1,
                "evidence": 220.0,
                "next_tier": 2,
                "progress_percent": 0,
                "effect_key": "trait.effect.krisenfest",
                "consequence_key": "trait.consequence.krisenfest",
            }
        ],
        "specialization": None,
        "biography": [
            {
                "entry_id": "bio-1",
                "event_id": "evt-1",
                "category": "trait",
                "title_key": "bio.trait.title",
                "body_key": "bio.trait.body",
                "placeholders": {},
                "sequence": 1,
            },
            {
                "entry_id": "bio-2",
                "event_id": "evt-2",
                "category": "major_success",
                "title_key": "bio.success.title",
                "body_key": "bio.success.body",
                "placeholders": {},
                "sequence": 2,
            },
        ],
        "capabilities": {
            "can_edit_profile": True,
            "can_undo_profile": True,
            "can_execute_action": True,
        },
        "feedback": [
            {"feedback_id": "feedback:keep", "kind": "level_up", "title_key": "feedback.keep"},
            {"feedback_id": "feedback:hide", "kind": "trait_unlocked", "title_key": "feedback.hide"},
        ],
    }


class SharedComponentsTest(unittest.TestCase):
    def test_builds_exactly_the_eight_shared_components_in_contract_order(self):
        components = build_components(projection(), PresentationState())
        self.assertEqual(tuple(components), COMPONENT_NAMES)
        self.assertEqual(
            COMPONENT_NAMES,
            (
                "CharacterHeader",
                "StatusSummary",
                "SkillList",
                "TraitList",
                "SpecializationCard",
                "BiographyTimeline",
                "ProfileEditor",
                "ProgressFeedback",
            ),
        )

    def test_components_are_detached_from_projection_input(self):
        source = projection()
        components = build_components(source, PresentationState())

        components["CharacterHeader"]["data"]["additional_nicknames"].append("changed")
        components["SkillList"]["data"][0]["value"] = 99
        components["ProfileEditor"]["data"]["fields"][0]["value"] = "changed"

        self.assertEqual(source["overview"]["additional_nicknames"], ["P"])
        self.assertEqual(source["skills"][0]["value"], 24)
        self.assertEqual(source["overview"]["display_name"], "PPPOPPI")

    def test_biography_filter_and_feedback_dismiss_apply_inside_component_data(self):
        state = PresentationState(
            biography_filter="trait",
            dismissed_feedback_ids={"feedback:hide"},
        )
        components = build_components(projection(), state)

        self.assertEqual(
            [item["entry_id"] for item in components["BiographyTimeline"]["data"]],
            ["bio-1"],
        )
        self.assertEqual(
            [item["feedback_id"] for item in components["ProgressFeedback"]["data"]],
            ["feedback:keep"],
        )

    def test_profile_editor_describes_only_existing_central_dispatcher_commands(self):
        editor = build_profile_editor(
            projection()["overview"],
            {"can_edit_profile": True, "can_undo_profile": False},
        )
        save, undo = editor["actions"]

        self.assertEqual(save["command_route"], "application.command_dispatcher.dispatch_command")
        self.assertEqual(save["command_type"], "profile.update")
        self.assertEqual(
            save["allowed_change_fields"],
            ["display_name", "alias", "additional_nicknames", "motto"],
        )
        self.assertTrue(save["enabled"])
        self.assertEqual(undo["command_route"], "application.command_dispatcher.dispatch_command")
        self.assertEqual(undo["command_type"], "profile.undo_last")
        self.assertFalse(undo["enabled"])

    def test_optional_empty_sections_remain_empty_instead_of_inventing_data(self):
        source = projection()
        source["traits"] = []
        source["specialization"] = None
        source["biography"] = []
        source["feedback"] = []
        components = build_components(source, PresentationState())

        self.assertTrue(components["TraitList"]["empty"])
        self.assertEqual(components["TraitList"]["data"], [])
        self.assertTrue(components["SpecializationCard"]["empty"])
        self.assertIsNone(components["SpecializationCard"]["data"])
        self.assertTrue(components["BiographyTimeline"]["empty"])
        self.assertTrue(components["ProgressFeedback"]["empty"])

    def test_reduced_motion_changes_only_component_presentation_mode(self):
        source = projection()["feedback"]
        regular = build_progress_feedback(source, PresentationState())
        reduced = build_progress_feedback(source, PresentationState(reduced_motion=True))

        self.assertEqual(regular["data"], reduced["data"])
        self.assertEqual(regular["presentation"]["motion_mode"], "animated")
        self.assertEqual(reduced["presentation"]["motion_mode"], "static")
        self.assertEqual(source[0]["kind"], "level_up")


if __name__ == "__main__":
    unittest.main()
