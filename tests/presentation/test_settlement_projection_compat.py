import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel
from bunkerfrequenz.presentation.biography_projection import build_biography_projection
from bunkerfrequenz.presentation.ranking_network import build_ranking_network_projection


ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {
    "economy.transaction_posted",
    "character.resources_changed",
    "character.reputation_changed",
    "character.biography_entry_added",
    "event.phase_changed",
    "event.completed",
}


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T23:00:00+02:00",
        "session-settlement-presentation",
        "player-1",
        "event",
        "event-1",
        command_id,
        "runtime",
        "0.8.3-c1",
    )


def event() -> EventState:
    return EventState(
        event_id="event-1",
        display_name="Projection Settlement",
        location={
            "location_id": "loc-1",
            "display_name": "Testort",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=50_000,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-1", "role": "leitung", "status": "confirmed"}],
        equipment=[],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
        phase="settlement",
        revision=8,
    )


def ui_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for path in sorted((ROOT / "content/de/ui").glob("*.json")):
        catalog.update(json.loads(path.read_text(encoding="utf-8")))
    return catalog


class SettlementProjectionCompatibilityTests(unittest.TestCase):
    def test_settlement_biography_is_attributed_and_negative_reputation_stays_rankable(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            incidents = IncidentState(event_id="event-1")
            incident_data = incidents.to_dict()
            incident_data["pending_settlement"]["reputation_delta"] = -8
            incidents = IncidentState.from_dict(incident_data)
            kernel.initialize_state({
                "event": event().to_dict(),
                "economy": EconomyState(catalog={}).to_dict(),
                "character": CharacterState("player-1", "Testfigur", reputation=0).to_dict(),
                "incidents": incidents.to_dict(),
            })

            result = SettlementService(kernel).complete(context=context("complete-projection"))
            records = kernel.read_records()

            self.assertEqual(result.character.reputation, 0)
            self.assertEqual(result.settlement.reputation, {"old": 0, "delta": -8, "new": 0})
            biography_records = [record for record in records if record["event_type"] == "character.biography_entry_added"]
            self.assertEqual(len(biography_records), 1)
            self.assertEqual(biography_records[0]["character_id"], "player-1")
            biography = build_biography_projection("player-1", records)
            self.assertEqual(len(biography), 1)
            self.assertEqual(biography[0]["entry_id"], "bio:settlement:complete-projection")

            participant = {
                "player_id": "player-1",
                "character": {
                    "meta": {"projection_version": "0.6", "character_id": "player-1"},
                    "overview": {
                        "display_name": "Testfigur",
                        "alias": "",
                        "level": 1,
                        "reputation": result.character.reputation,
                        "resonance_rank": 0,
                    },
                    "skills": [],
                },
            }
            ranking = build_ranking_network_projection(
                [participant],
                [],
                json.loads((ROOT / "manifests/RANKING_NETWORK_MANIFEST.json").read_text(encoding="utf-8")),
                json.loads((ROOT / "manifests/SYNC_MANIFEST.json").read_text(encoding="utf-8")),
                ui_catalog(),
                sort_by="reputation",
                show_all=True,
            )
            self.assertEqual(ranking["entries"][0]["reputation"], 0)
            self.assertEqual(ranking["entries"][0]["rank"], 1)

    def test_mismatching_optional_context_character_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({
                "event": event().to_dict(),
                "economy": EconomyState(catalog={}).to_dict(),
                "character": CharacterState("player-1", "Testfigur").to_dict(),
            })
            bad = JournalContext(
                "2026-08-22T23:00:00+02:00",
                "session-settlement-presentation",
                "player-1",
                "event",
                "event-1",
                "bad-character-context",
                "runtime",
                "0.8.3-c1",
                "player-2",
            )
            with self.assertRaisesRegex(ValueError, "character_id"):
                SettlementService(kernel).complete(context=bad)


class SettlementVenueComparisonTests(unittest.TestCase):
    def _settled_state(self):
        from bunkerfrequenz.domain.property import PropertyState
        from bunkerfrequenz.domain.property_upgrade import PropertyUpgradeState
        location_event = event().to_dict()
        location_event['location']['location_id'] = 'signalwerk'
        location_event['location']['display_name'] = 'Signalwerk'
        state = {
            'event': location_event,
            'economy': EconomyState(catalog={}).to_dict(),
            'character': CharacterState('player-1', 'Testfigur').to_dict(),
            'properties': PropertyState(contract_version='0.8.6-a1', revision=1, owned={
                'signalwerk': {'location_id': 'signalwerk', 'owner_character_id': 'player-1',
                              'purchase_price_cents': 6_200_000, 'economy_transaction_id': 'buy-1',
                              'event_id': 'event-1'},
            }).to_dict(),
            'property_upgrades': PropertyUpgradeState(contract_version='0.8.6-b1', revision=2, properties={
                'signalwerk': {'location_id': 'signalwerk', 'upgrades': {
                    'stage': {'level': 2, 'economy_transaction_ids': ['stage-1', 'stage-2']}}},
            }).to_dict(),
        }
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state(state)
            SettlementService(kernel, city_map_manifest=self._manifest('CITY_MAP'),
                              property_upgrade_manifest=self._manifest('PROPERTY_UPGRADE')).complete(
                                  context=context('venue-comparison'))
            return kernel.load_state()

    def _manifest(self, name):
        return json.loads((ROOT / 'manifests' / f'{name}_MANIFEST.json').read_text())

    def _project(self, state, *, with_properties=True):
        from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection
        manifests = {
            'city_map_manifest': self._manifest('CITY_MAP'),
            'district_manifest': self._manifest('DISTRICT_STATE'),
            'property_manifest': self._manifest('PROPERTY'),
            'property_upgrade_manifest': self._manifest('PROPERTY_UPGRADE'),
        } if with_properties else {}
        return build_a4_game_projection(state, incident_catalog={}, **manifests)

    def test_later_upgrade_changes_only_current_comparison_and_never_saved_receipt(self):
        from copy import deepcopy
        state = self._settled_state()
        state['property_upgrades']['revision'] = 3
        stage = state['property_upgrades']['properties']['signalwerk']['upgrades']['stage']
        stage['level'] = 3
        stage['economy_transaction_ids'].append('stage-3')
        original = deepcopy(state)
        projection = self._project(state)
        self.assertEqual(projection['settlement_venue_comparison'], {
            'location_id': 'signalwerk', 'at_settlement': 94, 'current': 99,
        })
        self.assertEqual(projection['settlement'], state['settlement'])
        self.assertEqual(state, original)

    def test_missing_current_sources_preserves_history_without_inventing_current_value(self):
        state = self._settled_state()
        self.assertEqual(self._project(state, with_properties=False)['settlement_venue_comparison'], {
            'location_id': 'signalwerk', 'at_settlement': 94, 'current': None,
        })

    def test_foreign_current_owner_cannot_supply_current_value_for_historical_owner(self):
        state = self._settled_state()
        state['properties']['owned']['signalwerk']['owner_character_id'] = 'another-character'
        self.assertIsNone(self._project(state)['settlement_venue_comparison']['current'])

    def test_legacy_receipt_never_gets_invented_historical_value_from_current_upgrades(self):
        state = self._settled_state()
        state['settlement']['contract_version'] = '0.8.3-c1'
        state['settlement'].pop('venue_evidence')
        self.assertIsNone(self._project(state)['settlement_venue_comparison'])

    def test_receipt_for_different_event_location_fails_closed(self):
        state = self._settled_state()
        state['event']['location']['location_id'] = 'concrete_orbit'
        with self.assertRaisesRegex(ValueError, 'Ortsnachweis'):
            self._project(state)


if __name__ == "__main__":
    unittest.main()
