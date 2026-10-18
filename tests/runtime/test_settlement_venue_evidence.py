from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import GameRecoveryService, replay_game_event
from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.property import PropertyState
from bunkerfrequenz.domain.property_upgrade import PropertyUpgradeState
from bunkerfrequenz.domain.settlement import (
    LEGACY_SETTLEMENT_CONTRACT_VERSION, SETTLEMENT_CONTRACT_VERSION, SettlementState,
)
from bunkerfrequenz.infrastructure.persistence import FaultInjectedCrash, JournalContext, PersistenceKernel

ROOT = Path(__file__).parents[2]
CITY_MAP = json.loads((ROOT / 'manifests/CITY_MAP_MANIFEST.json').read_text())
UPGRADES = json.loads((ROOT / 'manifests/PROPERTY_UPGRADE_MANIFEST.json').read_text())
ALLOWED = {
    'economy.transaction_posted', 'character.resources_changed',
    'character.reputation_changed', 'character.biography_entry_added',
    'event.phase_changed', 'event.completed', 'system.recovery_performed',
}


def context(command_id='settle-venue'):
    return JournalContext('2026-10-18T16:00:00+02:00', 'venue-test', 'player-1',
                          'event', 'venue-event', command_id, 'runtime', '0.8.4-alpha.1')


def initial_state():
    event = EventState(
        event_id='venue-event', display_name='Venue-Nachweis',
        location={'location_id': 'signalwerk', 'display_name': 'Signalwerk',
                  'region': 'Berlin', 'access_status': 'authorized'},
        budget_cents=100_000, acts=[], equipment=[],
        crew=[{'character_id': 'player-1', 'role': 'leitung', 'status': 'confirmed'}],
        time_window={'start_local': '2026-10-18T20:00:00+02:00',
                     'end_local': '2026-10-19T06:00:00+02:00', 'timezone': 'Europe/Berlin'},
        safety_status='cleared', phase='settlement', revision=8,
    )
    properties = PropertyState(contract_version='0.8.6-a1', revision=1, owned={
        'signalwerk': {'location_id': 'signalwerk', 'owner_character_id': 'player-1',
                      'purchase_price_cents': 6_200_000, 'economy_transaction_id': 'purchase-1',
                      'event_id': 'purchase-event'},
    })
    upgrades = PropertyUpgradeState(contract_version=UPGRADES['version'], revision=2, properties={
        'signalwerk': {'location_id': 'signalwerk', 'upgrades': {
            'stage': {'level': 2, 'economy_transaction_ids': ['stage-1', 'stage-2']}}},
    })
    return {'event': event.to_dict(), 'economy': EconomyState(catalog={}).to_dict(),
            'character': CharacterState('player-1', 'Testfigur').to_dict(),
            'properties': properties.to_dict(), 'property_upgrades': upgrades.to_dict()}


def service(kernel, **kwargs):
    return SettlementService(kernel, city_map_manifest=CITY_MAP,
                             property_upgrade_manifest=UPGRADES, **kwargs)


class SettlementVenueEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.before = initial_state()
        self.kernel.initialize_state(self.before)

    def test_owned_evidence_is_in_receipt_journal_and_reopened_save_without_bonus(self):
        result = service(self.kernel).complete(context=context())
        evidence = result.settlement.venue_evidence
        self.assertEqual(result.settlement.contract_version, SETTLEMENT_CONTRACT_VERSION)
        self.assertEqual(evidence['audience_pull'], 94)
        self.assertEqual(evidence['location_id'], 'signalwerk')
        self.assertEqual(evidence['owner_character_id'], 'player-1')
        self.assertEqual(evidence['property_revision'], 1)
        self.assertEqual(evidence['property_upgrade_revision'], 2)
        self.assertEqual(self.kernel.read_records()[-1]['payload']['settlement'], result.settlement.to_dict())
        reopened = PersistenceKernel(self.tmp.name, ALLOWED)
        self.assertEqual(reopened.load_state()['settlement'], result.settlement.to_dict())
        for key in ('properties', 'property_upgrades'):
            self.assertEqual(reopened.load_state()[key], self.before[key])
        self.assertEqual(result.settlement.budget['delta'], 0)
        self.assertFalse(any(result.settlement.effects.values()))
        self.assertEqual(result.character.to_dict(), self.before['character'])
        self.assertEqual(result.economy.ledger[-1]['budget_delta_cents'], 0)

    def test_retry_uses_saved_evidence_even_when_catalog_values_change(self):
        first = service(self.kernel).complete(context=context())
        records = self.kernel.read_records()
        changed = deepcopy(CITY_MAP)
        next(loc for loc in changed['locations'] if loc['location_id'] == 'signalwerk')['values']['audience_pull'] = 0
        retry = SettlementService(self.kernel, city_map_manifest=changed,
                                  property_upgrade_manifest=UPGRADES).complete(context=context())
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.settlement.to_dict(), first.settlement.to_dict())
        self.assertEqual(self.kernel.read_records(), records)

    def test_foreign_or_missing_ownership_has_explicit_null_evidence(self):
        for mode in ('foreign', 'empty', 'legacy_without_property_blocks'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                state = initial_state()
                if mode == 'foreign':
                    state['properties']['owned']['signalwerk']['owner_character_id'] = 'other'
                elif mode == 'empty':
                    state['properties']['owned'] = {}
                else:
                    state.pop('properties')
                    state.pop('property_upgrades')
                kernel = PersistenceKernel(tmp, ALLOWED)
                kernel.initialize_state(state)
                receipt = service(kernel).complete(context=context()).settlement.to_dict()
                self.assertIn('venue_evidence', receipt)
                self.assertIsNone(receipt['venue_evidence'])

    def test_owned_location_without_upgrades_uses_confirmed_base_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = initial_state()
            state.pop('property_upgrades')
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state(state)
            result = service(kernel).complete(context=context())
            base = next(loc for loc in CITY_MAP['locations'] if loc['location_id'] == 'signalwerk')['values']
            self.assertEqual(result.settlement.venue_evidence['audience_pull'], base['audience_pull'])
            self.assertEqual(result.settlement.venue_evidence['property_upgrade_revision'], 0)
            replayed = state
            for record in kernel.read_records():
                replayed = replay_game_event(replayed, record)
            self.assertEqual(replayed, kernel.load_state())

    def test_missing_source_contracts_abort_without_partial_writes(self):
        with self.assertRaisesRegex(ValueError, 'Quellverträge'):
            SettlementService(self.kernel).complete(context=context())
        self.assertEqual(self.kernel.load_state(), self.before)
        self.assertEqual(self.kernel.read_records(), ())

    def test_invalid_source_contract_aborts_without_partial_writes(self):
        upgrades = deepcopy(UPGRADES)
        upgrades['city_map_manifest_version'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'passen nicht zusammen'):
            SettlementService(self.kernel, city_map_manifest=CITY_MAP,
                              property_upgrade_manifest=upgrades).complete(context=context())
        self.assertEqual(self.kernel.load_state(), self.before)
        self.assertEqual(self.kernel.read_records(), ())

    def test_legacy_receipt_roundtrips_and_retries_through_new_service(self):
        legacy = service(self.kernel, contract_version=LEGACY_SETTLEMENT_CONTRACT_VERSION).complete(context=context())
        saved = legacy.settlement.to_dict()
        self.assertNotIn('venue_evidence', saved)
        self.assertEqual(SettlementState.from_dict(saved).to_dict(), saved)
        records = self.kernel.read_records()
        retry = service(self.kernel).complete(context=context())
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.settlement.to_dict(), saved)
        replayed = self.before
        for record in records:
            replayed = replay_game_event(replayed, record)
        self.assertEqual(replayed, self.kernel.load_state())
        self.assertEqual(self.kernel.read_records(), records)

    def test_crash_after_durable_journal_recovers_same_evidence_and_retries_once(self):
        self.kernel.create_snapshot('before-venue-settlement')
        def crash(point):
            if point == 'after_journal_durable':
                raise FaultInjectedCrash(point)
        crashing = PersistenceKernel(self.tmp.name, ALLOWED, fault_injector=crash)
        with self.assertRaises(FaultInjectedCrash):
            service(crashing).complete(context=context())
        recovering = PersistenceKernel.open_for_recovery(self.tmp.name, ALLOWED)
        journal_receipt = recovering.read_records()[-1]['payload']['settlement']
        recovery = GameRecoveryService(recovering).recover(context=context('recover-venue'))
        self.assertEqual(recovery.status, 'recovered')
        self.assertEqual(recovering.load_state()['settlement'], journal_receipt)
        count = len(recovering.read_records())
        retry = service(recovering).complete(context=context())
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.settlement.to_dict(), journal_receipt)
        self.assertEqual(len(recovering.read_records()), count)
        self.assertEqual(len(recovering.load_state()['economy']['ledger']), 1)

    def test_replay_is_idempotent_and_rejects_forged_evidence_without_mutation(self):
        service(self.kernel).complete(context=context())
        records = self.kernel.read_records()
        state = deepcopy(self.before)
        for record in records[:-1]:
            state = replay_game_event(state, record)
        original = deepcopy(state)
        missing = deepcopy(records[-1])
        missing['payload']['settlement']['venue_evidence'] = None
        with self.assertRaisesRegex(ValueError, 'gespeicherte Venue-Evidence'):
            replay_game_event(state, missing)
        self.assertEqual(state, original)
        for key, value in (
            ('location_id', 'concrete_orbit'), ('owner_character_id', 'other'),
            ('property_revision', 9), ('property_upgrade_revision', 99),
            ('property_upgrade_manifest_version', 'wrong'), ('audience_pull', True),
            ('audience_pull', 101), ('schema_version', 2), ('unexpected', 1),
        ):
            with self.subTest(key=key, value=value):
                record = deepcopy(records[-1])
                record['payload']['settlement']['venue_evidence'][key] = value
                with self.assertRaises(ValueError):
                    replay_game_event(state, record)
                self.assertEqual(state, original)
        replayed = replay_game_event(state, records[-1])
        self.assertEqual(replay_game_event(replayed, records[-1]), replayed)
        self.assertEqual(replayed, self.kernel.load_state())

    def test_contract_versions_cannot_silently_drop_or_add_evidence(self):
        saved = service(self.kernel).complete(context=context()).settlement.to_dict()
        missing = deepcopy(saved)
        missing.pop('venue_evidence')
        with self.assertRaisesRegex(ValueError, 'explizite'):
            SettlementState.from_dict(missing)
        legacy_with_extra = deepcopy(saved)
        legacy_with_extra['contract_version'] = LEGACY_SETTLEMENT_CONTRACT_VERSION
        with self.assertRaisesRegex(ValueError, 'Legacy'):
            SettlementState.from_dict(legacy_with_extra)
        unknown = deepcopy(saved)
        unknown['contract_version'] = 'future'
        with self.assertRaisesRegex(ValueError, 'Vertragsversion'):
            SettlementState.from_dict(unknown)


if __name__ == '__main__':
    unittest.main()
