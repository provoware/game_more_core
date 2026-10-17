from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

LEGACY_SETTLEMENT_VERSION = "0.8.3-c1"
VENUE_SETTLEMENT_VERSION = "0.8.8-venue-evidence1"

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
    nonnegative_result: bool = False,
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
    elif nonnegative_result:
        # Legacy saves may contain signed reputation values. Settlement is the
        # normalization boundary: the old value remains readable, the result
        # follows the canonical ranking floor at zero.
        expected = max(0, old + delta)
        if new != expected:
            raise ValueError(f"{field} ist inkonsistent")
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
    venue_evidence: dict[str, Any] | None = None

    def validate(self) -> None:
        _text(self.event_id, "event_id")
        _text(self.settlement_id, "settlement_id")
        _text(self.contract_version, "contract_version")
        if self.contract_version not in {LEGACY_SETTLEMENT_VERSION, VENUE_SETTLEMENT_VERSION}:
            raise ValueError("Unbekannte Settlement-Vertragsversion")
        _text(self.character_id, "character_id")
        self._validate_venue_evidence()
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
        stress = _triplet(self.stress, "stress", bounded_0_100=True)
        reputation = _triplet(self.reputation, "reputation", nonnegative_result=True)

        # A receipt may not describe one set of incident consequences while
        # proving different Economy/Character deltas. This cross-binding makes
        # imported/corrupt journals fail closed during recovery.
        expected_deltas = {
            "budget_delta_cents": budget["delta"],
            "crew_stress_delta": stress["delta"],
            "reputation_delta": reputation["delta"],
        }
        for effect_key, applied_delta in expected_deltas.items():
            if self.effects[effect_key] != applied_delta:
                raise ValueError(
                    f"Settlement-Effekt {effect_key} stimmt nicht mit dem angewandten Delta überein"
                )

        self._revision_triplet(self.event_revision, "event_revision", steps=2)
        self._revision_triplet(self.economy_revision, "economy_revision", steps=1)
        self._revision_triplet(self.incident_revision, "incident_revision", steps=1)
        _int(self.revision, "revision", minimum=1)
        if self.revision != 1:
            raise ValueError("0.8.3-C1 erlaubt genau Settlement-Revision 1")

    def _validate_venue_evidence(self) -> None:
        if self.contract_version == LEGACY_SETTLEMENT_VERSION:
            if self.venue_evidence is not None:
                raise ValueError("Legacy-Settlement erlaubt keine Venue-Evidence")
            return
        evidence = self.venue_evidence
        if evidence is None:
            return
        keys = {
            "schema_version", "location_id", "owner_character_id", "audience_pull",
            "city_map_manifest_version", "property_upgrade_manifest_version",
            "property_revision", "property_upgrade_revision",
        }
        if not isinstance(evidence, dict) or set(evidence) != keys:
            raise ValueError("Venue-Evidence besitzt ungültige Felder")
        if _int(evidence["schema_version"], "venue_evidence.schema_version") != 1:
            raise ValueError("Unbekannte Venue-Evidence-Version")
        for key in ("location_id", "owner_character_id", "city_map_manifest_version",
                    "property_upgrade_manifest_version"):
            if _text(evidence[key], f"venue_evidence.{key}") != evidence[key]:
                raise ValueError("Venue-Evidence benötigt kanonische Textwerte")
        if evidence["owner_character_id"] != self.character_id:
            raise ValueError("Venue-Evidence gehört anderem Character")
        if not 0 <= _int(evidence["audience_pull"], "venue_evidence.audience_pull") <= 100:
            raise ValueError("Venue-Publikumskraft muss in 0..100 liegen")
        for key in ("property_revision", "property_upgrade_revision"):
            _int(evidence[key], f"venue_evidence.{key}", minimum=0)

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
        data = {
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
        if self.contract_version == VENUE_SETTLEMENT_VERSION:
            data["venue_evidence"] = deepcopy(self.venue_evidence)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SettlementState":
        version = data["contract_version"]
        if (version == VENUE_SETTLEMENT_VERSION) != ("venue_evidence" in data):
            raise ValueError("Venue-Evidence-Feld passt nicht zur Settlement-Vertragsversion")
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
            venue_evidence=deepcopy(data.get("venue_evidence")),
        )
        state.validate()
        return state
