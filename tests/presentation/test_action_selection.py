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
from bunkerfrequenz.presentation import (
    PresentationState,
    build_a4_ops_deck,
    build_action_execute_command,
    build_action_selection,
)
from tests.presentation.test_a4_ops_deck import load_catalog, load_json, projection


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_EVENTS = {
    "character.profile_updated",
    "character.resources_changed",
    "character.skill_xp_gained",
    "character.skill_level_up",
    "character.trait_evidence_gained",
    "character.trait_unlocked",
    "character.trait_tier_up",
    "character.specialization_changed",
    "character.level_up",
    "character.resonance_xp_gained",
    "character.resonance_rank_up",
}


class ActionSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / "manifests/ACTION_MANIFEST.json").read_text(encoding="utf-8"))
        cls.actions = manifest["actions"]

    def all_rules_confirmed(self) -> dict[str, bool]:
        return {rule: True for action in self.actions for rule in action["prerequisites"]}

    def test_projects_all_manifest_actions_into_a4_without_executable_partial_commands(self):
        selection = build_action_selection(
            "char.pppoppi",
            self.actions,
            can_execute_action=True,
            prerequisite_status=self.all_rules_confirmed(),
        )
        deck = build_a4_ops_deck(
            projection(),
            PresentationState(),
            load_json("manifests/UI_MANIFEST.json"),
            load_catalog(),
            action_selection=selection,
        )

        projected = deck["zones"]["workspace"]["action_selection"]
        self.assertEqual(len(projected), 20)
        self.assertEqual(len({item["action_id"] for item in projected}), 20)
        self.assertTrue(all(item["enabled"] for item in projected))
        self.assertTrue(all(item["duration"]["minutes"] >= 0 for item in projected))
        self.assertTrue(all(item["expected_skill_effects"] for item in projected))
        self.assertTrue(all(item["resources"]["status"] == "defined" for item in projected))
        self.assertTrue(all(item["resources"]["status_key"] == "ui.action.resources.defined" for item in projected))
        self.assertTrue(all(isinstance(item["resources"]["energy_delta"], int) for item in projected))
        self.assertTrue(all(isinstance(item["resources"]["stress_delta"], int) for item in projected))
        self.assertTrue(all("command" not in item for item in projected))
        self.assertTrue(all(item["command_template"]["type"] == "action.execute" for item in projected))
        self.assertTrue(all(item["required_runtime_ids"] == ["command_id", "action_instance_id"] for item in projected))

        run_event = next(item for item in projected if item["action_id"] == "action.run_event")
        self.assertEqual(run_event["resources"]["energy_delta"], -28)
        self.assertEqual(run_event["resources"]["stress_delta"], 18)

    def test_unconfirmed_prerequisite_disables_action(self):
        selection = build_action_selection(
            "char.pppoppi", self.actions, can_execute_action=True
        )
        explore = next(item for item in selection if item["action_id"] == "action.explore_location")
        training = next(item for item in selection if item["action_id"] == "action.training_session")

        self.assertFalse(explore["enabled"])
        self.assertEqual(explore["prerequisites"], [{
            "rule_id": "location_access_is_legal_authorized_or_fictional", "met": False
        }])
        self.assertTrue(training["enabled"])
        self.assertEqual(training["selection_requirements"], ["selected_skill", "selected_trait_family"])

    def test_command_builder_requires_runtime_ids_and_required_selections(self):
        selection = build_action_selection(
            "char.pppoppi",
            self.actions,
            can_execute_action=True,
            prerequisite_status=self.all_rules_confirmed(),
        )
        training = next(item for item in selection if item["action_id"] == "action.training_session")

        with self.assertRaises(ValueError):
            build_action_execute_command(
                training,
                command_id="cmd-training",
                action_instance_id="instance-training",
            )

        command = build_action_execute_command(
            training,
            command_id="cmd-training",
            action_instance_id="instance-training",
            selected_skill="technik",
            selected_trait_family="technikfokus",
        )
        self.assertEqual(command["command_id"], "cmd-training")
        self.assertEqual(command["action_instance_id"], "instance-training")
        self.assertEqual(command["type"], "action.execute")
        self.assertEqual(command["action_id"], "action.training_session")

    def test_built_command_runs_unchanged_through_existing_dispatcher(self):
        selection = build_action_selection(
            "char.pppoppi",
            self.actions,
            can_execute_action=True,
            prerequisite_status=self.all_rules_confirmed(),
        )
        soundcheck = next(item for item in selection if item["action_id"] == "action.soundcheck")
        command = build_action_execute_command(
            soundcheck,
            command_id="cmd-selection-soundcheck",
            action_instance_id="instance-selection-soundcheck",
        )
        action = next(item for item in self.actions if item["action_id"] == "action.soundcheck")

        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED_EVENTS)
            profile_service = CharacterProfileService(kernel)
            action_service = CharacterActionService(ActionResolver(), kernel)
            character = CharacterState("char.pppoppi", "PPPOPPI")
            context = JournalContext(
                "2026-08-21T21:30:00+02:00",
                "session-selection",
                "player-selection",
                "character",
                "char.pppoppi",
                "unused",
                "presentation",
                "0.5.2-alpha.1",
                "char.pppoppi",
            )
            result = dispatch_command(
                command,
                character=character,
                profile_service=profile_service,
                action_service=action_service,
                actions={action["action_id"]: action},
                world_seed="selection-world",
                journal_context=context,
            )

        self.assertEqual(result.status, "confirmed")
        self.assertIsNone(result.error_code)
        self.assertTrue(result.committed_event_ids)
        self.assertEqual((result.confirmed_state.energy, result.confirmed_state.stress), (94, 3))

    def test_a4_rechecks_current_capability_and_disables_stale_enabled_selection(self):
        selection = build_action_selection(
            "char.pppoppi",
            self.actions,
            can_execute_action=True,
            prerequisite_status=self.all_rules_confirmed(),
        )
        source = projection()
        source["capabilities"]["can_execute_action"] = False

        deck = build_a4_ops_deck(
            source,
            PresentationState(),
            load_json("manifests/UI_MANIFEST.json"),
            load_catalog(),
            action_selection=selection,
        )
        training = next(
            item for item in deck["zones"]["workspace"]["action_selection"]
            if item["action_id"] == "action.training_session"
        )

        self.assertFalse(training["enabled"])
        self.assertEqual(training["blocked_reason"], "capability_unconfirmed")
        self.assertTrue(next(item for item in selection if item["action_id"] == "action.training_session")["enabled"])

    def test_command_builder_rejects_disabled_selection(self):
        selection = build_action_selection(
            "char.pppoppi", self.actions, can_execute_action=False
        )
        soundcheck = next(item for item in selection if item["action_id"] == "action.soundcheck")
        with self.assertRaises(ValueError):
            build_action_execute_command(
                soundcheck,
                command_id="cmd-disabled",
                action_instance_id="instance-disabled",
            )


if __name__ == "__main__":
    unittest.main()
