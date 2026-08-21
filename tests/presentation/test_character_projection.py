import json
import unittest
from copy import deepcopy
from pathlib import Path

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.presentation import build_character_projection


ROOT = Path(__file__).resolve().parents[2]
CATALOG_FILES = (
    "skills.json",
    "traits.json",
    "trait_effects.json",
    "trait_consequences.json",
    "specializations.json",
    "stages.json",
)


def load_catalog() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for name in CATALOG_FILES:
        catalog.update(json.loads((ROOT / "content/de/ui" / name).read_text(encoding="utf-8")))
    return catalog


def biography_record(event_id: str, sequence: int) -> dict:
    return {
        "event_id": event_id,
        "event_type": "character.biography_entry_added",
        "sequence": sequence,
        "character_id": "char.pppoppi",
        "payload": {
            "entry_id": f"entry-{event_id}",
            "category": "event",
            "title_key": "biography.event.title",
            "body_key": "biography.event.body",
            "placeholders": {"location": "bunker-09"},
        },
    }


class CharacterProjectionTest(unittest.TestCase):
    def test_every_manifest_id_has_its_separate_german_catalog_key(self):
        skills = json.loads((ROOT / "manifests/SKILL_MANIFEST.json").read_text(encoding="utf-8"))
        traits = json.loads((ROOT / "manifests/TRAIT_MANIFEST.json").read_text(encoding="utf-8"))
        engine = json.loads((ROOT / "manifests/TRAIT_ENGINE_MANIFEST.json").read_text(encoding="utf-8"))
        progression = json.loads((ROOT / "manifests/PROGRESSION_MANIFEST.json").read_text(encoding="utf-8"))
        catalog = load_catalog()

        expected = {f"{item['skill_id']}.label" for item in skills["skills"]}
        expected |= {f"{item['trait_id']}.label" for item in traits["traits"]}
        families = {
            item["effect_template_id"].removeprefix("trait_template.")
            for item in engine["effect_templates"]
        }
        expected |= {f"trait.effect.{family}" for family in families}
        expected |= {f"trait.consequence.{family}" for family in families}
        model = progression["specialization_model"]
        expected |= {
            f"specialization.{item['specialization_id'].removeprefix('spec.')}.label"
            for item in model["specializations"]
        }
        expected |= {f"stage.{item['stage']}.label" for item in model["stages"]}
        self.assertTrue(expected.issubset(catalog))

    def test_projection_is_catalogued_bounded_and_detached(self):
        character = CharacterState("char.pppoppi", "P", additional_nicknames=["Poppsen"])
        character.skills.update({"technik": 30, "musik": 20, "instinkt": 100})
        character.skill_xp.update({"technik": 35, "instinkt": 999})
        character.traits["krisenfest"] = 1
        character.trait_progress["krisenfest"] = {"evidence": 300.0}
        character.specialization = {
            "specialization_id": "spec.klangarchitektur",
            "stage": "tendenz",
        }
        catalog = load_catalog()

        projection = build_character_projection(character, [], catalog)
        emitted = []
        for entry in projection["skills"] + projection["traits"]:
            emitted.extend(value for key, value in entry.items() if key.endswith("_key"))
        emitted.extend(
            value
            for key, value in projection["specialization"].items()
            if key.endswith("_key")
        )

        self.assertTrue(all(key in catalog for key in emitted))
        self.assertEqual(
            [item["skill_id"] for item in projection["top_skills"]],
            ["skill.instinkt", "skill.technik", "skill.musik"],
        )
        max_skill = next(item for item in projection["skills"] if item["skill_id"] == "skill.instinkt")
        self.assertEqual(max_skill["xp_to_next"], 0)
        self.assertEqual(max_skill["progress_percent"], 100)
        self.assertTrue(
            all(0 <= item["progress_percent"] <= 100 for item in projection["skills"])
        )
        self.assertTrue(
            all(
                item["progress_percent"] is None or 0 <= item["progress_percent"] <= 100
                for item in projection["traits"]
            )
        )

        before = deepcopy(character.to_dict())
        projection["overview"]["additional_nicknames"].append("Copy")
        projection["skills"][0]["value"] = 99
        projection["traits"][0]["tier"] = 5
        projection["specialization"]["stage"] = "changed"
        self.assertEqual(character.to_dict(), before)

    def test_locked_known_trait_hides_evidence_and_progress(self):
        character = CharacterState("char.pppoppi", "P")
        character.trait_progress["scout"] = {"evidence": 219.0}
        character.trait_evidence["scout"] = 219.0

        projection = build_character_projection(character, [], load_catalog())
        scout = next(item for item in projection["traits"] if item["trait_id"] == "trait.pppoppi.scout")

        self.assertEqual(scout["tier"], 0)
        self.assertEqual(scout["next_tier"], 1)
        self.assertIsNone(scout["evidence"])
        self.assertIsNone(scout["progress_percent"])

    def test_biography_is_integrated_sorted_and_detached(self):
        character = CharacterState("char.pppoppi", "P")
        records = [biography_record("event-b", 2), biography_record("event-a", 1)]
        before = deepcopy(records)

        projection = build_character_projection(character, records, load_catalog())

        self.assertEqual(
            [entry["event_id"] for entry in projection["biography"]],
            ["event-a", "event-b"],
        )
        projection["biography"][0]["placeholders"]["location"] = "changed"
        self.assertEqual(records, before)


if __name__ == "__main__":
    unittest.main()
