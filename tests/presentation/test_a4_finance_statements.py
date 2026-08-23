import json
from pathlib import Path
import unittest

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.presentation.scene_jobs_projection import build_scene_jobs_projection


ROOT = Path(__file__).parents[2]
JOBS = json.loads((ROOT / "manifests" / "SCENE_JOB_MANIFEST.json").read_text(encoding="utf-8"))["jobs"]
UI = (ROOT / "web" / "a4" / "assistant_jobs_ui.js").read_text(encoding="utf-8")


def _entry(transaction_id, kind, amount, cash_after, bank_after, source_id):
    return {
        "transaction_id": transaction_id,
        "kind": kind,
        "amount_cents": amount,
        "cash_after_cents": cash_after,
        "bank_after_cents": bank_after,
        "asset_id": None,
        "units": 0,
        "unit_price_cents": 0,
        "source_id": source_id,
    }


class A4FinanceStatementsTests(unittest.TestCase):
    def test_statement_projects_only_confirmed_supported_ledger_rows_newest_first(self):
        finance = PlayerFinanceState(
            cash_cents=7_000,
            bank_cents=5_151,
            revision=5,
            ledger=[
                _entry("job:1", "job_income", 5_500, 5_500, 0, "scene.cable_repair"),
                _entry("bank:1", "bank_deposit", 2_000, 3_500, 2_000, "personal_bank"),
                _entry("interest:1", "savings_interest", 20, 3_500, 2_020, "confirmed_period:p1"),
                _entry("bank:2", "bank_withdrawal", 500, 4_000, 1_520, "personal_bank"),
                _entry("future:1", "investment_buy", 1_000, 3_000, 1_520, "asset.demo"),
            ],
        )
        state = {
            "character": CharacterState("char.local", "Local").to_dict(),
            "finance": finance.to_dict(),
        }
        original = json.loads(json.dumps(state))

        statement = build_scene_jobs_projection(state, JOBS)["finance_statement"]

        self.assertEqual(state, original)
        self.assertEqual(statement["supported_entries"], 4)
        self.assertEqual(statement["other_entries"], 1)
        self.assertEqual(statement["filters"], ("all", "jobs", "bank", "interest"))
        self.assertEqual(
            [entry["kind"] for entry in statement["entries"]],
            ["bank_withdrawal", "savings_interest", "bank_deposit", "job_income"],
        )
        self.assertEqual(statement["entries"][-1]["source_label"], "Kabel & Kleinkram reparieren")
        self.assertEqual(statement["totals"]["job_income_cents"], 5_500)
        self.assertEqual(statement["totals"]["bank_deposit_cents"], 2_000)
        self.assertEqual(statement["totals"]["bank_withdrawal_cents"], 500)
        self.assertEqual(statement["totals"]["savings_interest_cents"], 20)

    def test_statement_does_not_invent_timestamp_or_second_ledger(self):
        projected = build_scene_jobs_projection(
            {"character": CharacterState("char.local", "Local").to_dict()},
            JOBS,
        )["finance_statement"]

        self.assertEqual(projected["entries"], [])
        self.assertNotIn("timestamp", json.dumps(projected).lower())
        self.assertNotIn("created_at", json.dumps(projected).lower())

    def test_control_deck_filters_are_local_and_statement_has_no_write_command(self):
        for marker in (
            "jobs-finance-statement",
            "KONTOAUSZUG // BESTÄTIGTES LEDGER",
            "dataset.statementFilter",
            'statementFilter = "all"',
            "JOBLOHN",
            "EINZAHLUNGEN",
            "AUSZAHLUNGEN",
            "ZINSEN",
            "Keine Datumsangabe wird erfunden",
        ):
            self.assertIn(marker, UI)
        self.assertNotIn('type: "finance.statement"', UI)
        self.assertNotIn("localStorage", UI)
        self.assertNotIn("sessionStorage", UI)


if __name__ == "__main__":
    unittest.main()
