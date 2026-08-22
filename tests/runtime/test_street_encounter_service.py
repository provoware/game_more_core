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
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-22T16:00:00+02:00",
        "street-test-session",
        "player-local",
        "character",
        "player-local",
        command_id,
        "street-test",
        "0.8.7-b1",
        "player-local",
    )


def new_runtime(character: CharacterState | None = None):
    tmp = tempfile.TemporaryDirectory()
    kernel = PersistenceKernel(tmp.name, ALLOWED)
    state = character or CharacterState("player-local", "Street Tester")
    kernel.initialize_state({"character": state.to_dict()})
    return tmp, kernel, state, StreetEncounterService(kernel, STREET)


def single_encounter_manifest() -> dict:
    return {
        "schema_version": 2,
        "version": "street-test-v2",
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
        "approaches": [{
            "approach_id": "balanced",
            "label_key": "street.approach.balanced.label",
            "description_key": "street.approach.balanced.description",
            "weights": {"street.test_boost": 100},
        }],
        "encounters": [{
            "encounter_id": "street.test_boost",
            "polarity": "positive",
            "weight": 100,
            "title_key": "street.test.title",
            "body_key": "street.test.body",
            "effects": {"energy_delta": 5, "stress_delta": -5, "reputation_delta": 2},
        }],
    }


class StreetEncounterServiceTests(unittest.TestCase):
    def test_real_catalog_has_expected_distribution_and_four_player_approaches(self):
        totals = {"neutral": 0, "positive": 0, "negative": 0}
        for encounter in STREET["encounters"]:
            totals[encounter["polarity"]] += encounter["weight"]

        self.assertEqual(totals, {"neutral": 25, "positive": 60, "negative": 15})
        self.assertEqual(sum(totals.values()), 100)
        self.assertAlmostEqual(
            totals["positive"] / (totals["positive"] + totals["negative"]),
            0.8,
        )
        self.assertFalse(STREET["selection"]["system_time_as_seed"])
        self.assertEqual(
            [item["approach_id"] for item in STREET["approaches"]],
            ["balanced", "recovery", "network", "scout"],
        )
        encounter_weights = {item["encounter_id"]: item["weight"] for item in STREET["encounters"]}
        balanced = next(item for item in STREET["approaches"] if item["approach_id"] == "balanced")
        self.assertEqual(balanced["weights"], encounter_weights)
        self.assertTrue(STREET["approach_policy"]["effects_remain_encounter_authority"])
        for approach in STREET["approaches"]:
            self.assertEqual(set(approach["weights"]), set(encounter_weights))
            self.assertEqual(sum(approach["weights"].values()), 100)
            self.assertNotIn("effects", approach)

    def test_same_seed_walk_and_approach_produce_same_result_in_independent_saves(self):
        tmp_a, kernel_a, character_a, service_a = new_runtime()
        tmp_b, kernel_b, character_b, service_b = new_runtime()
        self.addCleanup(tmp_a.cleanup)
        self.addCleanup(tmp_b.cleanup)

        result_a = service_a.walk(
            character_a,
            walk_instance_id="street-repeatable-001",
            world_seed="stable-world",
            journal_context=context("street-repeatable-001"),
            approach_id="network",
        )
        result_b = service_b.walk(
            character_b,
            walk_instance_id="street-repeatable-001",
            world_seed="stable-world",
            journal_context=context("street-repeatable-001"),
            approach_id="network",
        )

        self.assertEqual(result_a.approach_id, "network")
        self.assertEqual(result_a.encounter_id, result_b.encounter_id)
        self.assertEqual(result_a.polarity, result_b.polarity)
        self.assertEqual(result_a.effects, result_b.effects)
        self.assertEqual(result_a.character_after.to_dict(), result_b.character_after.to_dict())
        self.assertEqual(
            [record["event_type"] for record in kernel_a.read_records()],
            [record["event_type"] for record in kernel_b.read_records()],
        )

    def test_retry_same_walk_is_idempotent_and_cannot_change_approach(self):
        tmp, kernel, character, service = new_runtime()
        self.addCleanup(tmp.cleanup)
        first = service.walk(
            character,
            walk_instance_id="street-idempotent-001",
            world_seed="stable-world",
            journal_context=context("street-idempotent-001"),
            approach_id="recovery",
        )
        records_after_first = kernel.read_records()
        state_after_first = kernel.load_state()
        second = service.walk(
            character,
            walk_instance_id="street-idempotent-001",
            world_seed="stable-world",
            journal_context=context("street-idempotent-001"),
            approach_id="recovery",
        )

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.approach_id, "recovery")
        self.assertEqual(second.committed_event_ids, ())
        self.assertEqual(first.encounter_id, second.encounter_id)
        self.assertEqual(first.effects, second.effects)
        self.assertEqual(kernel.read_records(), records_after_first)
        self.assertEqual(kernel.load_state(), state_after_first)

        with self.assertRaisesRegex(PersistenceError, "anderen Ansatz"):
            service.walk(
                character,
                walk_instance_id="street-idempotent-001",
                world_seed="stable-world",
                journal_context=context("street-idempotent-001"),
                approach_id="scout",
            )
        self.assertEqual(kernel.read_records(), records_after_first)
        self.assertEqual(kernel.load_state(), state_after_first)

    def test_unknown_approach_fails_before_write(self):
        tmp, kernel, character, service = new_runtime()
        self.addCleanup(tmp.cleanup)
        with self.assertRaisesRegex(ValueError, "Unbekannter Street-Ansatz"):
            service.walk(
                character,
                walk_instance_id="street-bad-approach",
                world_seed="stable-world",
                journal_context=context("street-bad-approach"),
                approach_id="invented-cheat-mode",
            )
        self.assertEqual(kernel.read_records(), ())

    def test_legacy_085_record_replays_as_balanced_without_reroll(self):
        tmp, kernel, character, service = new_runtime()
        self.addCleanup(tmp.cleanup)
        legacy_event = {
            "event_id": "legacy-walk:001",
            "event_type": "street.encounter_resolved",
            "payload": {
                "walk_instance_id": "legacy-walk",
                "encounter_id": "street.none",
                "polarity": "neutral",
                "title_key": "street.none.title",
                "body_key": "street.none.body",
                "effects": {"energy_delta": 0, "stress_delta": 0, "reputation_delta": 0},
                "contract_version": "0.8.5-c1",
            },
        }
        kernel.commit(
            transaction_id="tx:legacy-walk",
            events=[legacy_event],
            derived_state={"character": character.to_dict()},
            context=context("legacy-walk"),
        )
        record_count = len(kernel.read_records())

        replay = service.walk(
            character,
            walk_instance_id="legacy-walk",
            world_seed="stable-world",
            journal_context=context("legacy-walk"),
        )
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.approach_id, "balanced")
        self.assertEqual(replay.encounter_id, "street.none")
        self.assertEqual(len(kernel.read_records()), record_count)

    def test_encounter_event_is_written_before_existing_character_effect_events(self):
        tmp, kernel, character, service = new_runtime()
        self.addCleanup(tmp.cleanup)
        result = service.walk(
            character,
            walk_instance_id="street-order-001",
            world_seed="stable-world",
            journal_context=context("street-order-001"),
            approach_id="scout",
        )
        records = kernel.read_records()

        self.assertEqual(records[0]["event_type"], "street.encounter_resolved")
        payload = records[0]["payload"]
        self.assertEqual(payload["approach_id"], "scout")
        self.assertEqual(payload["encounter_id"], result.encounter_id)
        self.assertEqual(payload["effects"], result.effects)
        self.assertEqual(payload["contract_version"], STREET["version"])
        selected = next(item for item in STREET["encounters"] if item["encounter_id"] == result.encounter_id)
        self.assertEqual(set(result.effects), set(selected["effects"]))
        self.assertTrue(
            all(
                record["event_type"] in {
                    "street.encounter_resolved",
                    "character.resources_changed",
                    "character.reputation_changed",
                }
                for record in records
            )
        )

    def test_walk_requires_character_context_and_does_not_write_on_rejection(self):
        tmp, kernel, character, service = new_runtime()
        self.addCleanup(tmp.cleanup)
        wrong = JournalContext(
            "2026-08-22T16:00:00+02:00",
            "street-test-session",
            "player-local",
            "event",
            "event-a4",
            "street-wrong-context",
            "street-test",
            "0.8.7-b1",
            "player-local",
        )

        with self.assertRaisesRegex(ValueError, "Character-Kontext"):
            service.walk(
                character,
                walk_instance_id="street-wrong-context",
                world_seed="stable-world",
                journal_context=wrong,
            )
        self.assertEqual(kernel.read_records(), ())

    def test_applied_effects_are_clamped_and_match_persisted_character(self):
        character = CharacterState("player-local", "Clamp Tester")
        character.energy = 99
        character.stress = 1
        character.reputation = 4
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        kernel.initialize_state({"character": character.to_dict()})
        service = StreetEncounterService(kernel, single_encounter_manifest())

        result = service.walk(
            character,
            walk_instance_id="street-clamp-001",
            world_seed="stable-world",
            journal_context=context("street-clamp-001"),
        )

        self.assertEqual(result.effects, {"energy_delta": 1, "stress_delta": -1, "reputation_delta": 2})
        persisted = CharacterState.from_dict(kernel.load_state()["character"])
        self.assertEqual((persisted.energy, persisted.stress, persisted.reputation), (100, 0, 6))


if __name__ == "__main__":
    unittest.main()
