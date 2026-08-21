from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

PHASES = (
    "draft",
    "planning",
    "procurement",
    "transport",
    "setup",
    "soundcheck",
    "live",
    "crisis",
    "teardown",
    "settlement",
    "completed",
    "cancelled",
)

SAFETY_STATUSES = ("unreviewed", "cleared", "restricted", "blocked")
ACCESS_STATUSES = ("unverified", "authorized", "public", "fictionalized")

PHASE_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"planning", "cancelled"}),
    "planning": frozenset({"procurement", "cancelled"}),
    "procurement": frozenset({"planning", "transport", "cancelled"}),
    "transport": frozenset({"setup", "cancelled"}),
    "setup": frozenset({"soundcheck", "crisis", "cancelled"}),
    "soundcheck": frozenset({"live", "crisis", "cancelled"}),
    "live": frozenset({"crisis", "teardown"}),
    "crisis": frozenset({"live", "teardown", "cancelled"}),
    "teardown": frozenset({"settlement"}),
    "settlement": frozenset({"completed"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
}

PHYSICAL_PHASES = frozenset({"transport", "setup", "soundcheck", "live", "crisis", "teardown", "settlement"})


def _require_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} muss nicht leerer Text sein")
    return value.strip()


def _require_int(value: Any, field_name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{field_name} muss eine Ganzzahl >= {minimum} sein")
    return value


def _validate_unique(items: list[dict[str, Any]], key: str, label: str) -> None:
    values = [item.get(key) for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} enthält doppelte {key}")


def _validate_time_window(value: dict[str, Any] | None) -> None:
    if value is None:
        return
    if set(value) != {"start_local", "end_local", "timezone"}:
        raise ValueError("time_window benötigt start_local, end_local und timezone")
    start_raw = _require_text(value["start_local"], "time_window.start_local")
    end_raw = _require_text(value["end_local"], "time_window.end_local")
    _require_text(value["timezone"], "time_window.timezone")
    try:
        start = datetime.fromisoformat(start_raw)
        end = datetime.fromisoformat(end_raw)
    except ValueError as exc:
        raise ValueError("time_window benötigt ISO-8601-Zeitpunkte") from exc
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("time_window benötigt Zeitpunkte mit UTC-Offset")
    if end <= start:
        raise ValueError("time_window.end_local muss nach start_local liegen")


def _validate_location(value: dict[str, Any] | None) -> None:
    if value is None:
        return
    required = {"location_id", "display_name", "region", "access_status"}
    if set(value) != required:
        raise ValueError("location besitzt ungültige Felder")
    _require_text(value["location_id"], "location.location_id")
    _require_text(value["display_name"], "location.display_name")
    _require_text(value["region"], "location.region")
    if value["access_status"] not in ACCESS_STATUSES:
        raise ValueError("location.access_status ist unbekannt")


def _validate_acts(items: list[dict[str, Any]]) -> None:
    _validate_unique(items, "act_id", "acts")
    allowed_statuses = {"planned", "confirmed", "cancelled"}
    for item in items:
        if set(item) != {"act_id", "display_name", "status"}:
            raise ValueError("Act besitzt ungültige Felder")
        _require_text(item["act_id"], "act.act_id")
        _require_text(item["display_name"], "act.display_name")
        if item["status"] not in allowed_statuses:
            raise ValueError("act.status ist unbekannt")


def _validate_crew(items: list[dict[str, Any]]) -> None:
    _validate_unique(items, "character_id", "crew")
    allowed_statuses = {"assigned", "confirmed", "unavailable"}
    for item in items:
        if set(item) != {"character_id", "role", "status"}:
            raise ValueError("Crew-Zuordnung besitzt ungültige Felder")
        _require_text(item["character_id"], "crew.character_id")
        _require_text(item["role"], "crew.role")
        if item["status"] not in allowed_statuses:
            raise ValueError("crew.status ist unbekannt")


def _validate_equipment(items: list[dict[str, Any]]) -> None:
    _validate_unique(items, "equipment_id", "equipment")
    allowed_statuses = {"required", "reserved", "ready", "missing"}
    for item in items:
        if set(item) != {"equipment_id", "label", "quantity", "status"}:
            raise ValueError("Equipment-Anforderung besitzt ungültige Felder")
        _require_text(item["equipment_id"], "equipment.equipment_id")
        _require_text(item["label"], "equipment.label")
        _require_int(item["quantity"], "equipment.quantity", minimum=1)
        if item["status"] not in allowed_statuses:
            raise ValueError("equipment.status ist unbekannt")


@dataclass(slots=True)
class EventState:
    event_id: str
    display_name: str
    location: dict[str, Any] | None = None
    budget_cents: int = 0
    acts: list[dict[str, Any]] = field(default_factory=list)
    crew: list[dict[str, Any]] = field(default_factory=list)
    equipment: list[dict[str, Any]] = field(default_factory=list)
    time_window: dict[str, Any] | None = None
    safety_status: str = "unreviewed"
    phase: str = "draft"
    revision: int = 0

    def validate(self) -> None:
        _require_text(self.event_id, "event_id")
        _require_text(self.display_name, "display_name")
        _validate_location(self.location)
        _require_int(self.budget_cents, "budget_cents")
        if not isinstance(self.acts, list) or not all(isinstance(item, dict) for item in self.acts):
            raise ValueError("acts muss eine Liste von Objekten sein")
        if not isinstance(self.crew, list) or not all(isinstance(item, dict) for item in self.crew):
            raise ValueError("crew muss eine Liste von Objekten sein")
        if not isinstance(self.equipment, list) or not all(isinstance(item, dict) for item in self.equipment):
            raise ValueError("equipment muss eine Liste von Objekten sein")
        _validate_acts(self.acts)
        _validate_crew(self.crew)
        _validate_equipment(self.equipment)
        _validate_time_window(self.time_window)
        if self.safety_status not in SAFETY_STATUSES:
            raise ValueError("safety_status ist unbekannt")
        if self.phase not in PHASES:
            raise ValueError("phase ist unbekannt")
        _require_int(self.revision, "revision")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "event_id": self.event_id,
            "display_name": self.display_name,
            "location": None if self.location is None else dict(self.location),
            "budget_cents": self.budget_cents,
            "acts": [dict(item) for item in self.acts],
            "crew": [dict(item) for item in self.crew],
            "equipment": [dict(item) for item in self.equipment],
            "time_window": None if self.time_window is None else dict(self.time_window),
            "safety_status": self.safety_status,
            "phase": self.phase,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EventState":
        state = cls(
            event_id=data["event_id"],
            display_name=data["display_name"],
            location=None if data.get("location") is None else dict(data["location"]),
            budget_cents=data.get("budget_cents", 0),
            acts=[dict(item) for item in data.get("acts", [])],
            crew=[dict(item) for item in data.get("crew", [])],
            equipment=[dict(item) for item in data.get("equipment", [])],
            time_window=None if data.get("time_window") is None else dict(data["time_window"]),
            safety_status=data.get("safety_status", "unreviewed"),
            phase=data.get("phase", "draft"),
            revision=data.get("revision", 0),
        )
        state.validate()
        return state

    def transition_to(self, new_phase: str) -> "EventState":
        if new_phase not in PHASES:
            raise ValueError(f"Unbekannte Eventphase: {new_phase}")
        if new_phase not in PHASE_TRANSITIONS[self.phase]:
            raise ValueError(f"Ungültiger Phasenwechsel: {self.phase} -> {new_phase}")
        if new_phase in PHYSICAL_PHASES:
            if self.location is None:
                raise ValueError("Physische Eventphase benötigt einen Ort")
            if self.location["access_status"] == "unverified":
                raise ValueError("Physische Eventphase benötigt verifizierten Ortszugang")
            if self.time_window is None:
                raise ValueError("Physische Eventphase benötigt ein Zeitfenster")
            if self.safety_status != "cleared":
                raise ValueError("Physische Eventphase benötigt safety_status=cleared")
        data = self.to_dict()
        data["phase"] = new_phase
        data["revision"] = self.revision + 1
        return EventState.from_dict(data)
