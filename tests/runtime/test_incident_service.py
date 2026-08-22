import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.application.game_recovery import GameRecoveryService
from bunkerfrequenz.application.incident_service import IncidentService, build_incident_catalog
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import FaultInjectedCrash, JournalContext, PersistenceKernel, PersistenceError


ALLOWED = {
    "event.created", "event.phase_changed", "event.incident_started", "event.incident_resolved",
    "system.recovery_performed",
}


def context(command_id: str, *, entity_id: str = "event-1", entity_type: str = "event") -> JournalContext:
    return JournalContext(
        "2026-08-22T20:00:00+02:00", "session-0.8.3b", "player-1", entity_type,
        entity_id, command_id, "runtime", "0.8.3-b1",
    )


def live_event() -> EventState:
    return EventState(
        event_id="event-1",
        display_name="Bunkerfrequenz Test",
        location={"location_id": "loc-1", "display_name": "Testort", "region": "Berlin", "access_status": "authorized"},
        budget_cents=100_000,
        acts=[{"act_id": "act-1", "display_name": "Act 1", "status": "confirmed"}],
        crew=[{"character_id": "crew-1", "role": "tech", "status": "confirmed"}],
        equipment=[{"equipment_id": "equipment.pa", "label": "PA", "quantity": 1, "status": "ready"}],
        time_window={"start_local": "2026-08-22T20:00:00+02:00", "end_local": "2026-08-23T06:00:00+02:00", "timezone": "Europe/Berlin"},
        safety_status="cleared",
        phase="live",
    )


def load_catalog():
    manifest = json.loads((Path(__file__).parents[2] / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
    return manifest, build_incident_catalog(manifest)


def crash_after_journal(point: str) -> None:
    if point == "after_journal_durable":
        raise FaultInjectedCrash(point)


class IncidentServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.manifest, self.catalog = load_catalog()
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        EventStateService(self.kernel).create(live_event(), context=context("create-event"))
        self.service = IncidentService(self.kernel, self.catalog, contract_version=self.manifest["version"])

    def test_open_and_resolve_are_atomic_and_accumulate_pending_settlement(self):
        opened = self.service.open("power_drop", context=context("open-power"), severity=3)
        self.assertEqual(opened.event.phase, "crisis")
        self.assertEqual(opened.incidents.active["incident_type"], "power_drop")
        self.assertEqual(opened.incidents.revision, 1)

        resolved = self.service.resolve("power_drop.generator", context=context("resolve-power"))
        self.assertEqual(resolved.event.phase, "live")
        self.assertIsNone(resolved.incidents.active)
        self.assertEqual(len(resolved.incidents.history), 1)
        self.assertEqual(resolved.incidents.pending_settlement["budget_delta_cents"], -12000)
        self.assertEqual(resolved.incidents.pending_settlement["reputation_delta"], 3)
        self.assertEqual(resolved.incidents.revision, 2)

        records = self.kernel.read_records()
        self.assertEqual([r["event_type"] for r in records[-4:]], [
            "event.phase_changed", "event.incident_started", "event.phase_changed", "event.incident_resolved"
        ])

    def test_severity_scales_confirmed_effects_deterministically(self):
        self.service.open("power_drop", context=context("open-severe"), severity=5)
        resolved = self.service.resolve("power_drop.generator", context=context("resolve-severe"))
        effects = resolved.incidents.history[-1]["effects"]
        self.assertEqual(effects["budget_delta_cents"], -20000)
        self.assertEqual(effects["crew_stress_delta"], 13)

    def test_cumulative_pending_settlement_may_exceed_single_incident_bounds(self):
        result = None
        for index in range(5):
            self.service.open("power_drop", context=context(f"open-cumulative-{index}"), severity=5)
            result = self.service.resolve("power_drop.rewire", context=context(f"resolve-cumulative-{index}"))
        self.assertIsNotNone(result)
        self.assertEqual(result.event.phase, "live")
        self.assertEqual(result.incidents.pending_settlement["crew_stress_delta"], 115)
        self.assertEqual(len(result.incidents.history), 5)

    def test_incident_requires_live_and_one_active_incident_at_a_time(self):
        self.service.open("equipment_failure", context=context("open-first"))
        with self.assertRaises(ValueError):
            self.service.open("artist_delay", context=context("open-second"))

    def test_unknown_or_wrong_response_fails_closed(self):
        self.service.open("artist_delay", context=context("open-delay"))
        with self.assertRaises(ValueError):
            self.service.resolve("power_drop.generator", context=context("bad-response"))

    def test_command_replay_is_idempotent_after_state_advanced(self):
        first = self.service.open("noise_pressure", context=context("open-same"))
        replay = self.service.open("noise_pressure", context=context("open-same"))
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(first.incidents.to_dict(), replay.incidents.to_dict())

        first_resolve = self.service.resolve("noise_pressure.reduce", context=context("resolve-same"))
        replay_resolve = self.service.resolve("noise_pressure.reduce", context=context("resolve-same"))
        self.assertFalse(first_resolve.idempotent_replay)
        self.assertTrue(replay_resolve.idempotent_replay)
        self.assertEqual(first_resolve.incidents.to_dict(), replay_resolve.incidents.to_dict())

    def test_replay_still_requires_matching_event_context(self):
        self.service.open("noise_pressure", context=context("open-context"))
        with self.assertRaises(ValueError):
            self.service.open(
                "noise_pressure",
                context=context("open-context", entity_id="event-other"),
            )
        with self.assertRaises(ValueError):
            self.service.open(
                "noise_pressure",
                context=context("open-context", entity_type="character"),
            )

    def test_resolution_rejects_changed_contract_version(self):
        self.service.open("equipment_failure", context=context("open-versioned"))
        changed_contract = IncidentService(
            self.kernel,
            self.catalog,
            contract_version="0.8.3-b2-incompatible",
        )
        with self.assertRaises(PersistenceError):
            changed_contract.resolve("equipment_failure.swap", context=context("resolve-versioned"))
        state = self.kernel.load_state()
        self.assertEqual(state["event"]["phase"], "crisis")
        self.assertEqual(state["incidents"]["active"]["contract_version"], "0.8.3-b1")

    def test_recovery_replays_incident_and_event_phase_after_durable_journal_crash(self):
        self.kernel.create_snapshot("before_incident")
        crashing = PersistenceKernel(self.tmp.name, ALLOWED, fault_injector=crash_after_journal)
        service = IncidentService(crashing, self.catalog, contract_version=self.manifest["version"])
        with self.assertRaises(FaultInjectedCrash):
            service.open("security_breach", context=context("open-crash"))
        with self.assertRaises(PersistenceError):
            PersistenceKernel(self.tmp.name, ALLOWED)

        recovering = PersistenceKernel.open_for_recovery(self.tmp.name, ALLOWED)
        GameRecoveryService(recovering).recover(context=context("recover-crisis"))
        state = recovering.load_state()
        self.assertEqual(state["event"]["phase"], "crisis")
        self.assertEqual(state["incidents"]["active"]["incident_type"], "security_breach")
        self.assertEqual(state["incidents"]["revision"], 1)


if __name__ == "__main__":
    unittest.main()
