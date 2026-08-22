from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


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
            required = {"transaction_id", "kind", "item_id", "quantity", "unit_price_cents", "budget_delta_cents", "compensates"}
            if set(entry) != required or entry["transaction_id"] in seen:
                raise ValueError("Ledger-Eintrag ist ungültig oder doppelt")
            seen.add(entry["transaction_id"])

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
