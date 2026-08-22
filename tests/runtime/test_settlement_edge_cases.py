import tempfile
import unittest

from bunkerfrequenz.application.settlement_service import SettlementService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


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
        "2026-08-22T22:30:00+02:00",
        "session-settlement-edge",
        "player-1",
        "event",
        "event-1",
        command_id,
        "runtime",
        "0.8.3-c1",
    )


def settlement_event(*, budget_cents: int = 50_000, phase: str = "settlement") -> EventState:
    return EventState(
        event_id="event-1",
        display_name="Incidentfreies Testevent",
        location={
            "location_id": "loc-1",
            "display_name": "Testort",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=budget_cents,
        acts=[{"act_id": "act-1", "display_name": "Act", "status": "confirmed"}],
        crew=[{"character_id": "player-1", "role": "leitung", "status": "confirmed"}],
        equipment=[],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
        phase=phase,
        revision=8,
    )


def economy() -> EconomyState:
    return EconomyState(catalog={})


class SettlementEdgeCaseTests(unittest.TestCase):
    def test_event_without_any_incident_can_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({
                "event": settlement_event().to_dict(),
                "economy": economy().to_dict(),
                "character": CharacterState("player-1", "Testfigur").to_dict(),
            })

            result = SettlementService(kernel).complete(context=context("no-incident"))

            self.assertEqual(result.event.phase, "completed")
            self.assertEqual(result.settlement.incident_ids, [])
            self.assertEqual(result.settlement.effects, {
                "budget_delta_cents": 0,
                "reputation_delta": 0,
                "crew_stress_delta": 0,
                "stability_delta": 0,
                "heat_delta": 0,
            })
            self.assertEqual(result.incidents.revision, 1)
            self.assertFalse(any(result.incidents.pending_settlement.values()))
            self.assertEqual(result.economy.ledger[-1]["budget_delta_cents"], 0)

    def test_legacy_negative_reputation_loads_and_settlement_normalizes_result(self):
        legacy = CharacterState("player-1", "Legacy", reputation=-7)
        self.assertEqual(CharacterState.from_dict(legacy.to_dict()).reputation, -7)

        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({
                "event": settlement_event().to_dict(),
                "economy": economy().to_dict(),
                "character": legacy.to_dict(),
            })

            result = SettlementService(kernel).complete(context=context("legacy-reputation"))

            self.assertEqual(result.character.reputation, 0)
            self.assertEqual(result.settlement.reputation, {"old": -7, "delta": 0, "new": 0})
            reputation_record = next(
                record for record in kernel.read_records()
                if record["event_type"] == "character.reputation_changed"
            )
            self.assertEqual(reputation_record["payload"]["old"], -7)
            self.assertEqual(reputation_record["payload"]["new"], 0)

    def test_negative_final_budget_is_rejected_without_partial_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            incidents = IncidentState(event_id="event-1")
            data = incidents.to_dict()
            data["pending_settlement"]["budget_delta_cents"] = -50_001
            incidents = IncidentState.from_dict(data)
            kernel.initialize_state({
                "event": settlement_event().to_dict(),
                "economy": economy().to_dict(),
                "character": CharacterState("player-1", "Testfigur").to_dict(),
                "incidents": incidents.to_dict(),
            })
            before = kernel.load_state()

            with self.assertRaisesRegex(ValueError, "Budget|Defizit"):
                SettlementService(kernel).complete(context=context("deficit"))

            self.assertEqual(kernel.load_state(), before)
            self.assertEqual(len(kernel.read_records()), 0)

    def test_settlement_receipt_binds_applied_deltas_to_confirmed_effects(self):
        base = SettlementState(
            event_id="event-1",
            settlement_id="settlement:test",
            contract_version="0.8.3-c1",
            incident_ids=[],
            effects={
                "budget_delta_cents": 0,
                "reputation_delta": 0,
                "crew_stress_delta": 0,
                "stability_delta": 0,
                "heat_delta": 0,
            },
            budget={"old": 50_000, "delta": 0, "new": 50_000},
            character_id="player-1",
            stress={"old": 10, "delta": 0, "new": 10},
            reputation={"old": 4, "delta": 0, "new": 4},
            event_revision={"old": 8, "new": 10},
            economy_revision={"old": 0, "new": 1},
            incident_revision={"old": 0, "new": 1},
        ).to_dict()

        for effect_key in ("budget_delta_cents", "crew_stress_delta", "reputation_delta"):
            with self.subTest(effect_key=effect_key):
                corrupted = {
                    **base,
                    "effects": {**base["effects"], effect_key: 1},
                }
                with self.assertRaisesRegex(ValueError, "angewandten Delta"):
                    SettlementState.from_dict(corrupted)

    def test_settlement_service_rejects_wrong_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            kernel = PersistenceKernel(tmp, ALLOWED)
            kernel.initialize_state({
                "event": settlement_event(phase="teardown").to_dict(),
                "economy": economy().to_dict(),
                "character": CharacterState("player-1", "Testfigur").to_dict(),
            })
            with self.assertRaisesRegex(ValueError, "settlement"):
                SettlementService(kernel).complete(context=context("wrong-phase"))

    def test_character_reputation_bool_is_not_silently_coerced(self):
        raw = CharacterState("player-1", "Testfigur").to_dict()
        raw["reputation"] = True
        with self.assertRaisesRegex(ValueError, "Reputation"):
            CharacterState.from_dict(raw)


if __name__ == "__main__":
    unittest.main()
