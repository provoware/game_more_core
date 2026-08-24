from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[2]
A4 = ROOT / "web" / "a4"


class A4ClientResilienceTests(unittest.TestCase):
    def test_initial_assets_use_one_explicit_revision_and_resilience_loads_first(self):
        html = (A4 / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<meta name="bunker-asset-revision" content="([^"]+)">', html)
        self.assertIsNotNone(match)
        revision = match.group(1)
        self.assertTrue(revision)
        for asset in (
            "styles.css",
            "client_resilience.js",
            "map_pro.js",
            "ui_prefs.js",
            "event_timeline.js",
            "app.js",
            "assistant_jobs_ui.js",
        ):
            self.assertIn(f'{asset}?v={revision}', html)
        self.assertLess(html.index("client_resilience.js"), html.index("event_timeline.js"))
        self.assertLess(html.index("client_resilience.js"), html.index("app.js"))

    def test_dynamic_ui_modules_inherit_asset_revision(self):
        source = (A4 / "ui_prefs.js").read_text(encoding="utf-8")
        self.assertIn('meta[name="bunker-asset-revision"]', source)
        self.assertIn('url.searchParams.set("v", ASSET_REVISION)', source)
        for asset in (
            "control_deck_focus.js",
            "district_biography.js",
            "finance_statement_export.js",
            "scene_job_payout_preview.js",
            "recovery_actions_ui.js",
            "map_usability.js",
        ):
            self.assertIn(f'appendModule("{asset}"', source)

    def test_transport_retry_is_bounded_and_writes_require_idempotency_key(self):
        source = (A4 / "client_resilience.js").read_text(encoding="utf-8")
        self.assertIn("const API_TIMEOUT_MS = 8000", source)
        self.assertIn("const SAFE_GET_RETRY_DELAYS_MS = [250, 900]", source)
        self.assertIn("const IDEMPOTENT_WRITE_RETRY_DELAYS_MS = [400]", source)
        self.assertIn("function hasCommandId(body)", source)
        self.assertIn('method === "POST" && hasCommandId(init.body)', source)
        self.assertIn('url.pathname.startsWith("/api/")', source)
        self.assertNotIn("while (true)", source)

    def test_timeline_polling_is_single_flight_with_bounded_backoff(self):
        source = (A4 / "event_timeline.js").read_text(encoding="utf-8")
        self.assertIn("let refreshPromise = null", source)
        self.assertIn("if (refreshPromise) return refreshPromise", source)
        self.assertIn("const MAX_BACKOFF_MS = 30000", source)
        self.assertIn("window.setTimeout", source)
        self.assertNotIn("window.setInterval", source)


if __name__ == "__main__":
    unittest.main()
