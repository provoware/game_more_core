from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} muss nicht-leerer Text sein")
    return value.strip()


def _nonnegative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} muss eine nichtnegative Ganzzahl sein")
    return value


def _positive_int(value: Any, field_name: str) -> int:
    result = _nonnegative_int(value, field_name)
    if result < 1:
        raise ValueError(f"{field_name} muss mindestens 1 sein")
    return result


@dataclass(slots=True)
class PropertyState:
    contract_version: str
    revision: int = 0
    owned: dict[str, dict[str, Any]] = field(default_factory=dict)

    def validate(self) -> None:
        _text(self.contract_version, "contract_version")
        _nonnegative_int(self.revision, "revision")
        if not isinstance(self.owned, dict):
            raise ValueError("owned muss ein Mapping sein")
        transaction_ids: set[str] = set()
        for location_id, record in self.owned.items():
            location_id = _text(location_id, "location_id")
            if not isinstance(record, dict):
                raise ValueError("Property-Record muss Objekt sein")
            required = {
                "location_id",
                "owner_character_id",
                "purchase_price_cents",
                "economy_transaction_id",
                "event_id",
            }
            if set(record) != required:
                raise ValueError(f"Property {location_id} besitzt falsche Felder")
            if _text(record["location_id"], "record.location_id") != location_id:
                raise ValueError("Property-Key und record.location_id widersprechen sich")
            _text(record["owner_character_id"], "owner_character_id")
            _positive_int(record["purchase_price_cents"], "purchase_price_cents")
            transaction_id = _text(record["economy_transaction_id"], "economy_transaction_id")
            if transaction_id in transaction_ids:
                raise ValueError("Economy-Transaktion darf nicht mehreren Properties gehören")
            transaction_ids.add(transaction_id)
            _text(record["event_id"], "event_id")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "contract_version": self.contract_version,
            "revision": self.revision,
            "owned": deepcopy(self.owned),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PropertyState":
        state = cls(
            contract_version=data.get("contract_version", ""),
            revision=data.get("revision", 0),
            owned=deepcopy(data.get("owned", {})),
        )
        state.validate()
        return state
