import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.district_world_event_service import DistrictWorldEventService
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel
from bunkerfrequenz.presentation.biography_projection import build_biography_projection


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))


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

    def test_follow_up_contract_v1_catalogues_one_child_and_parent_binding(self):
        contract = DISTRICT_EVENTS["follow_up_contract"]
        self.assertEqual(contract["journal_event_type"], "world.district_followup_resolved")
        self.assertEqual(contract["parent_event_type"], "world.district_effect_applied")
        self.assertEqual(contract["required_payload_fields"], ["parent_event_id", "district_id", "followup_id"])
        self.assertEqual(contract["causation_id_source"], "parent_event_id")
        self.assertEqual(contract["correlation_id_pattern"], "district-chain:{parent_event_id}")
        self.assertTrue(contract["district_must_match_parent"])
        self.assertTrue(contract["runtime_authority_only"])
        self.assertFalse(contract["client_can_write"])
        self.assertIn(contract["journal_event_type"], JOURNAL["event_types"])
        self.assertIn(contract["journal_event_type"], JOURNAL["undo_policy_groups"]["not_user_undoable"])

    def test_persistence_preserves_causation_and_exact_retry_is_idempotent(self):
        event_type = DISTRICT_EVENTS["follow_up_contract"]["journal_event_type"]
        parent_event_id = "command-42:district-effect"
        child = {
            "event_id": "district-followup:command-42:district-effect:afterglow-1",
            "event_type": event_type,
            "causation_id": parent_event_id,
            "correlation_id": f"district-chain:{parent_event_id}",
            "payload": {
                "parent_event_id": parent_event_id,
                "district_id": "kreuzberg",
                "followup_id": "afterglow-1",
            },
        }
        context = JournalContext(
            "2026-08-25T22:00:00+02:00",
            "session-1",
            "player-1",
            "district",
            "kreuzberg",
            "command-42",
            "runtime",
            "0.8.8",
            "char-1",
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kernel = PersistenceKernel(root, set(JOURNAL["event_types"]))
            first = kernel.commit("chain-tx-1", [child], {"ok": True}, context)
            self.assertEqual(first.event_ids, (child["event_id"],))

            stored = json.loads((root / "journal" / "events.jsonl").read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(stored["causation_id"], parent_event_id)
            self.assertEqual(stored["correlation_id"], f"district-chain:{parent_event_id}")
            self.assertEqual(stored["payload"]["district_id"], "kreuzberg")

            retry = kernel.commit("chain-tx-2", [child], {"ok": False}, context)
            self.assertEqual(retry.event_ids, ())
            self.assertEqual(kernel.load_state(), {"ok": True})

            conflicting_parent = dict(child)
            conflicting_parent["payload"] = dict(child["payload"], parent_event_id="other-parent")
            with self.assertRaises(PersistenceError):
                kernel.commit("chain-tx-3", [conflicting_parent], {"ok": False}, context)


if __name__ == "__main__":
    unittest.main()
