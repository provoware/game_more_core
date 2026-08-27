import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
TEXT = json.loads((ROOT / "content" / "de" / "ui" / "street_encounters.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, *, character_id: str = "player-local") -> JournalContext:
    return JournalContext(
        "2026-08-27T17:30:00+02:00",
        "street-story-session",
        "player-local",
        "character",
        "player-local",
        command_id,
        "street-story-test",
        "0.8.8",
        character_id,
    )


def story_manifest() -> dict:
    return {
        "schema_version": 2,
        "version": "street-story-test-v1",
        "selection": {
            "method": "sha256_stable_weighted",
            "weight_total": 100,
            "system_time_as_seed": False,
        },
        "policy": {
            "neutral_weight": 0,
            "positive_weight": 100,
            "negative_weight": 0,
            "positive_share_of_actual_encounters": 1.0,
            "effects_are_small": True,
            "inventory_changes": False,
            "economy_changes": False,
        },
        "approach_policy": {
            "default_approach_id": "balanced",
            "player_choice": True,
            "approach_changes_only_selection_weights": True,
            "effects_remain_encounter_authority": True,
            "system_time_as_authority": False,
            "compatible_replay_versions": [],
        },
        "follow_up_contract": dict(STREET["follow_up_contract"]),
        "micro_story_001": dict(STREET["micro_story_001"]),
        "approaches": [{
            "approach_id": "balanced",
            "label_key": "street.approach.balanced.label",
            "description_key": "street.approach.balanced.description",
            "weights": {"street.cable_tip": 100},
        }],
        "encounters": [{
            "encounter_id": "street.cable_tip",
            "polarity": "positive",
            "weight": 100,
            "title_key": "street.cable_tip.title",
            "body_key": "street.cable_tip.body",
            "effects": {"energy_delta": 1, "stress_delta": 0, "reputation_delta": 1},
        }],
    }


class StreetChainMicroStoryTests(unittest.TestCase):
    def new_runtime(self):
        tmp = tempfile.TemporaryDirectory()
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        character = CharacterState("player-local", "Street Story Tester")
        kernel.initialize_state({"character": character.to_dict()})
        return tmp, kernel, character, StreetEncounterService(kernel, story_manifest())

    def test_cable_tip_echo_is_catalogued_and_has_externalized_text(self):
        story = STREET["micro_story_001"]
        self.assertEqual(story["parent_encounter_id"], "street.cable_tip")
        self.assertEqual(story["followup_id"], "cable_tip_echo")
        self.assertEqual(TEXT[story["title_key"]], "Der Tipp macht die Runde")
        self.assertIn("Kabeltrick", TEXT[story["body_key"]])

    def test_later_confirmed_walk_resolves_cable_tip_echo_atomically_and_exactly_once(self):
        tmp, kernel, character, service = self.new_runtime()
        self.addCleanup(tmp.cleanup)

        first = service.walk(
            character,
            walk_instance_id="story-walk-001",
            world_seed="street-story-seed",
            journal_context=context("story-walk-001"),
        )
        self.assertEqual(first.encounter_id, "street.cable_tip")
        self.assertFalse(any(record["event_type"] == "street.followup_resolved" for record in kernel.read_records()))

        second = service.walk(
            first.character_after,
            walk_instance_id="story-walk-002",
            world_seed="street-story-seed",
            journal_context=context("story-walk-002"),
        )
        parent_event_id = "story-walk-001:001"
        child_event_id = f"street-followup:{parent_event_id}:cable_tip_echo"
        child = next(record for record in kernel.read_records() if record["event_id"] == child_event_id)

        self.assertIn(child_event_id, second.committed_event_ids)
        self.assertEqual(child["event_type"], "street.followup_resolved")
        self.assertEqual(child["causation_id"], parent_event_id)
        self.assertEqual(child["correlation_id"], f"street-chain:{parent_event_id}")
        self.assertEqual(child["payload"]["parent_event_id"], parent_event_id)
        self.assertEqual(child["payload"]["character_id"], "player-local")
        self.assertEqual(child["payload"]["followup_id"], "cable_tip_echo")
        self.assertNotIn("effects", child["payload"])

        records_after_second = kernel.read_records()
        replay = service.walk(
            first.character_after,
            walk_instance_id="story-walk-002",
            world_seed="street-story-seed",
            journal_context=context("story-walk-002"),
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(kernel.read_records(), records_after_second)
        self.assertEqual(sum(record["event_id"] == child_event_id for record in records_after_second), 1)

    def test_parent_character_conflict_fails_closed_before_trigger_walk_is_written(self):
        tmp, kernel, character, service = self.new_runtime()
        self.addCleanup(tmp.cleanup)
        kernel.commit(
            transaction_id="tx:corrupt-parent",
            events=[{
                "event_id": "corrupt-parent:001",
                "event_type": "street.encounter_resolved",
                "payload": {
                    "walk_instance_id": "corrupt-parent",
                    "approach_id": "balanced",
                    "encounter_id": "street.cable_tip",
                    "polarity": "positive",
                    "title_key": "street.cable_tip.title",
                    "body_key": "street.cable_tip.body",
                    "effects": {"energy_delta": 0, "stress_delta": 0, "reputation_delta": 0},
                    "contract_version": "street-story-test-v1",
                },
            }],
            derived_state={"character": character.to_dict()},
            context=context("corrupt-parent", character_id="other-character"),
        )
        records_before = kernel.read_records()

        with self.assertRaisesRegex(PersistenceError, "widersprüchliche Charakter-ID"):
            service.walk(
                character,
                walk_instance_id="story-walk-conflict",
                world_seed="street-story-seed",
                journal_context=context("story-walk-conflict"),
            )

        self.assertEqual(kernel.read_records(), records_before)
        self.assertFalse(kernel.has_event("story-walk-conflict:001"))


if __name__ == "__main__":
    unittest.main()
