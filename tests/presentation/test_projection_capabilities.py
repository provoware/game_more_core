import json
import unittest
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


class ProjectionCapabilitiesTest(unittest.TestCase):
    def test_defaults_to_safe_false_capabilities(self):
        projection = build_character_projection(
            CharacterState("char.pppoppi", "PPPOPPI"),
            [],
            load_catalog(),
        )
        self.assertEqual(
            projection["capabilities"],
            {
                "can_edit_profile": False,
                "can_undo_profile": False,
                "can_execute_action": False,
            },
        )

    def test_confirmed_capabilities_are_bounded_and_detached(self):
        capabilities = {
            "can_edit_profile": True,
            "can_undo_profile": True,
            "can_execute_action": True,
            "internal_debug_permission": True,
        }
        projection = build_character_projection(
            CharacterState("char.pppoppi", "PPPOPPI"),
            [],
            load_catalog(),
            capabilities,
        )

        self.assertEqual(
            projection["capabilities"],
            {
                "can_edit_profile": True,
                "can_undo_profile": True,
                "can_execute_action": True,
            },
        )
        capabilities["can_edit_profile"] = False
        self.assertTrue(projection["capabilities"]["can_edit_profile"])


if __name__ == "__main__":
    unittest.main()
