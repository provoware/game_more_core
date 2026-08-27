import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MANIFEST = json.loads((ROOT / "manifests/DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
TEXTS = json.loads((ROOT / "content/de/ui/district_events.json").read_text(encoding="utf-8"))


class DistrictMicroStory002AuditTests(unittest.TestCase):
    def test_audit_selection_is_now_the_second_catalogued_micro_story(self):
        events = {entry["event_id"]: entry for entry in MANIFEST["events"]}
        story = MANIFEST["micro_story_002"]

        self.assertIn(story["parent_catalog_event_id"], events)
        self.assertEqual(story["parent_catalog_event_id"], "district.temporary_space_opens")
        self.assertEqual(story["followup_id"], "temporary_space_afterimage")
        self.assertEqual(story["title_key"], "district_followup.temporary_space_afterimage.title")
        self.assertEqual(story["body_key"], "district_followup.temporary_space_afterimage.body")

    def test_audit_candidate_assumptions_still_match_the_current_manifest(self):
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

    def test_temporary_space_story_text_and_contract_remain_read_only_and_balance_neutral(self):
        self.assertEqual(TEXTS["district_event.temporary_space_opens.title"], "Eine Tür steht plötzlich offen")
        self.assertIn("Niemand weiß, wie lange das Fenster bleibt", TEXTS["district_event.temporary_space_opens.body"])
        self.assertEqual(
            TEXTS["district_followup.temporary_space_afterimage.title"],
            "Die Tür ist zu – die Adresse lebt weiter.",
        )
        self.assertIn("Kreidestriche", TEXTS["district_followup.temporary_space_afterimage.body"])

        contract = MANIFEST["follow_up_contract"]
        self.assertEqual(contract["journal_event_type"], "world.district_followup_resolved")
        self.assertEqual(contract["parent_event_type"], "world.district_effect_applied")
        self.assertTrue(contract["district_must_match_parent"])
        self.assertTrue(contract["runtime_authority_only"])
        self.assertFalse(contract["client_can_write"])
        self.assertEqual(contract["replay_policy"], "same_event_id_same_payload_is_idempotent")
        self.assertNotIn("effects", MANIFEST["micro_story_002"])
        self.assertNotIn("deltas", MANIFEST["micro_story_002"])

    def test_two_micro_stories_use_distinct_parents_and_followup_ids(self):
        stories = [MANIFEST["micro_story_001"], MANIFEST["micro_story_002"]]
        self.assertEqual(
            {story["parent_catalog_event_id"] for story in stories},
            {"district.power_flicker", "district.temporary_space_opens"},
        )
        self.assertEqual(
            {story["followup_id"] for story in stories},
            {"power_flicker_afterglow", "temporary_space_afterimage"},
        )


if __name__ == "__main__":
    unittest.main()
