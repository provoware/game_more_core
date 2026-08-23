import json
from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bunkerfrequenz.application.district_service import DistrictService
from bunkerfrequenz.application.district_world_event_service import DistrictWorldEventService
from bunkerfrequenz.infrastructure.persistence import PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))


class DistrictEventCadenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        kernel = PersistenceKernel(self.tmp.name, set(JOURNAL["event_types"]))
        self.service = DistrictWorldEventService(DistrictService(kernel, DISTRICTS, CITY_MAP), DISTRICT_EVENTS)

    def test_manifest_requires_confirmed_game_world_time_and_24_hour_global_cooldown(self):
        cadence = DISTRICT_EVENTS["cadence"]
        self.assertEqual(cadence["authority"], "confirmed_event_game_world_time")
        self.assertEqual(cadence["timestamp_source"], "event.time_window.start_local")
        self.assertEqual(cadence["minimum_hours_between_events"], 24)
        self.assertEqual(cadence["scope"], "global")
        self.assertFalse(cadence["system_time_is_sole_authority"])

    def test_cooldown_blocks_before_24_hours_and_opens_at_boundary(self):
        prior_trigger = "settlement:settlement:old-command"
        current_trigger = "settlement:settlement:new-command"
        record = {
            "event_type": "world.district_effect_applied",
            "payload": {
                "source_type": "district_event",
                "source_id": "district-event:mitte:settlement:settlement:old-command:district.power_flicker",
            },
        }
        anchors = {
            prior_trigger: datetime.fromisoformat("2026-08-22T12:00:00+02:00"),
            current_trigger: datetime.fromisoformat("2026-08-23T11:59:59+02:00"),
        }
        with patch.object(self.service.district_service.persistence, "read_records", return_value=(record,)), patch.object(
            self.service, "_confirmed_game_time", side_effect=lambda trigger: anchors.get(trigger)
        ):
            self.assertEqual(self.service._cadence_block_reason(current_trigger), "cooldown_active")

        anchors[current_trigger] = datetime.fromisoformat("2026-08-23T12:00:00+02:00")
        with patch.object(self.service.district_service.persistence, "read_records", return_value=(record,)), patch.object(
            self.service, "_confirmed_game_time", side_effect=lambda trigger: anchors.get(trigger)
        ):
            self.assertIsNone(self.service._cadence_block_reason(current_trigger))

    def test_missing_or_backwards_confirmed_time_fails_closed_without_system_clock(self):
        current_trigger = "settlement:settlement:new-command"
        self.assertEqual(self.service._cadence_block_reason(current_trigger), "confirmed_time_unavailable")

        prior_trigger = "settlement:settlement:old-command"
        record = {
            "event_type": "world.district_effect_applied",
            "payload": {
                "source_type": "district_event",
                "source_id": "district-event:mitte:settlement:settlement:old-command:district.power_flicker",
            },
        }
        anchors = {
            prior_trigger: datetime.fromisoformat("2026-08-24T12:00:00+02:00"),
            current_trigger: datetime.fromisoformat("2026-08-23T12:00:00+02:00"),
        }
        with patch.object(self.service.district_service.persistence, "read_records", return_value=(record,)), patch.object(
            self.service, "_confirmed_game_time", side_effect=lambda trigger: anchors.get(trigger)
        ):
            self.assertEqual(self.service._cadence_block_reason(current_trigger), "cooldown_active")


if __name__ == "__main__":
    unittest.main()
