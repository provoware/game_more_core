from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from bunkerfrequenz.application.district_service import DistrictCommitResult, DistrictService
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError


@dataclass(frozen=True, slots=True)
class DistrictWorldEventResult:
    event_id: str | None
    title_key: str | None
    body_key: str | None
    event_instance_id: str | None
    district_result: DistrictCommitResult
    triggered: bool = True
    no_event_reason: str | None = None


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
        if policy.get("effects_apply_only_after_confirmed_resolution") is not True:
            raise ValueError("District-Event-Effekte benötigen bestätigte Auflösung")
        events = self.manifest.get("events")
        if not isinstance(events, list) or not events:
            raise ValueError("District-Event-Katalog ist leer")
        self.events = tuple(deepcopy(events))
        self._validate_catalog(selection)

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
                return DistrictWorldEventResult(
                    None,
                    None,
                    None,
                    None,
                    DistrictCommitResult(
                        state=state,
                        committed_event_ids=(),
                        idempotent_replay=False,
                        applied=False,
                        metadata={
                            "district_id": district_id,
                            "source_type": "district_event",
                            "source_id": f"district-event:{district_id}:{trigger_id}",
                            "reason": "no_eligible_event",
                        },
                    ),
                    triggered=False,
                    no_event_reason="no_eligible_event",
                )
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

    def _validate_catalog(self, selection: Mapping[str, Any]) -> None:
        effect_contract = self.manifest.get("effect_contract")
        if not isinstance(effect_contract, Mapping):
            raise ValueError("District-Event-Manifest benötigt effect_contract")
        metrics = effect_contract.get("metrics")
        expected_metrics = list(self.district_service.manifest.get("metrics", ()))
        if metrics != expected_metrics:
            raise ValueError("District-Event-Metriken weichen vom District-State-Vertrag ab")
        minimum = effect_contract.get("per_event_delta_minimum")
        maximum = effect_contract.get("per_event_delta_maximum")
        if (
            isinstance(minimum, bool)
            or not isinstance(minimum, int)
            or isinstance(maximum, bool)
            or not isinstance(maximum, int)
            or minimum > maximum
        ):
            raise ValueError("District-Event-Effektgrenzen sind ungültig")
        if effect_contract.get("district_bounds_remain") != self.district_service.manifest.get("bounds"):
            raise ValueError("District-Event-Grenzen weichen vom District-State-Vertrag ab")

        expected_weight = selection.get("weight_total")
        if isinstance(expected_weight, bool) or not isinstance(expected_weight, int) or expected_weight <= 0:
            raise ValueError("District-Event-Gesamtgewicht muss positive Ganzzahl sein")

        seen_ids: set[str] = set()
        total_weight = 0
        for index, event in enumerate(self.events):
            if not isinstance(event, Mapping):
                raise ValueError(f"events[{index}] muss Objekt sein")
            event_id = self._text(event.get("event_id"), f"events[{index}].event_id")
            if event_id in seen_ids:
                raise ValueError(f"events[{index}].event_id '{event_id}' ist doppelt")
            seen_ids.add(event_id)
            self._text(event.get("title_key"), f"events[{index}]({event_id}).title_key")
            self._text(event.get("body_key"), f"events[{index}]({event_id}).body_key")

            weight = event.get("weight")
            if isinstance(weight, bool) or not isinstance(weight, int) or weight <= 0:
                raise ValueError(f"events[{index}]({event_id}).weight muss positive Ganzzahl sein")
            total_weight += weight

            requirements = event.get("requirements", {})
            if not isinstance(requirements, Mapping):
                raise ValueError(f"events[{index}]({event_id}).requirements muss Objekt sein")
            for key, value in requirements.items():
                field = f"events[{index}]({event_id}).requirements.{key}"
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"{field} muss Ganzzahl sein")
                if key.startswith("minimum_"):
                    metric = key.removeprefix("minimum_")
                elif key.startswith("maximum_"):
                    metric = key.removeprefix("maximum_")
                else:
                    raise ValueError(f"{field} ist unbekannte Voraussetzung")
                if metric not in expected_metrics:
                    raise ValueError(f"{field} verweist auf unbekannte Metrik '{metric}'")

            effects = event.get("effects")
            if not isinstance(effects, Mapping) or set(effects) != set(expected_metrics):
                raise ValueError(
                    f"events[{index}]({event_id}).effects muss exakt alle District-Metriken enthalten"
                )
            for metric, value in effects.items():
                field = f"events[{index}]({event_id}).effects.{metric}"
                if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
                    raise ValueError(f"{field} liegt außerhalb des Vertrags [{minimum}, {maximum}]")

        if total_weight != expected_weight:
            raise ValueError(
                f"District-Event-Kataloggewicht {total_weight} weicht von selection.weight_total {expected_weight} ab"
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
