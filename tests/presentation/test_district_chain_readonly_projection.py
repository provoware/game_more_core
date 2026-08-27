import json
from pathlib import Path
import unittest

from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.presentation.event_timeline import build_event_timeline_projection


ROOT = Path(__file__).parents[2]
DISTRICT_TEXTS = json.loads((ROOT / "content/de/ui/district_events.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests/DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = build_incident_catalog(json.loads((ROOT / "manifests/INCIDENT_MANIFEST.json").read_text(encoding="utf-8")))
TIMELINE_JS = (ROOT / "web/a4/event_timeline.js").read_text(encoding="utf-8")


def project(records):
    return build_event_timeline_projection(
        records,
        street_text_catalog={},
        district_event_manifest=DISTRICT_EVENTS,
        district_text_catalog=DISTRICT_TEXTS,
        incident_catalog=INCIDENTS,
        incident_text_catalog={},
    )


def parent_record(*, district_id="friedrichshain", catalog_event_id="district.power_flicker", event_id="district-parent-1"):
    return {
        "sequence": 1,
        "event_id": event_id,
        "event_type": "world.district_effect_applied",
        "payload": {
            "source_type": "district_event",
            "source_id": f"district-event:{district_id}:settlement-1:{catalog_event_id}",
            "district_id": district_id,
            "deltas": {"scene_activity": -1},
        },
    }


def child_record(
    *,
    district_id="friedrichshain",
    causation_id="district-parent-1",
    parent_event_id="district-parent-1",
    followup_id="power_flicker_afterglow",
    event_id="district-child-1",
):
    return {
        "sequence": 2,
        "event_id": event_id,
        "event_type": "world.district_followup_resolved",
        "causation_id": causation_id,
        "correlation_id": f"district-chain:{parent_event_id}",
        "payload": {
            "parent_event_id": parent_event_id,
            "district_id": district_id,
            "followup_id": followup_id,
            "title_key": f"district_followup.{followup_id}.title",
            "body_key": f"district_followup.{followup_id}.body",
        },
    }


class DistrictChainReadonlyProjectionTests(unittest.TestCase):
    def test_confirmed_followup_links_to_confirmed_same_district_parent(self):
        result = project([child_record(), parent_record()])

        self.assertEqual([entry["event_id"] for entry in result], ["district-parent-1", "district-child-1"])
        child = result[1]
        self.assertEqual(child["title"], "Das Licht ist zurück – die Erinnerung bleibt")
        self.assertEqual(
            child["caused_by"],
            {"event_id": "district-parent-1", "title": "Das Netz flackert"},
        )
        self.assertEqual(child["metadata"]["district_id"], "friedrichshain")
        self.assertEqual(child["metadata"]["followup_id"], "power_flicker_afterglow")

    def test_temporary_space_afterimage_uses_the_same_readonly_causality_projection(self):
        parent = parent_record(catalog_event_id="district.temporary_space_opens", event_id="district-space-parent")
        child = child_record(
            causation_id="district-space-parent",
            parent_event_id="district-space-parent",
            followup_id="temporary_space_afterimage",
            event_id="district-space-child",
        )
        result = project([child, parent])

        self.assertEqual([entry["event_id"] for entry in result], ["district-space-parent", "district-space-child"])
        projected_child = result[1]
        self.assertEqual(projected_child["title"], "Die Tür ist zu – die Adresse lebt weiter.")
        self.assertEqual(
            projected_child["caused_by"],
            {"event_id": "district-space-parent", "title": "Eine Tür steht plötzlich offen"},
        )
        self.assertEqual(projected_child["metadata"]["followup_id"], "temporary_space_afterimage")

    def test_missing_or_cross_district_parent_never_invents_cause(self):
        missing_parent = project([child_record()])
        self.assertEqual(len(missing_parent), 1)
        self.assertNotIn("caused_by", missing_parent[0])

        wrong_district = project([parent_record(district_id="mitte"), child_record()])
        self.assertEqual(len(wrong_district), 2)
        self.assertNotIn("caused_by", wrong_district[1])

    def test_mismatched_causation_id_is_not_projected_as_valid_followup(self):
        self.assertEqual(project([child_record(causation_id="other-parent")]), [])

    def test_browser_only_renders_projected_cause_and_remains_read_only(self):
        self.assertIn("const causedBy = entry?.caused_by", TIMELINE_JS)
        self.assertIn('cause.textContent = `Folge von: ${causedBy.title}`', TIMELINE_JS)
        self.assertNotIn('method: "POST"', TIMELINE_JS)
        self.assertNotIn("sendCommand", TIMELINE_JS)
        self.assertNotIn("innerHTML", TIMELINE_JS)


if __name__ == "__main__":
    unittest.main()
