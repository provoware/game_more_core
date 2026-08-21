from copy import deepcopy
import json
from pathlib import Path
import unittest

from bunkerfrequenz.presentation.biography_projection import build_biography_projection


def biography_record(event_id="event-1", sequence=1, character_id="character-1"):
    return {
        "event_id": event_id,
        "event_type": "character.biography_entry_added",
        "sequence": sequence,
        "character_id": character_id,
        "payload": {
            "entry_id": f"entry-{event_id}",
            "category": "event",
            "title_key": "biography.event.title",
            "body_key": "biography.event.body",
            "placeholders": {"location": "location-1"},
        },
    }


class BiographyProjectionTest(unittest.TestCase):
    def test_accepts_only_catalogued_biography_event_type(self):
        manifest = json.loads(Path("manifests/JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertIn("character.biography_entry_added", manifest["event_types"])
        regular_event = biography_record("regular")
        regular_event["event_type"] = "event.completed"
        unknown_event = biography_record("unknown")
        unknown_event["event_type"] = "ui.biography_clicked"

        self.assertEqual(build_biography_projection("character-1", [regular_event, unknown_event]), [])

    def test_rejects_foreign_character_id(self):
        self.assertEqual(build_biography_projection("character-1", [biography_record(character_id="other")]), [])

    def test_rejects_missing_required_record_or_payload_fields(self):
        for field in ("event_id", "event_type", "sequence", "character_id", "payload"):
            record = biography_record()
            del record[field]
            with self.subTest(field=field):
                self.assertEqual(build_biography_projection("character-1", [record]), [])
        for field in ("entry_id", "category", "title_key", "body_key", "placeholders"):
            record = biography_record()
            del record["payload"][field]
            with self.subTest(payload_field=field):
                self.assertEqual(build_biography_projection("character-1", [record]), [])

    def test_sorts_by_sequence_then_event_id_stably(self):
        records = [
            biography_record("event-c", 2),
            biography_record("event-b", 1),
            biography_record("event-a", 1),
        ]

        result = build_biography_projection("character-1", records)

        self.assertEqual([entry["event_id"] for entry in result], ["event-a", "event-b", "event-c"])
        self.assertEqual(
            set(result[0]),
            {"entry_id", "event_id", "category", "title_key", "body_key", "placeholders", "sequence"},
        )

    def test_does_not_change_or_reuse_input_data(self):
        records = [biography_record()]
        before = deepcopy(records)

        result = build_biography_projection("character-1", records)
        result[0]["placeholders"]["location"] = "changed"

        self.assertEqual(records, before)


if __name__ == "__main__":
    unittest.main()
