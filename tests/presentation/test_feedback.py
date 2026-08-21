import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation import build_character_projection, build_confirmed_feedback


ROOT = Path(__file__).resolve().parents[2]
CATALOG_FILES = (
    "skills.json",
    "traits.json",
    "trait_effects.json",
    "trait_consequences.json",
    "specializations.json",
    "stages.json",
    "feedback.json",
)


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for name in CATALOG_FILES:
        catalog.update(json.loads((ROOT / "content/de/ui" / name).read_text(encoding="utf-8")))
    return catalog


def journal_event_types() -> set[str]:
    manifest = json.loads((ROOT / "manifests/JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
    return set(manifest["event_types"])


def event(event_id: str, event_type: str, payload: dict, *, character_id: str = "char.pppoppi", sequence: int = 1) -> dict:
    return {
        "event_id": event_id,
        "event_type": event_type,
        "character_id": character_id,
        "sequence": sequence,
        "payload": payload,
    }


class ConfirmedFeedbackTest(unittest.TestCase):
    def test_supported_feedback_events_are_journal_catalogued_and_externalized(self):
        events = [
            event("evt-level", "character.level_up", {"old": 9, "new": 10}, sequence=1),
            event("evt-skill", "character.skill_level_up", {"skill_id": "technik", "old": 20, "new": 21}, sequence=2),
            event("evt-trait", "character.trait_unlocked", {"family": "krisenfest", "old_tier": 0, "new_tier": 1}, sequence=3),
            event("evt-tier", "character.trait_tier_up", {"family": "krisenfest", "old_tier": 1, "new_tier": 2}, sequence=4),
            event(
                "evt-spec",
                "character.specialization_changed",
                {"old": None, "new": {"specialization_id": "spec.klangarchitektur", "stage": "tendenz"}},
                sequence=5,
            ),
            event("evt-res", "character.resonance_rank_up", {"old": 1, "new": 2}, sequence=6),
        ]
        confirmed = [item["event_id"] for item in events]
        feedback = build_confirmed_feedback(
            events,
            confirmed,
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
        )

        self.assertEqual(
            [item["kind"] for item in feedback],
            [
                "level_up",
                "skill_level_up",
                "trait_unlocked",
                "trait_tier_up",
                "specialization_changed",
                "resonance_rank_up",
            ],
        )
        self.assertEqual(feedback[1]["subject_label_key"], "skill.technik.label")
        self.assertEqual(feedback[2]["subject_label_key"], "trait.pppoppi.krisenfest.label")
        self.assertEqual(feedback[4]["subject_label_key"], "specialization.klangarchitektur.label")
        catalog = load_catalog()
        for item in feedback:
            self.assertIn(item["title_key"], catalog)
            if item["subject_label_key"] is not None:
                self.assertIn(item["subject_label_key"], catalog)
            self.assertIn(item["detail_keys"][0]["text_key"], catalog)

    def test_unknown_unconfirmed_and_malformed_events_fail_soft(self):
        events = [
            event("evt-xp", "character.skill_xp_gained", {"skill_id": "technik", "amount": 3}),
            event("evt-click", "character.level_up", {"old": 1, "new": 2}),
            event("evt-bad", "character.skill_level_up", {"skill_id": "technik", "old": 1}),
            event("evt-not-catalogued", "character.fake", {"old": 1, "new": 2}),
        ]
        feedback = build_confirmed_feedback(
            events,
            {"evt-xp", "evt-bad", "evt-not-catalogued"},
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
        )
        self.assertEqual(feedback, [])

    def test_feedback_ids_are_stable_and_dismissal_is_local(self):
        first = event("evt-stable", "character.resonance_rank_up", {"old": 1, "new": 2})
        changed_payload = event("evt-stable", "character.resonance_rank_up", {"old": 8, "new": 9})
        first_feedback = build_confirmed_feedback(
            [first],
            ["evt-stable"],
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
        )[0]
        repeated_feedback = build_confirmed_feedback(
            [changed_payload],
            ["evt-stable"],
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
        )[0]
        self.assertEqual(first_feedback["feedback_id"], repeated_feedback["feedback_id"])

        hidden = build_confirmed_feedback(
            [first],
            ["evt-stable"],
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
            dismissed_feedback_ids=[first_feedback["feedback_id"]],
        )
        self.assertEqual(hidden, [])

    def test_reduced_motion_changes_only_presentation_flag(self):
        source = event("evt-motion", "character.level_up", {"old": 2, "new": 3})
        regular = build_confirmed_feedback(
            [source],
            ["evt-motion"],
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
        )[0]
        reduced = build_confirmed_feedback(
            [source],
            ["evt-motion"],
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
            reduced_motion=True,
        )[0]
        self.assertFalse(regular["reduced_motion"])
        self.assertTrue(reduced["reduced_motion"])
        self.assertEqual(
            {key: value for key, value in regular.items() if key != "reduced_motion"},
            {key: value for key, value in reduced.items() if key != "reduced_motion"},
        )

    def test_projection_copies_feedback_and_validates_its_text_keys(self):
        source_event = event("evt-project", "character.skill_level_up", {"skill_id": "technik", "old": 10, "new": 11})
        feedback = build_confirmed_feedback(
            [source_event],
            ["evt-project"],
            journal_event_types=journal_event_types(),
            text_catalog=load_catalog(),
        )
        projection = build_character_projection(
            CharacterState("char.pppoppi", "PPPOPPI"),
            [],
            load_catalog(),
            feedback=feedback,
        )
        projection["feedback"][0]["kind"] = "changed"
        self.assertEqual(feedback[0]["kind"], "skill_level_up")

        broken_catalog = load_catalog()
        del broken_catalog[feedback[0]["title_key"]]
        with self.assertRaises(KeyError):
            build_character_projection(
                CharacterState("char.pppoppi", "PPPOPPI"),
                [],
                broken_catalog,
                feedback=feedback,
            )


if __name__ == "__main__":
    unittest.main()
