import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation import (
    COMPONENT_NAMES,
    PresentationState,
    build_a3_cinematic_forge,
    build_a4_ops_deck,
)


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for path in sorted((ROOT / "content/de/ui").glob("*.json")):
        catalog.update(json.loads(path.read_text(encoding="utf-8")))
    return catalog


def feedback_entry(feedback_id: str, kind: str, suffix: str) -> dict:
    return {
        "feedback_id": feedback_id,
        "source_event_id": f"event-{suffix}",
        "kind": kind,
        "title_key": f"feedback.character.{suffix}.title",
        "subject_label_key": None,
        "detail_keys": [
            {
                "text_key": f"feedback.character.{suffix}.detail",
                "placeholders": {},
            }
        ],
        "reduced_motion": False,
    }


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
            "resonance_xp": 22,
            "resonance_rank": 2,
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
        "traits": [],
        "specialization": None,
        "biography": [],
        "capabilities": {
            "can_edit_profile": True,
            "can_undo_profile": True,
            "can_execute_action": True,
        },
        "feedback": [
            feedback_entry("f-level", "level_up", "level_up"),
            feedback_entry("f-skill", "skill_level_up", "skill_level_up"),
            feedback_entry("f-unlock", "trait_unlocked", "trait_unlocked"),
            feedback_entry("f-tier", "trait_tier_up", "trait_tier_up"),
            feedback_entry("f-spec", "specialization_changed", "specialization_changed"),
            feedback_entry("f-res", "resonance_rank_up", "resonance_rank_up"),
        ],
    }


def profile_workflow() -> dict:
    return {
        "current_goal": {"title_key": "ui.character.training"},
        "primary_actions": [
            {
                "action_id": "save-profile",
                "label_key": "ui.profile.save",
                "icon_id": "save",
                "tone": "primary",
                "enabled": True,
                "command": {
                    "type": "profile.update",
                    "character_id": "char.pppoppi",
                    "command_id": "cmd-save",
                    "event_id": "evt-save",
                    "transaction_id": "tx-save",
                    "changes": {"alias": "Betonfunk"},
                },
            }
        ],
    }


class A3A4ContractTest(unittest.TestCase):
    def setUp(self):
        self.ui_manifest = load_json("manifests/UI_MANIFEST.json")
        self.animation_manifest = load_json("manifests/ANIMATION_MANIFEST.json")
        self.catalog = load_catalog()

    def build_views(self, *, state: PresentationState | None = None, animations: dict | None = None):
        current_state = state or PresentationState()
        source = projection()
        workflow = profile_workflow()
        a4 = build_a4_ops_deck(
            source,
            current_state,
            self.ui_manifest,
            self.catalog,
            workflow=workflow,
        )
        a3 = build_a3_cinematic_forge(
            source,
            current_state,
            self.ui_manifest,
            animations or self.animation_manifest,
            self.catalog,
            workflow=workflow,
        )
        return a3, a4

    def test_a3_reuses_exactly_the_same_eight_components_and_primary_commands(self):
        a3, a4 = self.build_views()

        self.assertEqual(tuple(a3["components"]), COMPONENT_NAMES)
        self.assertEqual(a3["components"], a4["components"])
        self.assertIsNot(a3["components"], a4["components"])
        self.assertEqual(
            a3["zones"]["action_dock"]["primary_actions"],
            a4["zones"]["workspace"]["primary_actions"],
        )
        self.assertEqual(a3["keyboard_order"], a4["keyboard_order"])
        self.assertEqual(
            a3["interaction_contract"]["command_types"],
            ["profile.update"],
        )
        self.assertEqual(
            a3["interaction_contract"]["command_routes"],
            ["application.command_dispatcher.dispatch_command"],
        )

    def test_a3_changes_layout_only_not_shared_accessibility_contract(self):
        a3, a4 = self.build_views()

        self.assertEqual(a3["layout"]["variant_id"], "A3_CINEMATIC_FORGE")
        self.assertEqual(a4["layout"]["variant_id"], "A4_OPS_DECK")
        for key in (
            "minimum_body_px",
            "preferred_body_px",
            "minimum_target_px",
            "focus_ring_px",
            "keyboard_navigation",
            "screen_reader_labels",
            "high_contrast_mode",
            "color_never_sole_information",
            "semantic_cues",
        ):
            self.assertEqual(a3["accessibility"][key], a4["accessibility"][key])
        self.assertTrue(a3["accessibility"]["animation_never_blocks_input"])
        self.assertTrue(a3["accessibility"]["development_overlay_skippable"])

    def test_all_progression_feedback_types_have_nonblocking_cinematic_cues(self):
        a3, _ = self.build_views()
        cues = a3["zones"]["development_overlay"]["cues"]

        self.assertEqual(
            [cue["animation_id"] for cue in cues],
            [
                "anim.level_up",
                "anim.skill_up",
                "anim.trait_unlock",
                "anim.trait_tier_up",
                "anim.specialization",
                "anim.resonance_up",
            ],
        )
        self.assertTrue(all(cue["mode"] == "animated" for cue in cues))
        self.assertTrue(all(cue["max_blocking_ms"] == 0 for cue in cues))
        self.assertTrue(all(cue["skippable"] for cue in cues))
        self.assertTrue(all(not cue["input_blocked"] for cue in cues))

    def test_reduced_motion_keeps_content_but_forces_static_fallbacks(self):
        regular, _ = self.build_views()
        reduced, _ = self.build_views(state=PresentationState(reduced_motion=True))
        regular_cues = regular["zones"]["development_overlay"]["cues"]
        reduced_cues = reduced["zones"]["development_overlay"]["cues"]

        self.assertEqual(
            [(cue["feedback_id"], cue["kind"], cue["title_key"]) for cue in regular_cues],
            [(cue["feedback_id"], cue["kind"], cue["title_key"]) for cue in reduced_cues],
        )
        self.assertTrue(all(cue["mode"] == "static" for cue in reduced_cues))
        self.assertTrue(all(cue["animation_id"] is None for cue in reduced_cues))
        self.assertTrue(all(cue["duration_ms"] == 0 for cue in reduced_cues))
        self.assertTrue(all(cue["fallback"] for cue in reduced_cues))

    def test_missing_or_unsafe_animation_fails_soft_to_static_without_blocking(self):
        animations = load_json("manifests/ANIMATION_MANIFEST.json")
        animations["animations"] = [
            item for item in animations["animations"] if item["id"] != "anim.resonance_up"
        ]
        next(item for item in animations["animations"] if item["id"] == "anim.level_up")[
            "max_blocking_ms"
        ] = 500

        a3, _ = self.build_views(animations=animations)
        cues = {cue["kind"]: cue for cue in a3["zones"]["development_overlay"]["cues"]}

        self.assertEqual(cues["level_up"]["mode"], "static")
        self.assertIsNone(cues["level_up"]["animation_id"])
        self.assertEqual(cues["resonance_rank_up"]["mode"], "static")
        self.assertIsNone(cues["resonance_rank_up"]["animation_id"])
        self.assertFalse(cues["level_up"]["input_blocked"])
        self.assertFalse(cues["resonance_rank_up"]["input_blocked"])

    def test_dismissed_feedback_is_absent_from_component_and_cinematic_overlay(self):
        state = PresentationState(dismissed_feedback_ids={"f-tier", "f-res"})
        a3, _ = self.build_views(state=state)

        component_ids = [
            item["feedback_id"]
            for item in a3["components"]["ProgressFeedback"]["data"]
        ]
        cue_ids = [
            item["feedback_id"]
            for item in a3["zones"]["development_overlay"]["cues"]
        ]
        self.assertNotIn("f-tier", component_ids)
        self.assertNotIn("f-res", component_ids)
        self.assertEqual(component_ids, cue_ids)

    def test_missing_cinematic_text_key_is_a_development_error(self):
        broken = dict(self.catalog)
        del broken["ui.cinematic.growth_web"]
        with self.assertRaises(KeyError):
            build_a3_cinematic_forge(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.animation_manifest,
                broken,
                workflow=profile_workflow(),
            )

    def test_a3_inherits_a4_primary_action_limit_and_validation(self):
        workflow = profile_workflow()
        workflow["primary_actions"] = workflow["primary_actions"] * 4
        with self.assertRaises(ValueError):
            build_a3_cinematic_forge(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.animation_manifest,
                self.catalog,
                workflow=workflow,
            )


if __name__ == "__main__":
    unittest.main()
