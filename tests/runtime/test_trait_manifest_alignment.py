import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.trait_effects import EFFECTS, NEGATIVE_CAP, POSITIVE_CAP, SOFT_CONFLICTS


class TraitManifestAlignmentTest(unittest.TestCase):
    def test_runtime_rules_match_trait_manifest(self):
        root = Path(__file__).resolve().parents[2]
        manifest = json.loads((root / "manifests/TRAIT_ENGINE_MANIFEST.json").read_text(encoding="utf-8"))
        expected = {}
        for template in manifest["effect_templates"]:
            family = template["effect_template_id"].split(".", 1)[1]
            expected[family] = (
                tuple(template["positive"]["tier_values"]), template["positive"]["metric"],
                tuple(template["tradeoff"]["tier_values"]), template["tradeoff"]["metric"],
            )
        self.assertEqual(EFFECTS, expected)
        self.assertEqual((POSITIVE_CAP, NEGATIVE_CAP), (manifest["effect_stack_caps"]["positive_pct"], manifest["effect_stack_caps"]["negative_pct"]))
        conflicts = tuple((item["templates"][0].split(".", 1)[1], item["templates"][1].split(".", 1)[1], item["activation_min_tier"], item["positive_effect_multiplier"]) for item in manifest["soft_conflicts"])
        self.assertEqual(SOFT_CONFLICTS, conflicts)


if __name__ == "__main__":
    unittest.main()
