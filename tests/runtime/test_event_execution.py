import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.event_execution_service import EVENT_ACTIONS, EventExecutionService
from bunkerfrequenz.application.event_state_service import EventStateService
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ALLOWED = {"event.created", "event.phase_changed"}


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T12:00:00+00:00",
        "session-0.8.3a",
        "player-1",
        "event",
        "event-1",
        command_id,
        "runtime",
        "0.8.3-a",
    )


def ready_event(*, phase: str = "draft", equipment_status: str = "ready") -> EventState:
    return EventState(
        event_id="event-1",
        display_name="Bunkerfrequenz Test",
        location={
            "location_id": "location-1",
            "display_name": "Testort",
            "region": "Berlin",
            "access_status": "authorized",
        },
        budget_cents=100_000,
        acts=[{"act_id": "act-1", "display_name": "Act 1", "status": "confirmed"}],
        crew=[{"character_id": "crew-1", "role": "tech", "status": "confirmed"}],
        equipment=[{
            "equipment_id": "equipment.pa",
            "label": "PA",
            "quantity": 1,
            "status": equipment_status,
        }],
        time_window={
            "start_local": "2026-08-22T20:00:00+02:00",
            "end_local": "2026-08-23T06:00:00+02:00",
            "timezone": "Europe/Berlin",
        },
        safety_status="cleared",
        phase=phase,
    )


class EventExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.state_service = EventStateService(self.kernel)
        created = self.state_service.create(ready_event(), context=context("create-event"))
        self.execution = EventExecutionService(self.state_service)
        self.event = created.event

    def execute(self, action_id: str) -> None:
        result = self.execution.execute(self.event, action_id, context=context(f"cmd-{action_id}"))
        self.event = result.event

    def test_happy_path_reaches_settlement_only_through_canonical_actions(self):
        for action_id in (
            "begin_planning",
            "begin_procurement",
            "start_transport",
            "begin_setup",
            "confirm_soundcheck",
            "start_live",
            "finish_live",
            "finish_teardown",
        ):
            availability = self.execution.available_actions(self.event)
            self.assertEqual([entry.action_id for entry in availability], [action_id])
            self.assertTrue(availability[0].enabled)
            self.execute(action_id)

        self.assertEqual(self.event.phase, "settlement")
        records = self.kernel.read_records()
        reasons = [
            record["payload"].get("reason")
            for record in records
            if record["event_type"] == "event.phase_changed"
        ]
        self.assertEqual(
            reasons,
            [
                "event_action:begin_planning",
                "event_action:begin_procurement",
                "event_action:start_transport",
                "event_action:begin_setup",
                "event_action:confirm_soundcheck",
                "event_action:start_live",
                "event_action:finish_live",
                "event_action:finish_teardown",
            ],
        )

    def test_transport_is_blocked_until_equipment_and_physical_gates_are_ready(self):
        self.execute("begin_planning")
        self.execute("begin_procurement")
        blocked = EventState.from_dict(self.event.to_dict())
        blocked.equipment[0]["status"] = "missing"
        availability = self.execution.availability(blocked, "start_transport")
        self.assertFalse(availability.enabled)
        self.assertIn("equipment_ready", availability.blockers)

        blocked.equipment[0]["status"] = "ready"
        blocked.safety_status = "restricted"
        availability = self.execution.availability(blocked, "start_transport")
        self.assertFalse(availability.enabled)
        self.assertIn("safety_clearance_required", availability.blockers)

    def test_procurement_requires_confirmed_people_and_budget(self):
        planning = ready_event(phase="planning")
        planning.acts[0]["status"] = "planned"
        planning.crew[0]["status"] = "assigned"
        planning.budget_cents = 0
        availability = self.execution.availability(planning, "begin_procurement")
        self.assertEqual(
            availability.blockers,
            ("confirmed_act", "confirmed_crew", "positive_budget"),
        )

    def test_wrong_phase_is_visible_and_execution_fails_closed(self):
        availability = self.execution.availability(self.event, "start_transport")
        self.assertFalse(availability.enabled)
        self.assertIn("wrong_phase", availability.blockers)
        with self.assertRaises(ValueError):
            self.execution.execute(self.event, "start_transport", context=context("bad-phase"))

    def test_repeating_same_command_is_idempotent(self):
        first = self.execution.execute(
            self.event,
            "begin_planning",
            context=context("same-command"),
        )
        replay = self.execution.execute(
            self.event,
            "begin_planning",
            context=context("same-command"),
        )
        self.assertFalse(first.idempotent_replay)
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.event.to_dict(), first.event.to_dict())

    def test_manifest_matches_runtime_action_contract(self):
        manifest = json.loads(
            (Path(__file__).parents[2] / "manifests" / "EVENT_ACTION_MANIFEST.json").read_text(
                encoding="utf-8"
            )
        )
        expected = [
            {
                "action_id": spec.action_id,
                "source_phase": spec.source_phase,
                "target_phase": spec.target_phase,
                "prerequisites": list(spec.prerequisites),
            }
            for spec in EVENT_ACTIONS.values()
        ]
        self.assertEqual(manifest["actions"], expected)
        self.assertEqual(manifest["journal_event"], "event.phase_changed")


if __name__ == "__main__":
    unittest.main()
