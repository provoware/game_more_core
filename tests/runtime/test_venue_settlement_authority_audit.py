import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
AUDIT = ROOT / "docs" / "VENUE_SETTLEMENT_AUTHORITY_AUDIT.md"
EVENT_SCHEMA = ROOT / "schemas" / "event_state.schema.json"
PROPERTY_SCHEMA = ROOT / "schemas" / "property_state.schema.json"
UPGRADE_SCHEMA = ROOT / "schemas" / "property_upgrade_state.schema.json"
SETTLEMENT_SCHEMA = ROOT / "schemas" / "settlement_state.schema.json"
UPGRADE_MANIFEST = ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json"
SETTLEMENT_MANIFEST = ROOT / "manifests" / "SETTLEMENT_MANIFEST.json"


class VenueSettlementAuthorityAuditTests(unittest.TestCase):
    def test_existing_states_share_location_id_authority(self):
        event = json.loads(EVENT_SCHEMA.read_text(encoding="utf-8"))
        properties = json.loads(PROPERTY_SCHEMA.read_text(encoding="utf-8"))
        upgrades = json.loads(UPGRADE_SCHEMA.read_text(encoding="utf-8"))

        event_location = event["properties"]["location"]
        owned_entry = properties["properties"]["owned"]["additionalProperties"]
        upgrade_entry = upgrades["properties"]["properties"]["additionalProperties"]

        self.assertIn("location_id", event_location["required"])
        self.assertIn("location_id", owned_entry["required"])
        self.assertIn("owner_character_id", owned_entry["required"])
        self.assertIn("location_id", upgrade_entry["required"])
        self.assertEqual(
            event_location["properties"]["location_id"]["type"], "string"
        )

    def test_audience_pull_is_confirmed_projection_input_but_not_settlement_effect(self):
        upgrades = json.loads(UPGRADE_MANIFEST.read_text(encoding="utf-8"))
        settlement = json.loads(SETTLEMENT_MANIFEST.read_text(encoding="utf-8"))

        self.assertIn("audience_pull", upgrades["value_keys"])
        self.assertEqual(upgrades["projection"]["location_value_bounds"], [0, 100])
        self.assertTrue(upgrades["projection"]["map_score_uses_confirmed_upgraded_values"])
        self.assertFalse(upgrades["projection"]["gameplay_event_rules_changed"])
        self.assertNotIn("audience_pull", settlement["source_effects"])
        self.assertFalse(settlement["scope_boundaries"]["property_changes"])

    def test_current_settlement_requires_explicit_versioned_receipt_extension(self):
        schema = json.loads(SETTLEMENT_SCHEMA.read_text(encoding="utf-8"))
        settlement = json.loads(SETTLEMENT_MANIFEST.read_text(encoding="utf-8"))

        self.assertFalse(schema["additionalProperties"])
        self.assertNotIn("venue_evidence", schema["properties"])
        self.assertNotIn("properties", settlement["required_state_blocks"])
        self.assertNotIn("property_upgrades", settlement["required_state_blocks"])

    def test_audit_keeps_evidence_go_separate_from_mechanic_go(self):
        text = AUDIT.read_text(encoding="utf-8")

        self.assertIn("GO für einen rein evidenzbasierten Authority-Bridge-Folgeslice", text)
        self.assertIn("weiterhin NO-GO für jeden Publikumskraft-Bonus", text)
        self.assertIn("event.location.location_id", text)
        self.assertIn("Settlement-Receipt-Evidence", text)
        self.assertIn("keine Venue-Bonusengine", text)
        self.assertIn("additionalProperties: false", text)
        self.assertIn("Architektur-GO für Evidence-Plumbing, Mechanik-NO-GO", text)


if __name__ == "__main__":
    unittest.main()
