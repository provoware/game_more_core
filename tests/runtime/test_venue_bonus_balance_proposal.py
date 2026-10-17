"""Audit reference for an inactive contract; never used by gameplay or payouts."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.domain.settlement import SettlementState
from tests.runtime import test_venue_settlement_receipt as receipt_fixtures
from tests.runtime.test_venue_settlement_receipt import initial_state, context, CITY_MAP, UPGRADES
from tests.runtime.test_game_client_property_upgrade_integration import (
    ALLOWED, DISTRICTS, INCIDENTS, PROPERTY,
)


ROOT = Path(__file__).parents[2]
PROPOSAL = json.loads((ROOT / "manifests/VENUE_AUDIENCE_BONUS_PROPOSAL.json").read_text())


def candidate_bonus(receipt, *, event_id):
    """Evaluate the proposed predicate for balance analysis, without a write path."""
    settlement = SettlementState.from_dict(receipt)
    if settlement.event_id != event_id:
        raise ValueError("Bonusvorschlag gehört zu anderem Event")
    evidence = settlement.venue_evidence
    if settlement.contract_version != PROPOSAL["required_receipt_contract"] or evidence is None:
        return 0
    if (evidence["audience_pull"] < PROPOSAL["minimum_audience_pull"]
            or settlement.effects["reputation_delta"] < PROPOSAL["minimum_base_reputation_delta"]
            or settlement.effects["budget_delta_cents"] > -PROPOSAL["minimum_incident_cost_cents"]):
        return 0
    return PROPOSAL["maximum_bonus_per_event"]


class VenueBonusBalanceProposalTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = receipt_fixtures.VenueSettlementReceiptTests()
        self.addCleanup(self.fixtures.doCleanups)
        state = initial_state()
        incidents = IncidentState(event_id="event-1").to_dict()
        incidents["pending_settlement"]["reputation_delta"] = 2
        incidents["pending_settlement"]["budget_delta_cents"] = -1000
        state["incidents"] = incidents
        self.kernel = self.fixtures.kernel(state, allowed=ALLOWED)
        self.service = self.fixtures.service(self.kernel)
        self.receipt = self.service.complete(context=context("bonus-audit")).settlement.to_dict()

    def test_proposal_is_inactive_and_has_one_canonical_bounded_target(self):
        self.assertFalse(PROPOSAL["enabled"])
        self.assertEqual(PROPOSAL["status"], "proposal_only_not_activated")
        self.assertEqual(PROPOSAL["target_effect"], "reputation_delta")
        self.assertEqual(PROPOSAL["maximum_bonus_per_event"], 1)
        self.assertEqual(PROPOSAL["maximum_relative_gain_bps"], 5000)
        self.assertEqual(PROPOSAL["once_key"], "settlement.event_id")
        self.assertEqual(PROPOSAL["budget_bonus_cents"], 0)
        self.assertFalse(PROPOSAL["stack_multiple_properties"])
        self.assertFalse(PROPOSAL["client_supplied_bonus_allowed"])
        self.assertTrue(PROPOSAL["activation_requires_versioned_effect_receipt_and_replay"])
        manifest = json.loads((ROOT / "manifests/SETTLEMENT_MANIFEST.json").read_text())
        self.assertFalse(manifest["venue_evidence"]["mechanical_effect"])

    def test_16665_boundary_combinations_have_no_loss_relief_or_unbounded_gain(self):
        checked = 0
        receipt = deepcopy(self.receipt)
        for base in range(-12, 21):
            receipt["effects"]["reputation_delta"] = base
            receipt["reputation"]["delta"] = base
            receipt["reputation"]["new"] = max(0, receipt["reputation"]["old"] + base)
            for pull in range(101):
                receipt["venue_evidence"]["audience_pull"] = pull
                for cost in (0, -999, -1000, -12000, 1000):
                    receipt["effects"]["budget_delta_cents"] = cost
                    receipt["budget"]["delta"] = cost
                    receipt["budget"]["new"] = receipt["budget"]["old"] + cost
                    bonus = candidate_bonus(receipt, event_id="event-1")
                    self.assertIn(bonus, (0, 1))
                    self.assertLessEqual(bonus * 10000, max(0, base) * 5000)
                    if base < 2 or pull < 50 or cost > -1000:
                        self.assertEqual(bonus, 0)
                    else:
                        self.assertEqual(bonus, 1)
                    checked += 1
        self.assertEqual(checked, 16665)

    def test_legacy_missing_evidence_wrong_event_and_forged_values_are_not_eligible(self):
        no_venue = deepcopy(self.receipt)
        no_venue["venue_evidence"] = None
        self.assertEqual(candidate_bonus(no_venue, event_id="event-1"), 0)
        legacy = deepcopy(self.receipt)
        legacy["contract_version"] = "0.8.3-c1"
        del legacy["venue_evidence"]
        self.assertEqual(candidate_bonus(legacy, event_id="event-1"), 0)
        with self.assertRaisesRegex(ValueError, "anderem Event"):
            candidate_bonus(self.receipt, event_id="event-other")
        for field, value in (("audience_pull", True), ("audience_pull", 101),
                             ("audience_pull", -1), ("owner_character_id", "foreign"),
                             ("additional_venues", ["free-bonus"]), ("schema_version", 2)):
            forged = deepcopy(self.receipt)
            forged["venue_evidence"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                candidate_bonus(forged, event_id="event-1")

    def test_retry_reload_and_current_runtime_do_not_award_the_proposed_bonus(self):
        before = self.kernel.load_state()
        self.assertEqual(candidate_bonus(self.receipt, event_id="event-1"), 1)
        retry = self.service.complete(context=context("bonus-audit"))
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.settlement.to_dict(), self.receipt)
        self.assertEqual(self.kernel.load_state(), before)
        self.assertEqual(before["character"]["reputation"], 2)
        self.assertEqual(self.receipt["effects"]["reputation_delta"], 2)
        self.assertEqual(len(self.kernel.read_records()), 6)
        reread = SettlementState.from_dict(self.kernel.load_state()["settlement"]).to_dict()
        self.assertEqual(candidate_bonus(reread, event_id="event-1"), 1)
        self.assertEqual(self.kernel.load_state(), before)

    def test_browser_cannot_supply_bonus_or_change_venue_evidence(self):
        kernel = self.fixtures.kernel(initial_state(), allowed=ALLOWED)
        session = GameClientSession(
            kernel, incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"], district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP, property_manifest=PROPERTY, property_upgrade_manifest=UPGRADES,
        )
        before = kernel.load_state()
        for key in ("bonus", "venue_bonus", "audience_pull", "reputation_delta", "venue_evidence"):
            result = session.dispatch(
                {"type": "settlement.complete", "command_id": "forged", key: 1000000},
                context=context("forged"),
            )
            self.assertEqual(result.status, "rejected")
            self.assertEqual(kernel.load_state(), before)
            self.assertEqual(kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
