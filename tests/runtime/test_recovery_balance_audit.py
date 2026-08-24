from __future__ import annotations

import unittest

from bunkerfrequenz.application.recovery_action_service import (
    RECOVERY_ACTIONS,
    recovery_action_availability,
)
from bunkerfrequenz.domain.character import CharacterState


ACTIONS = {action["recovery_id"]: action for action in RECOVERY_ACTIONS}
SMALL_ID = "recovery.koffein_kalte_luft"
BURST_ID = "recovery.mate_zucker_vollgas"


def character_at(energy: int, stress: int) -> CharacterState:
    character = CharacterState(character_id="audit.local", display_name="Audit")
    character.energy = energy
    character.stress = stress
    return character


def can_run(action: dict, energy: int, stress: int) -> bool:
    return recovery_action_availability(action, character_at(energy, stress))["can_run"] is True


def apply(action: dict, energy: int, stress: int) -> tuple[int, int]:
    if not can_run(action, energy, stress):
        raise AssertionError("Audit attempted blocked recovery action")
    return energy + action["energy_delta"], stress + action["stress_delta"]


class RecoveryBalanceAuditTests(unittest.TestCase):
    def test_full_energy_stress_matrix_matches_headroom_contract_without_clamping(self):
        self.assertEqual(set(ACTIONS), {SMALL_ID, BURST_ID})

        for action in RECOVERY_ACTIONS:
            for energy in range(101):
                for stress in range(101):
                    expected = (
                        energy <= action["max_energy_before"]
                        and stress <= action["max_stress_before"]
                    )
                    self.assertEqual(
                        can_run(action, energy, stress),
                        expected,
                        (action["recovery_id"], energy, stress),
                    )
                    if not expected:
                        continue

                    after_energy, after_stress = apply(action, energy, stress)
                    self.assertEqual(after_energy - energy, action["energy_delta"])
                    self.assertEqual(after_stress - stress, action["stress_delta"])
                    self.assertLessEqual(after_energy, 100)
                    self.assertLessEqual(after_stress, 100)

    def test_neither_recovery_option_globally_pareto_dominates_the_other(self):
        small = ACTIONS[SMALL_ID]
        burst = ACTIONS[BURST_ID]
        both_available = 0
        small_only = 0

        for energy in range(101):
            for stress in range(101):
                small_available = can_run(small, energy, stress)
                burst_available = can_run(burst, energy, stress)
                if small_available and not burst_available:
                    small_only += 1
                if not (small_available and burst_available):
                    continue

                both_available += 1
                small_after = apply(small, energy, stress)
                burst_after = apply(burst, energy, stress)

                # More burst energy is always paid for with more stress.
                self.assertGreater(burst_after[0], small_after[0])
                self.assertGreater(burst_after[1], small_after[1])

                small_dominates = (
                    small_after[0] >= burst_after[0]
                    and small_after[1] <= burst_after[1]
                    and small_after != burst_after
                )
                burst_dominates = (
                    burst_after[0] >= small_after[0]
                    and burst_after[1] <= small_after[1]
                    and burst_after != small_after
                )
                self.assertFalse(small_dominates)
                self.assertFalse(burst_dominates)

        self.assertGreater(both_available, 0)
        self.assertGreater(small_only, 0)

    def test_all_recovery_sequences_have_positive_cost_and_cannot_create_free_efficiency(self):
        max_single_efficiency = max(
            action["energy_delta"] / action["stress_delta"]
            for action in RECOVERY_ACTIONS
        )
        explored_transitions = 0
        multi_step_paths = 0

        for start_energy in range(101):
            for start_stress in range(101):
                stack = [(start_energy, start_stress, 0, 0, 0)]
                seen = set()

                while stack:
                    energy, stress, gained_energy, paid_stress, depth = stack.pop()
                    state_key = (energy, stress, gained_energy, paid_stress)
                    if state_key in seen:
                        continue
                    seen.add(state_key)

                    available = [
                        action for action in RECOVERY_ACTIONS
                        if can_run(action, energy, stress)
                    ]
                    if not available:
                        if depth >= 2:
                            multi_step_paths += 1
                        if gained_energy > 0:
                            self.assertGreater(paid_stress, 0)
                            self.assertLessEqual(
                                gained_energy / paid_stress,
                                max_single_efficiency + 1e-12,
                            )
                        continue

                    for action in available:
                        next_energy, next_stress = apply(action, energy, stress)
                        explored_transitions += 1
                        next_gained = gained_energy + action["energy_delta"]
                        next_paid = paid_stress + action["stress_delta"]

                        self.assertGreater(next_energy, energy)
                        self.assertGreater(next_stress, stress)
                        self.assertEqual(next_energy - start_energy, next_gained)
                        self.assertEqual(next_stress - start_stress, next_paid)
                        self.assertLessEqual(next_energy, 100)
                        self.assertLessEqual(next_stress, 100)

                        stack.append((
                            next_energy,
                            next_stress,
                            next_gained,
                            next_paid,
                            depth + 1,
                        ))

        self.assertGreater(explored_transitions, 0)
        self.assertGreater(multi_step_paths, 0)


if __name__ == "__main__":
    unittest.main()
