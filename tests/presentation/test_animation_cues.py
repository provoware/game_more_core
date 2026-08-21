import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation import PresentationState, build_animation_cues


ROOT = Path(__file__).resolve().parents[2]


def animation_manifest() -> dict:
    return json.loads((ROOT / "manifests/ANIMATION_MANIFEST.json").read_text(encoding="utf-8"))


def feedback(feedback_id: str, kind: str) -> dict:
    return {
        "feedback_id": feedback_id,
        "source_event_id": f"event:{feedback_id}",
        "kind": kind,
        "title_key": "feedback.character.level_up.title",
        "subject_label_key": None,
        "detail_keys": [],
        "reduced_motion": False,
    }


class AnimationCueTest(unittest.TestCase):
    def test_all_supported_progression_feedback_maps_to_non_blocking_cues(self):
        source = [
            feedback("level", "level_up"),
            feedback("skill", "skill_level_up"),
            feedback("trait", "trait_unlocked"),
            feedback("tier", "trait_tier_up"),
            feedback("spec", "specialization_changed"),
            feedback("resonance", "resonance_rank_up"),
        ]
        cues = build_animation_cues(source, PresentationState(), animation_manifest())

        self.assertEqual(
            [cue["animation_id"] for cue in cues],
            [
                "anim.level_up",
                "anim.skill_up",
                "anim.trait_unlock",
                "anim.trait_unlock",
                "anim.specialization",
                "anim.resonance_up",
            ],
        )
        self.assertTrue(all(cue["mode"] == "animated" for cue in cues))
        self.assertTrue(all(cue["max_blocking_ms"] == 0 for cue in cues))
        self.assertTrue(all(cue["skippable"] for cue in cues))
        self.assertTrue(all(cue["fallback"] for cue in cues))
        self.assertTrue(all(cue["duration_ms"] > 0 for cue in cues))

    def test_reduced_motion_uses_static_fallback_without_changing_source_feedback(self):
        source = [feedback("level", "level_up")]
        before = dict(source[0])
        cue = build_animation_cues(
            source,
            PresentationState(reduced_motion=True),
            animation_manifest(),
        )[0]

        self.assertEqual(cue["mode"], "static")
        self.assertEqual(cue["duration_ms"], 0)
        self.assertEqual(cue["max_blocking_ms"], 0)
        self.assertEqual(cue["reason"], "reduced_motion")
        self.assertEqual(source[0], before)

    def test_dismissed_feedback_never_generates_animation_cue(self):
        source = [feedback("keep", "level_up"), feedback("hide", "skill_level_up")]
        cues = build_animation_cues(
            source,
            PresentationState(dismissed_feedback_ids={"hide"}),
            animation_manifest(),
        )
        self.assertEqual([cue["source_feedback_id"] for cue in cues], ["keep"])

    def test_missing_animation_falls_back_static_instead_of_blocking_or_failing_gameplay(self):
        manifest = animation_manifest()
        manifest["animations"] = [
            entry for entry in manifest["animations"] if entry["id"] != "anim.resonance_up"
        ]
        cue = build_animation_cues(
            [feedback("res", "resonance_rank_up")],
            PresentationState(),
            manifest,
        )[0]

        self.assertEqual(cue["mode"], "static")
        self.assertIsNone(cue["animation_id"])
        self.assertEqual(cue["fallback"], "static_feedback_card")
        self.assertEqual(cue["max_blocking_ms"], 0)
        self.assertEqual(cue["reason"], "missing_animation")

    def test_blocking_or_unskippable_animation_contract_is_rejected(self):
        blocking = animation_manifest()
        blocking["animations"][0]["max_blocking_ms"] = 1
        with self.assertRaises(ValueError):
            build_animation_cues([feedback("level", "level_up")], PresentationState(), blocking)

        unskippable = animation_manifest()
        unskippable["animations"][0]["skippable"] = False
        with self.assertRaises(ValueError):
            build_animation_cues([feedback("level", "level_up")], PresentationState(), unskippable)

    def test_duplicate_animation_ids_are_rejected(self):
        manifest = animation_manifest()
        manifest["animations"].append(dict(manifest["animations"][0]))
        with self.assertRaises(ValueError):
            build_animation_cues([], PresentationState(), manifest)


if __name__ == "__main__":
    unittest.main()
