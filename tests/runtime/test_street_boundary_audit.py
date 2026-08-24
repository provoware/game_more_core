import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.street_encounter_service import StreetEncounterService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
STREET = json.loads((ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


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


def forced_manifest(*, encounter_id: str, polarity: str, energy_delta: int, stress_delta: int) -> dict:
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
            "positive_weight": 100 if polarity == "positive" else 0,
            "negative_weight": 100 if polarity == "negative" else 0,
            "positive_share_of_actual_encounters": 1.0 if polarity == "positive" else 0.0,
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
            "weights": {encounter_id: 100},
        }],
        "encounters": [{
            "encounter_id": encounter_id,
            "polarity": polarity,
            "weight": 100,
            "title_key": f"{encounter_id}.title",
            "body_key": f"{encounter_id}.body",
            "effects": {
                "energy_delta": energy_delta,
                "stress_delta": stress_delta,
                "reputation_delta": 0,
            },
        }],
    }


class StreetBoundaryAuditTests(unittest.TestCase):
    def _run_forced(self, *, energy: int, stress: int, manifest: dict, command_id: str):
        character = CharacterState("player-local", "Boundary Tester")
        character.energy = energy
        character.stress = stress
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        kernel.initialize_state({"character": character.to_dict()})
        result = StreetEncounterService(kernel, manifest).walk(
            character,
            walk_instance_id=command_id,
            world_seed="street-boundary-fixed-seed",
            journal_context=context(command_id),
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
        result, persisted = self._run_forced(
            energy=1,
            stress=99,
            manifest=forced_manifest(
                encounter_id="street.audit_negative",
                polarity="negative",
                energy_delta=-10,
                stress_delta=10,
            ),
            command_id="street-boundary-negative",
        )

        self.assertEqual(result.effects, {"energy_delta": -1, "stress_delta": 1, "reputation_delta": 0})
        self.assertEqual((persisted.energy, persisted.stress), (0, 100))

    def test_real_catalog_resource_effects_fit_the_same_bounded_contract(self):
        self.assertGreater(len(STREET["encounters"]), 0)
        for encounter in STREET["encounters"]:
            effects = encounter["effects"]
            with self.subTest(encounter_id=encounter["encounter_id"]):
                self.assertLessEqual(abs(effects["energy_delta"]), 10)
                self.assertLessEqual(abs(effects["stress_delta"]), 10)


if __name__ == "__main__":
    unittest.main()
