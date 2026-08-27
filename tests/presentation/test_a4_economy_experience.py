from pathlib import Path
import unittest

from bunkerfrequenz.domain.economy import EconomyState, market_price
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection


ROOT = Path(__file__).parents[2]
JOBS_UI = (ROOT / "web" / "a4" / "assistant_jobs_ui.js").read_text(encoding="utf-8")
CSS = (ROOT / "web" / "a4" / "economy_experience.css").read_text(encoding="utf-8")


class A4EconomyExperienceTests(unittest.TestCase):
    def test_projection_exposes_canonical_current_market_price_and_free_stock(self):
        economy = EconomyState(
            catalog={
                "speaker": {
                    "label": "Speaker",
                    "base_price_cents": 10_000,
                    "volatility_bps": 500,
                    "consumable": False,
                }
            },
            inventory={"speaker": {"owned": 3, "reserved": 1}},
            market_tick=4,
        )
        projection = build_a4_game_projection(
            {"economy": economy.to_dict()},
            incident_catalog={},
        )
        item = projection["economy"]["items"][0]
        expected = market_price(10_000, 4, 500)
        self.assertEqual(item["current_price_cents"], expected)
        self.assertEqual(item["price_delta_cents"], expected - 10_000)
        self.assertEqual(item["available_to_sell"], 2)
        self.assertEqual(item["volatility_bps"], 500)

    def test_browser_exposes_existing_sell_and_release_without_price_authority(self):
        self.assertIn('economyTrade("sell", item.item_id)', JOBS_UI)
        self.assertIn('economyTrade("release", item.item_id)', JOBS_UI)
        self.assertIn('kind,\n      item_id: itemId,\n      quantity: 1', JOBS_UI)
        trade_start = JOBS_UI.index("function economyTrade")
        trade_fragment = JOBS_UI[trade_start:trade_start + 360]
        self.assertNotIn("current_price_cents", trade_fragment)
        self.assertNotIn("base_price_cents", trade_fragment)
        self.assertNotIn("volatility_bps", trade_fragment)

    def test_job_guidance_shows_income_efficiency_and_resource_costs(self):
        for marker in (
            "Stundenlohn",
            "Erschöpfung drückt diesen Lauf",
            "Job wählen: Stundenlohn, Energie und Stress vergleichen.",
            "Equipment handeln: aktuellen Marktpreis sehen",
        ):
            self.assertIn(marker, JOBS_UI)

    def test_visual_layer_keeps_reduced_motion_and_responsive_fallbacks(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", CSS)
        self.assertIn("@media (max-width: 700px)", CSS)
        self.assertIn(".job-kpis", CSS)
        self.assertIn(".market-card", CSS)


if __name__ == "__main__":
    unittest.main()
