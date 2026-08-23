import copy
import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.district_service import DistrictService
from bunkerfrequenz.application.district_world_event_service import DistrictWorldEventService
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))


class DistrictWorldEventNoopTests(unittest.TestCase):
    def test_no_eligible_event_is_explicit_read_only_noop(self):
        manifest = copy.deepcopy(DISTRICT_EVENTS)
        for event in manifest["events"]:
            event["requirements"] = {"minimum_heat": 101}

        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, set(JOURNAL["event_types"]))
            districts = DistrictService(kernel, DISTRICTS, CITY_MAP)
            service = DistrictWorldEventService(districts, manifest)
            service._cadence_block_reason = lambda _trigger_id: None
            before = districts.current_state().to_dict()
            context = JournalContext(
                "2026-08-23T11:30:00+02:00",
                "session-no-event",
                "player-local",
                "district",
                "friedrichshain",
                "district-event-noop",
                "district-world-event-test",
                "0.8.7-c5",
                "player-local",
            )

            result = service.trigger(
                world_seed="confirmed-world",
                district_id="friedrichshain",
                trigger_id="catalog-no-eligible-test",
                context=context,
            )

            self.assertFalse(result.triggered)
            self.assertEqual(result.no_event_reason, "no_eligible_event")
            self.assertIsNone(result.event_id)
            self.assertIsNone(result.event_instance_id)
            self.assertFalse(result.district_result.applied)
            self.assertFalse(result.district_result.idempotent_replay)
            self.assertEqual(result.district_result.committed_event_ids, ())
            self.assertEqual(result.district_result.metadata["reason"], "no_eligible_event")
            self.assertEqual(result.district_result.state.to_dict(), before)
            self.assertEqual(kernel.read_records(), ())
            self.assertIsNone(kernel.load_state())


if __name__ == "__main__":
    unittest.main()
