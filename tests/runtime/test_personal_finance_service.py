import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.game_recovery import replay_game_event
from bunkerfrequenz.application.personal_finance_service import PersonalFinanceService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T21:30:00+02:00",
        "session-bank-transfer",
        "player-local",
        "character",
        "char.local",
        command_id,
        "bank-transfer-test",
        "0.8.8-d1",
        "char.local",
    )


class PersonalFinanceServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        character = CharacterState(character_id="char.local", display_name="Local")
        finance = PlayerFinanceState(cash_cents=12_000, bank_cents=3_000)
        self.initial = {"character": character.to_dict(), "finance": finance.to_dict()}
        self.kernel.initialize_state(self.initial)
        self.service = PersonalFinanceService(self.kernel)

    def test_deposit_and_withdraw_are_atomic_on_same_finance_ledger(self):
        deposited = self.service.transfer("deposit", 2_500, context=context("bank-deposit"))
        withdrawn = self.service.transfer("withdraw", 1_000, context=context("bank-withdraw"))

        self.assertEqual(deposited.finance.cash_cents, 9_500)
        self.assertEqual(deposited.finance.bank_cents, 5_500)
        self.assertEqual(withdrawn.finance.cash_cents, 10_500)
        self.assertEqual(withdrawn.finance.bank_cents, 4_500)
        self.assertEqual([entry["kind"] for entry in withdrawn.finance.ledger], ["bank_deposit", "bank_withdrawal"])
        self.assertEqual(withdrawn.finance.revision, 2)
        self.assertEqual(
            [record["event_type"] for record in self.kernel.read_records()],
            ["finance.bank_transfer_posted", "finance.bank_transfer_posted"],
        )

    def test_insufficient_source_balance_fails_without_write(self):
        before = self.kernel.load_state()
        with self.assertRaisesRegex(ValueError, "Nicht genug Bargeld"):
            self.service.transfer("deposit", 12_001, context=context("bank-too-much-cash"))
        with self.assertRaisesRegex(ValueError, "Nicht genug Bankguthaben"):
            self.service.transfer("withdraw", 3_001, context=context("bank-too-much-bank"))
        self.assertEqual(self.kernel.load_state(), before)
        self.assertEqual(self.kernel.read_records(), ())

    def test_retry_is_write_free_and_command_id_cannot_change_meaning(self):
        first = self.service.transfer("deposit", 1_500, context=context("bank-retry"))
        records = self.kernel.read_records()
        retry = self.service.transfer("deposit", 1_500, context=context("bank-retry"))

        self.assertFalse(first.idempotent_replay)
        self.assertTrue(retry.idempotent_replay)
        self.assertEqual(self.kernel.read_records(), records)
        with self.assertRaises(PersistenceError):
            self.service.transfer("withdraw", 1_500, context=context("bank-retry"))
        with self.assertRaises(PersistenceError):
            self.service.transfer("deposit", 1_501, context=context("bank-retry"))

    def test_recovery_reconstructs_exact_finance_target(self):
        self.service.transfer("deposit", 2_000, context=context("bank-recover-1"))
        self.service.transfer("withdraw", 500, context=context("bank-recover-2"))
        records = self.kernel.read_records()

        recovered = dict(self.initial)
        for record in records:
            recovered = replay_game_event(recovered, record)

        self.assertEqual(recovered["finance"], self.kernel.load_state()["finance"])

    def test_invalid_amount_direction_and_character_fail_closed(self):
        for direction, amount in (("save", 100), ("deposit", 0), ("withdraw", -1)):
            with self.assertRaises(ValueError):
                self.service.transfer(direction, amount, context=context(f"invalid-{direction}-{amount}"))
        wrong = JournalContext(
            "2026-08-23T21:30:00+02:00", "session-bank-transfer", "player-local",
            "character", "char.other", "bank-wrong-character", "bank-transfer-test", "0.8.8-d1", "char.other",
        )
        with self.assertRaises(PersistenceError):
            self.service.transfer("deposit", 100, context=wrong)
        self.assertEqual(self.kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
