import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.action_resolver import ActionResolver
from bunkerfrequenz.application.character_action_service import CharacterActionService
from bunkerfrequenz.application.command_dispatcher import dispatch_command
from bunkerfrequenz.application.profile_service import CharacterProfileService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel
from bunkerfrequenz.presentation import PresentationState, build_a4_ops_deck


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for path in sorted((ROOT / "content/de/ui").glob("*.json")):
        catalog.update(json.loads(path.read_text(encoding="utf-8")))
    return catalog


def projection(*, capabilities: dict | None = None) -> dict:
    return {
        "meta": {"projection_version": "0.6", "character_id": "char.pppoppi"},
        "overview": {
            "display_name": "PPPOPPI",
            "alias": "",
            "additional_nicknames": [],
            "motto": "",
            "level": 1,
            "total_xp": 0,
            "resonance_xp": 0,
            "resonance_rank": 0,
            "energy": 100,
            "stress": 0,
            "reputation": 0,
        },
        "top_skills": [],
        "skills": [
            {
                "skill_id": "skill.technik",
                "label_key": "skill.technik.label",
                "value": 10,
                "xp": 0,
                "xp_to_next": 70,
                "progress_percent": 0,
                "trend": None,
            }
        ],
        "traits": [],
        "specialization": None,
        "biography": [],
        "capabilities": capabilities
        or {
            "can_edit_profile": True,
            "can_undo_profile": True,
            "can_execute_action": True,
        },
        "feedback": [],
    }


def profile_action(action_id: str = "save-profile") -> dict:
    return {
        "action_id": action_id,
        "label_key": "ui.profile.save",
        "icon_id": "save",
        "tone": "primary",
        "enabled": True,
        "command": {
            "type": "profile.update",
            "character_id": "char.pppoppi",
            "command_id": f"cmd-{action_id}",
            "event_id": f"evt-{action_id}",
            "transaction_id": f"tx-{action_id}",
            "changes": {"alias": "Betonfunk"},
        },
    }


def action_execute(action_id: str = "run-action") -> dict:
    return {
        "action_id": action_id,
        "label_key": "ui.action.execute",
        "icon_id": "play",
        "tone": "primary",
        "enabled": True,
        "command": {
            "type": "action.execute",
            "character_id": "char.pppoppi",
            "command_id": f"cmd-{action_id}",
            "action_id": "action.soundcheck",
            "action_instance_id": f"instance-{action_id}",
        },
    }


def undo_action(action_id: str = "undo-profile") -> dict:
    return {
        "action_id": action_id,
        "label_key": "ui.undo",
        "icon_id": "undo",
        "tone": "attention",
        "enabled": True,
        "command": {
            "type": "profile.undo_last",
            "character_id": "char.pppoppi",
            "command_id": f"cmd-{action_id}",
            "event_id": f"evt-{action_id}",
            "transaction_id": f"tx-{action_id}",
        },
    }


class A4OpsDeckTest(unittest.TestCase):
    def setUp(self):
        self.ui_manifest = load_json("manifests/UI_MANIFEST.json")
        self.catalog = load_catalog()

    def test_manifest_drives_workflow_layout_and_accessibility(self):
        deck = build_a4_ops_deck(
            projection(),
            PresentationState(),
            self.ui_manifest,
            self.catalog,
        )

        self.assertEqual(deck["layout"]["variant_id"], "A4_OPS_DECK")
        self.assertEqual(
            [step["step_id"] for step in deck["workflow"]],
            self.ui_manifest["focus_model"]["workflow"],
        )
        self.assertEqual(
            deck["accessibility"]["minimum_target_px"],
            self.ui_manifest["accessibility"]["minimum_target_px"],
        )
        self.assertEqual(
            deck["accessibility"]["focus_ring_px"],
            self.ui_manifest["accessibility"]["focus_ring_px"],
        )
        self.assertTrue(deck["accessibility"]["keyboard_navigation"])
        self.assertTrue(deck["accessibility"]["screen_reader_labels"])
        self.assertTrue(deck["accessibility"]["high_contrast_mode"])
        self.assertTrue(deck["accessibility"]["color_never_sole_information"])
        self.assertEqual(deck["accessibility"]["semantic_cues"], ["text", "icon", "tone"])

    def test_empty_workflow_does_not_invent_goal_result_or_actions(self):
        deck = build_a4_ops_deck(
            projection(),
            PresentationState(),
            self.ui_manifest,
            self.catalog,
        )
        workspace = deck["zones"]["workspace"]
        self.assertIsNone(workspace["current_goal"])
        self.assertEqual(workspace["primary_actions"], [])
        result_step = next(step for step in deck["workflow"] if step["step_id"] == "result")
        next_goal_step = next(step for step in deck["workflow"] if step["step_id"] == "next_goal")
        self.assertIsNone(result_step["content"])
        self.assertIsNone(next_goal_step["content"])

    def test_accepts_exactly_three_dispatcher_ready_primary_actions(self):
        workflow = {
            "current_goal": {"title_key": "ui.character.training"},
            "primary_actions": [profile_action(), action_execute(), undo_action()],
            "result": {"title_key": "ui.workflow.current"},
            "next_goal": {"title_key": "ui.workflow.next"},
        }
        deck = build_a4_ops_deck(
            projection(),
            PresentationState(),
            self.ui_manifest,
            self.catalog,
            workflow=workflow,
        )
        actions = deck["zones"]["workspace"]["primary_actions"]

        self.assertEqual(len(actions), 3)
        self.assertEqual(deck["keyboard_order"], ["save-profile", "run-action", "undo-profile"])
        self.assertEqual(
            [action["dispatch"]["command"]["type"] for action in actions],
            ["profile.update", "action.execute", "profile.undo_last"],
        )
        self.assertTrue(all(action["dispatch"]["route"] == "application.command_dispatcher.dispatch_command" for action in actions))
        self.assertTrue(all(action["target_px"] == 44 for action in actions))
        self.assertTrue(all(action["focus_ring_px"] == 3 for action in actions))
        self.assertTrue(all(action["label_key"] == action["aria_label_key"] for action in actions))

    def test_more_than_manifest_limit_is_rejected_not_silently_truncated(self):
        actions = [profile_action(f"save-{index}") for index in range(4)]
        with self.assertRaises(ValueError):
            build_a4_ops_deck(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.catalog,
                workflow={"primary_actions": actions},
            )

    def test_untrusted_or_incomplete_command_payloads_are_rejected(self):
        incomplete = profile_action()
        del incomplete["command"]["transaction_id"]
        with self.assertRaises(ValueError):
            build_a4_ops_deck(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.catalog,
                workflow={"primary_actions": [incomplete]},
            )

        untrusted = action_execute()
        untrusted["command"]["base_xp"] = 999999
        with self.assertRaises(ValueError):
            build_a4_ops_deck(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.catalog,
                workflow={"primary_actions": [untrusted]},
            )

        invalid_profile = profile_action()
        invalid_profile["command"]["changes"] = {"level": 99}
        with self.assertRaises(ValueError):
            build_a4_ops_deck(
                projection(),
                PresentationState(),
                self.ui_manifest,
                self.catalog,
                workflow={"primary_actions": [invalid_profile]},
            )

    def test_enabled_action_must_match_confirmed_capability(self):
        source = projection(
            capabilities={
                "can_edit_profile": False,
                "can_undo_profile": False,
                "can_execute_action": False,
            }
        )
        with self.assertRaises(ValueError):
            build_a4_ops_deck(
                source,
                PresentationState(),
                self.ui_manifest,
                self.catalog,
                workflow={"primary_actions": [profile_action()]},
            )

        disabled = profile_action()
        disabled["enabled"] = False
        deck = build_a4_ops_deck(
            source,
            PresentationState(),
            self.ui_manifest,
            self.catalog,
            workflow={"primary_actions": [disabled]},
        )
        self.assertFalse(deck["zones"]["workspace"]["primary_actions"][0]["enabled"])

    def test_selected_view_changes_component_references_without_new_component_logic(self):
        expected = {
            "overview": ["ProfileEditor", "SpecializationCard"],
            "skills_traits": ["SkillList", "TraitList", "SpecializationCard"],
            "biography": ["BiographyTimeline"],
        }
        for view_id, refs in expected.items():
            with self.subTest(view_id=view_id):
                deck = build_a4_ops_deck(
                    projection(),
                    PresentationState(selected_view=view_id),
                    self.ui_manifest,
                    self.catalog,
                )
                self.assertEqual(deck["zones"]["workspace"]["selected_view_component_refs"], refs)
                self.assertEqual(len(deck["components"]), 8)

    def test_workflow_and_projection_inputs_are_detached(self):
        source_projection = projection()
        source_workflow = {
            "current_goal": {"title_key": "ui.character.training", "placeholders": {"x": 1}},
            "primary_actions": [profile_action()],
        }
        deck = build_a4_ops_deck(
            source_projection,
            PresentationState(),
            self.ui_manifest,
            self.catalog,
            workflow=source_workflow,
        )

        deck["zones"]["workspace"]["current_goal"]["placeholders"]["x"] = 99
        deck["zones"]["workspace"]["primary_actions"][0]["dispatch"]["command"]["changes"]["alias"] = "changed"
        deck["components"]["CharacterHeader"]["data"]["display_name"] = "changed"

        self.assertEqual(source_workflow["current_goal"]["placeholders"]["x"], 1)
        self.assertEqual(source_workflow["primary_actions"][0]["command"]["changes"]["alias"], "Betonfunk")
        self.assertEqual(source_projection["overview"]["display_name"], "PPPOPPI")

    def test_missing_visible_text_key_fails_closed(self):
        broken_catalog = dict(self.catalog)
        del broken_catalog["ui.workflow.current_goal"]
        with self.assertRaises(KeyError):
            build_a4_ops_deck(
                projection(),
                PresentationState(),
                self.ui_manifest,
                broken_catalog,
            )

    def test_emitted_profile_action_runs_directly_through_existing_dispatcher(self):
        workflow = {"primary_actions": [profile_action()]}
        deck = build_a4_ops_deck(
            projection(),
            PresentationState(),
            self.ui_manifest,
            self.catalog,
            workflow=workflow,
        )
        emitted_command = deck["zones"]["workspace"]["primary_actions"][0]["dispatch"]["command"]

        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, {"character.profile_updated"})
            profile_service = CharacterProfileService(kernel)
            action_service = CharacterActionService(ActionResolver(), kernel)
            character = CharacterState("char.pppoppi", "PPPOPPI")
            context = JournalContext(
                "2026-08-21T20:30:00+02:00",
                "session-a4",
                "player-a4",
                "character",
                "char.pppoppi",
                "unused",
                "presentation",
                "0.5.2-alpha.1",
                "char.pppoppi",
            )

            result = dispatch_command(
                emitted_command,
                character=character,
                profile_service=profile_service,
                action_service=action_service,
                actions={},
                world_seed="a4-world",
                journal_context=context,
            )

            self.assertEqual(result.status, "confirmed")
            self.assertEqual(result.confirmed_state.alias, "Betonfunk")
            self.assertEqual(result.committed_event_ids, ("evt-save-profile",))
            self.assertEqual(kernel.read_records()[0]["command_id"], "cmd-save-profile")


if __name__ == "__main__":
    unittest.main()
