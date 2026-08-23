import json
from pathlib import Path
import tempfile
import unittest

from bunkerfrequenz.application.assistant_game_client_session import AssistantGameClientSession
from bunkerfrequenz.application.incident_service import build_incident_catalog
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceKernel


ROOT = Path(__file__).parents[2]
JOURNAL = json.loads((ROOT / "manifests" / "JOURNAL_MANIFEST.json").read_text(encoding="utf-8"))
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))
INCIDENTS = json.loads((ROOT / "manifests" / "INCIDENT_MANIFEST.json").read_text(encoding="utf-8"))
ALLOWED = set(JOURNAL["event_types"])


def event_context(command_id: str) -> JournalContext:
    return JournalContext(
        "2026-08-23T21:30:00+02:00",
        "session-bank-ui",
        "player-local",
        "event",
        "event.local",
        command_id,
        "bank-ui-test",
        "0.8.8-d1",
        "char.local",
    )


class PersonalFinanceGameClientSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.kernel = PersistenceKernel(self.tmp.name, ALLOWED)
        character = CharacterState(character_id="char.local", display_name="Local")
        finance = PlayerFinanceState(cash_cents=5_000, bank_cents=2_000)
        self.kernel.initialize_state({"character": character.to_dict(), "finance": finance.to_dict()})
        self.session = AssistantGameClientSession(
            self.kernel,
            incident_catalog=build_incident_catalog(INCIDENTS),
            incident_contract_version=INCIDENTS["version"],
            scene_job_manifest=JOBS,
        )

    def test_transfer_uses_confirmed_character_and_only_direction_amount(self):
        result = self.session.dispatch(
            {
                "type": "finance.transfer",
                "command_id": "bank-ui-deposit",
                "direction": "deposit",
                "amount_cents": 1_250,
            },
            context=event_context("bank-ui-deposit"),
        )

        self.assertEqual(result.status, "confirmed")
        self.assertEqual(result.committed_event_ids, ("bank-ui-deposit:finance-transfer",))
        finance = result.metadata["personal_finance_transfer"]["finance"]
        self.assertEqual(finance["cash_cents"], 3_750)
        self.assertEqual(finance["bank_cents"], 3_250)

    def test_client_cannot_supply_target_balances_or_interest(self):
        for forbidden in ("cash_after_cents", "bank_after_cents", "interest_cents"):
            command = {
                "type": "finance.transfer",
                "command_id": f"bank-extra-{forbidden}",
                "direction": "deposit",
                "amount_cents": 100,
                forbidden: 999_999,
            }
            result = self.session.dispatch(command, context=event_context(command["command_id"]))
            self.assertEqual(result.status, "rejected")
            self.assertEqual(result.error_code, "unexpected_command_fields")
        self.assertEqual(self.kernel.read_records(), ())

    def test_invalid_direction_amount_and_context_character_fail_closed(self):
        bad_direction = self.session.dispatch(
            {"type": "finance.transfer", "command_id": "bank-bad-dir", "direction": "interest", "amount_cents": 100},
            context=event_context("bank-bad-dir"),
        )
        bad_amount = self.session.dispatch(
            {"type": "finance.transfer", "command_id": "bank-bad-amount", "direction": "deposit", "amount_cents": 0},
            context=event_context("bank-bad-amount"),
        )
        wrong_context = JournalContext(
            "2026-08-23T21:30:00+02:00", "session-bank-ui", "player-local",
            "event", "event.local", "bank-wrong-character", "bank-ui-test", "0.8.8-d1", "char.other",
        )
        wrong = self.session.dispatch(
            {"type": "finance.transfer", "command_id": "bank-wrong-character", "direction": "deposit", "amount_cents": 100},
            context=wrong_context,
        )

        self.assertEqual(bad_direction.error_code, "invalid_finance_direction")
        self.assertEqual(bad_amount.error_code, "invalid_finance_amount")
        self.assertEqual(wrong.error_code, "character_context_mismatch")
        self.assertEqual(self.kernel.read_records(), ())


if __name__ == "__main__":
    unittest.main()
