from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
EXPORT = (ROOT / "web" / "a4" / "finance_statement_export.js").read_text(encoding="utf-8")
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")


class A4FinanceExportTests(unittest.TestCase):
    def test_export_module_uses_existing_finance_statement_projection_only(self):
        self.assertIn("state.projection?.scene_jobs?.finance_statement", EXPORT)
        self.assertIn("statement?.entries", EXPORT)
        self.assertIn("statement?.totals", EXPORT)
        self.assertIn("statement?.supported_entries", EXPORT)
        self.assertIn("statement?.other_entries", EXPORT)
        self.assertIn("statement?.filters", EXPORT)
        self.assertNotIn("finance.ledger", EXPORT)
        self.assertNotIn("ledger", EXPORT.lower().replace("bestätigte fin-statements-projection", ""))
        self.assertNotIn("reduce(", EXPORT)
        self.assertNotIn("/api/command", EXPORT)
        self.assertNotIn("fetch(", EXPORT)

    def test_txt_and_csv_export_all_projection_entries_without_local_filter(self):
        self.assertIn("csvFromProjection", EXPORT)
        self.assertIn("txtFromProjection", EXPORT)
        self.assertIn("bunkerfrequenz-kontoauszug.csv", EXPORT)
        self.assertIn("bunkerfrequenz-kontoauszug.txt", EXPORT)
        self.assertNotIn("statementFilter", EXPORT)
        for field in (
            "sequence",
            "transaction_id",
            "kind",
            "group",
            "label",
            "amount_cents",
            "cash_after_cents",
            "bank_after_cents",
            "source_label",
        ):
            self.assertIn(f'"{field}"', EXPORT)

    def test_export_does_not_invent_time_or_persist_game_state(self):
        for forbidden in ("new Date", "Date.now", "timestamp", "created_at", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, EXPORT)
        self.assertIn("Blob", EXPORT)
        self.assertIn("URL.createObjectURL", EXPORT)
        self.assertIn("anchor.download", EXPORT)
        self.assertIn("Export bleibt lokal und verändert weder Save noch Ledger", EXPORT)

    def test_export_module_is_loaded_by_existing_small_ui_loader(self):
        self.assertIn('script.src = "finance_statement_export.js"', PREFS)
        self.assertIn('script.dataset.financeStatementExport = "true"', PREFS)
        self.assertIn("ensureFinanceStatementExportModule();", PREFS)


if __name__ == "__main__":
    unittest.main()
