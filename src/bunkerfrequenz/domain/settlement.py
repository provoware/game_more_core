from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

_EFFECT_KEYS = {
    "budget_delta_cents",
    "reputation_delta",
    "crew_stress_delta",
    "stability_delta",
    "heat_delta",
}


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss nicht leerer Text sein")
    return value.strip()


def _int(value: Any, field: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} muss Ganzzahl sein")
    if minimum is not None and value < minimum:
        raise ValueError(f"{field} muss >= {minimum} sein")
    return value


def _triplet(
    value: Any,
    field: str,
    *,
    bounded_0_100: bool = False,
    nonnegative: bool = False,
) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != {"old", "delta", "new"}:
        raise ValueError(f"{field} benötigt old/delta/new")
    old = _int(value["old"], f"{field}.old")
    delta = _int(value["delta"], f"{field}.delta")
    new = _int(value["new"], f"{field}.new")
    if bounded_0_100:
        expected = min(100, max(0, old + delta))
        if not 0 <= old <= 100 or new != expected:
            raise ValueError(f"{field} ist außerhalb 0..100 oder inkonsistent")
    elif nonnegative:
        expected = max(0, old + delta)
        if old < 0 or new != expected:
            raise ValueError(f"{field} ist negativ oder inkonsistent")
    elif new != old + delta:
        raise ValueError(f"{field} ist inkonsistent")
    return {"old": old, "delta": delta, "new": new}


@dataclass(slots=True)
class SettlementState:
    event_id: str
    settlement_id: str
    contract_version: str
    incident_ids: list[str]
    effects: dict[str, int]
    budget: dict[str, int]
    character_id: str
    stress: dict[str, int]
    reputation: dict[str, int]
    event_revision: dict[str, int]
    economy_revision: dict[str, int]
    incident_revision: dict[str, int]
    status: str = "completed"
    revision: int = 1

    def validate(self) -> None:
        _text(self.event_id, "event_id")
        _text(self.settlement_id, "settlement_id")
        _text(self.contract_version, "contract_version")
        _text(self.character_id, "character_id")
        if self.status != "completed":
            raise ValueError("SettlementState.status muss completed sein")
        if not isinstance(self.incident_ids, list):
            raise ValueError("incident_ids muss Liste sein")
        normalized = [_text(value, "incident_id") for value in self.incident_ids]
        if len(normalized) != len(set(normalized)):
            raise ValueError("incident_ids müssen eindeutig sein")
        if not isinstance(self.effects, dict) or set(self.effects) != _EFFECT_KEYS:
            raise ValueError("Settlement-Effekte besitzen ungültige Felder")
        for key in _EFFECT_KEYS:
            _int(self.effects[key], f"effects.{key}")
        budget = _triplet(self.budget, "budget")
        if budget["old"] < 0 or budget["new"] < 0:
            raise ValueError("Settlement-Budget darf nicht negativ sein")
        _triplet(self.stress, "stress", bounded_0_100=True)
        _triplet(self.reputation, "reputation", nonnegative=True)
        self._revision_triplet(self.event_revision, "event_revision", steps=2)
        self._revision_triplet(self.economy_revision, "economy_revision", steps=1)
        self._revision_triplet(self.incident_revision, "incident_revision", steps=1)
        _int(self.revision, "revision", minimum=1)
        if self.revision != 1:
            raise ValueError("0.8.3-C1 erlaubt genau Settlement-Revision 1")

    @staticmethod
    def _revision_triplet(value: Any, field: str, *, steps: int) -> None:
        if not isinstance(value, dict) or set(value) != {"old", "new"}:
            raise ValueError(f"{field} benötigt old/new")
        old = _int(value["old"], f"{field}.old", minimum=0)
        new = _int(value["new"], f"{field}.new", minimum=0)
        if new != old + steps:
            raise ValueError(f"{field} muss exakt um {steps} steigen")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "event_id": self.event_id,
            "settlement_id": self.settlement_id,
            "contract_version": self.contract_version,
            "incident_ids": list(self.incident_ids),
            "effects": dict(self.effects),
            "budget": dict(self.budget),
            "character_id": self.character_id,
            "stress": dict(self.stress),
            "reputation": dict(self.reputation),
            "event_revision": dict(self.event_revision),
            "economy_revision": dict(self.economy_revision),
            "incident_revision": dict(self.incident_revision),
            "status": self.status,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SettlementState":
        state = cls(
            event_id=data["event_id"],
            settlement_id=data["settlement_id"],
            contract_version=data["contract_version"],
            incident_ids=list(data.get("incident_ids", [])),
            effects=deepcopy(data["effects"]),
            budget=deepcopy(data["budget"]),
            character_id=data["character_id"],
            stress=deepcopy(data["stress"]),
            reputation=deepcopy(data["reputation"]),
            event_revision=deepcopy(data["event_revision"]),
            economy_revision=deepcopy(data["economy_revision"]),
            incident_revision=deepcopy(data["incident_revision"]),
            status=data.get("status", "completed"),
            revision=data.get("revision", 1),
        )
        state.validate()
        return state
