from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class BankTransferResult:
    finance: PlayerFinanceState
    direction: str
    amount_cents: int
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


@dataclass(frozen=True, slots=True)
class ConfirmedFinancePeriod:
    """Internal proof that one canonical savings period was already confirmed elsewhere."""

    period_id: str
    finance_tick: int
    character_id: str


@dataclass(frozen=True, slots=True)
class SavingsInterestResult:
    finance: PlayerFinanceState
    period_id: str
    finance_tick: int
    basis_points: int
    interest_cents: int
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class PersonalFinanceService:
    """Canonical personal finance operations on one PlayerFinanceState and ledger.

    Wallet/bank transfers are player commands. Savings interest is different: it
    accepts only an already-confirmed internal finance period and never derives
    authority from wall clock, browser time or a client-provided interest amount.
    """

    DIRECTIONS = frozenset({"deposit", "withdraw"})

    def __init__(
        self,
        persistence: PersistenceKernel,
        finance_manifest: Mapping[str, Any] | None = None,
    ) -> None:
        self.persistence = persistence
        self._interest_basis_points: int | None = None
        if finance_manifest is not None:
            self._interest_basis_points = self._validate_interest_manifest(finance_manifest)

    @staticmethod
    def _validate_interest_manifest(finance_manifest: Mapping[str, Any]) -> int:
        policy = finance_manifest.get("savings_interest")
        if not isinstance(policy, Mapping):
            raise ValueError("Personal-Finance-Manifest benötigt savings_interest")
        basis_points = policy.get("basis_points_per_confirmed_period")
        if isinstance(basis_points, bool) or not isinstance(basis_points, int) or not 1 <= basis_points <= 10_000:
            raise ValueError("Sparzins muss 1 bis 10000 Basispunkte betragen")
        required_true = (
            "compound_on_current_bank_balance",
            "confirmed_period_required",
            "consume_zero_interest_period",
            "require_sequential_finance_tick",
        )
        for field in required_true:
            if policy.get(field) is not True:
                raise ValueError(f"Sparzinsvertrag benötigt {field}=true")
        if policy.get("system_time_is_sole_authority") is not False:
            raise ValueError("Systemzeit darf keine alleinige Sparzins-Autorität sein")
        if policy.get("browser_can_confirm_period") is not False:
            raise ValueError("Browser darf keine Sparzinsperiode bestätigen")
        if policy.get("browser_can_supply_interest_amount") is not False:
            raise ValueError("Browser darf keinen Sparzinsbetrag liefern")
        return basis_points

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

    def apply_confirmed_interest(
        self,
        trigger: ConfirmedFinancePeriod,
        *,
        context: JournalContext,
    ) -> SavingsInterestResult:
        if self._interest_basis_points is None:
            raise ValueError("Sparzinsvertrag ist nicht konfiguriert")
        if not isinstance(trigger.period_id, str) or not trigger.period_id.strip():
            raise ValueError("Bestätigte Sparzinsperiode benötigt period_id")
        if isinstance(trigger.finance_tick, bool) or not isinstance(trigger.finance_tick, int) or trigger.finance_tick < 1:
            raise ValueError("Bestätigte Sparzinsperiode benötigt finance_tick >= 1")
        if not isinstance(trigger.character_id, str) or not trigger.character_id.strip():
            raise ValueError("Bestätigte Sparzinsperiode benötigt character_id")
        if context.entity_type != "character" or not context.entity_id or not context.command_id:
            raise ValueError("Sparzins benötigt Character-Kontext")
        if trigger.character_id != context.entity_id:
            raise ValueError("Sparzinsperiode passt nicht zum Character-Kontext")

        period_id = trigger.period_id.strip()
        event_id = f"finance-interest:{trigger.character_id}:tick:{trigger.finance_tick}"
        existing = next(
            (record for record in self.persistence.read_records() if record.get("event_id") == event_id),
            None,
        )
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("period_id") != period_id or payload.get("finance_tick") != trigger.finance_tick:
                raise PersistenceError("Bestätigter Finance-Tick wurde bereits anders verwendet")
            finance = self._confirmed_finance()
            return SavingsInterestResult(
                finance,
                period_id,
                trigger.finance_tick,
                int(payload.get("basis_points", 0)),
                int(payload.get("interest_cents", 0)),
                (),
                True,
            )

        state = deepcopy(self.persistence.load_state() or {})
        raw_character = state.get("character")
        if not isinstance(raw_character, dict) or raw_character.get("character_id") != trigger.character_id:
            raise PersistenceError("Sparzins benötigt passenden bestätigten Character-State")
        finance = PlayerFinanceState.from_dict(state.get("finance") if isinstance(state.get("finance"), dict) else None)
        expected_tick = finance.confirmed_finance_tick + 1
        if trigger.finance_tick != expected_tick:
            raise ValueError(
                f"Finance-Tick muss lückenlos {expected_tick} sein, erhalten: {trigger.finance_tick}"
            )

        basis_points = self._interest_basis_points
        interest_cents = (finance.bank_cents * basis_points) // 10_000
        finance_after = PlayerFinanceState.from_dict(finance.to_dict())
        finance_after.bank_cents += interest_cents
        finance_after.confirmed_finance_tick = trigger.finance_tick
        finance_after.revision += 1
        finance_after.ledger.append({
            "transaction_id": f"interest:{trigger.character_id}:{trigger.finance_tick}",
            "kind": "savings_interest",
            "amount_cents": interest_cents,
            "cash_after_cents": finance_after.cash_cents,
            "bank_after_cents": finance_after.bank_cents,
            "asset_id": None,
            "units": 0,
            "unit_price_cents": 0,
            "source_id": f"confirmed_period:{period_id}",
        })
        finance_after.validate()

        derived = deepcopy(state)
        derived["finance"] = finance_after.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:finance-interest:{trigger.character_id}:{trigger.finance_tick}",
            events=[{
                "event_id": event_id,
                "event_type": "finance.savings_interest_posted",
                "payload": {
                    "period_id": period_id,
                    "finance_tick": trigger.finance_tick,
                    "basis_points": basis_points,
                    "interest_cents": interest_cents,
                    "finance": finance_after.to_dict(),
                },
            }],
            derived_state=derived,
            context=context,
        )
        return SavingsInterestResult(
            finance_after,
            period_id,
            trigger.finance_tick,
            basis_points,
            interest_cents,
            receipt.event_ids,
            False,
        )

    def _confirmed_finance(self) -> PlayerFinanceState:
        state = self.persistence.load_state() or {}
        raw_finance = state.get("finance")
        if not isinstance(raw_finance, dict):
            raise PersistenceError("Finance-Replay verweist auf fehlenden Finance-State")
        return PlayerFinanceState.from_dict(raw_finance)


def replay_personal_finance_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    event_type = record.get("event_type")
    if event_type not in {
        "finance.bank_transfer_posted",
        "finance.savings_interest_posted",
    }:
        return derived_state
    payload = record.get("payload", {})
    raw_finance = payload.get("finance")
    if not isinstance(raw_finance, dict):
        raise ValueError("Persönliches Finance-Event benötigt Finance-Zielzustand")
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
    if event_type == "finance.savings_interest_posted":
        if target.confirmed_finance_tick != current.confirmed_finance_tick + 1:
            raise ValueError("Sparzins-Replay überspringt bestätigten Finance-Tick")
        if payload.get("finance_tick") != target.confirmed_finance_tick:
            raise ValueError("Sparzins-Replay widerspricht dem Finance-Zielzustand")
    elif target.confirmed_finance_tick != current.confirmed_finance_tick:
        raise ValueError("Banktransfer darf bestätigten Finance-Tick nicht verändern")
    state["finance"] = target.to_dict()
    return state


def replay_finance_bank_transfer_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Compatibility wrapper for callers introduced by 0.8.8-D."""
    return replay_personal_finance_event(derived_state, record)
