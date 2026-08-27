import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MANIFEST = json.loads((ROOT / "manifests/DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
TEXTS = json.loads((ROOT / "content/de/ui/district_events.json").read_text(encoding="utf-8"))


class DistrictMicroStory002AuditTests(unittest.TestCase):
    def test_audit_candidates_are_exactly_the_three_unused_catalog_events(self):
        events = {entry["event_id"]: entry for entry in MANIFEST["events"]}
        self.assertEqual(
            set(events) - {MANIFEST["micro_story_001"]["parent_catalog_event_id"]},
            {
                "district.word_of_mouth_wave",
                "district.patrol_sweep",
                "district.temporary_space_opens",
            },
        )
        self.assertNotIn("micro_story_002", MANIFEST)

    def test_candidate_story_assumptions_match_the_current_manifest(self):
        events = {entry["event_id"]: entry for entry in MANIFEST["events"]}

        word = events["district.word_of_mouth_wave"]
        self.assertEqual(word["requirements"], {"minimum_prestige": 15})
        self.assertEqual(word["effects"], {"heat": 1, "prestige": 3, "police_pressure": 0, "scene_activity": 4})

        patrol = events["district.patrol_sweep"]
        self.assertEqual(patrol["requirements"], {"minimum_heat": 20})
        self.assertEqual(patrol["effects"], {"heat": -2, "prestige": 0, "police_pressure": 5, "scene_activity": -2})

        space = events["district.temporary_space_opens"]
        self.assertEqual(space["requirements"], {"maximum_police_pressure": 60})
        self.assertEqual(space["effects"], {"heat": 1, "prestige": 2, "police_pressure": 0, "scene_activity": 5})

    def test_temporary_space_wording_and_contract_support_a_later_read_only_afterimage(self):
        self.assertEqual(TEXTS["district_event.temporary_space_opens.title"], "Eine Tür steht plötzlich offen")
        self.assertIn("Niemand weiß, wie lange das Fenster bleibt", TEXTS["district_event.temporary_space_opens.body"])

        contract = MANIFEST["follow_up_contract"]
        self.assertEqual(contract["journal_event_type"], "world.district_followup_resolved")
        self.assertEqual(contract["parent_event_type"], "world.district_effect_applied")
        self.assertTrue(contract["district_must_match_parent"])
        self.assertTrue(contract["runtime_authority_only"])
        self.assertFalse(contract["client_can_write"])
        self.assertEqual(contract["replay_policy"], "same_event_id_same_payload_is_idempotent")

    def test_micro_story_001_remains_the_only_implemented_followup(self):
        story = MANIFEST["micro_story_001"]
        self.assertEqual(story["parent_catalog_event_id"], "district.power_flicker")
        self.assertEqual(story["followup_id"], "power_flicker_afterglow")
        followup_keys = [key for key in MANIFEST if key.startswith("micro_story_")]
        self.assertEqual(followup_keys, ["micro_story_001"])


if __name__ == "__main__":
    unittest.main()
