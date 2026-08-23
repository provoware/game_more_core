import copy
import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.district_service import DistrictService
from bunkerfrequenz.application.district_world_event_service import DistrictWorldEventService
from bunkerfrequenz.infrastructure.persistence import PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


class DistrictWorldEventCatalogValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.districts = DistrictService(kernel, DISTRICTS, CITY_MAP)

    def build(self, manifest):
        return DistrictWorldEventService(self.districts, manifest)

    def test_real_catalog_is_accepted_fail_fast(self):
        service = self.build(EVENTS)
        self.assertEqual(len(service.events), 4)

    def test_duplicate_id_and_weight_total_mismatch_are_rejected_at_startup(self):
        duplicate = copy.deepcopy(EVENTS)
        duplicate["events"][1]["event_id"] = duplicate["events"][0]["event_id"]
        with self.assertRaisesRegex(ValueError, "doppelte Event-ID"):
            self.build(duplicate)

        bad_total = copy.deepcopy(EVENTS)
        bad_total["events"][0]["weight"] += 1
        with self.assertRaisesRegex(ValueError, "Kataloggewicht"):
            self.build(bad_total)

    def test_effect_shape_and_bounds_are_rejected_before_any_trigger(self):
        unknown_metric = copy.deepcopy(EVENTS)
        unknown_metric["events"][0]["effects"]["invented_metric"] = 1
        with self.assertRaisesRegex(ValueError, "exakt alle District-Metriken"):
            self.build(unknown_metric)

        out_of_bounds = copy.deepcopy(EVENTS)
        out_of_bounds["events"][0]["effects"]["heat"] = 7
        with self.assertRaisesRegex(ValueError, "außerhalb des Vertrags"):
            self.build(out_of_bounds)

    def test_unknown_requirement_metric_and_missing_text_key_are_rejected(self):
        bad_requirement = copy.deepcopy(EVENTS)
        bad_requirement["events"][0]["requirements"] = {"minimum_invented_metric": 1}
        with self.assertRaisesRegex(ValueError, "unbekannte Metrik"):
            self.build(bad_requirement)

        missing_text_key = copy.deepcopy(EVENTS)
        missing_text_key["events"][0]["title_key"] = ""
        with self.assertRaisesRegex(ValueError, "title_key"):
            self.build(missing_text_key)


if __name__ == "__main__":
    unittest.main()
