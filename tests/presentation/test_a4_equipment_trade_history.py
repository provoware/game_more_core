from pathlib import Path
import unittest

from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection


ROOT = Path(__file__).parents[2]
JOBS_UI = (ROOT / "web" / "a4" / "assistant_jobs_ui.js").read_text(encoding="utf-8")


class A4EquipmentTradeHistoryTests(unittest.TestCase):
    def test_projection_shows_recent_effective_trades_with_execution_price(self):
        economy = EconomyState(
            catalog={
                "speaker": {
                    "label": "Speaker",
                    "base_price_cents": 50_000,
                    "volatility_bps": 0,
                    "consumable": False,
                }
            },
            ledger=[
                {
                    "transaction_id": "buy-a",
                    "kind": "buy",
                    "item_id": "speaker",
                    "quantity": 1,
                    "unit_price_cents": 45_000,
                    "budget_delta_cents": -45_000,
                    "compensates": None,
                },
                {
                    "transaction_id": "sell-b",
                    "kind": "sell",
                    "item_id": "speaker",
                    "quantity": 1,
                    "unit_price_cents": 50_000,
                    "budget_delta_cents": 50_000,
                    "compensates": None,
                },
                {
                    "transaction_id": "buy-c",
                    "kind": "buy",
                    "item_id": "speaker",
                    "quantity": 1,
                    "unit_price_cents": 47_500,
                    "budget_delta_cents": -47_500,
                    "compensates": None,
                },
                {
                    "transaction_id": "undo-c",
                    "kind": "sell",
                    "item_id": "speaker",
                    "quantity": 1,
                    "unit_price_cents": 47_500,
                    "budget_delta_cents": 47_500,
                    "compensates": "buy-c",
                },
                {
                    "transaction_id": "buy-e",
                    "kind": "buy",
                    "item_id": "speaker",
                    "quantity": 2,
                    "unit_price_cents": 48_000,
                    "budget_delta_cents": -96_000,
                    "compensates": None,
                },
            ],
        )
        projection = build_a4_game_projection(
            {"economy": economy.to_dict()},
            incident_catalog={},
        )

        history = projection["economy"]["trade_history"]
        self.assertEqual([entry["transaction_id"] for entry in history], ["buy-e", "sell-b", "buy-a"])
        self.assertEqual(history[0]["label"], "Speaker")
        self.assertEqual(history[0]["quantity"], 2)
        self.assertEqual(history[0]["unit_price_cents"], 48_000)
        self.assertEqual(history[0]["sequence"], 5)
        self.assertNotIn("buy-c", {entry["transaction_id"] for entry in history})
        self.assertNotIn("undo-c", {entry["transaction_id"] for entry in history})
        for entry in history:
            self.assertNotIn("profit", entry)
            self.assertNotIn("cost_basis_cents", entry)

    def test_projection_limits_history_without_changing_ledger(self):
        ledger = [
            {
                "transaction_id": f"buy-{index}",
                "kind": "buy",
                "item_id": "speaker",
                "quantity": 1,
                "unit_price_cents": 50_000 + index,
                "budget_delta_cents": -(50_000 + index),
                "compensates": None,
            }
            for index in range(10)
        ]
        economy = EconomyState(
            catalog={
                "speaker": {
                    "label": "Speaker",
                    "base_price_cents": 50_000,
                    "volatility_bps": 0,
                    "consumable": False,
                }
            },
            ledger=ledger,
        )
        projection = build_a4_game_projection(
            {"economy": economy.to_dict()},
            incident_catalog={},
        )
        self.assertEqual(len(projection["economy"]["trade_history"]), 8)
        self.assertEqual(projection["economy"]["trade_history"][0]["transaction_id"], "buy-9")
        self.assertEqual(len(economy.ledger), 10)

    def test_browser_renders_projection_read_only_without_profit_or_command_logic(self):
        start = JOBS_UI.index("function renderEquipmentTradeHistory")
        end = JOBS_UI.index("function renderEconomyMarket", start)
        fragment = JOBS_UI[start:end]
        for marker in (
            "HANDELSVERLAUF // BESTÄTIGT",
            "Letzte Käufe & Verkäufe",
            "economy.trade_history",
            "Stückpreis",
            "Buchung #",
            "Rückgängig gemachte Paare werden ausgeblendet",
        ):
            self.assertIn(marker, fragment)
        self.assertNotIn("sendCommand", fragment)
        self.assertNotIn("profit", fragment.lower())
        self.assertNotIn("gewinn =", fragment.lower())
        self.assertNotIn("cost_basis", fragment.lower())


if __name__ == "__main__":
    unittest.main()
