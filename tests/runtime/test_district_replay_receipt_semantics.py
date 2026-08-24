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
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-24T03:00:00+02:00",
        "session-district-receipt",
        "player-local",
        "district",
        "friedrichshain",
        command_id,
        "district-receipt-semantics-test",
        "0.8.8",
        "player-local",
    )


class DistrictReplayReceiptSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.districts = DistrictService(self.kernel, DISTRICTS, CITY_MAP)
        self.service = DistrictWorldEventService(self.districts, DISTRICT_EVENTS)

    def test_applied_retry_and_no_event_have_distinct_receipt_semantics(self):
        self.service._cadence_block_reason = lambda _trigger_id: None
        applied = self.service.trigger(
            world_seed="receipt-seed",
            district_id="friedrichshain",
            trigger_id="receipt-cycle",
            context=context("receipt-first"),
        )
        records_after_apply = self.kernel.read_records()

        self.assertTrue(applied.triggered)
        self.assertIsNone(applied.no_event_reason)
        self.assertTrue(applied.district_result.applied)
        self.assertFalse(applied.district_result.idempotent_replay)
        self.assertEqual(len(applied.district_result.committed_event_ids), 1)

        replay = self.service.trigger(
            world_seed="tampered-seed-must-not-reroll",
            district_id="friedrichshain",
            trigger_id="receipt-cycle",
            context=context("receipt-retry"),
        )

        self.assertTrue(replay.triggered)
        self.assertIsNone(replay.no_event_reason)
        self.assertTrue(replay.district_result.applied)
        self.assertTrue(replay.district_result.idempotent_replay)
        self.assertEqual(replay.district_result.committed_event_ids, ())
        self.assertTrue(replay.district_result.metadata["replay"])
        self.assertEqual(replay.event_instance_id, applied.event_instance_id)
        self.assertEqual(self.kernel.read_records(), records_after_apply)

        self.service._cadence_block_reason = lambda _trigger_id: "cooldown_active"
        no_event = self.service.trigger(
            world_seed="unused-while-blocked",
            district_id="friedrichshain",
            trigger_id="blocked-cycle",
            context=context("receipt-blocked"),
        )

        self.assertFalse(no_event.triggered)
        self.assertEqual(no_event.no_event_reason, "cooldown_active")
        self.assertFalse(no_event.district_result.applied)
        self.assertFalse(no_event.district_result.idempotent_replay)
        self.assertEqual(no_event.district_result.committed_event_ids, ())
        self.assertEqual(no_event.district_result.metadata["reason"], "cooldown_active")
        self.assertEqual(self.kernel.read_records(), records_after_apply)

    def test_no_event_receipt_keeps_source_identity_without_inventing_event_instance(self):
        self.service._cadence_block_reason = lambda _trigger_id: "confirmed_time_unavailable"
        result = self.service.trigger(
            world_seed="unused",
            district_id="friedrichshain",
            trigger_id="missing-time",
            context=context("receipt-missing-time"),
        )

        self.assertIsNone(result.event_id)
        self.assertIsNone(result.event_instance_id)
        self.assertEqual(
            result.district_result.metadata["source_id"],
            "district-event:friedrichshain:missing-time",
        )
        self.assertEqual(result.no_event_reason, result.district_result.metadata["reason"])
        self.assertEqual(self.kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
