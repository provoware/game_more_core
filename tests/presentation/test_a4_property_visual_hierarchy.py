from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
CSS = (ROOT / "web" / "a4" / "visual_hierarchy_3.css").read_text(encoding="utf-8")
INDEX = (ROOT / "web" / "a4" / "index.html").read_text(encoding="utf-8")
APP = (ROOT / "web" / "a4" / "app.js").read_text(encoding="utf-8")


class A4PropertyVisualHierarchyTests(unittest.TestCase):
    def test_existing_property_surface_is_reused(self):
        self.assertIn('id="property-panel" class="panel hidden"', INDEX)
        self.assertIn('id="property-list" class="equipment-list"', INDEX)
        self.assertIn('function renderProperties(properties, propertyUpgrades)', APP)
        self.assertIn('#property-panel {', CSS)
        self.assertIn('#property-list {', CSS)

    def test_property_hierarchy_is_presentation_only(self):
        self.assertIn('grid-template-columns: repeat(2, minmax(0, 1fr));', CSS)
        self.assertIn('@media (max-width: 980px)', CSS)
        for token in ('fetch(', '/api/command', 'sendCommand', 'localStorage', 'sessionStorage'):
            self.assertNotIn(token, CSS)

    def test_accessibility_fallbacks_remain_explicit(self):
        self.assertIn('body.ui-high-contrast #property-list > .equipment-row', CSS)
        self.assertIn('@media (prefers-reduced-motion: reduce)', CSS)
        self.assertIn('#property-panel,', CSS)


if __name__ == "__main__":
    unittest.main()
