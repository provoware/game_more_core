from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping


MAX_UPGRADE_LEVEL = 3


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} muss nicht-leerer Text sein")
    return value.strip()


def _nonnegative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} muss eine nichtnegative Ganzzahl sein")
    return value


def upgrade_cost_cents(purchase_price_cents: int, cost_bps: int, level_multiplier_bps: int) -> int:
    """Return a deterministic fixed upgrade cost using integer basis points."""
    if isinstance(purchase_price_cents, bool) or not isinstance(purchase_price_cents, int) or purchase_price_cents < 1:
        raise ValueError("purchase_price_cents muss positive Ganzzahl sein")
    if isinstance(cost_bps, bool) or not isinstance(cost_bps, int) or cost_bps < 1:
        raise ValueError("cost_bps muss positive Ganzzahl sein")
    if isinstance(level_multiplier_bps, bool) or not isinstance(level_multiplier_bps, int) or level_multiplier_bps < 1:
        raise ValueError("level_multiplier_bps muss positive Ganzzahl sein")
    return max(1, purchase_price_cents * cost_bps * level_multiplier_bps // 10_000 // 10_000)


@dataclass(slots=True)
class PropertyUpgradeState:
    contract_version: str
    revision: int = 0
    properties: dict[str, dict[str, Any]] = field(default_factory=dict)

    def validate(self) -> None:
        _text(self.contract_version, "contract_version")
        _nonnegative_int(self.revision, "revision")
        if not isinstance(self.properties, dict):
            raise ValueError("properties muss ein Mapping sein")
        transaction_ids: set[str] = set()
        for location_id, record in self.properties.items():
            location_id = _text(location_id, "location_id")
            if not isinstance(record, dict) or set(record) != {"location_id", "upgrades"}:
                raise ValueError(f"Upgrade-Record {location_id} besitzt falsche Felder")
            if _text(record["location_id"], "record.location_id") != location_id:
                raise ValueError("Upgrade-Key und record.location_id widersprechen sich")
            upgrades = record["upgrades"]
            if not isinstance(upgrades, dict) or not upgrades:
                raise ValueError("Property-Upgrade-Record benötigt mindestens einen Ausbau")
            for upgrade_id, upgrade in upgrades.items():
                _text(upgrade_id, "upgrade_id")
                if not isinstance(upgrade, dict) or set(upgrade) != {"level", "economy_transaction_ids"}:
                    raise ValueError("Upgrade besitzt falsche Felder")
                level = _nonnegative_int(upgrade["level"], "upgrade.level")
                if not 1 <= level <= MAX_UPGRADE_LEVEL:
                    raise ValueError(f"Upgrade-Level muss zwischen 1 und {MAX_UPGRADE_LEVEL} liegen")
                ids = upgrade["economy_transaction_ids"]
                if not isinstance(ids, list) or len(ids) != level:
                    raise ValueError("Upgrade-Level und Economy-Transaktionen widersprechen sich")
                normalized = [_text(value, "economy_transaction_id") for value in ids]
                if len(normalized) != len(set(normalized)):
                    raise ValueError("Upgrade enthält doppelte Economy-Transaktion")
                for transaction_id in normalized:
                    if transaction_id in transaction_ids:
                        raise ValueError("Economy-Transaktion darf nur einem Upgrade-Level gehören")
                    transaction_ids.add(transaction_id)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "contract_version": self.contract_version,
            "revision": self.revision,
            "properties": deepcopy(self.properties),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PropertyUpgradeState":
        state = cls(
            contract_version=data.get("contract_version", ""),
            revision=data.get("revision", 0),
            properties=deepcopy(data.get("properties", {})),
        )
        state.validate()
        return state
