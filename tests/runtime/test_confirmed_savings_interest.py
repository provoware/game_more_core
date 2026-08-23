import json
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import replay_game_event
from bunkerfrequenz.application.personal_finance_service import (
    ConfirmedFinancePeriod,
    PersonalFinanceService,
    replay_personal_finance_event,
)
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
FINANCE = json.loads((ROOT / "manifests" / "PERSONAL_FINANCE_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str, character_id: str = "char.local") -> JournalContext:
    return JournalContext(
        "2026-08-23T21:50:00+02:00",
        "session-savings-interest",
        "player-local",
        "character",
        character_id,
        command_id,
        "confirmed-savings-interest-test",
        "0.8.8-d2",
        character_id,
    )


class ConfirmedSavingsInterestTests(unittest.TestCase):
    def make_service(self, *, bank_cents: int = 10_000):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        kernel = PersistenceKernel(tmp.name, ALLOWED)
        character = CharacterState(character_id="char.local", display_name="Local")
        finance = PlayerFinanceState(cash_cents=2_000, bank_cents=bank_cents)
        initial = {"character": character.to_dict(), "finance": finance.to_dict()}
        kernel.initialize_state(initial)
        return kernel, initial, PersonalFinanceService(kernel, FINANCE)

    def test_confirmed_periods_compound_on_current_bank_balance(self):
        kernel, _, service = self.make_service()

        first = service.apply_confirmed_interest(
            ConfirmedFinancePeriod("savings-001", 1, "char.local"),
            context=context("interest-1"),
        )
        second = service.apply_confirmed_interest(
            ConfirmedFinancePeriod("savings-002", 2, "char.local"),
            context=context("interest-2"),
        )

        self.assertEqual(first.basis_points, 100)
        self.assertEqual(first.interest_cents, 100)
        self.assertEqual(first.finance.bank_cents, 10_100)
        self.assertEqual(second.interest_cents, 101)
        self.assertEqual(second.finance.bank_cents, 10_201)
        self.assertEqual(second.finance.confirmed_finance_tick, 2)
        self.assertEqual(
            [entry["kind"] for entry in second.finance.ledger],
            ["savings_interest", "savings_interest"],
        )
        self.assertEqual(
            [record["event_type"] for record in kernel.read_records()],
            ["finance.savings_interest_posted", "finance.savings_interest_posted"],
        )

    def test_retry_same_tick_is_write_free_and_tick_cannot_change_meaning(self):
        kernel, _, service = self.make_service()
        trigger = ConfirmedFinancePeriod("savings-001", 1, "char.local")

        first = service.apply_confirmed_interest(trigger, context=context("interest-first"))
        records = kernel.read_records()
        retry = service.apply_confirmed_interest(trigger, context=context("interest-retry"))

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(retry.interest_cents, 100)
        self.assertEqual(kernel.read_records(), records)
        with self.assertRaises(PersistenceError):
            service.apply_confirmed_interest(
                ConfirmedFinancePeriod("different-period", 1, "char.local"),
                context=context("interest-changed-meaning"),
            )

    def test_periods_must_be_sequential_and_character_bound(self):
        kernel, _, service = self.make_service()
        with self.assertRaisesRegex(ValueError, "lückenlos 1"):
            service.apply_confirmed_interest(
                ConfirmedFinancePeriod("savings-002", 2, "char.local"),
                context=context("interest-skip"),
            )
        with self.assertRaisesRegex(ValueError, "passt nicht"):
            service.apply_confirmed_interest(
                ConfirmedFinancePeriod("savings-001", 1, "char.other"),
                context=context("interest-wrong-character"),
            )
        self.assertEqual(kernel.read_records(), ())

    def test_zero_interest_period_is_consumed_without_retroactive_interest(self):
        kernel, _, service = self.make_service(bank_cents=0)
        result = service.apply_confirmed_interest(
            ConfirmedFinancePeriod("empty-period", 1, "char.local"),
            context=context("interest-empty"),
        )

        self.assertEqual(result.interest_cents, 0)
        self.assertEqual(result.finance.bank_cents, 0)
        self.assertEqual(result.finance.confirmed_finance_tick, 1)
        self.assertEqual(result.finance.ledger[-1]["amount_cents"], 0)
        records = kernel.read_records()

        retry = service.apply_confirmed_interest(
            ConfirmedFinancePeriod("empty-period", 1, "char.local"),
            context=context("interest-empty-retry"),
        )
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(kernel.read_records(), records)

    def test_recovery_reconstructs_compounded_finance_state(self):
        kernel, initial, service = self.make_service()
        service.apply_confirmed_interest(
            ConfirmedFinancePeriod("savings-001", 1, "char.local"),
            context=context("interest-recover-1"),
        )
        service.apply_confirmed_interest(
            ConfirmedFinancePeriod("savings-002", 2, "char.local"),
            context=context("interest-recover-2"),
        )

        recovered = dict(initial)
        for record in kernel.read_records():
            recovered = replay_game_event(recovered, record)

        self.assertEqual(recovered["finance"], kernel.load_state()["finance"])

    def test_replay_rejects_tampered_or_skipped_confirmed_finance_tick(self):
        kernel, initial, service = self.make_service()
        service.apply_confirmed_interest(
            ConfirmedFinancePeriod("savings-001", 1, "char.local"),
            context=context("interest-replay-tamper"),
        )
        record = deepcopy(kernel.read_records()[0])
        record["payload"]["finance"]["confirmed_finance_tick"] = 2

        with self.assertRaisesRegex(ValueError, "Finance-Tick"):
            replay_personal_finance_event(dict(initial), record)

    def test_contract_explicitly_denies_system_time_and_browser_authority(self):
        policy = FINANCE["savings_interest"]
        self.assertTrue(policy["confirmed_period_required"])
        self.assertTrue(policy["require_sequential_finance_tick"])
        self.assertFalse(policy["system_time_is_sole_authority"])
        self.assertFalse(policy["browser_can_confirm_period"])
        self.assertFalse(policy["browser_can_supply_interest_amount"])


if __name__ == "__main__":
    unittest.main()
