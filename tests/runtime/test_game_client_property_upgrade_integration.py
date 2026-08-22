import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_client_session import GameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
PROPERTY = json.loads((ROOT / "manifests" / "PROPERTY_MANIFEST.json").read_text(encoding="utf-8"))
UPGRADES = json.loads((ROOT / "manifests" / "PROPERTY_UPGRADE_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def ctx(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T20:00:00+02:00",
        "session-upgrade-client",
        "player-local",
        "event",
        "event-upgrade-client",
        command_id,
        "upgrade-client-test",
        "0.8.6-b1",
        "char.upgrade-client",
    )


def event() -> EventState:
    return EventState(
        event_id="event-upgrade-client",
        display_name="Upgrade Client Test",
        location={
            "location_id": "signalwerk",
            "display_name": "Signalwerk",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=20_000_000,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "char.upgrade-client", "role": "leitung", "status": "confirmed"}],
        equipment=[],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T04:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


class GameClientPropertyUpgradeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.kernel.initialize_state({
            "character": CharacterState("char.upgrade-client", "Upgrade Crew").to_dict(),
            "event": event().to_dict(),
            "economy": EconomyState(catalog={
                "equipment.pa": {
                    "label": "PA",
                    "base_price_cents": 10_000,
                    "volatility_bps": 0,
                    "consumable": False,
                }
            }).to_dict(),
        })
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP,
            property_manifest=PROPERTY,
            property_upgrade_manifest=UPGRADES,
        )
        purchase = self.session.dispatch(
            {"type": "property.purchase", "command_id": "buy-signalwerk", "location_id": "signalwerk"},
            context=ctx("buy-signalwerk"),
        )
        self.assertEqual(purchase.status, "confirmed")

    def test_client_sends_only_location_and_upgrade_id(self):
        result = self.session.dispatch(
            {
                "type": "property.upgrade",
                "command_id": "stage-one",
                "location_id": "signalwerk",
                "upgrade_id": "stage",
            },
            context=ctx("stage-one"),
        )
        self.assertEqual(result.status, "confirmed")
        self.assertEqual(result.metadata["property_upgrade"]["level"], 1)
        self.assertEqual(result.metadata["property_upgrade"]["cost_cents"], 558_000)
        state = self.session.read_state()
        self.assertEqual(
            state["property_upgrades"]["properties"]["signalwerk"]["upgrades"]["stage"]["level"],
            1,
        )

    def test_cost_level_delta_and_quantity_injection_are_rejected_before_write(self):
        forbidden = {
            "upgrade_cost_cents": 1,
            "level": 3,
            "next_level": 3,
            "budget_delta_cents": 9_999_999,
            "value_delta_per_level": {"prestige": 99},
            "quantity": 99,
        }
        for field, value in forbidden.items():
            with self.subTest(field=field):
                before = self.session.read_state()
                records_before = self.kernel.read_records()
                result = self.session.dispatch(
                    {
                        "type": "property.upgrade",
                        "command_id": f"inject-{field}",
                        "location_id": "signalwerk",
                        "upgrade_id": "stage",
                        field: value,
                    },
                    context=ctx(f"inject-{field}"),
                )
                self.assertEqual(result.status, "rejected")
                self.assertEqual(result.error_code, "unexpected_command_fields")
                self.assertEqual(self.session.read_state(), before)
                self.assertEqual(self.kernel.read_records(), records_before)

    def test_equipment_command_cannot_smuggle_property_upgrade_kind(self):
        records_before = self.kernel.read_records()
        result = self.session.dispatch(
            {
                "type": "economy.transact",
                "command_id": "fake-upgrade-economy",
                "kind": "property_upgrade",
                "item_id": "property_upgrade:signalwerk:stage:1",
                "quantity": 1,
            },
            context=ctx("fake-upgrade-economy"),
        )
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.error_code, "validation_error")
        self.assertEqual(self.kernel.read_records(), records_before)


if __name__ == "__main__":
    unittest.main()
