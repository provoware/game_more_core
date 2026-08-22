import json
from copy import deepcopy
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation.hall_of_tribute import build_hall_of_tribute_projection
from bunkerfrequenz.presentation.seasonal_hall import (
    build_seasonal_hall_projection,
    derive_cycle_contexts_from_completed_event,
)


ROOT = Path(__file__).parents[2]
HALL = json.loads((ROOT / "manifests" / "HALL_OF_TRIBUTE_MANIFEST.json").read_text(encoding="utf-8"))
SEASON = json.loads((ROOT / "manifests" / "HALL_SEASON_MANIFEST.json").read_text(encoding="utf-8"))
RANKING = json.loads((ROOT / "manifests" / "RANKING_NETWORK_MANIFEST.json").read_text(encoding="utf-8"))
SYNC = json.loads((ROOT / "manifests" / "SYNC_MANIFEST.json").read_text(encoding="utf-8"))
ZEIT = json.loads((ROOT / "manifests" / "ZEIT_MANIFEST.json").read_text(encoding="utf-8"))
CITY = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))
TEXT = json.loads((ROOT / "content" / "de" / "ui" / "character_forge.json").read_text(encoding="utf-8"))


def participant(index: int, *, reputation: int, level: int, resonance: int) -> dict:
    return {
        "player_id": f"remote-{index}",
        "character": {
            "meta": {"projection_version": "test", "character_id": f"char.remote-{index}"},
            "overview": {
                "display_name": f"Remote {index}",
                "alias": "",
                "level": level,
                "reputation": reputation,
                "resonance_rank": resonance,
            },
            "skills": [],
        },
    }


def hall(local: CharacterState, peers=()):
    return build_hall_of_tribute_projection(
        {"character": local.to_dict()},
        hall_manifest=HALL,
        ranking_manifest=RANKING,
        sync_manifest=SYNC,
        city_map_manifest=CITY,
        text_catalog=TEXT,
        confirmed_participants=list(peers),
    )


def closed_context(cycle_type: str, anchor_at: str) -> dict:
    if cycle_type == "weekly":
        cycle_id = "week:2026-W34"
    else:
        cycle_id = "month:2026-08"
    return {
        "cycle_id": cycle_id,
        "cycle_type": cycle_type,
        "authority": "confirmed_online_time",
        "anchor_at": anchor_at,
        "closed": True,
        "confirmation_id": f"server-season:{cycle_id}:closed",
    }


class SeasonalHallTests(unittest.TestCase):
    def build(self, hall_projection, contexts=None, *, season=SEASON, zeit=ZEIT):
        return build_seasonal_hall_projection(
            hall_projection,
            season_manifest=season,
            hall_manifest=HALL,
            ranking_manifest=RANKING,
            zeit_manifest=zeit,
            confirmed_cycle_contexts=contexts,
        )

    def test_completed_event_derives_stable_week_and_month_without_wall_clock(self):
        event = {
            "event_id": "event-season-anchor",
            "phase": "completed",
            "revision": 17,
            "time_window": {
                "start_local": "2026-08-22T20:00:00+02:00",
                "end_local": "2026-08-23T04:00:00+02:00",
                "timezone": "Europe/Berlin",
            },
        }
        first = derive_cycle_contexts_from_completed_event(
            event,
            season_manifest=SEASON,
            hall_manifest=HALL,
            ranking_manifest=RANKING,
            zeit_manifest=ZEIT,
        )
        second = derive_cycle_contexts_from_completed_event(
            deepcopy(event),
            season_manifest=SEASON,
            hall_manifest=HALL,
            ranking_manifest=RANKING,
            zeit_manifest=ZEIT,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["weekly"]["cycle_id"], "week:2026-W34")
        self.assertEqual(first["monthly"]["cycle_id"], "month:2026-08")
        self.assertEqual(first["weekly"]["authority"], "game_world_time")
        self.assertFalse(first["weekly"]["closed"])
        self.assertEqual(first["weekly"]["confirmation_id"], "event:event-season-anchor:revision:17")

    def test_non_completed_event_does_not_invent_season(self):
        contexts = derive_cycle_contexts_from_completed_event(
            {
                "event_id": "event-live",
                "phase": "live",
                "revision": 8,
                "time_window": {"start_local": "2026-08-22T20:00:00+02:00"},
            },
            season_manifest=SEASON,
            hall_manifest=HALL,
            ranking_manifest=RANKING,
            zeit_manifest=ZEIT,
        )
        self.assertEqual(contexts, {})
        local = CharacterState("player-local", "Local", reputation=20)
        result = self.build(hall(local), contexts)
        self.assertFalse(result["available"])
        self.assertEqual(result["unavailable_reason"], "no_confirmed_cycle")
        self.assertEqual(result["local_titles"], [])

    def test_closed_cycle_with_real_competition_awards_mode_titles_and_grand_title(self):
        local = CharacterState(
            "player-local",
            "Local",
            reputation=100,
            level=20,
            resonance_rank=8,
        )
        peer = participant(1, reputation=10, level=2, resonance=1)
        hall_projection = hall(local, [peer])
        contexts = {
            "monthly": closed_context("monthly", "2026-08-22T20:00:00+02:00")
        }
        result = self.build(hall_projection, contexts)
        monthly = result["cycles"]["monthly"]
        self.assertTrue(monthly["closed"])
        self.assertTrue(monthly["confirmed_competition"])
        self.assertTrue(monthly["titles_final"])
        self.assertEqual(monthly["modes"]["reputation"]["awarded_title"], "Nachtminister")
        self.assertEqual(monthly["modes"]["level"]["awarded_title"], "Bunkerbaron")
        self.assertEqual(monthly["modes"]["resonance"]["awarded_title"], "Stromheiland")
        self.assertEqual(monthly["grand_title"], {
            "character_id": "player-local",
            "title": "Betonlegende",
        })
        self.assertEqual(
            [item["title"] for item in result["local_titles"]],
            ["Nachtminister", "Bunkerbaron", "Stromheiland", "Betonlegende"],
        )

    def test_local_only_or_open_cycle_never_awards_final_title(self):
        local = CharacterState("player-local", "Local", reputation=100, level=20, resonance_rank=8)
        local_only = self.build(
            hall(local),
            {"monthly": closed_context("monthly", "2026-08-22T20:00:00+02:00")},
        )
        monthly = local_only["cycles"]["monthly"]
        self.assertFalse(monthly["confirmed_competition"])
        self.assertFalse(monthly["titles_final"])
        self.assertIsNone(monthly["modes"]["reputation"]["awarded_title"])
        self.assertEqual(local_only["local_titles"], [])

        peer = participant(1, reputation=10, level=2, resonance=1)
        open_context = closed_context("weekly", "2026-08-22T20:00:00+02:00")
        open_context["closed"] = False
        open_cycle = self.build(hall(local, [peer]), {"weekly": open_context})
        self.assertFalse(open_cycle["cycles"]["weekly"]["titles_final"])
        self.assertIsNone(open_cycle["cycles"]["weekly"]["modes"]["reputation"]["awarded_title"])

    def test_system_time_and_mismatched_cycle_id_fail_closed(self):
        local = CharacterState("player-local", "Local")
        bad_time = deepcopy(ZEIT)
        bad_time["system_time_is_sole_authority"] = True
        with self.assertRaises(ValueError):
            self.build(hall(local), {}, zeit=bad_time)

        context = closed_context("weekly", "2026-08-22T20:00:00+02:00")
        context["authority"] = "system_time"
        with self.assertRaises(ValueError):
            self.build(hall(local), {"weekly": context})

        context = closed_context("weekly", "2026-08-22T20:00:00+02:00")
        context["cycle_id"] = "week:2026-W33"
        with self.assertRaises(ValueError):
            self.build(hall(local), {"weekly": context})


if __name__ == "__main__":
    unittest.main()
