import json
from pathlib import Path
import unittest

from bunkerfrequenz.application.district_world_event_service import DistrictWorldEventService
from bunkerfrequenz.presentation.biography_projection import build_biography_projection


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))


class DistrictEventChainContractAuditTests(unittest.TestCase):
    def test_confirmed_district_effect_is_append_only_parent_evidence(self):
        self.assertTrue(JOURNAL["append_only"])
        self.assertEqual(JOURNAL["canonical_order_key"], ["sequence", "event_id"])
        self.assertIn("world.district_effect_applied", JOURNAL["event_types"])
        self.assertIn("causation_id", JOURNAL["optional_fields"])
        self.assertIn("correlation_id", JOURNAL["optional_fields"])

    def test_existing_source_identity_recovers_colon_rich_trigger_without_new_chain_id(self):
        service = object.__new__(DistrictWorldEventService)
        service.events = ({"event_id": "district.test_afterglow"},)
        trigger_id = "settlement:settlement:command-42"
        source_id = f"district-event:kreuzberg:{trigger_id}:district.test_afterglow"

        self.assertEqual(service._trigger_from_event_source(source_id), trigger_id)

    def test_biography_projection_is_read_only_output_not_chain_authority(self):
        district_record = {
            "event_id": "command-42:district-effect",
            "event_type": "world.district_effect_applied",
            "sequence": 7,
            "character_id": "char-1",
            "payload": {
                "source_type": "district_event",
                "source_id": "district-event:kreuzberg:settlement:settlement:command-42:district.test_afterglow",
                "district_id": "kreuzberg",
            },
        }
        biography_record = {
            "event_id": "bio-1",
            "event_type": "character.biography_entry_added",
            "sequence": 8,
            "character_id": "char-1",
            "payload": {
                "entry_id": "district-afterglow-1",
                "category": "district",
                "title_key": "story.district.afterglow.title",
                "body_key": "story.district.afterglow.body",
                "placeholders": {"district_id": "kreuzberg"},
            },
        }

        self.assertEqual(build_biography_projection("char-1", [district_record]), [])
        projection = build_biography_projection("char-1", [district_record, biography_record])
        self.assertEqual([item["event_id"] for item in projection], ["bio-1"])

    def test_follow_up_runtime_must_wait_for_explicit_catalogued_child_event_contract(self):
        event_types = set(JOURNAL["event_types"])
        self.assertFalse(
            {
                "world.district_followup_resolved",
                "world.district_chain_progressed",
                "world.district_memory_triggered",
            }
            & event_types,
            "Eine Folgeketten-Runtime darf erst nach einem expliziten Journal-Eventvertrag entstehen",
        )


if __name__ == "__main__":
    unittest.main()
