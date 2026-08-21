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
import unittest

from bunkerfrequenz.domain.character import CharacterState, initial_skills
from bunkerfrequenz.domain.progression import ProgressionRules
from bunkerfrequenz.presentation import build_character_projection


CATALOG = {
    "skills": {
        skill_id: {"label_key": f"skill.{skill_id}.label"}
        for skill_id in initial_skills()
    },
    "traits": {
        "krisenfest": {
            "trait_id": "trait.test.krisenfest",
            "label_key": "trait.test.krisenfest.label",
            "effect_key": "trait.krisenfest.effect",
            "consequence_key": "trait.krisenfest.consequence",
        },
        "scout": {
            "trait_id": "trait.test.scout",
            "label_key": "trait.test.scout.label",
            "effect_key": "trait.scout.effect",
            "consequence_key": "trait.scout.consequence",
        },
    },
    "specializations": {
        "spec.spurensuche": {
            "label_key": "specialization.spurensuche.label",
            "stage_label_keys": {"profil": "specialization.stage.profil"},
        }
    },
    "journal_events": {
        "character.level_up": {
            "category": "level_milestone",
            "title_key": "biography.level_up.title",
            "body_key": "biography.level_up.body",
        }
    },
}


class CharacterProjectionTests(unittest.TestCase):
    def setUp(self):
        skills = initial_skills()
        skills.update({"technik": 80, "musik": 80, "organisation": 70})
        self.character = CharacterState(
            "char.test", "Test", additional_nicknames=["Echo"], skills=skills,
            skill_xp={"technik": 10_000, "musik": -5, "instinkt": 15},
            traits={"krisenfest": 1, "unknown": 2},
            trait_progress={
                "krisenfest": {"evidence": 10_000.0},
                "scout": {"evidence": 219.0},
                "unknown": {"evidence": 500.0},
            },
            specialization={"specialization_id": "spec.spurensuche", "stage": "profil"},
        )
        self.records = [
            {"event_id": "event-b", "event_type": "character.level_up", "sequence": 2,
             "payload": {"placeholders": {"level": 3}}},
            {"event_id": "event-a", "event_type": "character.level_up", "sequence": 2,
             "payload": {"placeholders": {"level": 2}}},
            {"event_id": "ignored", "event_type": "unknown", "sequence": 1, "payload": {}},
        ]

    def test_projection_is_deterministic_and_sorted(self):
        first = build_character_projection(self.character, self.records, CATALOG)
        second = build_character_projection(self.character, list(reversed(self.records)), CATALOG)

        self.assertEqual(first, second)
        self.assertEqual(
            [entry["skill_id"] for entry in first["top_skills"]],
            ["musik", "technik", "organisation"],
        )
        self.assertEqual([entry["event_id"] for entry in first["biography"]], ["event-a", "event-b"])

    def test_progress_is_bounded_and_uses_progression_rules(self):
        projection = build_character_projection(self.character, self.records, CATALOG)
        skills = {entry["skill_id"]: entry for entry in projection["skills"]}

        self.assertEqual(len(skills), 16)
        self.assertEqual(skills["technik"]["progress_percent"], 100.0)
        self.assertEqual(skills["technik"]["xp_to_next"], 0)
        self.assertEqual(skills["musik"]["progress_percent"], 0.0)
        required = ProgressionRules.xp_to_next_skill(10)
        self.assertEqual(skills["instinkt"]["xp_to_next"], required - 15)
        self.assertEqual(skills["instinkt"]["progress_percent"], round(15 / required * 100, 2))

        traits = {entry["trait_id"]: entry for entry in projection["traits"]}
        self.assertNotIn("trait.test.unknown", traits)
        self.assertEqual(traits["trait.test.krisenfest"]["progress_percent"], 100.0)
        self.assertIsNone(traits["trait.test.scout"]["evidence"])
        self.assertIsNone(traits["trait.test.scout"]["progress_percent"])

    def test_projection_is_detached_from_domain_state(self):
        projection = build_character_projection(self.character, self.records, CATALOG)
        projection["overview"]["additional_nicknames"].append("Copy")
        projection["skills"][0]["value"] = 99
        projection["traits"][0]["tier"] = 5
        projection["specialization"]["stage"] = "changed"

        self.assertEqual(self.character.additional_nicknames, ["Echo"])
        self.assertEqual(self.character.skills["belastbarkeit"], 10)
        self.assertEqual(self.character.traits["krisenfest"], 1)
        self.assertEqual(self.character.specialization["stage"], "profil")


if __name__ == "__main__":
    unittest.main()
