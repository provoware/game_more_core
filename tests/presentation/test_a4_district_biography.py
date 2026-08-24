from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
BIO = (ROOT / "web" / "a4" / "district_biography.js").read_text(encoding="utf-8")
PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")


class A4DistrictBiographyTests(unittest.TestCase):
    def test_afterglow_uses_only_confirmed_district_timeline_entries(self):
        for marker in (
            'fetch("/api/state"',
            'entry?.kind === "district"',
            "entry?.metadata?.district_id",
            ".slice(-LIMIT)",
            "const LIMIT = 5",
            'document.getElementById("profile-panel")',
            'section.id = "district-biography"',
            "BERLIN // BESTÄTIGTE ERINNERUNGEN",
            "Quelle: Ereignis-Chronik",
        ):
            self.assertIn(marker, BIO)

    def test_afterglow_has_no_write_progression_random_or_time_authority(self):
        forbidden = (
            "/api/command",
            "localStorage",
            "sessionStorage",
            "Math.random",
            "Date.now",
            "new Date",
            "fetch(\"/api/checkpoint\"",
            "character.biography_entry_added",
            "xp",
            "relationship",
        )
        for marker in forbidden:
            self.assertNotIn(marker, BIO, marker)

    def test_loader_reuses_existing_small_ui_bootstrap(self):
        self.assertIn('appendModule("district_biography.js", "district-biography")', PREFS)
        self.assertIn('url.searchParams.set("v", ASSET_REVISION)', PREFS)
        self.assertIn("ensureDistrictBiographyModule();", PREFS)

    def test_visible_copy_does_not_claim_unconfirmed_timestamp(self):
        lowered = BIO.lower()
        self.assertNotIn("timestamp", lowered)
        self.assertNotIn("uhrzeit", lowered)
        self.assertNotIn("datum", lowered)
        self.assertIn("keine neuen werte, boni oder erfundenen zeitangaben", lowered)


if __name__ == "__main__":
    unittest.main()
