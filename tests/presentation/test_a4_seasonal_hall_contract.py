import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
LAUNCHER = (ROOT / "tools" / "start_a4_game_client.py").read_text(encoding="utf-8")
SEASON = json.loads((ROOT / "manifests" / "HALL_SEASON_MANIFEST.json").read_text(encoding="utf-8"))


class A4SeasonalHallContractTests(unittest.TestCase):
    def test_weekly_and_monthly_controls_are_view_only(self):
        self.assertIn('id="hall-cycle-weekly"', INDEX)
        self.assertIn('id="hall-cycle-monthly"', INDEX)
        self.assertIn('role="group" aria-label="Saisonzyklus wählen"', INDEX)
        self.assertIn('id="hall-season-status"', INDEX)
        self.assertIn('id="hall-season-title-status"', INDEX)
        self.assertIn("state.hallCycleType = cycleType", APP)
        self.assertIn("renderHallSeason(state.projection?.hall_of_tribute?.seasonal)", APP)

    def test_season_renderer_does_not_compute_or_write_cycle_authority(self):
        start = APP.index("function renderHallSeason")
        end = APP.index("\nfunction renderHall(", start)
        seasonal_renderer = APP[start:end]
        for token in (
            "fetch(",
            "sendCommand(",
            "Date.now",
            "new Date",
            "localStorage",
            "sessionStorage",
            "navigator.geolocation",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, seasonal_renderer)
        self.assertIn("cycle.cycle_id", seasonal_renderer)
        self.assertIn("cycle.authority", seasonal_renderer)
        self.assertIn("modeResult.awarded_title", seasonal_renderer)

    def test_manifest_and_launcher_reject_system_time_as_season_authority(self):
        self.assertFalse(SEASON["system_time_is_sole_authority"])
        self.assertNotIn("system_time", SEASON["allowed_authorities"])
        self.assertTrue(SEASON["title_policy"]["requires_closed_cycle"])
        self.assertTrue(SEASON["title_policy"]["requires_confirmed_competition"])
        self.assertGreaterEqual(SEASON["title_policy"]["minimum_confirmed_participants"], 2)
        self.assertIn('"manifests/HALL_SEASON_MANIFEST.json"', LAUNCHER)
        self.assertIn('"manifests/ZEIT_MANIFEST.json"', LAUNCHER)
        self.assertIn("hall_season_manifest=self.hall_season_manifest", LAUNCHER)
        self.assertIn("zeit_manifest=self.zeit_manifest", LAUNCHER)

    def test_ui_copy_never_claims_local_rank_one_is_automatically_a_title(self):
        self.assertIn("Systemzeit allein bestimmt niemals eine Saison.", INDEX)
        self.assertIn("endgültige Titel benötigen einen bestätigten geschlossenen Zyklus", INDEX)
        self.assertIn("keine bestätigte Konkurrenz, daher kein Titel", APP)
        self.assertIn("Titel erst nach bestätigtem Zyklusabschluss", APP)


if __name__ == "__main__":
    unittest.main()
