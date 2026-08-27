import unittest

from bunkerfrequenz.presentation.event_timeline import build_event_timeline_projection


STREET_TEXT = {
    "street.cable_tip.title": "Kabeltipp am Bauzaun",
    "street.cable_tip.body": "Ein Kabeltipp bleibt hängen.",
    "street.cable_tip.echo.title": "Der Tipp macht die Runde",
    "street.cable_tip.echo.body": "Derselbe Kabeltrick taucht später wieder auf.",
}


def project(records):
    return build_event_timeline_projection(
        records,
        street_text_catalog=STREET_TEXT,
        district_event_manifest={"events": []},
        district_text_catalog={},
        incident_catalog={},
        incident_text_catalog={},
    )


def parent(*, sequence=1, character_id="player-local"):
    return {
        "sequence": sequence,
        "event_id": "walk-001:001",
        "event_type": "street.encounter_resolved",
        "entity_id": character_id,
        "payload": {
            "encounter_id": "street.cable_tip",
            "polarity": "positive",
            "approach_id": "balanced",
            "title_key": "street.cable_tip.title",
            "body_key": "street.cable_tip.body",
        },
    }


def followup(*, sequence=2, character_id="player-local", causation_id="walk-001:001"):
    return {
        "sequence": sequence,
        "event_id": "street-followup:walk-001:001:cable_tip_echo",
        "event_type": "street.followup_resolved",
        "causation_id": causation_id,
        "payload": {
            "parent_event_id": "walk-001:001",
            "character_id": character_id,
            "followup_id": "cable_tip_echo",
            "title_key": "street.cable_tip.echo.title",
            "body_key": "street.cable_tip.echo.body",
        },
    }


class StreetChainReadonlyProjectionTests(unittest.TestCase):
    def test_confirmed_followup_projects_with_verified_parent_cause(self):
        timeline = project([parent(), followup()])

        self.assertEqual([entry["title"] for entry in timeline], [
            "Kabeltipp am Bauzaun",
            "Der Tipp macht die Runde",
        ])
        child = timeline[1]
        self.assertEqual(child["kind"], "street")
        self.assertEqual(child["metadata"]["character_id"], "player-local")
        self.assertEqual(child["caused_by"], {
            "event_id": "walk-001:001",
            "title": "Kabeltipp am Bauzaun",
        })

    def test_character_mismatch_keeps_followup_visible_but_does_not_invent_cause(self):
        timeline = project([parent(character_id="player-local"), followup(character_id="other-character")])

        self.assertEqual(len(timeline), 2)
        self.assertNotIn("caused_by", timeline[1])

    def test_wrong_causation_id_rejects_followup_projection(self):
        timeline = project([parent(), followup(causation_id="different-parent")])

        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]["title"], "Kabeltipp am Bauzaun")

    def test_followup_before_parent_does_not_invent_cause(self):
        timeline = project([followup(sequence=1), parent(sequence=2)])
        child = next(entry for entry in timeline if entry["title"] == "Der Tipp macht die Runde")

        self.assertNotIn("caused_by", child)


if __name__ == "__main__":
    unittest.main()
