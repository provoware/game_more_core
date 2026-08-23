import json
from pathlib import Path
import unittest

from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.presentation.event_timeline import build_event_timeline_projection


ROOT = Path(__file__).parents[2]
STREET_TEXTS = json.loads((ROOT / "content/de/ui/street_encounters.json").read_text(encoding="utf-8"))
DISTRICT_TEXTS = json.loads((ROOT / "content/de/ui/district_events.json").read_text(encoding="utf-8"))
INCIDENT_TEXTS = json.loads((ROOT / "content/de/ui/incidents.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests/DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = build_incident_catalog(json.loads((ROOT / "manifests/INCIDENT_MANIFEST.json").read_text(encoding="utf-8")))


def project(records, *, limit=12):
    return build_event_timeline_projection(
        records,
        street_text_catalog=STREET_TEXTS,
        district_event_manifest=DISTRICT_EVENTS,
        district_text_catalog=DISTRICT_TEXTS,
        incident_catalog=INCIDENTS,
        incident_text_catalog=INCIDENT_TEXTS,
        limit=limit,
    )


class EventTimelineProjectionTests(unittest.TestCase):
    def test_empty_and_unrelated_records_stay_honestly_empty(self):
        self.assertEqual(project([]), [])
        self.assertEqual(project([{
            "sequence": 1,
            "event_id": "profile-1",
            "event_type": "character.profile_updated",
            "payload": {},
        }]), [])

    def test_street_district_and_crisis_use_confirmed_sequence_order_and_catalog_texts(self):
        street = {
            "sequence": 7,
            "event_id": "street-7",
            "event_type": "street.encounter_resolved",
            "payload": {
                "encounter_id": "street.none",
                "polarity": "neutral",
                "approach_id": "balanced",
                "title_key": "street.none.title",
                "body_key": "street.none.body",
            },
        }
        district_spec = DISTRICT_EVENTS["events"][0]
        district = {
            "sequence": 9,
            "event_id": "district-9",
            "event_type": "world.district_effect_applied",
            "payload": {
                "source_type": "district_event",
                "source_id": f"district-event:kreuzberg:settlement-1:{district_spec['event_id']}",
                "district_id": "kreuzberg",
                "deltas": {"heat": 1, "prestige": 0, "police_pressure": 0, "scene_activity": -1},
            },
        }
        crisis = {
            "sequence": 8,
            "event_id": "crisis-8",
            "event_type": "event.incident_resolved",
            "payload": {
                "incident_type": "power_drop",
                "response_id": "power_drop.generator",
                "target_phase": "live",
            },
        }

        result = project([district, street, crisis])

        self.assertEqual([item["sequence"] for item in result], [7, 8, 9])
        self.assertEqual([item["kind"] for item in result], ["street", "crisis", "district"])
        self.assertEqual(result[0]["title"], STREET_TEXTS["street.none.title"])
        self.assertEqual(result[1]["title"], INCIDENT_TEXTS["incident.power_drop.title"])
        self.assertEqual(result[1]["body"], INCIDENT_TEXTS["incident.power_drop.generator"])
        self.assertEqual(result[2]["title"], DISTRICT_TEXTS[district_spec["title_key"]])
        self.assertEqual(result[2]["body"], DISTRICT_TEXTS[district_spec["body_key"]])

    def test_non_district_world_effect_and_malformed_supported_record_are_ignored(self):
        records = [
            {
                "sequence": 3,
                "event_id": "settlement-district",
                "event_type": "world.district_effect_applied",
                "payload": {
                    "source_type": "settlement",
                    "source_id": "settlement:settlement-1",
                    "district_id": "kreuzberg",
                },
            },
            {
                "sequence": "4",
                "event_id": "broken-street",
                "event_type": "street.encounter_resolved",
                "payload": {},
            },
        ]
        self.assertEqual(project(records), [])

    def test_missing_catalog_text_never_invents_fallback_story(self):
        record = {
            "sequence": 1,
            "event_id": "street-1",
            "event_type": "street.encounter_resolved",
            "payload": {
                "encounter_id": "street.none",
                "polarity": "neutral",
                "title_key": "street.missing.title",
                "body_key": "street.none.body",
            },
        }
        self.assertEqual(project([record]), [])

    def test_limit_keeps_latest_confirmed_records_without_reordering(self):
        records = []
        for sequence in range(1, 5):
            records.append({
                "sequence": sequence,
                "event_id": f"street-{sequence}",
                "event_type": "street.encounter_resolved",
                "payload": {
                    "encounter_id": "street.none",
                    "polarity": "neutral",
                    "approach_id": "balanced",
                    "title_key": "street.none.title",
                    "body_key": "street.none.body",
                },
            })
        self.assertEqual([item["sequence"] for item in project(records, limit=2)], [3, 4])

    def test_projection_is_detached_from_journal_payload(self):
        record = {
            "sequence": 1,
            "event_id": "street-1",
            "event_type": "street.encounter_resolved",
            "payload": {
                "encounter_id": "street.none",
                "polarity": "neutral",
                "approach_id": "balanced",
                "title_key": "street.none.title",
                "body_key": "street.none.body",
            },
        }
        result = project([record])
        result[0]["metadata"]["approach_id"] = "changed"
        self.assertEqual(record["payload"]["approach_id"], "balanced")

    def test_invalid_limit_is_rejected(self):
        for invalid in (0, -1, True):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    project([], limit=invalid)


if __name__ == "__main__":
    unittest.main()
