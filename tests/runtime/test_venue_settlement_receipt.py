from copy import deepcopy
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import GameRecoveryService, replay_game_event
from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.application.settlement_service import SettlementService, replay_settlement_event
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.settlement import (
    LEGACY_SETTLEMENT_VERSION, VENUE_SETTLEMENT_VERSION, SettlementState,
)
from bunkerfrequenz.infrastructure.persistence import FaultInjectedCrash, PersistenceKernel
from tests.runtime.test_settlement_edge_cases import ALLOWED, context, economy, settlement_event
from tests.runtime.test_venue_settlement_evidence_resolver import (
    CITY_MAP, UPGRADES, _property_state, _upgrade_state,
)
from tests.runtime.test_game_client_property_upgrade_integration import (
    ALLOWED as GAME_ALLOWED, DISTRICTS, INCIDENTS, PROPERTY,
)


def initial_state():
    event = settlement_event().to_dict()
    event["location"]["location_id"] = "signalwerk"
    properties = _property_state().to_dict()
    properties["owned"]["signalwerk"]["owner_character_id"] = "player-1"
    return {
        "event": event,
        "economy": economy().to_dict(),
        "character": CharacterState("player-1", "Testfigur").to_dict(),
        "properties": properties,
        "property_upgrades": _upgrade_state().to_dict(),
    }


class VenueSettlementReceiptTests(unittest.TestCase):
    def kernel(self, state=None, *, allowed=ALLOWED, **kwargs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, allowed, **kwargs)
        kernel.initialize_state(initial_state() if state is None else state)
        return kernel

    @staticmethod
    def service(kernel, **kwargs):
        return SettlementService(kernel, city_map_manifest=CITY_MAP, upgrade_manifest=UPGRADES, **kwargs)

    def test_receipt_is_frozen_in_same_commit_without_new_effects_or_property_writes(self):
        original = initial_state()
        kernel = self.kernel(original)
        legacy = SettlementService(self.kernel(original)).complete(context=context("complete"))
        result = self.service(kernel).complete(context=context("complete"))
        receipt = result.settlement.to_dict()
        evidence = receipt["venue_evidence"]
        self.assertEqual(receipt["contract_version"], VENUE_SETTLEMENT_VERSION)
        self.assertEqual(evidence["audience_pull"], 94)
        self.assertEqual(evidence["location_id"], "signalwerk")
        self.assertEqual(evidence["owner_character_id"], "player-1")
        self.assertEqual(evidence["property_revision"], 7)
        self.assertEqual(evidence["property_upgrade_revision"], 4)
        self.assertEqual(evidence["city_map_manifest_version"], CITY_MAP["version"])
        self.assertEqual(evidence["property_upgrade_manifest_version"], UPGRADES["version"])
        for field in ("effects", "budget", "stress", "reputation"):
            self.assertEqual(receipt[field], legacy.settlement.to_dict()[field])
        self.assertEqual(result.economy.to_dict(), legacy.economy.to_dict())
        self.assertEqual(result.character.to_dict(), legacy.character.to_dict())
        self.assertEqual(kernel.load_state()["properties"], original["properties"])
        self.assertEqual(kernel.load_state()["property_upgrades"], original["property_upgrades"])
        self.assertEqual(kernel.read_records()[-1]["payload"]["settlement"], receipt)
        self.assertEqual(len(kernel.read_records()), 6)
        retry = self.service(kernel).complete(context=context("complete"))
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.settlement.to_dict(), receipt)
        self.assertEqual(len(kernel.read_records()), 6)

    def test_missing_or_foreign_ownership_has_explicit_null_evidence(self):
        for mode in ("missing", "foreign", "other-location"):
            with self.subTest(mode=mode):
                state = initial_state()
                if mode == "missing":
                    del state["properties"]
                    del state["property_upgrades"]
                elif mode == "foreign":
                    state["properties"]["owned"]["signalwerk"]["owner_character_id"] = "other"
                else:
                    state["event"]["location"]["location_id"] = "concrete_orbit"
                kernel = self.kernel(state)
                result = self.service(kernel).complete(context=context("complete"))
                self.assertIsNone(result.settlement.to_dict()["venue_evidence"])
                recovered = deepcopy(state)
                for record in kernel.read_records():
                    recovered = replay_game_event(recovered, record)
                self.assertEqual(recovered, kernel.load_state())

    def test_game_session_wires_existing_catalogs_and_rejects_caller_evidence(self):
        kernel = self.kernel(allowed=GAME_ALLOWED)
        session = GameClientSession(
            kernel, incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"], district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP, property_manifest=PROPERTY, property_upgrade_manifest=UPGRADES,
        )
        result = session.dispatch(
            {"type": "settlement.complete", "command_id": "complete", "venue_evidence": {}},
            context=context("complete"),
        )
        self.assertEqual(result.status, "rejected")
        self.assertEqual(kernel.read_records(), ())
        result = session.dispatch(
            {"type": "settlement.complete", "command_id": "complete"}, context=context("complete"),
        )
        self.assertEqual(result.status, "confirmed")
        self.assertEqual(kernel.load_state()["settlement"]["venue_evidence"]["audience_pull"], 94)

    def test_absent_upgrade_state_uses_confirmed_base_value_and_revision_zero(self):
        state = initial_state()
        del state["property_upgrades"]
        result = self.service(self.kernel(state)).complete(context=context("complete"))
        base = next(item for item in CITY_MAP["locations"] if item["location_id"] == "signalwerk")
        self.assertEqual(result.settlement.venue_evidence["audience_pull"], base["values"]["audience_pull"])
        self.assertEqual(result.settlement.venue_evidence["property_upgrade_revision"], 0)

    def test_invalid_catalog_fails_before_any_commit(self):
        kernel = self.kernel()
        before = kernel.load_state()
        for version in ("", "unknown", VENUE_SETTLEMENT_VERSION):
            with self.subTest(version=version), self.assertRaises(ValueError):
                SettlementService(kernel, contract_version=version)
        with self.assertRaisesRegex(ValueError, "gemeinsam"):
            SettlementService(kernel, city_map_manifest=CITY_MAP)
        upgrades = deepcopy(UPGRADES)
        upgrades["city_map_manifest_version"] = "wrong-version"
        service = SettlementService(kernel, city_map_manifest=CITY_MAP, upgrade_manifest=upgrades)
        with self.assertRaisesRegex(ValueError, "Vertrag passen nicht"):
            service.complete(context=context("invalid"))
        self.assertEqual(kernel.load_state(), before)
        self.assertEqual(kernel.read_records(), ())

    def test_crash_recovery_and_retry_preserve_exact_evidence(self):
        def crash(point):
            if point == "after_journal_durable":
                raise FaultInjectedCrash(point)

        kernel = self.kernel(fault_injector=crash)
        with self.assertRaises(FaultInjectedCrash):
            self.service(kernel).complete(context=context("crash"))
        recovering = PersistenceKernel.open_for_recovery(kernel.root, ALLOWED)
        receipt = GameRecoveryService(recovering).recover()
        self.assertEqual(receipt.status, "recovered")
        expected = recovering.read_records()[-1]["payload"]["settlement"]
        self.assertEqual(recovering.load_state()["settlement"], expected)
        self.assertEqual(self.service(recovering).complete(context=context("crash")).settlement.to_dict(), expected)

    def test_replay_rejects_missing_or_misbound_evidence_without_mutation(self):
        original = initial_state()
        kernel = self.kernel(original)
        self.service(kernel).complete(context=context("complete"))
        records = kernel.read_records()
        before = deepcopy(original)
        for record in records[:-1]:
            before = replay_game_event(before, record)
        for field, value in (("location_id", "concrete_orbit"), ("property_revision", 8),
                             ("property_upgrade_revision", 5), ("property_upgrade_manifest_version", "future"),
                             ("owner_character_id", "other"), ("audience_pull", 101)):
            with self.subTest(field=field):
                record = deepcopy(records[-1])
                record["payload"]["settlement"]["venue_evidence"][field] = value
                with self.assertRaises(ValueError):
                    replay_settlement_event(before, record)
                self.assertNotIn("settlement", before)
        record = deepcopy(records[-1])
        record["payload"]["settlement"]["venue_evidence"] = None
        with self.assertRaisesRegex(ValueError, "Evidence für eigenen"):
            replay_settlement_event(before, record)
        record = deepcopy(records[-1])
        record["payload"]["request"]["contract_version"] = LEGACY_SETTLEMENT_VERSION
        with self.assertRaisesRegex(ValueError, "Abschlussrequest"):
            replay_settlement_event(before, record)
        unowned = deepcopy(before)
        unowned["properties"]["owned"].clear()
        with self.assertRaisesRegex(ValueError, "ohne bestätigten eigenen"):
            replay_settlement_event(unowned, records[-1])

    def test_replay_does_not_use_later_changed_catalogs(self):
        state = initial_state()
        kernel = self.kernel(state)
        service = self.service(kernel)
        expected = service.complete(context=context("complete")).settlement.to_dict()
        service.city_map_manifest["locations"].clear()
        service.upgrade_manifest["version"] = "future"
        replayed = deepcopy(state)
        for record in kernel.read_records():
            replayed = replay_game_event(replayed, record)
        self.assertEqual(replayed["settlement"], expected)
        self.assertEqual(service.complete(context=context("complete")).settlement.to_dict(), expected)

    def test_legacy_receipt_remains_unchanged_after_session_upgrade(self):
        kernel = self.kernel()
        legacy = SettlementService(kernel).complete(context=context("old-complete"))
        expected = legacy.settlement.to_dict()
        self.assertEqual(expected["contract_version"], LEGACY_SETTLEMENT_VERSION)
        self.assertNotIn("venue_evidence", expected)
        self.assertEqual(SettlementState.from_dict(expected).to_dict(), expected)
        replay = self.service(kernel).complete(context=context("old-complete"))
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.settlement.to_dict(), expected)
        self.assertEqual(len(kernel.read_records()), 6)

    def test_evidence_validation_rejects_invalid_types_versions_and_extra_fields(self):
        receipt = self.service(self.kernel()).complete(context=context("complete")).settlement.to_dict()
        for field, value in (("schema_version", True), ("schema_version", 2), ("audience_pull", True),
                             ("audience_pull", -1), ("audience_pull", 101), ("audience_pull", 1.5),
                             ("property_revision", -1), ("property_upgrade_revision", True),
                             ("city_map_manifest_version", " "), ("location_id", " signalwerk"),
                             ("owner_character_id", "other"), ("extra", 1)):
            with self.subTest(field=field, value=value):
                bad = deepcopy(receipt)
                bad["venue_evidence"][field] = value
                with self.assertRaises(ValueError):
                    SettlementState.from_dict(bad)
        for version in (LEGACY_SETTLEMENT_VERSION, "unknown"):
            bad = deepcopy(receipt)
            bad["contract_version"] = version
            with self.assertRaises(ValueError):
                SettlementState.from_dict(bad)
        bad = deepcopy(receipt)
        del bad["venue_evidence"]
        with self.assertRaises(ValueError):
            SettlementState.from_dict(bad)

    def test_boundary_values_and_defensive_copies(self):
        data = self.service(self.kernel()).complete(context=context("complete")).settlement.to_dict()
        for value in (0, 100):
            data["venue_evidence"]["audience_pull"] = value
            state = SettlementState.from_dict(data)
            exported = state.to_dict()
            exported["venue_evidence"]["audience_pull"] = 77
            self.assertEqual(state.venue_evidence["audience_pull"], value)
            data["venue_evidence"]["audience_pull"] = 88
            self.assertEqual(state.venue_evidence["audience_pull"], value)


if __name__ == "__main__":
    unittest.main()
