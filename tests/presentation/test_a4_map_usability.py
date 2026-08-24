from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MODULE = (ROOT / "web" / "a4" / "map_usability.js").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "map_usability.css").read_text(encoding="utf-8")
UI_PREFS = (ROOT / "web" / "a4" / "ui_prefs.js").read_text(encoding="utf-8")
MAP_JS = (ROOT / "web" / "a4" / "map_pro.js").read_text(encoding="utf-8")


class A4MapUsabilityTests(unittest.TestCase):
    def test_module_is_loaded_without_replacing_existing_map_renderer(self):
        self.assertIn('script.src = "map_usability.js"', UI_PREFS)
        self.assertIn('script.dataset.mapUsability = "true"', UI_PREFS)
        self.assertIn("window.BunkerMapPro = Object.freeze({ render });", MAP_JS)
        self.assertNotIn("BunkerMapPro", MODULE)

    def test_usability_layer_is_local_read_only_presentation(self):
        forbidden = (
            "/api/command",
            "sendCommand",
            "fetch(",
            "XMLHttpRequest",
            "localStorage",
            "sessionStorage",
            "navigator.geolocation",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, MODULE)
        self.assertIn('link.href = "map_usability.css"', MODULE)
        self.assertIn("MutationObserver", MODULE)

    def test_labels_are_optional_and_selected_objects_remain_visible(self):
        self.assertIn('button.dataset.mapViewAction = LABEL_ACTION', MODULE)
        self.assertIn('canvas.classList.toggle("map-labels-all", labelsVisible)', MODULE)
        self.assertIn('button.setAttribute("aria-pressed"', MODULE)
        self.assertIn(".map-marker.is-selected .map-marker-label", STYLES)
        self.assertIn("#berlin-map-canvas.map-labels-all .map-marker-label", STYLES)
        self.assertIn("opacity: 0;", STYLES)
        self.assertIn("visibility: hidden;", STYLES)

    def test_visual_hierarchy_and_legend_cover_object_types(self):
        self.assertIn('legend.setAttribute("aria-label", "Kartenlegende")', MODULE)
        for label in ("Standard", "Strong", "Prime", "Legendary", "Eigentum", "Hall"):
            self.assertIn(f'"{label}"', MODULE)
        for selector in (
            ".map-marker.tier-standard",
            ".map-marker.tier-strong",
            ".map-marker.tier-prime",
            ".map-marker.tier-legendary",
            ".map-marker.owned::after",
            ".map-marker.hall",
            ".map-district.is-selected",
        ):
            self.assertIn(selector, STYLES)

    def test_small_screen_high_contrast_and_reduced_motion_are_supported(self):
        self.assertIn("@media (max-width: 760px)", STYLES)
        self.assertIn("body.ui-high-contrast #berlin-map-canvas", STYLES)
        self.assertIn("@media (prefers-reduced-motion: reduce)", STYLES)
        self.assertIn('canvas.setAttribute(\n      "aria-description"', MODULE)


if __name__ == "__main__":
    unittest.main()
