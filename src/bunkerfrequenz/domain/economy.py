from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

REGULAR_LEDGER_KINDS = frozenset({"buy", "sell", "consume", "reserve", "release"})
PROPERTY_PURCHASE_LEDGER_KIND = "property_purchase"
PROPERTY_LEDGER_ITEM_PREFIX = "property:"
SETTLEMENT_LEDGER_KIND = "settlement"
SETTLEMENT_LEDGER_ITEM_ID = "__event_settlement__"


def _positive_int(value: Any, name: str, *, allow_zero: bool = False) -> int:
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} muss eine Ganzzahl >= {minimum} sein")
    return value


def market_price(base_price_cents: int, market_tick: int, volatility_bps: int) -> int:
    """Return a deterministic price; bps are basis points (1/100 percent)."""
    _positive_int(base_price_cents, "base_price_cents")
    _positive_int(market_tick, "market_tick", allow_zero=True)
    _positive_int(volatility_bps, "volatility_bps", allow_zero=True)
    cycle = (market_tick % 5) - 2
    return max(1, (base_price_cents * (10_000 + cycle * volatility_bps)) // 10_000)


def _validate_ledger_entry(entry: dict[str, Any], seen: set[str]) -> None:
    required = {
        "transaction_id", "kind", "item_id", "quantity", "unit_price_cents",
        "budget_delta_cents", "compensates",
    }
    if set(entry) != required:
        raise ValueError("Ledger-Eintrag besitzt ungültige Felder")
    transaction_id = entry["transaction_id"]
    if not isinstance(transaction_id, str) or not transaction_id.strip() or transaction_id in seen:
        raise ValueError("Ledger-Transaktions-ID ist ungültig oder doppelt")
    seen.add(transaction_id)
    kind = entry["kind"]
    if kind not in REGULAR_LEDGER_KINDS | {PROPERTY_PURCHASE_LEDGER_KIND, SETTLEMENT_LEDGER_KIND}:
        raise ValueError("Ledger-kind ist unbekannt")
    item_id = entry["item_id"]
    if not isinstance(item_id, str) or not item_id.strip():
        raise ValueError("Ledger-item_id muss nicht leerer Text sein")
    _positive_int(entry["quantity"], "ledger.quantity")
    if isinstance(entry["budget_delta_cents"], bool) or not isinstance(entry["budget_delta_cents"], int):
        raise ValueError("ledger.budget_delta_cents muss Ganzzahl sein")
    compensates = entry["compensates"]
    if compensates is not None and (not isinstance(compensates, str) or not compensates.strip()):
        raise ValueError("ledger.compensates muss Text oder null sein")

    if kind == SETTLEMENT_LEDGER_KIND:
        if item_id != SETTLEMENT_LEDGER_ITEM_ID:
            raise ValueError("Settlement-Ledger benötigt kanonische item_id")
        if entry["quantity"] != 1 or entry["unit_price_cents"] != 0 or compensates is not None:
            raise ValueError("Settlement-Ledger besitzt ungültige Buchungsfelder")
        return

    _positive_int(entry["unit_price_cents"], "ledger.unit_price_cents")
    if item_id == SETTLEMENT_LEDGER_ITEM_ID:
        raise ValueError("Normale Economy-Transaktion darf Settlement-item_id nicht verwenden")

    if kind == PROPERTY_PURCHASE_LEDGER_KIND:
        if not item_id.startswith(PROPERTY_LEDGER_ITEM_PREFIX) or len(item_id) <= len(PROPERTY_LEDGER_ITEM_PREFIX):
            raise ValueError("Property-Kauf benötigt kanonische property:item_id")
        if entry["quantity"] != 1:
            raise ValueError("Property-Kauf benötigt quantity=1")
        if entry["budget_delta_cents"] != -entry["unit_price_cents"]:
            raise ValueError("Property-Kauf muss exakt den bestätigten Kaufpreis abbuchen")
        if compensates is not None:
            raise ValueError("Property-Kauf ist in 0.8.6-A nicht kompensierbar")


@dataclass(slots=True)
class EconomyState:
    catalog: dict[str, dict[str, Any]]
    inventory: dict[str, dict[str, int]] = field(default_factory=dict)
    ledger: list[dict[str, Any]] = field(default_factory=list)
    market_tick: int = 0
    revision: int = 0

    def validate(self) -> None:
        _positive_int(self.market_tick, "market_tick", allow_zero=True)
        _positive_int(self.revision, "revision", allow_zero=True)
        for item_id, item in self.catalog.items():
            if not item_id or set(item) != {"label", "base_price_cents", "volatility_bps", "consumable"}:
                raise ValueError("Katalogeintrag besitzt ungültige Felder")
            if not isinstance(item["label"], str) or not item["label"].strip():
                raise ValueError("Kataloglabel muss Text sein")
            _positive_int(item["base_price_cents"], "base_price_cents")
            _positive_int(item["volatility_bps"], "volatility_bps", allow_zero=True)
            if not isinstance(item["consumable"], bool):
                raise ValueError("consumable muss boolesch sein")
        for item_id, stock in self.inventory.items():
            if item_id not in self.catalog or set(stock) != {"owned", "reserved"}:
                raise ValueError("Inventareintrag ist nicht katalogisiert")
            owned = _positive_int(stock["owned"], "owned", allow_zero=True)
            reserved = _positive_int(stock["reserved"], "reserved", allow_zero=True)
            if reserved > owned:
                raise ValueError("Reservierung übersteigt Besitz")
        seen: set[str] = set()
        for entry in self.ledger:
            if not isinstance(entry, dict):
                raise ValueError("Ledger-Eintrag muss Objekt sein")
            _validate_ledger_entry(entry, seen)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "catalog": deepcopy(self.catalog),
            "inventory": deepcopy(self.inventory),
            "ledger": deepcopy(self.ledger),
            "market_tick": self.market_tick,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EconomyState":
        state = cls(
            catalog=deepcopy(data.get("catalog", {})),
            inventory=deepcopy(data.get("inventory", {})),
            ledger=deepcopy(data.get("ledger", [])),
            market_tick=data.get("market_tick", 0),
            revision=data.get("revision", 0),
        )
        state.validate()
        return state
