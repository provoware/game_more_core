from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class IncidentCommitResult:
    event: EventState
    incidents: IncidentState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


def build_incident_catalog(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if manifest.get("version") != "0.8.3-b1":
        raise ValueError("Incident-Manifest besitzt unerwartete Version")
    if manifest.get("trigger_phases") != ["live"]:
        raise ValueError("0.8.3-B1 erlaubt Incidents ausschließlich aus live")
    result: dict[str, dict[str, Any]] = {}
    response_ids: set[str] = set()
    for item in manifest.get("incident_types", []):
        incident_type = item.get("incident_type")
        if not isinstance(incident_type, str) or not incident_type or incident_type in result:
            raise ValueError("Incident-Typen müssen eindeutige IDs besitzen")
        base = item.get("base_severity")
        if isinstance(base, bool) or not isinstance(base, int) or not 1 <= base <= 5:
            raise ValueError("base_severity muss zwischen 1 und 5 liegen")
        responses: dict[str, dict[str, Any]] = {}
        for response in item.get("responses", []):
            response_id = response.get("response_id")
            if not isinstance(response_id, str) or not response_id or response_id in response_ids:
                raise ValueError("Response-IDs müssen global eindeutig sein")
            if response.get("target_phase") not in {"live", "teardown", "cancelled"}:
                raise ValueError("Incident-Response besitzt ungültige Zielphase")
            effects = response.get("effects")
            required = {
                "budget_delta_cents", "reputation_delta", "crew_stress_delta",
                "stability_delta", "heat_delta",
            }
            if not isinstance(effects, dict) or set(effects) != required:
                raise ValueError("Incident-Response besitzt ungültige Effekte")
            if any(isinstance(value, bool) or not isinstance(value, int) for value in effects.values()):
                raise ValueError("Incident-Effekte müssen Ganzzahlen sein")
            response_ids.add(response_id)
            responses[response_id] = deepcopy(response)
        if len(responses) < 2:
            raise ValueError("Jeder Incident benötigt mindestens zwei Reaktionen")
        normalized = deepcopy(item)
        normalized["responses"] = responses
        result[incident_type] = normalized
    if not result:
        raise ValueError("Incident-Katalog darf nicht leer sein")
    return result


class IncidentService:
    """Atomic crisis orchestration. Consequences stay pending until 0.8.3-C settlement."""

    def __init__(self, persistence: PersistenceKernel, catalog: dict[str, dict[str, Any]], *, contract_version: str):
        self.persistence = persistence
        self.catalog = catalog
        self.contract_version = contract_version

    def open(
        self,
        incident_type: str,
        *,
        context: JournalContext,
        severity: int | None = None,
    ) -> IncidentCommitResult:
        spec = self.catalog.get(incident_type)
        if spec is None:
            raise ValueError("Unbekannter Incident-Typ")
        resolved_severity = spec["base_severity"] if severity is None else severity
        if isinstance(resolved_severity, bool) or not isinstance(resolved_severity, int) or not 1 <= resolved_severity <= 5:
            raise ValueError("severity muss Ganzzahl zwischen 1 und 5 sein")
        request = {"operation": "open", "incident_type": incident_type, "severity": resolved_severity}
        existing = self._existing(context.command_id)
        if existing is not None:
            if existing.get("payload", {}).get("request") != request:
                raise PersistenceError("Command-ID wurde mit anderem Incident-Open verwendet")
            return self._current_result((), True)

        event, incidents, state = self._load(context)
        if event.phase != "live":
            raise ValueError("Incident kann in 0.8.3-B1 nur während live eröffnet werden")
        if incidents.active is not None:
            raise ValueError("Es ist bereits ein Incident aktiv")

        updated_event = event.transition_to("crisis")
        incident_id = f"incident:{context.command_id}"
        data = incidents.to_dict()
        data["active"] = {
            "incident_id": incident_id,
            "incident_type": incident_type,
            "severity": resolved_severity,
            "status": "open",
            "phase_origin": "live",
            "response_ids": list(spec["responses"]),
            "contract_version": self.contract_version,
        }
        data["revision"] += 1
        updated_incidents = IncidentState.from_dict(data)
        return self._commit(
            request=request,
            event_before=event,
            event_after=updated_event,
            incidents_after=updated_incidents,
            incident_event_type="event.incident_started",
            incident_payload={"incident_id": incident_id, "incident_type": incident_type, "severity": resolved_severity},
            state=state,
            context=context,
        )

    def resolve(self, response_id: str, *, context: JournalContext) -> IncidentCommitResult:
        request = {"operation": "resolve", "response_id": response_id}
        existing = self._existing(context.command_id)
        if existing is not None:
            if existing.get("payload", {}).get("request") != request:
                raise PersistenceError("Command-ID wurde mit anderer Incident-Auflösung verwendet")
            return self._current_result((), True)

        event, incidents, state = self._load(context)
        if event.phase != "crisis" or incidents.active is None:
            raise ValueError("Kein aktiver Incident in crisis vorhanden")
        active = deepcopy(incidents.active)
        spec = self.catalog.get(active["incident_type"])
        if spec is None:
            raise PersistenceError("Aktiver Incident-Typ fehlt im Katalog")
        if response_id not in active["response_ids"] or response_id not in spec["responses"]:
            raise ValueError("Response ist für diesen Incident nicht erlaubt")
        response = spec["responses"][response_id]
        effects = self._scaled_effects(response["effects"], active["severity"], spec["base_severity"])
        target_phase = response["target_phase"]
        updated_event = event.transition_to(target_phase)

        data = incidents.to_dict()
        resolved_revision = data["revision"] + 1
        history_entry = {
            "incident_id": active["incident_id"],
            "incident_type": active["incident_type"],
            "severity": active["severity"],
            "status": "resolved",
            "phase_origin": active["phase_origin"],
            "response_id": response_id,
            "target_phase": target_phase,
            "effects": effects,
            "resolved_at_revision": resolved_revision,
            "contract_version": active["contract_version"],
        }
        data["history"].append(history_entry)
        data["active"] = None
        for key, value in effects.items():
            data["pending_settlement"][key] += value
        data["revision"] = resolved_revision
        updated_incidents = IncidentState.from_dict(data)
        return self._commit(
            request=request,
            event_before=event,
            event_after=updated_event,
            incidents_after=updated_incidents,
            incident_event_type="event.incident_resolved",
            incident_payload={
                "incident_id": history_entry["incident_id"],
                "incident_type": history_entry["incident_type"],
                "response_id": response_id,
                "target_phase": target_phase,
                "effects": effects,
            },
            state=state,
            context=context,
        )

    @staticmethod
    def _scaled_effects(effects: dict[str, int], severity: int, base_severity: int) -> dict[str, int]:
        return {key: round(value * severity / base_severity) for key, value in effects.items()}

    def _load(self, context: JournalContext) -> tuple[EventState, IncidentState, dict[str, Any]]:
        if context.entity_type != "event" or not context.command_id:
            raise ValueError("Incident-Commit benötigt Event-Kontext und command_id")
        state = deepcopy(self.persistence.load_state() or {})
        if "event" not in state:
            raise PersistenceError("Incident-System benötigt bestätigten Eventzustand")
        event = EventState.from_dict(state["event"])
        if context.entity_id != event.event_id:
            raise ValueError("JournalContext.entity_id passt nicht zum bestätigten Event")
        incidents = (
            IncidentState.from_dict(state["incidents"])
            if "incidents" in state
            else IncidentState(event_id=event.event_id)
        )
        if incidents.event_id != event.event_id:
            raise PersistenceError("Incident-State gehört zu anderem Event")
        return event, incidents, state

    def _existing(self, command_id: str) -> dict[str, Any] | None:
        event_id = f"{command_id}:incident"
        return next((record for record in self.persistence.read_records() if record["event_id"] == event_id), None)

    def _current_result(self, ids: tuple[str, ...], replay: bool) -> IncidentCommitResult:
        state = self.persistence.load_state() or {}
        if "event" not in state or "incidents" not in state:
            raise PersistenceError("Incident-Replay verweist auf fehlenden Zustand")
        return IncidentCommitResult(
            EventState.from_dict(state["event"]),
            IncidentState.from_dict(state["incidents"]),
            ids,
            replay,
        )

    def _commit(
        self,
        *,
        request: dict[str, Any],
        event_before: EventState,
        event_after: EventState,
        incidents_after: IncidentState,
        incident_event_type: str,
        incident_payload: dict[str, Any],
        state: dict[str, Any],
        context: JournalContext,
    ) -> IncidentCommitResult:
        state["event"] = event_after.to_dict()
        state["incidents"] = incidents_after.to_dict()
        phase_payload = {
            "event_id": event_before.event_id,
            "old_phase": event_before.phase,
            "new_phase": event_after.phase,
            "old_revision": event_before.revision,
            "new_revision": event_after.revision,
            "reason": f"event_incident:{request['operation']}",
        }
        payload = dict(incident_payload)
        payload["request"] = request
        payload["incidents"] = incidents_after.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}",
            events=[
                {"event_id": f"{context.command_id}:event", "event_type": "event.phase_changed", "payload": phase_payload},
                {"event_id": f"{context.command_id}:incident", "event_type": incident_event_type, "payload": payload},
            ],
            derived_state=state,
            context=context,
        )
        return IncidentCommitResult(event_after, incidents_after, receipt.event_ids, False)


def replay_incident_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record["event_type"] not in {"event.incident_started", "event.incident_resolved"}:
        return derived_state
    payload = record.get("payload", {})
    target = IncidentState.from_dict(payload["incidents"])
    state = deepcopy(derived_state)
    if "event" in state and EventState.from_dict(state["event"]).event_id != target.event_id:
        raise ValueError("Incident-Replay verweist auf anderes Event")
    current_raw = state.get("incidents")
    if current_raw is None:
        if target.revision != 1:
            raise ValueError("Erster Incident-Replay benötigt Revision 1")
    else:
        current = IncidentState.from_dict(current_raw)
        if target.revision != current.revision + 1:
            raise ValueError("Incident-Replay besitzt unerwartete Revision")
    state["incidents"] = target.to_dict()
    return state
