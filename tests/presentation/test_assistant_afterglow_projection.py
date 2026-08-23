import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.assistant_afterglow_projection import build_assistant_afterglow_projection


ROOT = Path(__file__).parents[2]
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))["jobs"]
TEXTS = json.loads((ROOT / "content" / "de" / "ui" / "assistant_afterglow.json").read_text(encoding="utf-8"))


def _confirmed_pair(round_id: str, job_id: str, *, start_sequence: int = 1):
    prefix = f"assistant:char.local:round:{round_id}"
    return [
        {
            "sequence": start_sequence,
            "event_id": f"{prefix}:job",
            "event_type": "finance.job_completed",
            "payload": {"job_id": job_id},
        },
        {
            "sequence": start_sequence + 1,
            "event_id": f"{prefix}:processed",
            "event_type": "assistant.round_processed",
            "payload": {
                "round_id": round_id,
                "character_id": "char.local",
                "job_id": job_id,
                "assistant_revision": 2,
            },
        },
    ]


class AssistantAfterglowProjectionTests(unittest.TestCase):
    def test_requires_confirmed_round_marker_and_matching_durable_job(self):
        projection = build_assistant_afterglow_projection(
            _confirmed_pair("r-7", "scene.cable_repair", start_sequence=4),
            JOBS,
            TEXTS,
        )

        self.assertTrue(projection["available"])
        self.assertEqual(len(projection["entries"]), 1)
        item = projection["entries"][0]
        self.assertEqual(item["round_id"], "r-7")
        self.assertEqual(item["job_id"], "scene.cable_repair")
        self.assertEqual(item["job_label"], "Kabel & Kleinkram reparieren")
        self.assertIn(item["variant_index"], range(3))
        self.assertFalse(projection["reroll_on_refresh"])
        self.assertFalse(projection["progression_effects"])

    def test_manual_job_marker_without_job_and_off_round_create_no_story(self):
        manual = [{
            "sequence": 1,
            "event_id": "manual-job:1:job",
            "event_type": "finance.job_completed",
            "payload": {"job_id": "scene.bar_support"},
        }]
        marker_only = [{
            "sequence": 2,
            "event_id": "assistant:char.local:round:r-2:processed",
            "event_type": "assistant.round_processed",
            "payload": {"round_id": "r-2", "character_id": "char.local", "job_id": "scene.bar_support"},
        }]
        off_round = [{
            "sequence": 3,
            "event_id": "assistant:char.local:round:r-off:processed",
            "event_type": "assistant.round_processed",
            "payload": {"round_id": "r-off", "character_id": "char.local", "job_id": None},
        }]

        for records in (manual, marker_only, off_round):
            self.assertFalse(build_assistant_afterglow_projection(records, JOBS, TEXTS)["available"])

    def test_mismatching_or_out_of_order_job_pair_fails_soft_to_no_story(self):
        mismatch = _confirmed_pair("r-mismatch", "scene.bar_support")
        mismatch[0]["payload"]["job_id"] = "scene.flyer_shift"
        out_of_order = _confirmed_pair("r-order", "scene.bar_support")
        out_of_order[0]["sequence"] = 9
        out_of_order[1]["sequence"] = 8

        self.assertEqual(build_assistant_afterglow_projection(mismatch, JOBS, TEXTS)["entries"], [])
        self.assertEqual(build_assistant_afterglow_projection(out_of_order, JOBS, TEXTS)["entries"], [])

    def test_same_confirmed_round_never_rerolls_but_many_rounds_vary(self):
        records = _confirmed_pair("stable-round", "scene.flyer_shift")
        first = build_assistant_afterglow_projection(records, JOBS, TEXTS)["entries"][0]
        second = build_assistant_afterglow_projection(records, JOBS, TEXTS)["entries"][0]
        self.assertEqual(first, second)

        variants = set()
        for number in range(1, 13):
            entry = build_assistant_afterglow_projection(
                _confirmed_pair(f"var-{number}", "scene.flyer_shift"),
                JOBS,
                TEXTS,
            )["entries"][0]
            variants.add(entry["variant_index"])
        self.assertGreaterEqual(len(variants), 2)

    def test_projection_is_bounded_ordered_and_detached(self):
        records = []
        for number in range(1, 5):
            records.extend(
                _confirmed_pair(
                    f"r-{number}",
                    "scene.flyer_shift",
                    start_sequence=number * 2 - 1,
                )
            )
        original = json.loads(json.dumps(records))

        projection = build_assistant_afterglow_projection(records, JOBS, TEXTS, limit=3)

        self.assertEqual([item["round_id"] for item in projection["entries"]], ["r-2", "r-3", "r-4"])
        projection["entries"][0]["headline"] = "changed"
        self.assertEqual(records, original)

    def test_catalog_requires_multiple_complete_variants_per_scene_job(self):
        broken = json.loads(json.dumps(TEXTS))
        broken["entries"]["scene.bar_support"] = [{"headline": "Nur eins", "body": "Zu wenig"}]
        with self.assertRaisesRegex(ValueError, "mindestens zwei Textvarianten"):
            build_assistant_afterglow_projection([], JOBS, broken)


if __name__ == "__main__":
    unittest.main()
