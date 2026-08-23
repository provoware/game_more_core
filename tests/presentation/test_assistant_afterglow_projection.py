import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.assistant_afterglow_projection import build_assistant_afterglow_projection


ROOT = Path(__file__).parents[2]
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))["jobs"]
TEXTS = json.loads((ROOT / "content" / "de" / "ui" / "assistant_afterglow.json").read_text(encoding="utf-8"))


class AssistantAfterglowProjectionTests(unittest.TestCase):
    def test_requires_confirmed_round_marker_and_matching_durable_job(self):
        records = [
            {
                "sequence": 4,
                "event_id": "assistant:char.local:round:r-7:job",
                "event_type": "finance.job_completed",
                "payload": {"job_id": "scene.cable_repair"},
            },
            {
                "sequence": 5,
                "event_id": "assistant:char.local:round:r-7:processed",
                "event_type": "assistant.round_processed",
                "payload": {
                    "round_id": "r-7",
                    "character_id": "char.local",
                    "job_id": "scene.cable_repair",
                    "assistant_revision": 2,
                },
            },
        ]

        projection = build_assistant_afterglow_projection(records, JOBS, TEXTS)

        self.assertTrue(projection["available"])
        self.assertEqual(len(projection["entries"]), 1)
        item = projection["entries"][0]
        self.assertEqual(item["round_id"], "r-7")
        self.assertEqual(item["job_id"], "scene.cable_repair")
        self.assertEqual(item["job_label"], "Kabel & Kleinkram reparieren")
        self.assertIn("Wackler", item["headline"])

    def test_manual_job_or_marker_without_matching_job_creates_no_story(self):
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

        self.assertFalse(build_assistant_afterglow_projection(manual, JOBS, TEXTS)["available"])
        self.assertFalse(build_assistant_afterglow_projection(marker_only, JOBS, TEXTS)["available"])

    def test_assistant_off_round_has_no_friendship_reaction(self):
        records = [{
            "sequence": 3,
            "event_id": "assistant:char.local:round:r-off:processed",
            "event_type": "assistant.round_processed",
            "payload": {"round_id": "r-off", "character_id": "char.local", "job_id": None},
        }]
        projection = build_assistant_afterglow_projection(records, JOBS, TEXTS)
        self.assertEqual(projection["entries"], [])

    def test_projection_is_bounded_ordered_and_detached(self):
        records = []
        for number in range(1, 5):
            prefix = f"assistant:char.local:round:r-{number}"
            records.extend([
                {
                    "sequence": number * 2 - 1,
                    "event_id": f"{prefix}:job",
                    "event_type": "finance.job_completed",
                    "payload": {"job_id": "scene.flyer_shift"},
                },
                {
                    "sequence": number * 2,
                    "event_id": f"{prefix}:processed",
                    "event_type": "assistant.round_processed",
                    "payload": {"round_id": f"r-{number}", "character_id": "char.local", "job_id": "scene.flyer_shift"},
                },
            ])
        original = json.loads(json.dumps(records))

        projection = build_assistant_afterglow_projection(records, JOBS, TEXTS, limit=3)

        self.assertEqual([item["round_id"] for item in projection["entries"]], ["r-2", "r-3", "r-4"])
        projection["entries"][0]["headline"] = "changed"
        self.assertEqual(records, original)


if __name__ == "__main__":
    unittest.main()
