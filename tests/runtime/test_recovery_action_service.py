from pathlib import Path
import json
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import replay_game_event
from bunkerfrequenz.application.recovery_action_service import RECOVERY_ACTIONS, RecoveryActionService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-24T01:00:00+02:00",
        "session-recovery",
        "player-local",
        "character",
        "char.local",
        command_id,
        "recovery-test",
        "0.8.8-econ-recovery-actions",
        "char.local",
    )


def runtime_at(energy: int, stress: int):
    tmp = tempfile.TemporaryDirectory()
    kernel = PersistenceKernel(tmp.name, ALLOWED)
    character = CharacterState(character_id="char.local", display_name="Local")
    character.energy = energy
    character.stress = stress
    kernel.initialize_state({"character": character.to_dict()})
    return tmp, kernel, RecoveryActionService(kernel)


class RecoveryActionServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        character = CharacterState(character_id="char.local", display_name="Local")
        character.energy = 40
        character.stress = 30
        self.initial = character.to_dict()
        self.kernel.initialize_state({"character": self.initial})
        self.service = RecoveryActionService(self.kernel)

    def test_recovery_catalog_has_two_non_dominating_tradeoffs(self):
        self.assertEqual([a["recovery_id"] for a in RECOVERY_ACTIONS], [
            "recovery.koffein_kalte_luft",
            "recovery.mate_zucker_vollgas",
        ])
        small, burst = RECOVERY_ACTIONS
        self.assertEqual((small["energy_delta"], small["stress_delta"]), (20, 12))
        self.assertEqual((burst["energy_delta"], burst["stress_delta"]), (30, 20))
        self.assertGreater(burst["energy_delta"], small["energy_delta"])
        self.assertGreater(burst["stress_delta"], small["stress_delta"])
        self.assertGreater(
            small["energy_delta"] / small["stress_delta"],
            burst["energy_delta"] / burst["stress_delta"],
        )
        for action in RECOVERY_ACTIONS:
            self.assertLessEqual(action["max_energy_before"] + action["energy_delta"], 100)
            self.assertLessEqual(action["max_stress_before"] + action["stress_delta"], 100)

    def test_recovery_trades_confirmed_stress_for_energy_without_xp_or_time(self):
        result = self.service.run("recovery.koffein_kalte_luft", context=context("recover-one"))

        self.assertEqual(result.character.energy, 60)
        self.assertEqual(result.character.stress, 42)
        records = self.kernel.read_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["event_type"], "character.resources_changed")
        self.assertEqual(records[0]["payload"]["source_recovery_id"], "recovery.koffein_kalte_luft")
        self.assertNotIn("skill", records[0]["payload"])
        self.assertNotIn("trait", records[0]["payload"])

    def test_burst_variant_reaches_full_energy_for_higher_stress_price(self):
        tmp_a, _, small_service = runtime_at(70, 40)
        tmp_b, _, burst_service = runtime_at(70, 40)
        self.addCleanup(tmp_a.cleanup)
        self.addCleanup(tmp_b.cleanup)
        small = small_service.run("recovery.koffein_kalte_luft", context=context("recover-small-choice"))
        burst = burst_service.run("recovery.mate_zucker_vollgas", context=context("recover-burst-choice"))
        self.assertEqual((small.character.energy, small.character.stress), (90, 52))
        self.assertEqual((burst.character.energy, burst.character.stress), (100, 60))

    def test_burst_variant_has_stricter_stress_headroom(self):
        tmp, kernel, service = runtime_at(60, 81)
        self.addCleanup(tmp.cleanup)
        with self.assertRaisesRegex(ValueError, "stress_above_recovery_threshold"):
            service.run("recovery.mate_zucker_vollgas", context=context("recover-burst-blocked"))
        allowed = service.run("recovery.koffein_kalte_luft", context=context("recover-small-allowed"))
        self.assertEqual((allowed.character.energy, allowed.character.stress), (80, 93))
        self.assertEqual(len(kernel.read_records()), 1)

    def test_recovery_requires_full_cost_headroom_and_cannot_be_spammed_at_high_stress(self):
        high_stress = CharacterState(character_id="char.local", display_name="Local")
        high_stress.energy = 20
        high_stress.stress = 89
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        kernel.initialize_state({"character": high_stress.to_dict()})
        service = RecoveryActionService(kernel)

        with self.assertRaisesRegex(ValueError, "stress_above_recovery_threshold"):
            service.run("recovery.koffein_kalte_luft", context=context("recover-stress"))
        self.assertEqual(kernel.read_records(), ())

    def test_recovery_is_not_available_when_energy_is_already_above_threshold(self):
        character = CharacterState(character_id="char.local", display_name="Local")
        character.energy = 81
        character.stress = 10
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        kernel.initialize_state({"character": character.to_dict()})
        service = RecoveryActionService(kernel)

        with self.assertRaisesRegex(ValueError, "energy_above_recovery_threshold"):
            service.run("recovery.koffein_kalte_luft", context=context("recover-energy"))
        self.assertEqual(kernel.read_records(), ())

    def test_retry_is_write_free_and_semantic_reuse_conflicts(self):
        first = self.service.run("recovery.koffein_kalte_luft", context=context("recover-retry"))
        records = self.kernel.read_records()
        retry = self.service.run("recovery.koffein_kalte_luft", context=context("recover-retry"))

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.character.energy, 60)
        self.assertEqual(self.kernel.read_records(), records)

        with self.assertRaisesRegex(PersistenceError, "andere Regenerationsaktion"):
            self.service.run("recovery.mate_zucker_vollgas", context=context("recover-retry"))
        self.assertEqual(self.kernel.read_records(), records)

    def test_recovery_replays_exact_character_state(self):
        result = self.service.run("recovery.mate_zucker_vollgas", context=context("recover-replay"))
        state = {"character": self.initial}
        for record in self.kernel.read_records():
            state = replay_game_event(state, record)
        self.assertEqual(state["character"], result.character.to_dict())

    def test_wrong_context_and_unknown_action_fail_before_write(self):
        with self.assertRaisesRegex(ValueError, "Unbekannte Regenerationsaktion"):
            self.service.run("recovery.fake", context=context("recover-fake"))
        wrong = JournalContext(
            "2026-08-24T01:00:00+02:00",
            "session-recovery",
            "player-local",
            "event",
            "event.local",
            "recover-wrong",
            "recovery-test",
            "0.8.8-econ-recovery-actions",
            "char.local",
        )
        with self.assertRaisesRegex(ValueError, "Character-Kontext"):
            self.service.run("recovery.koffein_kalte_luft", context=wrong)
        self.assertEqual(self.kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
