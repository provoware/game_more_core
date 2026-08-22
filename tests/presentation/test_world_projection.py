import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.application.world_service import WorldService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel
from bunkerfrequenz.presentation.a4_game_projection import build_a4_game_projection
from bunkerfrequenz.presentation.world_projection import build_world_projection

ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
WORLD = json.loads((ROOT / "manifests" / "WORLD_MANIFEST.json").read_text(encoding="utf-8"))
TEXTS = json.loads((ROOT / "content" / "de" / "world.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T17:30:00+02:00",
        "world-projection-session",
        "player-local",
        "character",
        "player-local",
        command_id,
        "world-projection-test",
        "0.8.5-d1",
        "player-local",
    )


class WorldProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        self.character = CharacterState("player-local", "Ria Beton")
        self.kernel.initialize_state({"character": self.character.to_dict()})
        self.service = WorldService(self.kernel, WORLD)
        self.service.ensure_player(self.character, context=context("register"))

    def test_intro_uses_confirmed_player_name_and_identity_is_visible(self):
        projection = build_world_projection(self.kernel.load_state(), manifest=WORLD, texts=TEXTS)
        self.assertEqual(projection["booking_id"], "BF-000001")
        self.assertIn("Ria Beton", projection["intro"]["text"])
        self.assertFalse(projection["intro"]["acknowledged"])
        self.assertEqual(projection["housing"]["status"], "homeless")
        self.assertEqual(projection["city"]["price_multiplier_bps"], 10000)
        self.assertEqual(
            set(projection["district_metrics"]),
            {"heat", "prestige", "police_pressure", "scene_activity"},
        )

    def test_storefront_projection_exposes_availability_but_not_secret_classification(self):
        self.service.move(
            "player-local",
            city_id="berlin",
            district_id="neukoelln",
            location_id="tape_kiosk",
            context=context("move-tape"),
        )
        projection = build_world_projection(self.kernel.load_state(), manifest=WORLD, texts=TEXTS)
        current = projection["current_location"]
        self.assertTrue(current["storefront_available"])
        self.assertEqual(set(current["mini_games"]), {"xoxo", "slot"})
        serialized = json.dumps(projection, ensure_ascii=False)
        self.assertNotIn("note_keys", serialized)
        self.assertNotIn("secret_index", serialized)
        self.assertNotIn("window.tape.secret", serialized)

    def test_a4_projection_includes_world_without_mutating_confirmed_state(self):
        before = self.kernel.load_state()
        projection = build_a4_game_projection(
            before,
            incident_catalog=build_incident_catalog(INCIDENTS),
            world_manifest=WORLD,
            world_texts=TEXTS,
        )
        self.assertEqual(projection["view_model_version"], "0.8.5-d1")
        self.assertTrue(projection["state_blocks"]["world"])
        self.assertEqual(projection["world"]["booking_id"], "BF-000001")
        self.assertEqual(self.kernel.load_state(), before)


if __name__ == "__main__":
    unittest.main()
