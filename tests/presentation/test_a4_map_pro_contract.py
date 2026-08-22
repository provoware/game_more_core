from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
MAP_JS = (ROOT / "web" / "a4" / "map_pro.js").read_text(encoding="utf-8")
APP_JS = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
STYLES = (ROOT / "web" / "a4" / "styles.css").read_text(encoding="utf-8")


class A4MapProContractTests(unittest.TestCase):
    def test_map_renderer_has_no_write_or_external_map_path(self):
        forbidden = (
            "/api/command",
            "sendCommand",
            "fetch(",
            "XMLHttpRequest",
            "localStorage",
            "sessionStorage",
            "navigator.geolocation",
            "maps.google",
            "mapbox",
            "leaflet",
        )
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, MAP_JS)
        self.assertIn("window.BunkerMapPro = Object.freeze({ render });", MAP_JS)

    def test_existing_a4_render_cycle_is_the_only_map_data_bridge(self):
        self.assertIn("window.BunkerMapPro?.render(p.berlin_ops_map);", APP_JS)
        self.assertLess(INDEX.index('src="map_pro.js"'), INDEX.index('src="app.js"'))
        self.assertIn('id="map-pro-panel"', INDEX)
        self.assertIn('id="berlin-map-canvas"', INDEX)
        self.assertIn('id="map-detail"', INDEX)

    def test_filter_and_accessibility_contract_is_visible_in_markup_and_css(self):
        for filter_id in ("all", "owned", "prime", "hall"):
            self.assertIn(f'data-map-filter="{filter_id}"', INDEX)
        self.assertIn('role="group" aria-label="Kartenfilter"', INDEX)
        self.assertIn('aria-live="polite" aria-label="Kartendetails"', INDEX)
        self.assertIn("button.addEventListener(\"focus\"", MAP_JS)
        self.assertIn("aria-pressed", MAP_JS)
        self.assertIn(".map-marker:focus-visible", STYLES)
        self.assertIn("@media (prefers-reduced-motion: reduce)", STYLES)
        self.assertIn(".map-marker.tier-standard", STYLES)
        self.assertIn(".map-marker.tier-strong", STYLES)
        self.assertIn(".map-marker.tier-prime", STYLES)
        self.assertIn(".map-marker.tier-legendary", STYLES)
        self.assertIn(".map-marker.owned", STYLES)
        self.assertIn(".map-marker.hall", STYLES)

    def test_map_copy_states_that_navigation_and_domain_writes_are_outside_renderer(self):
        self.assertIn("Keine Navigation, kein Geocoding, keine eigene Fachlogik.", INDEX)
        self.assertIn("Die Karte ist read-only.", INDEX)
        self.assertIn("Kaufen und Ausbauen bleibt im Property-Panel", INDEX)


if __name__ == "__main__":
    unittest.main()
