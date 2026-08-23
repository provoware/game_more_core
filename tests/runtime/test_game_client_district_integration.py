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
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICT_EVENTS = json.loads((ROOT / "manifests" / "DISTRICT_EVENT_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def ctx(command_id: str, entity_type: str = "event", entity_id: str = "event-local-1") -> JournalContext:
    return JournalContext(
        "2026-08-22T18:00:00+02:00",
        "session-district-integration",
        "player-local",
        entity_type,
        entity_id,
        command_id,
        "district-integration-test",
        "0.8.7-c3",
        "player-local",
    )


def event() -> EventState:
    return EventState(
        event_id="event-local-1",
        display_name="District Integration",
        location={
            "location_id": "loc-a4-demo",
            "display_name": "A4 Testlocation",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-a4", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-local", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "required"}],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
    )


def economy() -> EconomyState:
    return EconomyState(catalog={
        "equipment.pa": {
            "label": "PA",
            "base_price_cents": 10_000,
            "volatility_bps": 0,
            "consumable": False,
        }
    })


class GameClientDistrictIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.session = GameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            street_manifest=STREET,
            street_world_seed="district-integration-seed",
            district_manifest=DISTRICTS,
            city_map_manifest=CITY_MAP,
            district_event_manifest=DISTRICT_EVENTS,
            district_world_seed="district-world-integration-seed",
        )
        self.session.bootstrap_character(CharacterState("player-local", "District Crew"))
        self.assertEqual(self.session.dispatch(
            {"type": "event.create", "command_id": "create", "event": event().to_dict()},
            context=ctx("create"),
        ).status, "confirmed")
        self.assertEqual(self.session.dispatch(
            {"type": "economy.initialize", "command_id": "economy", "economy": economy().to_dict()},
            context=ctx("economy"),
        ).status, "confirmed")

    def event_command(self, command):
        return self.session.dispatch(command, context=ctx(command["command_id"]))

    def test_street_walk_derives_district_effect_without_client_deltas(self):
        before_event = self.session.read_state()["event"]
        result = self.session.dispatch(
            {"type": "street.walk", "command_id": "walk-with-district"},
            context=ctx("walk-with-district", "character", "player-local"),
        )
        self.assertEqual(result.status, "confirmed")
        self.assertIn("district", result.metadata)
        self.assertTrue(result.metadata["district"]["applied"])
        self.assertNotIn("district_world_event", result.metadata)
        state = self.session.read_state()
        self.assertIn("districts", state)
        self.assertEqual(state["event"], before_event)
        district_records = [r for r in self.kernel.read_records() if r["event_type"] == "world.district_effect_applied"]
        self.assertEqual(len(district_records), 1)
        self.assertNotIn("district", {"type": "street.walk", "command_id": "walk-with-district"})

        retry = self.session.dispatch(
            {"type": "street.walk", "command_id": "walk-with-district"},
            context=ctx("walk-with-district", "character", "player-local"),
        )
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(len([r for r in self.kernel.read_records() if r["event_type"] == "world.district_effect_applied"]), 1)

    def test_settlement_triggers_one_deterministic_district_world_event(self):
        commands = [
            {"type": "event.execute", "command_id": "planning", "action_id": "begin_planning"},
            {"type": "event.execute", "command_id": "procurement", "action_id": "begin_procurement"},
            {"type": "economy.transact", "command_id": "buy", "kind": "buy", "item_id": "equipment.pa", "quantity": 1},
            {"type": "economy.transact", "command_id": "reserve", "kind": "reserve", "item_id": "equipment.pa", "quantity": 1},
            {"type": "event.execute", "command_id": "transport", "action_id": "start_transport"},
            {"type": "event.execute", "command_id": "setup", "action_id": "begin_setup"},
            {"type": "event.execute", "command_id": "soundcheck", "action_id": "confirm_soundcheck"},
            {"type": "event.execute", "command_id": "live", "action_id": "start_live"},
            {"type": "incident.open", "command_id": "incident-open", "incident_type": "power_drop", "severity": 3},
            {"type": "incident.resolve", "command_id": "incident-resolve", "response_id": "power_drop.generator"},
            {"type": "event.execute", "command_id": "finish-live", "action_id": "finish_live"},
            {"type": "event.execute", "command_id": "finish-teardown", "action_id": "finish_teardown"},
        ]
        for command in commands:
            result = self.event_command(command)
            self.assertEqual(result.status, "confirmed", (command, result.error_code, result.error_detail))

        settlement_command = {"type": "settlement.complete", "command_id": "settle-district"}
        first = self.event_command(settlement_command)
        self.assertEqual(first.status, "confirmed")
        self.assertIn("district", first.metadata)
        self.assertTrue(first.metadata["district"]["applied"])
        self.assertIn("district_world_event", first.metadata)
        world_event = first.metadata["district_world_event"]
        self.assertIn(world_event["event_id"], {item["event_id"] for item in DISTRICT_EVENTS["events"]})
        self.assertEqual(world_event["district_id"], first.metadata["district"]["district_id"])
        self.assertTrue(world_event["event_instance_id"].startswith(
            f"district-event:{world_event['district_id']}:settlement:"
        ))

        state = self.session.read_state()
        self.assertEqual(state["event"]["phase"], "completed")
        self.assertIn("districts", state)
        self.assertEqual(state["districts"]["last_change"]["source_type"], "district_event")
        district_records = [r for r in self.kernel.read_records() if r["event_type"] == "world.district_effect_applied"]
        self.assertEqual(len(district_records), 2)
        self.assertEqual([r["payload"]["source_type"] for r in district_records], ["settlement", "district_event"])

        record_count = len(self.kernel.read_records())
        retry = self.event_command(settlement_command)
        self.assertEqual(retry.status, "confirmed")
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.metadata["district_world_event"]["event_id"], world_event["event_id"])
        self.assertEqual(len(self.kernel.read_records()), record_count)
        self.assertEqual(len([r for r in self.kernel.read_records() if r["event_type"] == "world.district_effect_applied"]), 2)


if __name__ == "__main__":
    unittest.main()
