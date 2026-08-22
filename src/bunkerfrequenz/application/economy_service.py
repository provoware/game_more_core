from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from bunkerfrequenz.domain.economy import EconomyState, market_price
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class EconomyCommitResult:
    economy: EconomyState
    event: EventState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class EconomyService:
    def __init__(self, persistence: PersistenceKernel):
        self.persistence = persistence

    def initialize(self, economy: EconomyState, *, context: JournalContext) -> EconomyCommitResult:
        economy.validate()
        self._validate_context(context)
        existing = self._existing(context.command_id, suffix="catalog")
        if existing is not None:
            if existing.get("payload", {}).get("economy") != economy.to_dict():
                raise PersistenceError("Command-ID wurde mit anderem Katalog verwendet")
            return self._current_result((), True, context=context)
        state = deepcopy(self.persistence.load_state() or {})
        if "event" not in state:
            raise PersistenceError("Economy benötigt einen bestätigten Eventzustand")
        if "economy" in state:
            raise PersistenceError("Economy-Zustand ist bereits initialisiert")
        event = EventState.from_dict(state["event"])
        self._assert_event_context(event, context)
        state["economy"] = economy.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}",
            events=[{
                "event_id": f"{context.command_id}:catalog",
                "event_type": "economy.catalog_initialized",
                "payload": {"economy": economy.to_dict(), "event": event.to_dict()},
            }],
            derived_state=state,
            context=context,
        )
        return EconomyCommitResult(economy, event, receipt.event_ids, False)

    def transact(
        self,
        kind: str,
        item_id: str,
        quantity: int,
        *,
        context: JournalContext,
        price_multiplier_bps: int = 10000,
    ) -> EconomyCommitResult:
        if kind not in {"buy", "sell", "consume", "reserve", "release"}:
            raise ValueError("Unbekannte Economy-Aktion")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("quantity muss eine Ganzzahl >= 1 sein")
        if (
            isinstance(price_multiplier_bps, bool)
            or not isinstance(price_multiplier_bps, int)
            or not 1000 <= price_multiplier_bps <= 50000
        ):
            raise ValueError("price_multiplier_bps muss zwischen 1000 und 50000 liegen")
        self._validate_context(context)
        existing = self._existing(context.command_id)
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("request") != {"kind": kind, "item_id": item_id, "quantity": quantity}:
                raise PersistenceError("Command-ID wurde mit anderer Economy-Aktion verwendet")
            return self._current_result((), True, context=context)

        economy, event = self._load()
        self._assert_event_context(event, context)
        if item_id not in economy.catalog:
            raise ValueError("Equipment ist nicht katalogisiert")
        updated_economy, budget_delta = self._apply(
            economy,
            kind,
            item_id,
            quantity,
            context.command_id,
            price_multiplier_bps=price_multiplier_bps,
        )
        updated_event = self._resolve_event(event, updated_economy, budget_delta)
        payload = {
            "request": {"kind": kind, "item_id": item_id, "quantity": quantity},
            "market_context": {"price_multiplier_bps": price_multiplier_bps},
            "economy": updated_economy.to_dict(),
            "event": updated_event.to_dict(),
        }
        event_type = "economy.transaction_posted"
        inventory_type = "inventory.item_acquired" if kind == "buy" else "inventory.item_removed"
        events = [{"event_id": f"{context.command_id}:economy", "event_type": event_type, "payload": payload}]
        if kind in {"buy", "sell", "consume"}:
            events.append({
                "event_id": f"{context.command_id}:inventory",
                "event_type": inventory_type,
                "payload": {"item_id": item_id, "quantity": quantity, "reason": kind},
            })
        current = deepcopy(self.persistence.load_state() or {})
        current["economy"] = updated_economy.to_dict()
        current["event"] = updated_event.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}", events=events, derived_state=current, context=context
        )
        return EconomyCommitResult(updated_economy, updated_event, receipt.event_ids, False)

    def compensate(self, transaction_id: str, *, context: JournalContext) -> EconomyCommitResult:
        self._validate_context(context)
        existing = self._existing(context.command_id, suffix="compensation")
        if existing is not None:
            if existing.get("payload", {}).get("transaction_id") != transaction_id:
                raise PersistenceError("Command-ID wurde mit anderer Kompensation verwendet")
            return self._current_result((), True, context=context)
        economy, event = self._load()
        self._assert_event_context(event, context)
        original = next((entry for entry in economy.ledger if entry["transaction_id"] == transaction_id), None)
        if original is None or original["kind"] not in {"buy", "sell"}:
            raise ValueError("Nur bestätigte Kauf-/Verkaufstransaktionen sind kompensierbar")
        if any(entry["compensates"] == transaction_id for entry in economy.ledger):
            raise ValueError("Transaktion wurde bereits kompensiert")
        inverse = "sell" if original["kind"] == "buy" else "buy"
        updated, delta = self._apply(
            economy,
            inverse,
            original["item_id"],
            original["quantity"],
            context.command_id,
            unit_price=original["unit_price_cents"],
            compensates=transaction_id,
        )
        updated_event = self._resolve_event(event, updated, delta)
        payload = {"transaction_id": transaction_id, "economy": updated.to_dict(), "event": updated_event.to_dict()}
        current = deepcopy(self.persistence.load_state() or {})
        current.update(economy=updated.to_dict(), event=updated_event.to_dict())
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}",
            events=[{"event_id": f"{context.command_id}:compensation", "event_type": "economy.transaction_compensated", "payload": payload}],
            derived_state=current,
            context=context,
        )
        return EconomyCommitResult(updated, updated_event, receipt.event_ids, False)

    def _apply(
        self,
        state: EconomyState,
        kind: str,
        item_id: str,
        quantity: int,
        transaction_id: str,
        *,
        unit_price: int | None = None,
        compensates: str | None = None,
        price_multiplier_bps: int = 10000,
    ) -> tuple[EconomyState, int]:
        data = state.to_dict()
        stock = data["inventory"].setdefault(item_id, {"owned": 0, "reserved": 0})
        item = data["catalog"][item_id]
        if unit_price is not None:
            price = unit_price
        else:
            reference = market_price(
                item["base_price_cents"], state.market_tick, item["volatility_bps"]
            )
            price = max(0, (reference * price_multiplier_bps + 5000) // 10000)
        delta = 0
        if kind == "buy":
            stock["owned"] += quantity
            delta = -(price * quantity)
        elif kind == "sell":
            if stock["owned"] - stock["reserved"] < quantity:
                raise ValueError("Nicht genug unreservierter Besitz zum Verkaufen")
            stock["owned"] -= quantity
            delta = price * quantity
        elif kind == "consume":
            if not item["consumable"] or stock["owned"] - stock["reserved"] < quantity:
                raise ValueError("Equipment ist nicht verbrauchbar oder nicht frei verfügbar")
            stock["owned"] -= quantity
        elif kind == "reserve":
            if stock["owned"] - stock["reserved"] < quantity:
                raise ValueError("Nicht genug freier Besitz zum Reservieren")
            stock["reserved"] += quantity
        else:
            if stock["reserved"] < quantity:
                raise ValueError("Nicht genug reservierten Besitz zum Freigeben")
            stock["reserved"] -= quantity
        data["ledger"].append({
            "transaction_id": transaction_id,
            "kind": kind,
            "item_id": item_id,
            "quantity": quantity,
            "unit_price_cents": price,
            "budget_delta_cents": delta,
            "compensates": compensates,
        })
        data["market_tick"] += 1
        data["revision"] += 1
        return EconomyState.from_dict(data), delta

    @staticmethod
    def _resolve_event(event: EventState, economy: EconomyState, budget_delta: int) -> EventState:
        data = event.to_dict()
        new_budget = data["budget_cents"] + budget_delta
        if new_budget < 0:
            raise ValueError("Event-Budget reicht für diese Transaktion nicht aus")
        data["budget_cents"] = new_budget
        for requirement in data["equipment"]:
            stock = economy.inventory.get(requirement["equipment_id"], {"owned": 0, "reserved": 0})
            needed = requirement["quantity"]
            requirement["status"] = "ready" if stock["reserved"] >= needed else ("reserved" if stock["reserved"] else "missing")
        data["revision"] += 1
        return EventState.from_dict(data)

    def _load(self) -> tuple[EconomyState, EventState]:
        state = self.persistence.load_state() or {}
        if "economy" not in state or "event" not in state:
            raise PersistenceError("Economy- und Eventzustand müssen initialisiert sein")
        return EconomyState.from_dict(state["economy"]), EventState.from_dict(state["event"])

    def _existing(self, command_id: str, suffix: str = "economy") -> dict[str, Any] | None:
        event_id = f"{command_id}:{suffix}"
        return next((record for record in self.persistence.read_records() if record["event_id"] == event_id), None)

    def _current_result(
        self,
        ids: tuple[str, ...],
        replay: bool,
        *,
        context: JournalContext,
    ) -> EconomyCommitResult:
        economy, event = self._load()
        self._assert_event_context(event, context)
        return EconomyCommitResult(economy, event, ids, replay)

    @staticmethod
    def _validate_context(context: JournalContext) -> None:
        if context.entity_type != "event" or not context.command_id:
            raise ValueError("Economy-Commit benötigt Event-Kontext und command_id")
        if not context.entity_id:
            raise ValueError("Economy-Commit benötigt eine Event-entity_id")

    @staticmethod
    def _assert_event_context(event: EventState, context: JournalContext) -> None:
        if context.entity_id != event.event_id:
            raise ValueError("JournalContext.entity_id passt nicht zum bestätigten Event")


def replay_economy_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record["event_type"] not in {
        "economy.catalog_initialized", "economy.transaction_posted", "economy.transaction_compensated"
    }:
        return derived_state
    payload = record.get("payload", {})
    economy = EconomyState.from_dict(payload["economy"])
    event = EventState.from_dict(payload["event"])
    state = deepcopy(derived_state)
    current = state.get("economy")
    if current is not None:
        current_economy = EconomyState.from_dict(current)
        if current_economy.revision > economy.revision:
            return state
        if current_economy.revision == economy.revision:
            current_event = state.get("event")
            if current_economy.to_dict() != economy.to_dict() or current_event != event.to_dict():
                raise ValueError("Economy-Replay kollidiert mit Zustand derselben Revision")
            return state
    state.update(economy=economy.to_dict(), event=event.to_dict())
    return state
