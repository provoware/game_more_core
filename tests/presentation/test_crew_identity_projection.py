import unittest

from bunkerfrequenz.domain.crew_identity import default_crew_identity
from bunkerfrequenz.presentation.crew_identity_projection import build_crew_identity_projection


class CrewIdentityProjectionTests(unittest.TestCase):
    def test_projection_exposes_only_catalogued_render_values_and_sync_recipe(self):
        projection = build_crew_identity_projection({
            "mode": "logo",
            "style": "band",
            "symbol": "speaker",
            "primary_color_id": "acid_green",
            "secondary_color_id": "black",
            "accent_color_id": "hot_pink",
            "mark": "BF",
        })

        self.assertEqual(projection["identity"]["mode"], "logo")
        self.assertTrue(projection["render"]["primary"].startswith("#"))
        self.assertEqual(projection["render"]["symbol_glyph"], "▣")
        self.assertFalse(projection["sync_contract"]["image_blob_required"])
        self.assertTrue(projection["sync_contract"]["stable_character_id_required"])
        self.assertEqual(
            set(projection["sync_contract"]["field_set"]),
            set(default_crew_identity()),
        )

        projection["identity"]["mark"] = "MUTATED"
        self.assertEqual(default_crew_identity()["mark"], "")

    def test_legacy_none_uses_stable_default(self):
        projection = build_crew_identity_projection(None)
        self.assertEqual(projection["identity"], default_crew_identity())


if __name__ == "__main__":
    unittest.main()
