from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
SYNC_JS = (ROOT / "web" / "a4" / "crew_identity_hud_sync.js").read_text(encoding="utf-8")
APP_JS = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "crew_identity.css").read_text(encoding="utf-8")


class A4AvatarRankingPresenceTests(unittest.TestCase):
    def test_local_ranking_badge_uses_confirmed_character_id_boundary(self):
        self.assertIn('entry.character_id === hall.local_character_id', APP_JS)
        self.assertIn('entry.character_id === hall.local_character_id', SYNC_JS)
        self.assertIn('const localIndex = (board.entries || []).findIndex', SYNC_JS)
        self.assertNotIn('textContent.endsWith', SYNC_JS)
        self.assertNotIn('includes(" · DU")', SYNC_JS)

    def test_existing_hall_renderer_is_wrapped_without_second_ranking_source(self):
        self.assertIn('const baseRenderHall = renderHall;', SYNC_JS)
        self.assertIn('renderHall = function renderHallWithConfirmedCrew(hall)', SYNC_JS)
        self.assertIn('const result = baseRenderHall(hall);', SYNC_JS)
        self.assertIn('renderConfirmedHallCrew(hall);', SYNC_JS)
        for forbidden in ('fetch(', '/api/', 'XMLHttpRequest', 'localStorage', 'sessionStorage'):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, SYNC_JS)

    def test_only_local_row_receives_confirmed_hud_identity_clone(self):
        self.assertIn('.hud-crew-preview', SYNC_JS)
        self.assertIn('.hud-crew-identity', SYNC_JS)
        self.assertIn('badge.className = "hall-local-crew-preview";', SYNC_JS)
        self.assertIn('marker.className = "hall-local-crew";', SYNC_JS)
        self.assertIn('marker.setAttribute("aria-label", "Deine bestätigte Crew-Marke")', SYNC_JS)
        self.assertIn('row.prepend(marker);', SYNC_JS)

    def test_ranking_badge_is_compact_responsive_and_accessible(self):
        for token in (
            '.hall-local-crew {',
            '.hall-local-crew-preview {',
            '.hall-local-crew-preview[data-mode="logo"]',
            'body.ui-high-contrast .hall-local-crew-preview',
            '@media (max-width: 720px)',
            '@media (prefers-reduced-motion: reduce)',
        ):
            with self.subTest(token=token):
                self.assertIn(token, STYLES)


if __name__ == "__main__":
    unittest.main()
