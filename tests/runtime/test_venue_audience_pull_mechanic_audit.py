import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class VenueAudiencePullMechanicAuditTests(unittest.TestCase):
    def setUp(self):
        self.upgrade_manifest = json.loads(
            (ROOT / "manifests/PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8")
        )
        self.settlement_manifest = json.loads(
            (ROOT / "manifests/SETTLEMENT_MANIFEST.json").read_text(encoding="utf-8")
        )
        self.scene_job_manifest = json.loads(
            (ROOT / "manifests/SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8")
        )
        self.audit = (ROOT / "docs/VENUE_AUDIENCE_PULL_MECHANIC_AUDIT.md").read_text(
            encoding="utf-8"
        )

    def test_audience_pull_is_confirmed_bounded_value_without_event_rule_authority(self):
        self.assertIn("audience_pull", self.upgrade_manifest["value_keys"])
        self.assertEqual(self.upgrade_manifest["projection"]["location_value_bounds"], [0, 100])
        self.assertFalse(self.upgrade_manifest["projection"]["gameplay_event_rules_changed"])

    def test_settlement_has_no_property_input_or_venue_effect_contract(self):
        required = self.settlement_manifest["required_state_blocks"]
        self.assertNotIn("property", required)
        self.assertNotIn("property_upgrades", required)
        self.assertFalse(self.settlement_manifest["scope_boundaries"]["property_changes"])
        self.assertNotIn("audience_pull", self.settlement_manifest["source_effects"])
        self.assertNotIn("venue_audience_pull", self.settlement_manifest["application"])

    def test_audit_freshness_guard_pins_exact_settlement_authority_surface(self):
        self.assertEqual(
            self.settlement_manifest["required_state_blocks"],
            ["event", "economy", "character"],
        )
        self.assertEqual(
            self.settlement_manifest["optional_initial_state_blocks"],
            ["incidents"],
        )
        self.assertEqual(
            self.settlement_manifest["source_effects"],
            [
                "budget_delta_cents",
                "reputation_delta",
                "crew_stress_delta",
                "stability_delta",
                "heat_delta",
            ],
        )
        self.assertEqual(
            self.settlement_manifest["application"],
            {
                "budget_delta_cents": "economy_ledger_settlement_transaction",
                "reputation_delta": "character.reputation_changed",
                "crew_stress_delta": "character.resources_changed",
                "stability_delta": "settlement_receipt_event_outcome_only",
                "heat_delta": "settlement_receipt_event_outcome_only",
            },
        )
        self.assertEqual(
            self.settlement_manifest["receipt_invariants"],
            {
                "budget_delta_matches_effect": True,
                "stress_delta_matches_effect": True,
                "reputation_delta_matches_effect": True,
            },
        )
        self.assertEqual(
            self.settlement_manifest["scope_boundaries"],
            {
                "persistent_district_simulation": False,
                "heat_is_district_state": False,
                "stability_is_world_state": False,
                "client_changes": False,
                "property_changes": False,
                "network_changes": False,
            },
        )

    def test_scene_jobs_do_not_offer_modifier_shortcut(self):
        availability = self.scene_job_manifest["availability"]
        exhaustion = self.scene_job_manifest["exhaustion_policy"]
        self.assertFalse(availability["client_can_supply_payout_or_effects"])
        self.assertFalse(exhaustion["client_can_supply_modifier"])

    def test_audit_fails_closed_without_second_bonus_architecture(self):
        self.assertIn("NO-GO", self.audit)
        self.assertIn("audience_pull", self.audit)
        self.assertIn("Keine generische Venue-Bonusengine", self.audit)
        self.assertIn("kein stiller Settlement-Multiplikator", self.audit)
        self.assertIn("Replay/Recovery mit demselben Ergebnis", self.audit)
        self.assertIn("Audit-Freshness-Guard", self.audit)
        self.assertIn("Scope-Grenzen", self.audit)


if __name__ == "__main__":
    unittest.main()
