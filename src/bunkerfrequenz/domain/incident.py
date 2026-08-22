from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

INCIDENT_STATUSES = ("open", "resolved")
TARGET_PHASES = ("live", "teardown", "cancelled")
_EFFECT_FIELDS = {
    "budget_delta_cents",
    "reputation_delta",
    "crew_stress_delta",
    "stability_delta",
    "heat_delta",
}


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} muss nicht leerer Text sein")
    return value.strip()


def _int(value: Any, field_name: str, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field_name} muss eine Ganzzahl >= {minimum} sein")
    if maximum is not None and value > maximum:
        raise ValueError(f"{field_name} muss <= {maximum} sein")
    return value


def _validate_effects(value: dict[str, Any], *, bounded: bool) -> None:
    if not isinstance(value, dict) or set(value) != _EFFECT_FIELDS:
        raise ValueError("Incident-Effekte besitzen ungültige Felder")
    for key in _EFFECT_FIELDS:
        raw = value[key]
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise ValueError(f"Incident-Effekt {key} muss Ganzzahl sein")
    if bounded:
        if abs(value["reputation_delta"]) > 100 or abs(value["crew_stress_delta"]) > 100:
            raise ValueError("Incident-Reputation/Stress außerhalb -100..100")
        if abs(value["stability_delta"]) > 100 or abs(value["heat_delta"]) > 100:
            raise ValueError("Incident-Stabilität/Heat außerhalb -100..100")


def _validate_active(value: dict[str, Any]) -> None:
    required = {
        "incident_id",
        "incident_type",
        "severity",
        "status",
        "phase_origin",
        "response_ids",
        "contract_version",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("Aktiver Incident besitzt ungültige Felder")
    _text(value["incident_id"], "active.incident_id")
    _text(value["incident_type"], "active.incident_type")
    _int(value["severity"], "active.severity", 1, 5)
    if value["status"] != "open":
        raise ValueError("Aktiver Incident muss status=open besitzen")
    if value["phase_origin"] != "live":
        raise ValueError("0.8.3-B1 erlaubt Incidents nur aus live")
    if not isinstance(value["response_ids"], list) or not value["response_ids"]:
        raise ValueError("Aktiver Incident benötigt response_ids")
    normalized = [_text(item, "active.response_id") for item in value["response_ids"]]
    if len(normalized) != len(set(normalized)):
        raise ValueError("response_ids müssen eindeutig sein")
    _text(value["contract_version"], "active.contract_version")


def _validate_resolved(value: dict[str, Any]) -> None:
    required = {
        "incident_id",
        "incident_type",
        "severity",
        "status",
        "phase_origin",
        "response_id",
        "target_phase",
        "effects",
        "resolved_at_revision",
        "contract_version",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError("Aufgelöster Incident besitzt ungültige Felder")
    _text(value["incident_id"], "resolved.incident_id")
    _text(value["incident_type"], "resolved.incident_type")
    _int(value["severity"], "resolved.severity", 1, 5)
    if value["status"] != "resolved":
        raise ValueError("Historischer Incident muss status=resolved besitzen")
    if value["phase_origin"] != "live":
        raise ValueError("phase_origin muss live sein")
    _text(value["response_id"], "resolved.response_id")
    if value["target_phase"] not in TARGET_PHASES:
        raise ValueError("resolved.target_phase ist unbekannt")
    _validate_effects(value["effects"], bounded=True)
    _int(value["resolved_at_revision"], "resolved.resolved_at_revision", 1)
    _text(value["contract_version"], "resolved.contract_version")


@dataclass(slots=True)
class IncidentState:
    event_id: str
    active: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    pending_settlement: dict[str, int] = field(
        default_factory=lambda: {
            "budget_delta_cents": 0,
            "reputation_delta": 0,
            "crew_stress_delta": 0,
            "stability_delta": 0,
            "heat_delta": 0,
        }
    )
    revision: int = 0

    def validate(self) -> None:
        _text(self.event_id, "event_id")
        if self.active is not None:
            _validate_active(self.active)
        if not isinstance(self.history, list) or not all(isinstance(item, dict) for item in self.history):
            raise ValueError("history muss Liste von Objekten sein")
        for item in self.history:
            _validate_resolved(item)
        ids = [item["incident_id"] for item in self.history]
        if self.active is not None:
            ids.append(self.active["incident_id"])
        if len(ids) != len(set(ids)):
            raise ValueError("Incident-IDs müssen eindeutig sein")
        # Einzelne Incident-Effekte sind fachlich begrenzt; kumulierte Settlement-
        # Summen dürfen mehrere bestätigte Incidents ohne künstliche ±100-Grenze addieren.
        _validate_effects(self.pending_settlement, bounded=False)
        _int(self.revision, "revision", 0)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "event_id": self.event_id,
            "active": None if self.active is None else deepcopy(self.active),
            "history": deepcopy(self.history),
            "pending_settlement": dict(self.pending_settlement),
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IncidentState":
        state = cls(
            event_id=data["event_id"],
            active=None if data.get("active") is None else deepcopy(data["active"]),
            history=deepcopy(data.get("history", [])),
            pending_settlement=dict(data.get("pending_settlement", {})),
            revision=data.get("revision", 0),
        )
        state.validate()
        return state
