import json
import unittest
from pathlib import Path

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation import build_character_projection


ROOT = Path(__file__).resolve().parents[2]
CATALOG_FILES = (
    "skills.json", "traits.json", "trait_effects.json",
    "trait_consequences.json", "specializations.json", "stages.json",
)


def load_catalog() -> dict[str, str]:
    catalog = {}
    for name in CATALOG_FILES:
        catalog.update(json.loads((ROOT / "content/de/ui" / name).read_text(encoding="utf-8")))
    return catalog


class CharacterProjectionTest(unittest.TestCase):
    def test_every_manifest_id_has_its_separate_german_catalog_key(self):
        skills = json.loads((ROOT / "manifests/SKILL_MANIFEST.json").read_text(encoding="utf-8"))
        traits = json.loads((ROOT / "manifests/TRAIT_MANIFEST.json").read_text(encoding="utf-8"))
        engine = json.loads((ROOT / "manifests/TRAIT_ENGINE_MANIFEST.json").read_text(encoding="utf-8"))
        progression = json.loads((ROOT / "manifests/PROGRESSION_MANIFEST.json").read_text(encoding="utf-8"))
        catalog = load_catalog()

        expected = {f"{item['skill_id']}.label" for item in skills["skills"]}
        expected |= {f"{item['trait_id']}.label" for item in traits["traits"]}
        families = {item["effect_template_id"].removeprefix("trait_template.") for item in engine["effect_templates"]}
        expected |= {f"trait.effect.{family}" for family in families}
        expected |= {f"trait.consequence.{family}" for family in families}
        model = progression["specialization_model"]
        expected |= {
            f"specialization.{item['specialization_id'].removeprefix('spec.')}.label"
            for item in model["specializations"]
        }
        expected |= {f"stage.{item['stage']}.label" for item in model["stages"]}
        self.assertTrue(expected.issubset(catalog))

    def test_projection_emits_only_existing_keys_and_detached_values(self):
        character = CharacterState("char.pppoppi", "P", additional_nicknames=["Poppsen"])
        character.skills.update({"technik": 30, "musik": 20, "instinkt": 100})
        character.skill_xp.update({"technik": 35, "instinkt": 999})
        character.traits["krisenfest"] = 1
        character.trait_progress["krisenfest"] = {"evidence": 300.0}
        character.specialization = {"specialization_id": "spec.klangarchitektur", "stage": "tendenz"}
        catalog = load_catalog()

        projection = build_character_projection(character, [], catalog)
        emitted = []
        for entry in projection["skills"] + projection["traits"]:
            emitted.extend(value for key, value in entry.items() if key.endswith("_key"))
        emitted.extend(value for key, value in projection["specialization"].items() if key.endswith("_key"))

        self.assertTrue(all(key in catalog for key in emitted))
        self.assertEqual([item["skill_id"] for item in projection["top_skills"]], ["skill.instinkt", "skill.technik", "skill.musik"])
        self.assertEqual(next(item for item in projection["skills"] if item["skill_id"] == "skill.instinkt")["progress_percent"], 100)
        self.assertTrue(all(0 <= item["progress_percent"] <= 100 for item in projection["skills"] + projection["traits"]))
        character.additional_nicknames.append("Später")
        self.assertEqual(projection["overview"]["additional_nicknames"], ["Poppsen"])


if __name__ == "__main__":
    unittest.main()
