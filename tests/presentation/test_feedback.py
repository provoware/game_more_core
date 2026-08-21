import unittest

from bunkerfrequenz.presentation import build_confirmed_feedback


class ConfirmedFeedbackTest(unittest.TestCase):
    def test_supports_only_catalogued_progress_events(self):
        supported = (
            "character.level_up",
            "character.skill_level_up",
            "character.trait_unlocked",
            "character.trait_tier_up",
            "character.specialization_changed",
            "character.resonance_rank_up",
        )

        for event_type in supported:
            with self.subTest(event_type=event_type):
                event = self.event(event_type, event_type, old=1, new=2)
                feedback = build_confirmed_feedback([event], (event_type,))
                self.assertEqual(len(feedback), 1)

    def test_preserves_supported_event_order(self):
        events = [
            self.event("evt-2", "character.trait_unlocked", trait_id="focused", old_tier=0, new_tier=1),
            self.event("evt-1", "character.level_up", old=1, new=2),
        ]

        feedback = build_confirmed_feedback(events, ("evt-1", "evt-2"))

        self.assertEqual([item["kind"] for item in feedback], ["trait_unlocked", "level_up"])

    def test_ignores_unknown_and_unconfirmed_events(self):
        events = [
            self.event("unknown", "character.skill_xp_gained", amount=5),
            self.event("clicked", "character.level_up", old=1, new=2),
        ]

        self.assertEqual(build_confirmed_feedback(events, ()), [])
        self.assertEqual(build_confirmed_feedback(events, ("unknown", "clicked-later")), [])

    def test_feedback_id_is_stable_and_derived_from_confirmed_event_id(self):
        first = self.event("evt-stable", "character.resonance_rank_up", old=1, new=2)
        changed_payload = self.event("evt-stable", "character.resonance_rank_up", old=8, new=9)

        first_id = build_confirmed_feedback([first], ("evt-stable",))[0]["feedback_id"]
        repeated_id = build_confirmed_feedback([changed_payload], ("evt-stable",))[0]["feedback_id"]
        other_id = build_confirmed_feedback(
            [self.event("evt-other", "character.resonance_rank_up", old=1, new=2)],
            ("evt-other",),
        )[0]["feedback_id"]

        self.assertEqual(first_id, repeated_id)
        self.assertNotEqual(first_id, other_id)

    def test_reduced_motion_keeps_static_feedback_content(self):
        event = self.event("evt-skill", "character.skill_level_up", skill_id="logic", old=2, new=3)

        regular = build_confirmed_feedback([event], ("evt-skill",))[0]
        reduced = build_confirmed_feedback([event], ("evt-skill",), reduced_motion=True)[0]

        self.assertFalse(regular["reduced_motion"])
        self.assertTrue(reduced["reduced_motion"])
        self.assertEqual(
            {key: value for key, value in regular.items() if key != "reduced_motion"},
            {key: value for key, value in reduced.items() if key != "reduced_motion"},
        )
        self.assertEqual(
            reduced["detail_keys"],
            [{
                "text_key": "feedback.character.skill_level_up.detail",
                "placeholders": {"skill_id": "logic", "old": 2, "new": 3},
            }],
        )

    @staticmethod
    def event(event_id, event_type, **payload):
        return {"event_id": event_id, "event_type": event_type, "payload": payload}


if __name__ == "__main__":
    unittest.main()
