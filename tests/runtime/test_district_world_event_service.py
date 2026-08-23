import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.district_recovery import replay_district_event
from bunkerfrequenz.application.district_service import DistrictService
from bunkerfrequenz.application.district_world_event_service import DistrictWorldEventService
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, district_id: str = "friedrichshain") -> JournalContext:
    return JournalContext(
        "2026-08-23T05:00:00+02:00",
        "session-district-event",
        "player-local",
        "district",
        district_id,
        command_id,
        "district-world-event-test",
        "0.8.7-c2",
        "player-local",
    )


class DistrictWorldEventServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.districts = DistrictService(self.kernel, DISTRICTS, CITY_MAP)
        self.service = DistrictWorldEventService(self.districts, DISTRICT_EVENTS)

    def test_same_seed_district_and_trigger_are_deterministic_across_saves(self):
        first = self.service.trigger(
            world_seed="berlin-world-1",
            district_id="friedrichshain",
            trigger_id="cycle-001",
            context=context("district-event-a"),
        )

        other_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(other_tmp.cleanup)
        other_kernel = PersistenceKernel(other_tmp.name, ALLOWED)
        other_districts = DistrictService(other_kernel, DISTRICTS, CITY_MAP)
        other_service = DistrictWorldEventService(other_districts, DISTRICT_EVENTS)
        second = other_service.trigger(
            world_seed="berlin-world-1",
            district_id="friedrichshain",
            trigger_id="cycle-001",
            context=JournalContext(
                "2026-08-23T09:00:00+02:00",
                "different-session",
                "player-local",
                "district",
                "friedrichshain",
                "district-event-b",
                "district-world-event-test",
                "0.8.7-c2",
                "player-local",
            ),
        )

        self.assertEqual(first.event_id, second.event_id)
        self.assertEqual(first.district_result.state.metrics, second.district_result.state.metrics)

    def test_retry_cannot_reroll_or_double_apply_even_with_different_seed(self):
        first = self.service.trigger(
            world_seed="confirmed-seed",
            district_id="friedrichshain",
            trigger_id="cycle-retry",
            context=context("district-event-first"),
        )
        records_after_first = self.kernel.read_records()
        revision_after_first = first.district_result.state.revision

        retry = self.service.trigger(
            world_seed="tampered-different-seed",
            district_id="friedrichshain",
            trigger_id="cycle-retry",
            context=context("district-event-retry"),
        )

        self.assertEqual(retry.event_id, first.event_id)
        self.assertTrue(retry.district_result.idempotent_replay)
        self.assertEqual(retry.district_result.state.revision, revision_after_first)
        self.assertEqual(self.kernel.read_records(), records_after_first)
        matching_sources = [
            source for source in retry.district_result.state.applied_sources
            if source.startswith("district-event:friedrichshain:cycle-retry:")
        ]
        self.assertEqual(matching_sources, [first.event_instance_id])

    def test_requirements_filter_catalog_before_weighted_selection(self):
        current = self.districts.current_state().to_dict()
        current["metrics"]["friedrichshain"] = {
            "heat": 0,
            "prestige": 0,
            "police_pressure": 10,
            "scene_activity": 0,
        }
        self.kernel.initialize_state({"districts": current})

        result = self.service.trigger(
            world_seed="requirements-seed",
            district_id="friedrichshain",
            trigger_id="only-open-space",
            context=context("district-event-requirements"),
        )

        self.assertEqual(result.event_id, "district.temporary_space_opens")
        self.assertEqual(result.district_result.state.last_change["source_type"], "district_event")
        self.assertEqual(result.district_result.state.last_change["deltas"], {
            "heat": 1,
            "prestige": 2,
            "police_pressure": 0,
            "scene_activity": 5,
        })

    def test_effect_is_journaled_once_and_recovery_restores_district_state(self):
        result = self.service.trigger(
            world_seed="recovery-seed",
            district_id="friedrichshain",
            trigger_id="recovery-cycle",
            context=context("district-event-recovery"),
        )
        records = [record for record in self.kernel.read_records() if record["event_type"] == "world.district_effect_applied"]

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["payload"]["source_type"], "district_event")
        self.assertEqual(records[0]["payload"]["source_id"], result.event_instance_id)
        replayed = replay_district_event({}, records[0])
        self.assertEqual(replayed["districts"], result.district_result.state.to_dict())

    def test_invalid_district_context_fails_before_write(self):
        with self.assertRaisesRegex(ValueError, "passenden District-Kontext"):
            self.service.trigger(
                world_seed="safe-seed",
                district_id="friedrichshain",
                trigger_id="bad-context",
                context=context("district-event-wrong", "mitte"),
            )
        self.assertEqual(self.kernel.read_records(), ())
        self.assertIsNone(self.kernel.load_state())


if __name__ == "__main__":
    unittest.main()
