from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[2]
MAP_JS = (ROOT / "web" / "a4" / "map_pro.js").read_text(encoding="utf-8")
MAP_MANIFEST = json.loads((ROOT / "manifests" / "CITY_MAP_MANIFEST.json").read_text(encoding="utf-8"))


class A4MapViewportAuditTests(unittest.TestCase):
    def test_edge_location_stays_off_center_after_focus_because_pan_is_bounded(self):
        generator_ost = next(item for item in MAP_MANIFEST["locations"] if item["location_id"] == "generator_ost")
        self.assertEqual(generator_ost["position"]["x"], 87)

        focus_zoom = 1.6
        max_pan = (focus_zoom - 1) * 50
        requested_pan_x = -(generator_ost["position"]["x"] - 50) * focus_zoom
        bounded_pan_x = max(-max_pan, min(max_pan, requested_pan_x))
        transformed_x = 50 + (generator_ost["position"]["x"] - 50) * focus_zoom + bounded_pan_x

        self.assertAlmostEqual(max_pan, 30.0)
        self.assertAlmostEqual(requested_pan_x, -59.2)
        self.assertAlmostEqual(transformed_x, 79.2)
        self.assertGreater(abs(transformed_x - 50), 25)

    def test_existing_reset_is_explicit_accessible_and_restores_overview(self):
        self.assertIn('mapViewButton("1:1", "reset", resetView, "Gesamtansicht wiederherstellen")', MAP_JS)
        self.assertRegex(
            MAP_JS,
            re.compile(
                r"function resetView\(\) \{\s*view\.zoom = 1;\s*view\.panX = 0;\s*view\.panY = 0;\s*applyView\(\);\s*updateViewStatus\(\"Gesamtansicht 1\.0× wiederhergestellt\.\"\);",
                re.MULTILINE,
            ),
        )

    def test_audit_does_not_require_second_map_or_persistence_path(self):
        forbidden = ("localStorage", "sessionStorage", "/api/command", "fetch(")
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, MAP_JS)
        self.assertIn("const MAX_ZOOM = 2.2;", MAP_JS)
        self.assertIn("function maxPan()", MAP_JS)
        self.assertIn("window.BunkerMapPro = Object.freeze({ render });", MAP_JS)


if __name__ == "__main__":
    unittest.main()
