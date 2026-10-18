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
            ["incidents", "properties", "property_upgrades"],
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
                "client_changes": True,
                "property_changes": False,
                "network_changes": False,
            },
        )

    def test_versioned_evidence_is_read_only_and_legacy_remains_readable(self):
        self.assertEqual(self.settlement_manifest["version"], "0.8.8-venue-evidence-v1")
        self.assertEqual(self.settlement_manifest["readable_contract_versions"],
                         ["0.8.3-c1", "0.8.8-venue-evidence-v1"])
        evidence = self.settlement_manifest["venue_evidence"]
        self.assertFalse(evidence["changes_effects"])
        self.assertTrue(evidence["replay_uses_stored_evidence_not_current_catalog_values"])
        self.assertTrue(evidence["replay_checks_event_character_ownership_and_source_revisions"])
        self.assertEqual(evidence["stored_fields"], [
            "schema_version", "location_id", "owner_character_id", "audience_pull",
            "city_map_manifest_version", "property_upgrade_manifest_version",
            "property_revision", "property_upgrade_revision",
        ])

    def test_proposed_reputation_effect_is_bounded_and_not_activated(self):
        from tools.venue_reputation_balance_audit import run_audit
        report = run_audit()
        self.assertEqual(report["exhaustive_cases"], 40602)
        self.assertEqual(report["extra_large_delta_cases"], 404)
        self.assertEqual(sum(item["upgrade_combinations"] for item in report["venues"]), 2176)
        self.assertEqual(report["absolute_cap"], 2)
        self.assertEqual(report["relative_cap_percent"], 25)
        self.assertFalse(report["runtime_mechanic_enabled"])
        self.assertEqual(report["money_effect"], 0)
        self.assertTrue(report["decision"].startswith("NO_GO_ACTIVATION"))

    def test_proposed_thresholds_do_not_reward_tiny_losing_or_foreign_events(self):
        from tools.venue_reputation_balance_audit import proposed_bonus
        for audience, delta, expected in ((49, 8, 0), (50, 8, 1), (99, 8, 1),
                                          (100, 8, 2), (100, 3, 0), (100, 4, 1),
                                          (100, 0, 0), (100, -4, 0)):
            with self.subTest(audience=audience, delta=delta):
                self.assertEqual(proposed_bonus(audience, delta, owned=True), expected)
                self.assertEqual(proposed_bonus(audience, delta, owned=False), 0)

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
