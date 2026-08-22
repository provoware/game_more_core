import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.district_recovery import replay_district_event
from bunkerfrequenz.application.district_service import DistrictService
from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
DISTRICTS = json.loads((ROOT / "manifests" / "DISTRICT_STATE_MANIFEST.json").read_text(encoding="utf-8"))
CITY_MAP = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, entity_type: str, entity_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T18:00:00+02:00",
        "session-district",
        "player-local",
        entity_type,
        entity_id,
        command_id,
        "district-test",
        "0.8.5-d1",
        "player-local",
    )


def completed_event(location_id: str = "signalwerk") -> EventState:
    return EventState(
        event_id="event-district",
        display_name="District Test",
        location={
            "location_id": location_id,
            "display_name": "Signalwerk" if location_id == "signalwerk" else "Unbekannter Ort",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-local", "role": "leitung", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "ready"}],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T04:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
        phase="completed",
        revision=10,
    )


def settlement() -> SettlementState:
    return SettlementState(
        event_id="event-district",
        settlement_id="settlement-district",
        contract_version="0.8.3-c1",
        incident_ids=[],
        effects={
            "budget_delta_cents": 0,
            "reputation_delta": 4,
            "crew_stress_delta": 0,
            "stability_delta": 6,
            "heat_delta": 8,
        },
        budget={"old": 100_000, "delta": 0, "new": 100_000},
        character_id="player-local",
        stress={"old": 0, "delta": 0, "new": 0},
        reputation={"old": 0, "delta": 4, "new": 4},
        event_revision={"old": 8, "new": 10},
        economy_revision={"old": 1, "new": 2},
        incident_revision={"old": 0, "new": 1},
    )


class DistrictServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.service = DistrictService(self.kernel, DISTRICTS, CITY_MAP)

    def test_defaults_cover_all_city_map_districts_without_write(self):
        state = self.service.current_state()
        expected_ids = {item["district_id"] for item in CITY_MAP["districts"]}
        self.assertEqual(set(state.metrics), expected_ids)
        self.assertEqual(state.revision, 0)
        self.assertEqual(state.metrics["friedrichshain"], CITY_MAP["district_metric_defaults"])
        self.assertEqual(self.kernel.read_records(), ())
        self.assertIsNone(self.kernel.load_state())

    def test_confirmed_settlement_updates_mapped_district_once(self):
        self.kernel.initialize_state({
            "event": completed_event().to_dict(),
            "settlement": settlement().to_dict(),
        })
        ctx = context("district-settlement", "event", "event-district")
        first = self.service.apply_confirmed_settlement(context=ctx)
        second = self.service.apply_confirmed_settlement(context=ctx)

        self.assertTrue(first.applied)
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(len(first.committed_event_ids), 1)
        self.assertEqual(second.committed_event_ids, ())
        values = first.state.metrics["friedrichshain"]
        self.assertEqual(values, {
            "heat": 28,
            "prestige": 24,
            "police_pressure": 17,
            "scene_activity": 35,
        })
        self.assertEqual(first.state.applied_sources, ["settlement:settlement-district"])
        records = [r for r in self.kernel.read_records() if r["event_type"] == "world.district_effect_applied"]
        self.assertEqual(len(records), 1)

    def test_unknown_event_location_is_safe_noop(self):
        self.kernel.initialize_state({
            "event": completed_event("location-not-catalogued").to_dict(),
            "settlement": settlement().to_dict(),
        })
        result = self.service.apply_confirmed_settlement(
            context=context("district-unknown", "event", "event-district")
        )
        self.assertFalse(result.applied)
        self.assertEqual(result.committed_event_ids, ())
        self.assertEqual(result.state.revision, 0)
        self.assertFalse(any(r["event_type"] == "world.district_effect_applied" for r in self.kernel.read_records()))

    def test_street_effect_uses_confirmed_journal_polarity(self):
        character = CharacterState("player-local", "Street Crew")
        event = completed_event()
        self.kernel.initialize_state({"character": character.to_dict(), "event": event.to_dict()})
        street = StreetEncounterService(self.kernel, STREET)
        street_result = street.walk(
            character,
            walk_instance_id="street-source",
            world_seed="district-street-seed",
            journal_context=context("street-source", "character", "player-local"),
        )
        before_event = self.kernel.load_state()["event"]
        result = self.service.apply_confirmed_street_encounter(
            source_event_id="street-source:001",
            context=context("street-district", "character", "player-local"),
        )
        expected = DISTRICTS["street_mapping"][street_result.polarity]
        self.assertEqual(result.state.last_change["deltas"], expected)
        self.assertEqual(self.kernel.load_state()["event"], before_event)
        replay = self.service.apply_confirmed_street_encounter(
            source_event_id="street-source:001",
            context=context("street-district-retry", "character", "player-local"),
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.state.revision, 1)

    def test_values_are_clamped_and_replay_restores_confirmed_state(self):
        current = self.service.current_state().to_dict()
        current["metrics"]["friedrichshain"] = {
            "heat": 98,
            "prestige": 99,
            "police_pressure": 99,
            "scene_activity": 99,
        }
        self.kernel.initialize_state({
            "event": completed_event().to_dict(),
            "settlement": settlement().to_dict(),
            "districts": current,
        })
        result = self.service.apply_confirmed_settlement(
            context=context("district-clamp", "event", "event-district")
        )
        values = result.state.metrics["friedrichshain"]
        self.assertEqual(values["heat"], 100)
        self.assertEqual(values["prestige"], 100)
        self.assertEqual(values["police_pressure"], 100)
        self.assertEqual(values["scene_activity"], 100)
        record = next(r for r in self.kernel.read_records() if r["event_type"] == "world.district_effect_applied")
        replayed = replay_district_event({}, record)
        self.assertEqual(replayed["districts"], result.state.to_dict())

    def test_wrong_contract_or_unconfirmed_street_source_fails_closed(self):
        bad = json.loads(json.dumps(DISTRICTS))
        bad["city_map_manifest_version"] = "wrong"
        with self.assertRaises(ValueError):
            DistrictService(self.kernel, bad, CITY_MAP)
        with self.assertRaises(Exception):
            self.service.apply_confirmed_street_encounter(
                source_event_id="missing:001",
                context=context("missing", "character", "player-local"),
            )


if __name__ == "__main__":
    unittest.main()
