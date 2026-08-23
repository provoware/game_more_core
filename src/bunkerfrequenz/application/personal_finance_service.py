from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class BankTransferResult:
    finance: PlayerFinanceState
    direction: str
    amount_cents: int
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class PersonalFinanceService:
    """Move personal money atomically between wallet and bank on the canonical finance ledger."""

    DIRECTIONS = frozenset({"deposit", "withdraw"})

    def __init__(self, persistence: PersistenceKernel) -> None:
        self.persistence = persistence

    def transfer(
        self,
        direction: str,
        amount_cents: int,
        *,
        context: JournalContext,
    ) -> BankTransferResult:
        if context.entity_type != "character" or not context.entity_id or not context.command_id:
            raise ValueError("Banktransfer benötigt Character-Kontext")
        if not isinstance(direction, str) or direction not in self.DIRECTIONS:
            raise ValueError("Banktransfer-Richtung muss deposit oder withdraw sein")
        if isinstance(amount_cents, bool) or not isinstance(amount_cents, int) or amount_cents <= 0:
            raise ValueError("Banktransfer-Betrag muss positive Ganzzahl in Cent sein")

        event_id = f"{context.command_id}:finance-transfer"
        existing = next(
            (record for record in self.persistence.read_records() if record.get("event_id") == event_id),
            None,
        )
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("direction") != direction or payload.get("amount_cents") != amount_cents:
                raise PersistenceError("Command-ID wurde bereits für anderen Banktransfer verwendet")
            finance = self._confirmed_finance()
            return BankTransferResult(finance, direction, amount_cents, (), True)

        state = deepcopy(self.persistence.load_state() or {})
        raw_character = state.get("character")
        if not isinstance(raw_character, dict) or raw_character.get("character_id") != context.entity_id:
            raise PersistenceError("Banktransfer benötigt passenden bestätigten Character-State")
        finance = PlayerFinanceState.from_dict(state.get("finance") if isinstance(state.get("finance"), dict) else None)
        finance_after = PlayerFinanceState.from_dict(finance.to_dict())

        if direction == "deposit":
            if finance_after.cash_cents < amount_cents:
                raise ValueError("Nicht genug Bargeld für Einzahlung")
            finance_after.cash_cents -= amount_cents
            finance_after.bank_cents += amount_cents
            ledger_kind = "bank_deposit"
        else:
            if finance_after.bank_cents < amount_cents:
                raise ValueError("Nicht genug Bankguthaben für Auszahlung")
            finance_after.bank_cents -= amount_cents
            finance_after.cash_cents += amount_cents
            ledger_kind = "bank_withdrawal"

        finance_after.revision += 1
        finance_after.ledger.append({
            "transaction_id": f"bank:{context.command_id}",
            "kind": ledger_kind,
            "amount_cents": amount_cents,
            "cash_after_cents": finance_after.cash_cents,
            "bank_after_cents": finance_after.bank_cents,
            "asset_id": None,
            "units": 0,
            "unit_price_cents": 0,
            "source_id": "personal_bank",
        })
        finance_after.validate()

        derived = deepcopy(state)
        derived["finance"] = finance_after.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:finance-transfer",
            events=[{
                "event_id": event_id,
                "event_type": "finance.bank_transfer_posted",
                "payload": {
                    "direction": direction,
                    "amount_cents": amount_cents,
                    "finance": finance_after.to_dict(),
                },
            }],
            derived_state=derived,
            context=context,
        )
        return BankTransferResult(finance_after, direction, amount_cents, receipt.event_ids, False)

    def _confirmed_finance(self) -> PlayerFinanceState:
        state = self.persistence.load_state() or {}
        raw_finance = state.get("finance")
        if not isinstance(raw_finance, dict):
            raise PersistenceError("Banktransfer-Replay verweist auf fehlenden Finance-State")
        return PlayerFinanceState.from_dict(raw_finance)


def replay_finance_bank_transfer_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("event_type") != "finance.bank_transfer_posted":
        return derived_state
    payload = record.get("payload", {})
    raw_finance = payload.get("finance")
    if not isinstance(raw_finance, dict):
        raise ValueError("finance.bank_transfer_posted benötigt Finance-Zielzustand")
    target = PlayerFinanceState.from_dict(raw_finance)
    state = deepcopy(derived_state)
    current = PlayerFinanceState.from_dict(state.get("finance") if isinstance(state.get("finance"), dict) else None)
    if target.revision < current.revision:
        raise ValueError("Finance-Replay würde Revision zurücksetzen")
    if target.revision == current.revision:
        if target.to_dict() != current.to_dict():
            raise ValueError("Finance-Replay kollidiert auf gleicher Revision")
        return state
    if target.revision != current.revision + 1:
        raise ValueError("Finance-Replay überspringt Revision")
    state["finance"] = target.to_dict()
    return state
