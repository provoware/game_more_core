from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class ConfirmedFinancePeriod:
    """Already-authorized finance period; this type does not produce time authority."""

    period_id: str
    finance_tick: int
    character_id: str

    def validate(self) -> None:
        if not isinstance(self.period_id, str) or not self.period_id.strip():
            raise ValueError("Bestätigte Finanzperiode benötigt period_id")
        if isinstance(self.finance_tick, bool) or not isinstance(self.finance_tick, int) or self.finance_tick < 1:
            raise ValueError("Bestätigte Finanzperiode benötigt finance_tick >= 1")
        if not isinstance(self.character_id, str) or not self.character_id.strip():
            raise ValueError("Bestätigte Finanzperiode benötigt character_id")


@dataclass(frozen=True, slots=True)
class SavingsInterestResult:
    finance: PlayerFinanceState
    period_id: str
    finance_tick: int
    interest_cents: int
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class SavingsInterestService:
    """Apply catalogued compound interest only from an already confirmed finance period."""

    def __init__(self, persistence: PersistenceKernel, manifest: Mapping[str, Any]) -> None:
        self.persistence = persistence
        policy = manifest.get("savings_interest")
        if not isinstance(policy, Mapping):
            raise ValueError("Personal-Finance-Manifest benötigt savings_interest")
        rate = policy.get("basis_points_per_confirmed_period")
        if isinstance(rate, bool) or not isinstance(rate, int) or not 1 <= rate <= 10_000:
            raise ValueError("Sparzins benötigt 1..10000 Basispunkte")
        required_flags = {
            "compound_on_current_bank_balance": True,
            "confirmed_period_required": True,
            "consume_zero_interest_period": True,
            "require_sequential_finance_tick": True,
            "system_time_is_sole_authority": False,
            "browser_can_confirm_period": False,
            "browser_can_supply_interest_amount": False,
        }
        for field, expected in required_flags.items():
            if policy.get(field) is not expected:
                raise ValueError(f"Sparzins-Vertrag verletzt {field}")
        self.rate_basis_points = rate

    def apply_confirmed_period(
        self,
        trigger: ConfirmedFinancePeriod,
        *,
        context: JournalContext,
    ) -> SavingsInterestResult:
        trigger.validate()
        if context.entity_type != "character" or context.entity_id != trigger.character_id:
            raise ValueError("Sparzins benötigt passenden Character-Kontext")
        if not context.command_id:
            raise ValueError("Sparzins benötigt command_id")

        event_id = f"finance-interest:{trigger.period_id}"
        existing = next(
            (record for record in self.persistence.read_records() if record.get("event_id") == event_id),
            None,
        )
        if existing is not None:
            payload = existing.get("payload", {})
            if (
                payload.get("period_id") != trigger.period_id
                or payload.get("finance_tick") != trigger.finance_tick
                or payload.get("rate_basis_points") != self.rate_basis_points
            ):
                raise PersistenceError("Bestätigte Finanzperiode kollidiert mit bestehender Zinsbuchung")
            raw_finance = payload.get("finance")
            if not isinstance(raw_finance, dict):
                raise PersistenceError("Zins-Replay verweist auf fehlenden Finance-Zielzustand")
            interest_cents = payload.get("interest_cents")
            if isinstance(interest_cents, bool) or not isinstance(interest_cents, int) or interest_cents < 0:
                raise PersistenceError("Zins-Replay besitzt ungültigen Zinsbetrag")
            return SavingsInterestResult(
                PlayerFinanceState.from_dict(raw_finance),
                trigger.period_id,
                trigger.finance_tick,
                interest_cents,
                (),
                True,
            )

        state = deepcopy(self.persistence.load_state() or {})
        raw_character = state.get("character")
        if not isinstance(raw_character, dict) or raw_character.get("character_id") != trigger.character_id:
            raise PersistenceError("Sparzins benötigt passenden bestätigten Character-State")
        raw_finance = state.get("finance")
        finance = PlayerFinanceState.from_dict(raw_finance if isinstance(raw_finance, dict) else None)
        expected_tick = finance.confirmed_finance_tick + 1
        if trigger.finance_tick != expected_tick:
            raise ValueError(
                f"Sparzins benötigt nächsten bestätigten Finance-Tick {expected_tick}, erhalten {trigger.finance_tick}"
            )

        finance_after = PlayerFinanceState.from_dict(finance.to_dict())
        interest_cents = finance_after.bank_cents * self.rate_basis_points // 10_000
        finance_after.bank_cents += interest_cents
        finance_after.confirmed_finance_tick = trigger.finance_tick
        finance_after.revision += 1
        finance_after.ledger.append({
            "transaction_id": f"interest:{trigger.period_id}",
            "kind": "savings_interest",
            "amount_cents": interest_cents,
            "cash_after_cents": finance_after.cash_cents,
            "bank_after_cents": finance_after.bank_cents,
            "asset_id": None,
            "units": 0,
            "unit_price_cents": 0,
            "source_id": f"confirmed_period:{trigger.period_id}",
        })
        finance_after.validate()

        derived = deepcopy(state)
        derived["finance"] = finance_after.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:finance-interest:{trigger.period_id}",
            events=[{
                "event_id": event_id,
                "event_type": "finance.savings_interest_posted",
                "payload": {
                    "period_id": trigger.period_id,
                    "finance_tick": trigger.finance_tick,
                    "rate_basis_points": self.rate_basis_points,
                    "interest_cents": interest_cents,
                    "finance": finance_after.to_dict(),
                },
            }],
            derived_state=derived,
            context=context,
        )
        return SavingsInterestResult(
            finance_after,
            trigger.period_id,
            trigger.finance_tick,
            interest_cents,
            receipt.event_ids,
            False,
        )


def replay_finance_savings_interest_event(
    derived_state: dict[str, Any], record: dict[str, Any]
) -> dict[str, Any]:
    if record.get("event_type") != "finance.savings_interest_posted":
        return derived_state
    payload = record.get("payload", {})
    raw_finance = payload.get("finance")
    if not isinstance(raw_finance, dict):
        raise ValueError("finance.savings_interest_posted benötigt Finance-Zielzustand")
    target = PlayerFinanceState.from_dict(raw_finance)
    state = deepcopy(derived_state)
    current = PlayerFinanceState.from_dict(
        state.get("finance") if isinstance(state.get("finance"), dict) else None
    )
    if target.revision < current.revision:
        raise ValueError("Finance-Replay würde Revision zurücksetzen")
    if target.revision == current.revision:
        if target.to_dict() != current.to_dict():
            raise ValueError("Finance-Replay kollidiert auf gleicher Revision")
        return state
    if target.revision != current.revision + 1:
        raise ValueError("Finance-Replay überspringt Revision")
    if target.confirmed_finance_tick != current.confirmed_finance_tick + 1:
        raise ValueError("Sparzins-Replay überspringt bestätigten Finance-Tick")
    state["finance"] = target.to_dict()
    return state
