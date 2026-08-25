from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
CREW_STYLES = (ROOT / "web" / "a4" / "crew_identity.css").read_text(encoding="utf-8")
MAP_UI = (ROOT / "web" / "a4" / "map_usability.js").read_text(encoding="utf-8")


class A4AvatarVisualConsistencyTests(unittest.TestCase):
    def test_profile_hud_map_clone_and_ranking_share_high_contrast_outline(self):
        block_start = "body.ui-high-contrast .crew-identity-preview,"
        self.assertIn(block_start, CREW_STYLES)
        block = CREW_STYLES[CREW_STYLES.index(block_start):CREW_STYLES.index("@media (prefers-reduced-motion: reduce)")]
        for token in (
            "body.ui-high-contrast .crew-identity-preview",
            "body.ui-high-contrast .hud-crew-preview",
            "body.ui-high-contrast .hall-local-crew-preview",
            "border-color: #fff",
            "0 0 0 2px #000",
            "var(--crew-accent, #ff5a1f)",
        ):
            with self.subTest(token=token):
                self.assertIn(token, block)

    def test_symbols_and_short_marks_remain_visible_in_high_contrast(self):
        for token in (
            "body.ui-high-contrast .crew-identity-symbol",
            "body.ui-high-contrast .hud-crew-symbol",
            "outline: 1px solid #fff",
            "body.ui-high-contrast .crew-identity-mark",
            "body.ui-high-contrast .hud-crew-mark",
            "background: #000",
            "color: #fff",
        ):
            with self.subTest(token=token):
                self.assertIn(token, CREW_STYLES)

    def test_compact_ranking_mark_keeps_same_readable_floor_as_small_hud(self):
        ranking_block_start = ".hall-local-crew-preview .hud-crew-mark {"
        ranking_block = CREW_STYLES[
            CREW_STYLES.index(ranking_block_start):CREW_STYLES.index("@media (max-width: 1100px)")
        ]
        compact_hud = CREW_STYLES[
            CREW_STYLES.index("@media (max-width: 1100px)"):CREW_STYLES.index("@media (min-width: 721px)")
        ]
        self.assertIn("font-size: .34rem", ranking_block)
        self.assertIn("font-size: .34rem", compact_hud)
        self.assertNotIn("font-size: .3rem", ranking_block)

    def test_map_badges_reuse_hud_preview_so_the_same_contrast_rule_applies(self):
        self.assertIn('badge.className = `hud-crew-preview ${className}`', MAP_UI)
        self.assertIn('crewBadge("map-crew-badge", "1.35rem")', MAP_UI)
        self.assertIn('crewBadge("map-detail-crew-preview", "2rem")', MAP_UI)
        for forbidden in ("fetch(", "/api/", "sendCommand", "localStorage"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, MAP_UI)

    def test_reduced_motion_still_covers_all_shared_avatar_surfaces(self):
        reduced = CREW_STYLES[CREW_STYLES.index("@media (prefers-reduced-motion: reduce)"):]
        for token in (
            ".crew-identity-preview",
            ".hud-crew-preview",
            ".hall-local-crew-preview",
            "transition: none !important",
            "animation: none !important",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reduced)


if __name__ == "__main__":
    unittest.main()
