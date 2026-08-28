from pathlib import Path
import unittest

from bunkerfrequenz.domain.economy import EconomyState


ROOT = Path(__file__).parents[2]
DOMAIN = (ROOT / "src/bunkerfrequenz/domain/economy.py").read_text(encoding="utf-8")
SERVICE = (ROOT / "src/bunkerfrequenz/application/economy_service.py").read_text(encoding="utf-8")


class EquipmentTradeHistoryAuditTests(unittest.TestCase):
    def test_ledger_preserves_confirmed_trade_identity_quantity_and_execution_price(self):
        state = EconomyState(
            catalog={
                "equipment.pa": {
                    "label": "PA",
                    "base_price_cents": 50_000,
                    "volatility_bps": 500,
                    "consumable": False,
                }
            },
            ledger=[
                {
                    "transaction_id": "buy-a",
                    "kind": "buy",
                    "item_id": "equipment.pa",
                    "quantity": 1,
                    "unit_price_cents": 45_000,
                    "budget_delta_cents": -45_000,
                    "compensates": None,
                },
                {
                    "transaction_id": "buy-b",
                    "kind": "buy",
                    "item_id": "equipment.pa",
                    "quantity": 1,
                    "unit_price_cents": 47_500,
                    "budget_delta_cents": -47_500,
                    "compensates": None,
                },
                {
                    "transaction_id": "sell-c",
                    "kind": "sell",
                    "item_id": "equipment.pa",
                    "quantity": 1,
                    "unit_price_cents": 50_000,
                    "budget_delta_cents": 50_000,
                    "compensates": None,
                },
            ],
        )
        state.validate()

        sell = state.ledger[-1]
        self.assertEqual(sell["transaction_id"], "sell-c")
        self.assertEqual(sell["item_id"], "equipment.pa")
        self.assertEqual(sell["quantity"], 1)
        self.assertEqual(sell["unit_price_cents"], 50_000)
        self.assertEqual(sell["budget_delta_cents"], 50_000)

    def test_current_contract_does_not_define_cost_basis_or_sell_to_buy_lot_binding(self):
        required_fields = {
            "transaction_id",
            "kind",
            "item_id",
            "quantity",
            "unit_price_cents",
            "budget_delta_cents",
            "compensates",
        }
        forbidden_cost_basis_fields = {
            "cost_basis_cents",
            "purchase_lot_id",
            "source_buy_transaction_id",
            "fifo_index",
            "realized_profit_cents",
        }
        self.assertTrue(forbidden_cost_basis_fields.isdisjoint(required_fields))
        for field in forbidden_cost_basis_fields:
            self.assertNotIn(f'"{field}"', DOMAIN)
            self.assertNotIn(f'"{field}"', SERVICE)

    def test_two_purchase_lots_plus_one_sale_are_valid_but_profit_attribution_is_ambiguous(self):
        buy_prices = [45_000, 47_500]
        sell_price = 50_000
        possible_realized_results = {sell_price - price for price in buy_prices}
        self.assertEqual(possible_realized_results, {5_000, 2_500})
        self.assertGreater(len(possible_realized_results), 1)

    def test_compensation_link_is_not_a_general_cost_basis_link(self):
        self.assertIn('original["kind"] not in {"buy", "sell"}', SERVICE)
        self.assertIn('compensates=transaction_id', SERVICE)
        self.assertIn('"compensates": compensates', SERVICE)
        self.assertIn('if any(entry["compensates"] == transaction_id', SERVICE)


if __name__ == "__main__":
    unittest.main()
