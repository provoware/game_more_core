from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
HARNESS = (ROOT / "tools" / "equipment_trade_history_browser_e2e.py").read_text(encoding="utf-8")


class EquipmentTradeHistoryBrowserE2EContractTests(unittest.TestCase):
    def test_fixture_uses_compensation_pair_and_real_runtime_commands(self):
        self.assertIn('"compensates": COMPENSATED_BUY_ID', HARNESS)
        self.assertIn('"type": "economy.transact"', HARNESS)
        self.assertIn('for kind in ("buy", "sell")', HARNESS)
        self.assertIn('result.get("status") != "confirmed"', HARNESS)
        self.assertIn('runtime.projection().get("economy", {}).get("trade_history")', HARNESS)

    def test_browser_checks_empty_and_filled_history_without_commands(self):
        self.assertIn('_browser_phase(save_dir, "empty")', HARNESS)
        self.assertIn('_browser_phase(save_dir, "filled")', HARNESS)
        self.assertIn("Noch kein wirksamer bestätigter Kauf oder Verkauf.", HARNESS)
        self.assertIn("GEKAUFT · PA", HARNESS)
        self.assertIn("VERKAUFT · PA", HARNESS)
        self.assertIn("Stückpreis 100,00", HARNESS)
        browser_fragment = HARNESS[HARNESS.index("def _harness") : HARNESS.index("def _passed")]
        self.assertNotIn("/api/command", browser_fragment)
        self.assertNotIn("sendCommand", browser_fragment)
        self.assertNotIn("cost_basis", browser_fragment.lower())

    def test_browser_checks_high_contrast_and_horizontal_overflow(self):
        self.assertIn('BunkerUIPrefs.set(\\"highContrast\\", true)', HARNESS)
        self.assertIn("width: 760px; height: 680px", HARNESS)
        self.assertIn("rect.right > viewportWidth + 1", HARNESS)
        self.assertIn("node.scrollWidth > node.clientWidth + 1", HARNESS)
        self.assertIn("Read-only Handelsverlauf enthält unerwartete Aktion", HARNESS)

    def test_projection_proof_rejects_compensated_pair_and_wrong_execution_price(self):
        self.assertIn("COMPENSATED_BUY_ID in ids or COMPENSATION_ID in ids", HARNESS)
        self.assertIn('entry.get("unit_price_cents") != UNIT_PRICE_CENTS', HARNESS)
        self.assertIn('[entry.get("kind") for entry in history] != ["sell", "buy"]', HARNESS)


if __name__ == "__main__":
    unittest.main()
