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
            "resonance_xp": 80,
            "resonance_rank": 2,
            "energy": 73,
            "stress": 21,
            "reputation": 9,
        },
        "top_skills": [],
        "skills": [
            {
                "skill_id": "skill.musik",
                "label_key": "skill.musik.label",
                "value": 31,
                "xp": 12,
                "xp_to_next": 90,
                "progress_percent": 12,
                "trend": None,
            },
            {
                "skill_id": "skill.technik",
                "label_key": "skill.technik.label",
                "value": 24,
                "xp": 8,
                "xp_to_next": 92,
                "progress_percent": 8,
                "trend": None,
            },
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
        "specialization": {
            "specialization_id": "spec.klangarchitektur",
            "label_key": "specialization.klangarchitektur.label",
            "stage": "tendenz",
            "stage_label_key": "stage.tendenz.label",
        },
        "biography": [],
        "capabilities": {
            "can_edit_profile": True,
            "can_undo_profile": True,
            "can_execute_action": True,
        },
        "feedback": [
            {
                "feedback_id": "feedback:level",
                "source_event_id": "evt-level",
                "kind": "level_up",
                "title_key": "feedback.character.level_up.title",
                "subject_label_key": None,
                "detail_keys": [
                    {
                        "text_key": "feedback.character.level_up.detail",
                        "placeholders": {"old": 11, "new": 12},
                    }
                ],
                "reduced_motion": False,
            },
            {
                "feedback_id": "feedback:hide",
                "source_event_id": "evt-skill",
                "kind": "skill_level_up",
                "title_key": "feedback.character.skill_level_up.title",
                "subject_label_key": "skill.technik.label",
                "detail_keys": [
                    {
                        "text_key": "feedback.character.skill_level_up.detail",
                        "placeholders": {"old": 23, "new": 24},
                    }
                ],
                "reduced_motion": False,
            },
        ],
    }


def actions() -> list[dict]:
    return [
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
                "changes": {"motto": "Beton bleibt."},
            },
        },
        {
            "action_id": "run-action",
            "label_key": "ui.action.execute",
            "icon_id": "play",
            "tone": "attention",
            "enabled": True,
            "command": {
                "type": "action.execute",
                "character_id": "char.pppoppi",
                "command_id": "cmd-run",
                "action_id": "action.soundcheck",
                "action_instance_id": "instance-run",
            },
        },
        {
            "action_id": "undo-profile",
            "label_key": "ui.undo",
            "icon_id": "undo",
            "tone": "attention",
            "enabled": True,
            "command": {
                "type": "profile.undo_last",
                "character_id": "char.pppoppi",
                "command_id": "cmd-undo",
                "event_id": "evt-undo",
                "transaction_id": "tx-undo",
            },
        },
    ]


class A3CinematicForgeTest(unittest.TestCase):
    def setUp(self):
        self.ui_manifest = load_json("manifests/UI_MANIFEST.json")
        self.animation_manifest = load_json("manifests/ANIMATION_MANIFEST.json")
        self.catalog = load_catalog()

    def build(self, state: PresentationState | None = None, source_projection: dict | None = None):
        return build_a3_cinematic_forge(
            source_projection or projection(),
            state or PresentationState(),
            self.ui_manifest,
            self.animation_manifest,
            self.catalog,
            primary_actions=actions(),
        )

    def test_uses_exactly_the_same_eight_shared_components_as_a4(self):
        source = projection()
        state = PresentationState()
        a3 = build_a3_cinematic_forge(
            source,
            state,
            self.ui_manifest,
            self.animation_manifest,
            self.catalog,
            primary_actions=actions(),
        )
        a4 = build_a4_ops_deck(
            source,
            state,
            self.ui_manifest,
            self.catalog,
            workflow={"primary_actions": actions()},
        )

        self.assertEqual(tuple(a3["components"]), COMPONENT_NAMES)
        self.assertEqual(a3["components"], a4["components"])
        self.assertEqual(a3["cinematic_contract"]["shared_component_names"], list(COMPONENT_NAMES))

    def test_a3_and_a4_emit_identical_normalized_dispatch_actions(self):
        source = projection()
        state = PresentationState()
        a3 = build_a3_cinematic_forge(
            source,
            state,
            self.ui_manifest,
            self.animation_manifest,
            self.catalog,
            primary_actions=actions(),
        )
        a4 = build_a4_ops_deck(
            source,
            state,
            self.ui_manifest,
            self.catalog,
            workflow={"primary_actions": actions()},
        )

        a3_actions = a3["zones"]["action_dock"]["primary_actions"]
        a4_actions = a4["zones"]["workspace"]["primary_actions"]
        self.assertEqual(a3_actions, a4_actions)
        self.assertEqual(
            [item["dispatch"]["command"]["type"] for item in a3_actions],
            ["profile.update", "action.execute", "profile.undo_last"],
        )
        self.assertTrue(a3["cinematic_contract"]["commands_use_shared_dispatcher"])

    def test_cinematic_layout_is_distinct_but_derived_from_component_data(self):
        forge = self.build()

        self.assertEqual(forge["layout"]["variant_id"], "A3_CINEMATIC_FORGE")
        self.assertEqual(
            forge["layout"]["layout_token"],
            "large_character_stage_radial_skill_web_context_drawer",
        )
        self.assertEqual(forge["zones"]["character_stage"]["portrait_source"], None)
        self.assertFalse(forge["cinematic_contract"]["portrait_data_invented"])
        self.assertEqual(
            [node["node_id"] for node in forge["zones"]["skill_web"]["nodes"]],
            ["skill.musik", "skill.technik"],
        )
        self.assertEqual(
            [node["angle_degrees"] for node in forge["zones"]["skill_web"]["nodes"]],
            [0.0, 180.0],
        )
        self.assertEqual(
            forge["zones"]["trait_orbit"]["nodes"][0]["node_id"],
            "trait.pppoppi.krisenfest",
        )

    def test_feedback_dismissal_applies_to_component_and_animation_overlay(self):
        state = PresentationState(dismissed_feedback_ids={"feedback:hide"})
        forge = self.build(state)

        self.assertEqual(
            [item["feedback_id"] for item in forge["components"]["ProgressFeedback"]["data"]],
            ["feedback:level"],
        )
        self.assertEqual(
            [cue["source_feedback_id"] for cue in forge["zones"]["progress_overlay"]["animation_cues"]],
            ["feedback:level"],
        )

    def test_reduced_motion_keeps_content_but_turns_cinematics_static(self):
        regular = self.build(PresentationState())
        reduced = self.build(PresentationState(reduced_motion=True))

        self.assertEqual(
            regular["components"]["ProgressFeedback"]["data"],
            reduced["components"]["ProgressFeedback"]["data"],
        )
        self.assertTrue(all(cue["mode"] == "animated" for cue in regular["zones"]["progress_overlay"]["animation_cues"]))
        self.assertTrue(all(cue["mode"] == "static" for cue in reduced["zones"]["progress_overlay"]["animation_cues"]))
        self.assertTrue(all(cue["duration_ms"] == 0 for cue in reduced["zones"]["progress_overlay"]["animation_cues"]))
        self.assertFalse(reduced["zones"]["character_stage"]["presentation"]["camera_motion_allowed"])
        self.assertFalse(reduced["zones"]["progress_overlay"]["presentation"]["blocking"])

    def test_all_animation_cues_are_non_blocking_and_have_static_fallbacks(self):
        forge = self.build()
        cues = forge["zones"]["progress_overlay"]["animation_cues"]
        self.assertTrue(cues)
        self.assertTrue(all(cue["max_blocking_ms"] == 0 for cue in cues))
        self.assertTrue(all(cue["skippable"] for cue in cues))
        self.assertTrue(all(cue["fallback"] for cue in cues))
        self.assertTrue(forge["cinematic_contract"]["animation_never_blocks_gameplay"])

    def test_selected_view_only_changes_context_drawer_references(self):
        expected = {
            "overview": ["ProfileEditor", "SpecializationCard"],
            "skills_traits": ["SkillList", "TraitList", "SpecializationCard"],
            "biography": ["BiographyTimeline"],
        }
        for view_id, refs in expected.items():
            with self.subTest(view_id=view_id):
                forge = self.build(PresentationState(selected_view=view_id))
                self.assertEqual(forge["zones"]["context_drawer"]["component_refs"], refs)
                self.assertEqual(tuple(forge["components"]), COMPONENT_NAMES)

    def test_accessibility_and_action_limit_remain_identical_to_shared_manifest(self):
        forge = self.build()
        accessibility = self.ui_manifest["accessibility"]
        self.assertEqual(forge["accessibility"]["minimum_target_px"], accessibility["minimum_target_px"])
        self.assertEqual(forge["accessibility"]["focus_ring_px"], accessibility["focus_ring_px"])
        self.assertTrue(forge["accessibility"]["keyboard_navigation"])
        self.assertTrue(forge["accessibility"]["screen_reader_labels"])
        self.assertTrue(forge["accessibility"]["color_never_sole_information"])

        with self.assertRaises(ValueError):
            build_a3_cinematic_forge(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.animation_manifest,
                self.catalog,
                primary_actions=actions() + [actions()[0]],
            )

    def test_missing_text_key_fails_closed(self):
        broken = dict(self.catalog)
        del broken["ui.cinematic.skill_web"]
        with self.assertRaises(KeyError):
            build_a3_cinematic_forge(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.animation_manifest,
                broken,
                primary_actions=actions(),
            )

    def test_inputs_are_detached(self):
        source = projection()
        source_actions = actions()
        forge = build_a3_cinematic_forge(
            source,
            PresentationState(),
            self.ui_manifest,
            self.animation_manifest,
            self.catalog,
            primary_actions=source_actions,
        )

        forge["zones"]["skill_web"]["nodes"][0]["value"] = 99
        forge["zones"]["action_dock"]["primary_actions"][0]["dispatch"]["command"]["changes"]["motto"] = "changed"
        forge["components"]["CharacterHeader"]["data"]["display_name"] = "changed"

        self.assertEqual(source["skills"][0]["value"], 31)
        self.assertEqual(source_actions[0]["command"]["changes"]["motto"], "Beton bleibt.")
        self.assertEqual(source["overview"]["display_name"], "PPPOPPI")


if __name__ == "__main__":
    unittest.main()
