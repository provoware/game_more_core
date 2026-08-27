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


def context(command_id: str, district_id: str = "friedrichshain") -> JournalContext:
    return JournalContext(
        "2026-08-26T01:00:00+02:00",
        "session-micro-story",
        "player-local",
        "district",
        district_id,
        command_id,
        "district-chain-micro-story-test",
        "0.8.8",
        "player-local",
    )


class DistrictChainMicroStoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.districts = DistrictService(self.kernel, DISTRICTS, CITY_MAP)
        self.service = DistrictWorldEventService(self.districts, DISTRICT_EVENTS)
        self.service._cadence_block_reason = lambda _trigger_id: None

    def _force_event(self, event_id: str) -> None:
        selected = next(item for item in self.service.events if item["event_id"] == event_id)
        self.service._select = lambda _eligible, **_kwargs: selected

    def _trigger(self, event_id: str, cycle: str, command: str, district_id: str = "friedrichshain"):
        self._force_event(event_id)
        return self.service.trigger(
            world_seed="story-seed",
            district_id=district_id,
            trigger_id=cycle,
            context=context(command, district_id),
        )

    def test_power_flicker_followup_is_delayed_until_next_confirmed_district_cycle(self):
        first = self._trigger("district.power_flicker", "cycle-001", "district-story-001")
        first_records = self.kernel.read_records()
        self.assertEqual(first.event_id, "district.power_flicker")
        self.assertEqual([r["event_type"] for r in first_records], ["world.district_effect_applied"])

        second = self._trigger("district.word_of_mouth_wave", "cycle-002", "district-story-002")
        records = self.kernel.read_records()
        parents = [r for r in records if r["event_type"] == "world.district_effect_applied"]
        children = [r for r in records if r["event_type"] == "world.district_followup_resolved"]

        self.assertEqual(second.event_id, "district.word_of_mouth_wave")
        self.assertEqual(len(parents), 2)
        self.assertEqual(len(children), 1)
        child = children[0]
        first_parent = parents[0]
        self.assertEqual(child["causation_id"], first_parent["event_id"])
        self.assertEqual(child["correlation_id"], f"district-chain:{first_parent['event_id']}")
        self.assertEqual(child["payload"]["parent_event_id"], first_parent["event_id"])
        self.assertEqual(child["payload"]["district_id"], "friedrichshain")
        self.assertEqual(child["payload"]["followup_id"], "power_flicker_afterglow")
        self.assertEqual(child["payload"]["title_key"], "district_followup.power_flicker_afterglow.title")
        self.assertEqual(second.district_result.metadata["followup"]["event_id"], child["event_id"])

    def test_retry_of_second_cycle_does_not_duplicate_followup(self):
        self._trigger("district.power_flicker", "cycle-001", "district-story-001")
        self._trigger("district.word_of_mouth_wave", "cycle-002", "district-story-002")
        before = self.kernel.read_records()

        retry = self.service.trigger(
            world_seed="different-seed",
            district_id="friedrichshain",
            trigger_id="cycle-002",
            context=context("district-story-002-retry"),
        )

        self.assertTrue(retry.district_result.idempotent_replay)
        self.assertEqual(self.kernel.read_records(), before)

    def test_followup_never_crosses_district_boundary(self):
        self._trigger("district.power_flicker", "cycle-001", "district-story-001")
        self._trigger("district.word_of_mouth_wave", "cycle-002", "district-story-002", "mitte")

        children = [r for r in self.kernel.read_records() if r["event_type"] == "world.district_followup_resolved"]
        self.assertEqual(children, [])

    def test_temporary_space_afterimage_is_delayed_and_uses_same_contract(self):
        first = self._trigger("district.temporary_space_opens", "cycle-space-001", "district-space-001")
        self.assertEqual(first.event_id, "district.temporary_space_opens")
        self.assertEqual(
            [r["event_type"] for r in self.kernel.read_records()],
            ["world.district_effect_applied"],
        )

        second = self._trigger("district.word_of_mouth_wave", "cycle-space-002", "district-space-002")
        records = self.kernel.read_records()
        parents = [r for r in records if r["event_type"] == "world.district_effect_applied"]
        children = [r for r in records if r["event_type"] == "world.district_followup_resolved"]

        self.assertEqual(len(children), 1)
        parent = parents[0]
        child = children[0]
        self.assertEqual(child["event_type"], "world.district_followup_resolved")
        self.assertEqual(child["causation_id"], parent["event_id"])
        self.assertEqual(child["correlation_id"], f"district-chain:{parent['event_id']}")
        self.assertEqual(child["payload"]["parent_event_id"], parent["event_id"])
        self.assertEqual(child["payload"]["district_id"], "friedrichshain")
        self.assertEqual(child["payload"]["followup_id"], "temporary_space_afterimage")
        self.assertEqual(child["payload"]["title_key"], "district_followup.temporary_space_afterimage.title")
        self.assertEqual(child["payload"]["body_key"], "district_followup.temporary_space_afterimage.body")
        self.assertEqual(second.district_result.metadata["followup"]["event_id"], child["event_id"])

    def test_temporary_space_afterimage_retry_is_exactly_once(self):
        self._trigger("district.temporary_space_opens", "cycle-space-001", "district-space-001")
        self._trigger("district.word_of_mouth_wave", "cycle-space-002", "district-space-002")
        before = self.kernel.read_records()

        retry = self.service.trigger(
            world_seed="other-seed",
            district_id="friedrichshain",
            trigger_id="cycle-space-002",
            context=context("district-space-002-retry"),
        )

        self.assertTrue(retry.district_result.idempotent_replay)
        self.assertEqual(self.kernel.read_records(), before)
        self.assertEqual(
            len([r for r in before if r["event_type"] == "world.district_followup_resolved"]),
            1,
        )

    def test_temporary_space_afterimage_never_crosses_district_boundary(self):
        self._trigger("district.temporary_space_opens", "cycle-space-001", "district-space-001")
        self._trigger("district.word_of_mouth_wave", "cycle-space-002", "district-space-002", "mitte")

        children = [r for r in self.kernel.read_records() if r["event_type"] == "world.district_followup_resolved"]
        self.assertEqual(children, [])

    def test_only_one_pending_followup_is_resolved_per_district_cycle(self):
        self._trigger("district.power_flicker", "cycle-001", "district-story-001")
        self._trigger("district.temporary_space_opens", "cycle-002", "district-story-002")
        children_after_second = [
            r for r in self.kernel.read_records() if r["event_type"] == "world.district_followup_resolved"
        ]
        self.assertEqual(len(children_after_second), 1)
        self.assertEqual(children_after_second[0]["payload"]["followup_id"], "power_flicker_afterglow")

        self._trigger("district.word_of_mouth_wave", "cycle-003", "district-story-003")
        children = [r for r in self.kernel.read_records() if r["event_type"] == "world.district_followup_resolved"]
        self.assertEqual(len(children), 2)
        self.assertEqual(
            {child["payload"]["followup_id"] for child in children},
            {"power_flicker_afterglow", "temporary_space_afterimage"},
        )


if __name__ == "__main__":
    unittest.main()
