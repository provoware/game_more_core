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
        for forbidden in ("finance.ledger", "ledger_entries", "PlayerFinanceState", "build_scene_jobs_projection"):
            self.assertNotIn(forbidden, EXPORT)
        self.assertNotIn("reduce(", EXPORT)
        self.assertNotIn("/api/command", EXPORT)
        self.assertNotIn("fetch(", EXPORT)

    def test_txt_and_csv_export_all_projection_entries_without_local_filter(self):
        self.assertIn("csvFromProjection", EXPORT)
        self.assertIn("txtFromProjection", EXPORT)
        self.assertIn('FILE_BASENAME = "bunkerfrequenz-kontoauszug"', EXPORT)
        self.assertIn('`${FILE_BASENAME}.${format}`', EXPORT)
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

    def test_preview_checksum_copy_and_download_share_exact_serializer_output(self):
        self.assertIn("function serializeStatement(format, statement)", EXPORT)
        self.assertIn("function checksum32(content)", EXPORT)
        self.assertIn("new TextEncoder().encode(content)", EXPORT)
        self.assertIn("Math.imul(hash, 0x01000193)", EXPORT)
        self.assertIn("const content = renderPreview(format);", EXPORT)
        self.assertIn("downloadText(`${FILE_BASENAME}.${format}`, mimeType, content)", EXPORT)
        self.assertIn("navigator.clipboard.writeText(previewContent)", EXPORT)
        self.assertIn('preview.id = "jobs-finance-export-preview"', EXPORT)
        self.assertIn('checksum.id = "jobs-finance-export-checksum"', EXPORT)
        self.assertIn("TXT PRÜFEN", EXPORT)
        self.assertIn("CSV PRÜFEN", EXPORT)
        self.assertIn("VORSCHAU KOPIEREN", EXPORT)
        self.assertIn("Bytes · Prüfsumme", EXPORT)
        self.assertNotIn("crypto.subtle", EXPORT)

    def test_export_does_not_invent_time_or_persist_game_state(self):
        for forbidden in ("new Date", "Date.now", "timestamp", "created_at", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, EXPORT)
        self.assertIn("Blob", EXPORT)
        self.assertIn("URL.createObjectURL", EXPORT)
        self.assertIn("anchor.download", EXPORT)
        self.assertIn("Vorschau, Prüfsumme, Kopieren und Download bleiben lokal", EXPORT)

    def test_export_module_is_loaded_by_existing_small_ui_loader(self):
        self.assertIn('appendModule("finance_statement_export.js", "finance-statement-export")', PREFS)
        self.assertIn('url.searchParams.set("v", ASSET_REVISION)', PREFS)
        self.assertIn("ensureFinanceStatementExportModule();", PREFS)


if __name__ == "__main__":
    unittest.main()
