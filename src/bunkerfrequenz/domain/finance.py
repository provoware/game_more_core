from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


FINANCE_LEDGER_KINDS = frozenset({
    "job_income",
    "bank_deposit",
    "bank_withdrawal",
    "savings_interest",
    "investment_buy",
    "investment_sell",
    "investment_dividend",
})


def _non_negative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} muss Ganzzahl >= 0 sein")
    return value


@dataclass(slots=True)
class PlayerFinanceState:
    cash_cents: int = 0
    bank_cents: int = 0
    investment_units: dict[str, int] = field(default_factory=dict)
    ledger: list[dict[str, Any]] = field(default_factory=list)
    confirmed_finance_tick: int = 0
    revision: int = 0

    def validate(self) -> None:
        _non_negative_int(self.cash_cents, "finance.cash_cents")
        _non_negative_int(self.bank_cents, "finance.bank_cents")
        _non_negative_int(self.confirmed_finance_tick, "finance.confirmed_finance_tick")
        _non_negative_int(self.revision, "finance.revision")
        for asset_id, units in self.investment_units.items():
            if not isinstance(asset_id, str) or not asset_id.strip():
                raise ValueError("finance.investment_units benötigt gültige Asset-ID")
            _non_negative_int(units, f"finance.investment_units.{asset_id}")

        seen: set[str] = set()
        required = {
            "transaction_id", "kind", "amount_cents", "cash_after_cents", "bank_after_cents",
            "asset_id", "units", "unit_price_cents", "source_id",
        }
        for entry in self.ledger:
            if not isinstance(entry, dict) or set(entry) != required:
                raise ValueError("Finance-Ledger-Eintrag besitzt ungültige Felder")
            transaction_id = entry["transaction_id"]
            if not isinstance(transaction_id, str) or not transaction_id.strip() or transaction_id in seen:
                raise ValueError("Finance-Transaktions-ID ist ungültig oder doppelt")
            seen.add(transaction_id)
            if entry["kind"] not in FINANCE_LEDGER_KINDS:
                raise ValueError("Finance-Ledger-kind ist unbekannt")
            if isinstance(entry["amount_cents"], bool) or not isinstance(entry["amount_cents"], int):
                raise ValueError("Finance-Betrag muss Ganzzahl sein")
            _non_negative_int(entry["cash_after_cents"], "finance.cash_after_cents")
            _non_negative_int(entry["bank_after_cents"], "finance.bank_after_cents")
            asset_id = entry["asset_id"]
            if asset_id is not None and (not isinstance(asset_id, str) or not asset_id.strip()):
                raise ValueError("Finance-Asset-ID muss Text oder null sein")
            _non_negative_int(entry["units"], "finance.units")
            _non_negative_int(entry["unit_price_cents"], "finance.unit_price_cents")
            source_id = entry["source_id"]
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError("Finance-source_id fehlt")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "cash_cents": self.cash_cents,
            "bank_cents": self.bank_cents,
            "investment_units": dict(self.investment_units),
            "ledger": deepcopy(self.ledger),
            "confirmed_finance_tick": self.confirmed_finance_tick,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "PlayerFinanceState":
        raw = data or {}
        state = cls(
            cash_cents=raw.get("cash_cents", 0),
            bank_cents=raw.get("bank_cents", 0),
            investment_units=dict(raw.get("investment_units", {})),
            ledger=deepcopy(raw.get("ledger", [])),
            confirmed_finance_tick=raw.get("confirmed_finance_tick", 0),
            revision=raw.get("revision", 0),
        )
        state.validate()
        return state
