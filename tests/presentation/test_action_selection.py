import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation import PresentationState, build_a4_ops_deck, build_action_selection
from tests.presentation.test_a4_ops_deck import load_catalog, load_json, projection


ROOT = Path(__file__).resolve().parents[2]


class ActionSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = json.loads((ROOT / "manifests/ACTION_MANIFEST.json").read_text(encoding="utf-8"))
        cls.actions = manifest["actions"]

    def test_projects_all_manifest_actions_into_a4(self):
        rules = {rule: True for action in self.actions for rule in action["prerequisites"]}
        selection = build_action_selection(
            "char.pppoppi", self.actions, can_execute_action=True, prerequisite_status=rules
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
        self.assertTrue(all(item["resources"]["status"] == "not_defined" for item in projected))

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


if __name__ == "__main__":
    unittest.main()
