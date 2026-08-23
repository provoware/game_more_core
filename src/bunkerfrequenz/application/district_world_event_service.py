from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from bunkerfrequenz.application.district_service import DistrictCommitResult, DistrictService
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError


@dataclass(frozen=True, slots=True)
class DistrictWorldEventResult:
    event_id: str
    title_key: str
    body_key: str
    event_instance_id: str
    district_result: DistrictCommitResult


class DistrictWorldEventService:
    """Select one catalogued district event deterministically and reuse DistrictService for persistence."""

    def __init__(self, district_service: DistrictService, event_manifest: Mapping[str, Any]) -> None:
        self.district_service = district_service
        self.manifest = deepcopy(dict(event_manifest))
        self.version = self._text(self.manifest.get("version"), "DISTRICT_EVENT_MANIFEST.version")
        if self.manifest.get("district_state_manifest_version") != district_service.version:
            raise ValueError("District-Event- und District-State-Vertrag passen nicht zusammen")
        selection = self.manifest.get("selection")
        if not isinstance(selection, Mapping):
            raise ValueError("District-Event-Manifest benötigt selection")
        if selection.get("method") != "sha256_stable_weighted":
            raise ValueError("District-Events benötigen sha256_stable_weighted")
        if selection.get("seed_fields") != ["world_seed", "district_id", "trigger_id"]:
            raise ValueError("District-Event-Seedfelder weichen vom Vertrag ab")
        if selection.get("system_time_as_seed") is not False or selection.get("reroll_on_reload") is not False:
            raise ValueError("District-Events dürfen weder Systemzeit noch Reload-Reroll verwenden")
        policy = self.manifest.get("activation_policy")
        if not isinstance(policy, Mapping):
            raise ValueError("District-Event-Manifest benötigt activation_policy")
        if policy.get("maximum_active_instances_per_context") != 1:
            raise ValueError("District-Event-Kontext erlaubt exakt eine aktive Instanz")
        if policy.get("client_can_activate") is not False or policy.get("client_can_supply_effects") is not False:
            raise ValueError("Client darf District-Events weder aktivieren noch Effekte liefern")
        events = self.manifest.get("events")
        if not isinstance(events, list) or not events:
            raise ValueError("District-Event-Katalog ist leer")
        self.events = tuple(deepcopy(events))

    def trigger(
        self,
        *,
        world_seed: str,
        district_id: str,
        trigger_id: str,
        context: JournalContext,
    ) -> DistrictWorldEventResult:
        world_seed = self._text(world_seed, "world_seed")
        district_id = self._text(district_id, "district_id")
        trigger_id = self._text(trigger_id, "trigger_id")
        if district_id not in self.district_service.district_ids:
            raise ValueError("Unbekannter District für Welt-Ereignis")
        if context.entity_type != "district" or context.entity_id != district_id:
            raise ValueError("District-Event benötigt passenden District-Kontext")

        source_prefix = f"district-event:{district_id}:{trigger_id}:"
        replay_event_id = self._existing_event_id(source_prefix)
        if replay_event_id is None:
            state = self.district_service.current_state()
            metrics = state.metrics[district_id]
            eligible = [event for event in self.events if self._requirements_met(event, metrics)]
            if not eligible:
                raise PersistenceError("Für diesen District-Kontext ist kein katalogisiertes Ereignis zulässig")
            event = self._select(eligible, world_seed=world_seed, district_id=district_id, trigger_id=trigger_id)
        else:
            event = self._event_by_id(replay_event_id)

        event_instance_id = f"{source_prefix}{event['event_id']}"
        result = self.district_service._apply(
            source_type="district_event",
            source_id=event_instance_id,
            district_id=district_id,
            requested_deltas=event["effects"],
            context=context,
        )
        return DistrictWorldEventResult(
            event["event_id"],
            event["title_key"],
            event["body_key"],
            event_instance_id,
            result,
        )

    def _existing_event_id(self, source_prefix: str) -> str | None:
        state = self.district_service.current_state()
        matches = [source for source in state.applied_sources if source.startswith(source_prefix)]
        if not matches:
            return None
        if len(matches) != 1:
            raise PersistenceError("District-Event-Trigger besitzt mehr als eine bestätigte Instanz")
        event_id = matches[0][len(source_prefix):]
        if not event_id:
            raise PersistenceError("Bestätigte District-Event-Quelle besitzt keine Event-ID")
        return event_id

    def _event_by_id(self, event_id: str) -> Mapping[str, Any]:
        event = next((item for item in self.events if item.get("event_id") == event_id), None)
        if event is None:
            raise PersistenceError("Bestätigtes District-Event fehlt im aktuellen Katalog")
        return event

    def _select(
        self,
        eligible: list[Mapping[str, Any]],
        *,
        world_seed: str,
        district_id: str,
        trigger_id: str,
    ) -> Mapping[str, Any]:
        weighted: list[tuple[Mapping[str, Any], int]] = []
        total = 0
        for event in eligible:
            weight = event.get("weight")
            if isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0:
                raise ValueError("District-Event-Gewicht muss positive Ganzzahl sein")
            total += weight
            weighted.append((event, weight))
        digest = hashlib.sha256("\x1f".join((world_seed, district_id, trigger_id)).encode("utf-8")).digest()
        draw = int.from_bytes(digest[:8], "big") % total
        cursor = 0
        for event, weight in weighted:
            cursor += weight
            if draw < cursor:
                return event
        raise RuntimeError("District-Event-Auswahl konnte keinen Katalogeintrag bestimmen")

    @staticmethod
    def _requirements_met(event: Mapping[str, Any], metrics: Mapping[str, int]) -> bool:
        requirements = event.get("requirements", {})
        if not isinstance(requirements, Mapping):
            raise ValueError("District-Event-requirements muss Objekt sein")
        for key, value in requirements.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError("District-Event-Voraussetzung muss Ganzzahl sein")
            if key.startswith("minimum_"):
                metric = key.removeprefix("minimum_")
                if metric not in metrics or metrics[metric] < value:
                    return False
            elif key.startswith("maximum_"):
                metric = key.removeprefix("maximum_")
                if metric not in metrics or metrics[metric] > value:
                    return False
            else:
                raise ValueError("Unbekannte District-Event-Voraussetzung")
        return True

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} muss nicht-leerer Text sein")
        return value.strip()
