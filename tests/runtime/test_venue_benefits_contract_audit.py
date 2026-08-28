import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class VenueBenefitsContractAuditTests(unittest.TestCase):
    def setUp(self):
        self.property_manifest = json.loads((ROOT / "manifests/PROPERTY_MANIFEST.json").read_text(encoding="utf-8"))
        self.upgrade_manifest = json.loads((ROOT / "manifests/PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))
        self.event_execution = (ROOT / "src/bunkerfrequenz/application/event_execution_service.py").read_text(encoding="utf-8")
        self.upgrade_projection = (ROOT / "src/bunkerfrequenz/presentation/property_upgrade_projection.py").read_text(encoding="utf-8")
        self.audit = (ROOT / "docs/VENUE_BENEFITS_CONTRACT_AUDIT.md").read_text(encoding="utf-8")

    def test_existing_property_contract_has_no_running_economy_benefit(self):
        ownership = self.property_manifest["ownership"]
        self.assertFalse(ownership["resale_supported"])
        self.assertFalse(ownership["rent_supported"])
        self.assertNotIn("yield", ownership)

    def test_upgrade_values_are_confirmed_projection_facts_not_event_rules(self):
        self.assertEqual(
            self.upgrade_manifest["value_keys"],
            ["prestige", "audience_pull", "risk", "underground_factor", "utility"],
        )
        self.assertTrue(self.upgrade_manifest["projection"]["map_score_uses_confirmed_upgraded_values"])
        self.assertFalse(self.upgrade_manifest["projection"]["gameplay_event_rules_changed"])
        self.assertIn('"effective_values"', self.upgrade_projection)
        self.assertIn('"effective_values_by_location"', self.upgrade_projection)

    def test_event_availability_has_no_property_or_upgrade_authority(self):
        availability_block = self.event_execution.split("def availability", 1)[1].split("def available_actions", 1)[0]
        self.assertIn("event: EventState", availability_block)
        self.assertNotIn("PropertyState", availability_block)
        self.assertNotIn("PropertyUpgradeState", availability_block)
        self.assertNotIn("property_upgrades", availability_block)

    def test_audit_is_fail_closed_for_mechanical_benefits(self):
        self.assertIn("GO ausschließlich für ein read-only Betriebsprofil", self.audit)
        self.assertIn("NO-GO für mechanische Event-, Kosten-, Kapazitäts- oder Ertragsboni", self.audit)
        self.assertIn("keine neue Persistenz", self.audit)
        self.assertIn("keine Browserautorität", self.audit)


if __name__ == "__main__":
    unittest.main()
