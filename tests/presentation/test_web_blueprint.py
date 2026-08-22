import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class BlueprintParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.image_sources = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "img":
            self.image_sources.append(values.get("src"))


class WebBlueprintContractTests(unittest.TestCase):
    def test_html_keeps_exact_asset_and_evaluation_targets(self):
        parser = BlueprintParser()
        parser.feed((ROOT / "web/index.html").read_text(encoding="utf-8"))
        self.assertIn("../docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp", parser.image_sources)
        self.assertTrue({"workflow", "variants", "debug-output", "system-status"} <= parser.ids)

    def test_renderer_consumes_canonical_manifest_contract(self):
        manifest = json.loads((ROOT / "manifests/UI_MANIFEST.json").read_text(encoding="utf-8"))
        script = (ROOT / "web/app.js").read_text(encoding="utf-8")
        self.assertEqual(5, len(manifest["focus_model"]["workflow"]))
        self.assertEqual(4, len(manifest["variants"]))
        self.assertIn("../manifests/UI_MANIFEST.json", script)
        self.assertIn("window.blueprintReport", script)
        self.assertIn('record("visual_integrity"', script)


if __name__ == "__main__":
    unittest.main()
