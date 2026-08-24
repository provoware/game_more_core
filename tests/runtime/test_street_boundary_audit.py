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
WORLD_SEED = "street-boundary-fixed-seed"


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-24T17:00:00+02:00",
        "street-boundary-audit",
        "player-local",
        "character",
        "player-local",
        command_id,
        "street-boundary-audit",
        "0.8.8",
        "player-local",
    )


def forced_manifest(
    *,
    encounter_id: str,
    polarity: str,
    energy_delta: int,
    stress_delta: int,
    reputation_delta: int = 0,
) -> dict:
    target = {
        "encounter_id": encounter_id,
        "polarity": polarity,
        "weight": 100 if polarity == "positive" else 49,
        "title_key": f"{encounter_id}.title",
        "body_key": f"{encounter_id}.body",
        "effects": {
            "energy_delta": energy_delta,
            "stress_delta": stress_delta,
            "reputation_delta": reputation_delta,
        },
    }
    encounters = [target]
    weights = {encounter_id: target["weight"]}
    positive_weight = 100
    negative_weight = 0
    if polarity == "negative":
        filler_id = "street.audit_positive_filler"
        encounters.append({
            "encounter_id": filler_id,
            "polarity": "positive",
            "weight": 51,
            "title_key": f"{filler_id}.title",
            "body_key": f"{filler_id}.body",
            "effects": {"energy_delta": 1, "stress_delta": -1, "reputation_delta": 0},
        })
        weights[filler_id] = 51
        positive_weight = 51
        negative_weight = 49

    return {
        "schema_version": 2,
        "version": "street-boundary-audit-v1",
        "selection": {
            "method": "sha256_stable_weighted",
            "weight_total": 100,
            "system_time_as_seed": False,
        },
        "policy": {
            "neutral_weight": 0,
            "positive_weight": positive_weight,
            "negative_weight": negative_weight,
            "positive_share_of_actual_encounters": positive_weight / 100,
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
            "weights": weights,
        }],
        "encounters": encounters,
    }


def sequence_for_bucket_below(command_id: str, upper_bound: int) -> int:
    for server_sequence in range(1000):
        if _stable_bucket(WORLD_SEED, command_id, server_sequence, 100) < upper_bound:
            return server_sequence
    raise AssertionError("Kein deterministischer Street-Bucket im Testbereich gefunden")


def sequence_for_real_encounter(command_id: str, encounter_id: str) -> int:
    balanced = next(
        approach for approach in STREET["approaches"] if approach["approach_id"] == "balanced"
    )
    lower_bound = 0
    upper_bound = 0
    for encounter in STREET["encounters"]:
        weight = balanced["weights"][encounter["encounter_id"]]
        upper_bound = lower_bound + weight
        if encounter["encounter_id"] == encounter_id:
            break
        lower_bound = upper_bound
    else:
        raise AssertionError(f"Unbekannte reale Street-Begegnung: {encounter_id}")

    for server_sequence in range(10000):
        bucket = _stable_bucket(WORLD_SEED, command_id, server_sequence, STREET["selection"]["weight_total"])
        if lower_bound <= bucket < upper_bound:
            return server_sequence
    raise AssertionError(f"Kein deterministischer Bucket für {encounter_id} gefunden")


class StreetBoundaryAuditTests(unittest.TestCase):
    def _run_forced(
        self,
        *,
        energy: int,
        stress: int,
        manifest: dict,
        command_id: str,
        reputation: int = 0,
        server_sequence: int | None = None,
    ):
        character = CharacterState("player-local", "Boundary Tester")
        character.energy = energy
        character.stress = stress
        character.reputation = reputation
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        kernel.initialize_state({"character": character.to_dict()})
        result = StreetEncounterService(kernel, manifest).walk(
            character,
            walk_instance_id=command_id,
            world_seed=WORLD_SEED,
            journal_context=context(command_id),
            server_sequence=server_sequence,
        )
        persisted = CharacterState.from_dict(kernel.load_state()["character"])
        return result, persisted

    def test_positive_effects_saturate_at_energy_max_and_stress_min(self):
        result, persisted = self._run_forced(
            energy=99,
            stress=1,
            manifest=forced_manifest(
                encounter_id="street.audit_positive",
                polarity="positive",
                energy_delta=10,
                stress_delta=-10,
            ),
            command_id="street-boundary-positive",
        )

        self.assertEqual(result.effects, {"energy_delta": 1, "stress_delta": -1, "reputation_delta": 0})
        self.assertEqual((persisted.energy, persisted.stress), (100, 0))

    def test_negative_effects_saturate_at_energy_min_and_stress_max(self):
        command_id = "street-boundary-negative"
        result, persisted = self._run_forced(
            energy=1,
            stress=99,
            manifest=forced_manifest(
                encounter_id="street.audit_negative",
                polarity="negative",
                energy_delta=-10,
                stress_delta=10,
            ),
            command_id=command_id,
            server_sequence=sequence_for_bucket_below(command_id, 49),
        )

        self.assertEqual(result.encounter_id, "street.audit_negative")
        self.assertEqual(result.effects, {"energy_delta": -1, "stress_delta": 1, "reputation_delta": 0})
        self.assertEqual((persisted.energy, persisted.stress), (0, 100))

    def test_negative_reputation_effect_stops_at_canonical_zero_floor(self):
        command_id = "street-boundary-reputation-floor"
        result, persisted = self._run_forced(
            energy=50,
            stress=50,
            reputation=2,
            manifest=forced_manifest(
                encounter_id="street.audit_reputation_floor",
                polarity="negative",
                energy_delta=0,
                stress_delta=1,
                reputation_delta=-10,
            ),
            command_id=command_id,
            server_sequence=sequence_for_bucket_below(command_id, 49),
        )

        self.assertEqual(result.encounter_id, "street.audit_reputation_floor")
        self.assertEqual(result.effects["reputation_delta"], -2)
        self.assertEqual(persisted.reputation, 0)

    def test_replay_at_all_resource_boundaries_is_idempotent(self):
        cases = (
            {
                "name": "energy_max",
                "polarity": "positive",
                "energy": 99,
                "stress": 50,
                "reputation": 0,
                "energy_delta": 10,
                "stress_delta": 0,
                "reputation_delta": 0,
                "expected": {"energy_delta": 1, "stress_delta": 0, "reputation_delta": 0},
            },
            {
                "name": "energy_min",
                "polarity": "negative",
                "energy": 1,
                "stress": 50,
                "reputation": 0,
                "energy_delta": -10,
                "stress_delta": 0,
                "reputation_delta": 0,
                "expected": {"energy_delta": -1, "stress_delta": 0, "reputation_delta": 0},
            },
            {
                "name": "stress_min",
                "polarity": "positive",
                "energy": 50,
                "stress": 1,
                "reputation": 0,
                "energy_delta": 0,
                "stress_delta": -10,
                "reputation_delta": 0,
                "expected": {"energy_delta": 0, "stress_delta": -1, "reputation_delta": 0},
            },
            {
                "name": "stress_max",
                "polarity": "negative",
                "energy": 50,
                "stress": 99,
                "reputation": 0,
                "energy_delta": 0,
                "stress_delta": 10,
                "reputation_delta": 0,
                "expected": {"energy_delta": 0, "stress_delta": 1, "reputation_delta": 0},
            },
            {
                "name": "reputation_floor",
                "polarity": "negative",
                "energy": 50,
                "stress": 50,
                "reputation": 2,
                "energy_delta": 0,
                "stress_delta": 0,
                "reputation_delta": -10,
                "expected": {"energy_delta": 0, "stress_delta": 0, "reputation_delta": -2},
            },
        )

        for case in cases:
            with self.subTest(boundary=case["name"]):
                command_id = f"street-boundary-replay-{case['name']}"
                encounter_id = f"street.audit_replay_{case['name']}"
                manifest = forced_manifest(
                    encounter_id=encounter_id,
                    polarity=case["polarity"],
                    energy_delta=case["energy_delta"],
                    stress_delta=case["stress_delta"],
                    reputation_delta=case["reputation_delta"],
                )
                character = CharacterState("player-local", "Boundary Replay Tester")
                character.energy = case["energy"]
                character.stress = case["stress"]
                character.reputation = case["reputation"]
                tmp = tempfile.TemporaryDirectory()
                self.addCleanup(tmp.cleanup)
                kernel = PersistenceKernel(tmp.name, ALLOWED)
                kernel.initialize_state({"character": character.to_dict()})
                service = StreetEncounterService(kernel, manifest)
                server_sequence = None
                if case["polarity"] == "negative":
                    server_sequence = sequence_for_bucket_below(command_id, 49)

                first = service.walk(
                    character,
                    walk_instance_id=command_id,
                    world_seed=WORLD_SEED,
                    journal_context=context(command_id),
                    server_sequence=server_sequence,
                )
                state_after_first = kernel.load_state()
                records_after_first = list(kernel.read_records())

                replay = service.walk(
                    character,
                    walk_instance_id=command_id,
                    world_seed=WORLD_SEED,
                    journal_context=context(command_id),
                    server_sequence=server_sequence,
                )

                self.assertFalse(first.idempotent_replay)
                self.assertEqual(first.encounter_id, encounter_id)
                self.assertEqual(first.effects, case["expected"])
                self.assertTrue(replay.idempotent_replay)
                self.assertEqual(replay.effects, case["expected"])
                self.assertEqual(replay.committed_event_ids, ())
                self.assertEqual(kernel.load_state(), state_after_first)
                self.assertEqual(list(kernel.read_records()), records_after_first)

    def test_real_catalog_effect_encounters_clamp_and_replay_idempotently(self):
        effect_encounters = [
            encounter
            for encounter in STREET["encounters"]
            if any(encounter["effects"].values())
        ]
        self.assertGreater(len(effect_encounters), 0)

        for encounter in effect_encounters:
            with self.subTest(encounter_id=encounter["encounter_id"]):
                requested = encounter["effects"]
                energy = 99 if requested["energy_delta"] > 0 else 1 if requested["energy_delta"] < 0 else 50
                stress = 99 if requested["stress_delta"] > 0 else 1 if requested["stress_delta"] < 0 else 50
                reputation = 0
                command_id = f"street-real-catalog-replay-{encounter['encounter_id'].split('.')[-1]}"
                server_sequence = sequence_for_real_encounter(command_id, encounter["encounter_id"])

                character = CharacterState("player-local", "Real Catalog Boundary Tester")
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
                    server_sequence=server_sequence,
                )
                expected = {
                    "energy_delta": min(100, max(0, energy + requested["energy_delta"])) - energy,
                    "stress_delta": min(100, max(0, stress + requested["stress_delta"])) - stress,
                    "reputation_delta": max(0, reputation + requested["reputation_delta"]) - reputation,
                }
                state_after_first = kernel.load_state()
                records_after_first = list(kernel.read_records())

                replay = service.walk(
                    character,
                    walk_instance_id=command_id,
                    world_seed=WORLD_SEED,
                    journal_context=context(command_id),
                    server_sequence=server_sequence,
                )

                self.assertEqual(first.encounter_id, encounter["encounter_id"])
                self.assertEqual(first.effects, expected)
                self.assertFalse(first.idempotent_replay)
                self.assertTrue(replay.idempotent_replay)
                self.assertEqual(replay.encounter_id, encounter["encounter_id"])
                self.assertEqual(replay.effects, expected)
                self.assertEqual(replay.committed_event_ids, ())
                self.assertEqual(kernel.load_state(), state_after_first)
                self.assertEqual(list(kernel.read_records()), records_after_first)

    def test_real_catalog_resource_effects_fit_the_same_bounded_contract(self):
        self.assertGreater(len(STREET["encounters"]), 0)
        for encounter in STREET["encounters"]:
            effects = encounter["effects"]
            with self.subTest(encounter_id=encounter["encounter_id"]):
                self.assertLessEqual(abs(effects["energy_delta"]), 10)
                self.assertLessEqual(abs(effects["stress_delta"]), 10)


if __name__ == "__main__":
    unittest.main()
