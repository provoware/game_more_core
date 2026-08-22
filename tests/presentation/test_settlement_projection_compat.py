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


if __name__ == "__main__":
    unittest.main()
