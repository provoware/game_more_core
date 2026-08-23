import json
from copy import deepcopy
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


class DistrictEventCatalogDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.districts = DistrictService(kernel, DISTRICTS, CITY_MAP)

    def test_out_of_bounds_effect_names_event_and_field(self):
        manifest = deepcopy(EVENTS)
        event = manifest["events"][0]
        event["effects"]["heat"] = 999

        with self.assertRaisesRegex(
            ValueError,
            rf"events\[0\]\({event['event_id']}\)\.effects\.heat.*außerhalb",
        ):
            DistrictWorldEventService(self.districts, manifest)

    def test_unknown_requirement_names_event_and_field(self):
        manifest = deepcopy(EVENTS)
        event = manifest["events"][1]
        event["requirements"]["minimum_invented_metric"] = 1

        with self.assertRaisesRegex(
            ValueError,
            rf"events\[1\]\({event['event_id']}\)\.requirements\.minimum_invented_metric.*unbekannte Metrik",
        ):
            DistrictWorldEventService(self.districts, manifest)

    def test_duplicate_id_names_duplicate_entry(self):
        manifest = deepcopy(EVENTS)
        manifest["events"][1]["event_id"] = manifest["events"][0]["event_id"]

        with self.assertRaisesRegex(ValueError, r"events\[1\]\.event_id.*doppelt"):
            DistrictWorldEventService(self.districts, manifest)


if __name__ == "__main__":
    unittest.main()
