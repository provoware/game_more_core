import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.street_encounter_service import StreetEncounterService, _stable_bucket
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])
WORLD_SEED = "street-approach-catalog-matrix-fixed-seed"


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-24T22:00:00+02:00",
        "street-approach-catalog-matrix-audit",
        "player-local",
        "character",
        "player-local",
        command_id,
        "street-approach-catalog-matrix-audit",
        "0.8.8",
        "player-local",
    )


def sequence_for_approach_encounter(command_id: str, approach: dict, encounter_id: str) -> int:
    lower_bound = 0
    upper_bound = 0
    target_weight = approach["weights"][encounter_id]
    if target_weight <= 0:
        raise AssertionError(f"{encounter_id} ist unter {approach['approach_id']} nicht auswählbar")

    for encounter in STREET["encounters"]:
        weight = approach["weights"][encounter["encounter_id"]]
        upper_bound = lower_bound + weight
        if encounter["encounter_id"] == encounter_id:
            break
        lower_bound = upper_bound
    else:
        raise AssertionError(f"Unbekannte reale Street-Begegnung: {encounter_id}")

    for server_sequence in range(10000):
        bucket = _stable_bucket(
            WORLD_SEED,
            command_id,
            server_sequence,
            STREET["selection"]["weight_total"],
        )
        if lower_bound <= bucket < upper_bound:
            return server_sequence
    raise AssertionError(
        f"Kein deterministischer Bucket für {approach['approach_id']} / {encounter_id} gefunden"
    )


def bounded_expected(start: int, delta: int) -> int:
    return min(100, max(0, start + delta)) - start


class StreetApproachCatalogMatrixAuditTests(unittest.TestCase):
    def test_all_four_canonical_approaches_are_covered(self):
        self.assertEqual(
            [approach["approach_id"] for approach in STREET["approaches"]],
            ["balanced", "recovery", "network", "scout"],
        )

    def test_real_selectable_catalog_entries_clamp_and_replay_for_every_approach(self):
        matrix_cases = 0
        zero_weight_cases = 0

        for approach in STREET["approaches"]:
            approach_id = approach["approach_id"]
            for encounter in STREET["encounters"]:
                encounter_id = encounter["encounter_id"]
                weight = approach["weights"][encounter_id]
                with self.subTest(approach=approach_id, encounter=encounter_id, weight=weight):
                    if weight == 0:
                        zero_weight_cases += 1
                        continue

                    matrix_cases += 1
                    requested = encounter["effects"]
                    energy = (
                        99 if requested["energy_delta"] > 0
                        else 1 if requested["energy_delta"] < 0
                        else 50
                    )
                    stress = (
                        99 if requested["stress_delta"] > 0
                        else 1 if requested["stress_delta"] < 0
                        else 50
                    )
                    reputation = 1 if requested["reputation_delta"] < 0 else 0
                    command_id = (
                        "street-approach-matrix-"
                        f"{approach_id}-{encounter_id.split('.')[-1]}"
                    )
                    server_sequence = sequence_for_approach_encounter(
                        command_id,
                        approach,
                        encounter_id,
                    )

                    character = CharacterState("player-local", "Approach Matrix Tester")
                    character.energy = energy
                    character.stress = stress
                    character.reputation = reputation
                    tmp = tempfile.TemporaryDirectory()
                    self.addCleanup(tmp.cleanup)
                    kernel = PersistenceKernel(tmp.name, ALLOWED)
                    kernel.initialize_state({"character": character.to_dict()})
                    service = StreetEncounterService(kernel, STREET)

                    first = service.walk(
                        character,
                        walk_instance_id=command_id,
                        world_seed=WORLD_SEED,
                        journal_context=context(command_id),
                        approach_id=approach_id,
                        server_sequence=server_sequence,
                    )
                    expected = {
                        "energy_delta": bounded_expected(energy, requested["energy_delta"]),
                        "stress_delta": bounded_expected(stress, requested["stress_delta"]),
                        "reputation_delta": max(
                            0,
                            reputation + requested["reputation_delta"],
                        ) - reputation,
                    }
                    state_after_first = kernel.load_state()
                    records_after_first = list(kernel.read_records())

                    replay = service.walk(
                        character,
                        walk_instance_id=command_id,
                        world_seed=WORLD_SEED,
                        journal_context=context(command_id),
                        approach_id=approach_id,
                        server_sequence=server_sequence,
                    )

                    self.assertEqual(first.approach_id, approach_id)
                    self.assertEqual(first.encounter_id, encounter_id)
                    self.assertEqual(first.effects, expected)
                    self.assertFalse(first.idempotent_replay)
                    self.assertTrue(replay.idempotent_replay)
                    self.assertEqual(replay.approach_id, approach_id)
                    self.assertEqual(replay.encounter_id, encounter_id)
                    self.assertEqual(replay.effects, expected)
                    self.assertEqual(replay.committed_event_ids, ())
                    self.assertEqual(kernel.load_state(), state_after_first)
                    self.assertEqual(list(kernel.read_records()), records_after_first)

        expected_selectable = sum(
            1
            for approach in STREET["approaches"]
            for weight in approach["weights"].values()
            if weight > 0
        )
        expected_zero_weight = sum(
            1
            for approach in STREET["approaches"]
            for weight in approach["weights"].values()
            if weight == 0
        )
        self.assertEqual(matrix_cases, expected_selectable)
        self.assertEqual(zero_weight_cases, expected_zero_weight)
        self.assertGreater(matrix_cases, 0)

    def test_zero_weight_entries_are_never_accidentally_selectable(self):
        zero_weight_pairs = [
            (approach, encounter_id)
            for approach in STREET["approaches"]
            for encounter_id, weight in approach["weights"].items()
            if weight == 0
        ]
        self.assertGreater(len(zero_weight_pairs), 0)

        for approach, encounter_id in zero_weight_pairs:
            approach_id = approach["approach_id"]
            with self.subTest(approach=approach_id, encounter=encounter_id):
                selected_ids = set()
                service_tmp = tempfile.TemporaryDirectory()
                self.addCleanup(service_tmp.cleanup)
                kernel = PersistenceKernel(service_tmp.name, ALLOWED)
                service = StreetEncounterService(kernel, STREET)
                for bucket in range(STREET["selection"]["weight_total"]):
                    cursor = 0
                    for encounter in service.encounters:
                        cursor += approach["weights"][encounter["encounter_id"]]
                        if bucket < cursor:
                            selected_ids.add(encounter["encounter_id"])
                            break
                self.assertNotIn(encounter_id, selected_ids)


if __name__ == "__main__":
    unittest.main()
