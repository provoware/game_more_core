from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.domain.district import DISTRICT_METRICS, DistrictState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class DistrictCommitResult:
    state: DistrictState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool
    applied: bool
    metadata: dict[str, Any]


class DistrictService:
    """Persist district metrics only from already confirmed gameplay records."""

    def __init__(
        self,
        persistence: PersistenceKernel,
        district_manifest: Mapping[str, Any],
        city_map_manifest: Mapping[str, Any],
    ) -> None:
        self.persistence = persistence
        self.manifest = deepcopy(dict(district_manifest))
        self.city_map = deepcopy(dict(city_map_manifest))
        self.version = self._text(self.manifest.get("version"), "DISTRICT_STATE_MANIFEST.version")
        if self.manifest.get("state_block") != "districts":
            raise ValueError("District-Manifest besitzt falschen state_block")
        if self.city_map.get("version") != self.manifest.get("city_map_manifest_version"):
            raise ValueError("District- und City-Map-Vertrag passen nicht zusammen")
        if tuple(self.manifest.get("metrics", ())) != DISTRICT_METRICS:
            raise ValueError("District-Metrikvertrag weicht von der Runtime ab")
        bounds = self.manifest.get("bounds")
        if bounds != {"minimum": 0, "maximum": 100}:
            raise ValueError("District-Grenzen müssen 0..100 sein")
        source_policy = self.manifest.get("source_policy")
        if not isinstance(source_policy, Mapping):
            raise ValueError("District-Manifest benötigt source_policy")
        if source_policy.get("client_metric_writes") is not False:
            raise ValueError("Client darf District-Metriken nicht direkt schreiben")
        if source_policy.get("system_time_as_authority") is not False:
            raise ValueError("Systemzeit darf keine District-Autorität sein")

        defaults = self.city_map.get("district_metric_defaults")
        districts = self.city_map.get("districts")
        locations = self.city_map.get("locations")
        if not isinstance(defaults, Mapping) or set(defaults) != set(DISTRICT_METRICS):
            raise ValueError("City-Map besitzt ungültige District-Defaults")
        if not isinstance(districts, list) or not districts:
            raise ValueError("City-Map besitzt keine Bezirke")
        if not isinstance(locations, list):
            raise ValueError("City-Map besitzt ungültige Orte")
        self.defaults = {key: self._metric(defaults[key], f"defaults.{key}") for key in DISTRICT_METRICS}
        self.district_ids = tuple(self._text(item.get("district_id"), "district_id") for item in districts)
        if len(self.district_ids) != len(set(self.district_ids)):
            raise ValueError("City-Map besitzt doppelte District-IDs")
        self.location_to_district: dict[str, str] = {}
        for item in locations:
            location_id = self._text(item.get("location_id"), "location_id")
            district_id = self._text(item.get("district_id"), f"{location_id}.district_id")
            if district_id not in self.district_ids:
                raise ValueError("City-Map-Ort verweist auf unbekannten Bezirk")
            if location_id in self.location_to_district:
                raise ValueError("City-Map besitzt doppelte Location-ID")
            self.location_to_district[location_id] = district_id
        aliases = self.manifest.get("location_district_aliases", {})
        if not isinstance(aliases, Mapping):
            raise ValueError("location_district_aliases muss Objekt sein")
        for location_id, district_id in aliases.items():
            location_id = self._text(location_id, "alias.location_id")
            district_id = self._text(district_id, f"alias.{location_id}")
            if district_id not in self.district_ids:
                raise ValueError("District-Alias verweist auf unbekannten Bezirk")
            self.location_to_district.setdefault(location_id, district_id)

        street_mapping = self.manifest.get("street_mapping")
        if not isinstance(street_mapping, Mapping) or set(street_mapping) != {"positive", "neutral", "negative"}:
            raise ValueError("street_mapping muss positive/neutral/negative enthalten")
        self.street_mapping: dict[str, dict[str, int]] = {}
        for polarity, deltas in street_mapping.items():
            self.street_mapping[polarity] = self._deltas(deltas, f"street_mapping.{polarity}")

    def current_state(self) -> DistrictState:
        raw = (self.persistence.load_state() or {}).get("districts")
        if raw is None:
            return DistrictState.from_city_map(
                contract_version=self.version,
                district_ids=self.district_ids,
                defaults=self.defaults,
            )
        if not isinstance(raw, Mapping):
            raise PersistenceError("District-State ist beschädigt")
        state = DistrictState.from_dict(raw)
        self._validate_state_contract(state)
        return state

    def apply_confirmed_settlement(self, *, context: JournalContext) -> DistrictCommitResult:
        if context.entity_type != "event" or not context.entity_id:
            raise ValueError("District-Settlement benötigt Event-Kontext")
        save = deepcopy(self.persistence.load_state() or {})
        raw_event = save.get("event")
        raw_settlement = save.get("settlement")
        if not isinstance(raw_event, dict) or not isinstance(raw_settlement, dict):
            raise PersistenceError("District-Folge benötigt bestätigtes Event und Settlement")
        event = EventState.from_dict(raw_event)
        settlement = SettlementState.from_dict(raw_settlement)
        if event.event_id != context.entity_id or settlement.event_id != event.event_id:
            raise ValueError("District-Settlement passt nicht zum Event-Kontext")
        if event.phase != "completed" or settlement.status != "completed":
            raise ValueError("District-Folge benötigt abgeschlossenes Settlement")
        source_id = f"settlement:{settlement.settlement_id}"
        district_id = self._district_for_event(event)
        if district_id is None:
            return self._no_location(source_id, "settlement")
        effects = settlement.effects
        mapping = self.manifest.get("settlement_mapping")
        if not isinstance(mapping, Mapping):
            raise ValueError("settlement_mapping fehlt")
        reputation = self._signed_int(effects.get("reputation_delta"), "reputation_delta")
        stability = self._signed_int(effects.get("stability_delta"), "stability_delta")
        heat = self._signed_int(effects.get("heat_delta"), "heat_delta")
        deltas = {
            "heat": heat,
            "prestige": self._scaled(reputation, mapping.get("prestige_from_reputation_bps")),
            "police_pressure": (
                self._scaled(max(0, heat), mapping.get("police_from_positive_heat_bps"))
                - self._scaled(max(0, stability), mapping.get("police_relief_from_positive_stability_bps"))
            ),
            "scene_activity": (
                self._scaled(reputation, mapping.get("scene_from_reputation_bps"))
                + self._scaled(stability, mapping.get("scene_from_stability_bps"))
            ),
        }
        return self._apply(
            source_type="settlement",
            source_id=source_id,
            district_id=district_id,
            requested_deltas=deltas,
            context=context,
        )

    def apply_confirmed_street_encounter(
        self,
        *,
        source_event_id: str,
        context: JournalContext,
    ) -> DistrictCommitResult:
        if context.entity_type != "character" or not context.entity_id:
            raise ValueError("Street-District-Folge benötigt Character-Kontext")
        source_event_id = self._text(source_event_id, "source_event_id")
        record = next(
            (item for item in self.persistence.read_records() if item.get("event_id") == source_event_id),
            None,
        )
        if record is None or record.get("event_type") != "street.encounter_resolved":
            raise PersistenceError("Street-District-Folge benötigt bestätigten Encounter-Record")
        payload = record.get("payload")
        if not isinstance(payload, Mapping):
            raise PersistenceError("Street-Encounter besitzt ungültigen Payload")
        polarity = payload.get("polarity")
        if polarity not in self.street_mapping:
            raise PersistenceError("Street-Encounter besitzt unbekannte Polarität")
        save = self.persistence.load_state() or {}
        raw_event = save.get("event")
        if not isinstance(raw_event, dict):
            return self._no_location(f"street:{source_event_id}", "street")
        event = EventState.from_dict(raw_event)
        district_id = self._district_for_event(event)
        if district_id is None:
            return self._no_location(f"street:{source_event_id}", "street")
        return self._apply(
            source_type="street",
            source_id=f"street:{source_event_id}",
            district_id=district_id,
            requested_deltas=self.street_mapping[str(polarity)],
            context=context,
        )

    def _apply(
        self,
        *,
        source_type: str,
        source_id: str,
        district_id: str,
        requested_deltas: Mapping[str, int],
        context: JournalContext,
    ) -> DistrictCommitResult:
        current = self.current_state()
        if source_id in current.applied_sources:
            return DistrictCommitResult(
                current,
                (),
                True,
                True,
                {"source_type": source_type, "source_id": source_id, "district_id": district_id, "replay": True},
            )
        deltas = self._deltas(requested_deltas, "requested_deltas")
        data = current.to_dict()
        before = dict(data["metrics"][district_id])
        after: dict[str, int] = {}
        applied: dict[str, int] = {}
        for key in DISTRICT_METRICS:
            new_value = self._clamp(before[key] + deltas[key])
            after[key] = new_value
            applied[key] = new_value - before[key]
        data["metrics"][district_id] = after
        data["applied_sources"].append(source_id)
        data["last_change"] = {
            "source_type": source_type,
            "source_id": source_id,
            "district_id": district_id,
            "deltas": applied,
        }
        data["revision"] += 1
        updated = DistrictState.from_dict(data)
        self._validate_state_contract(updated)

        event_id = f"{context.command_id}:district-effect"
        existing = next(
            (item for item in self.persistence.read_records() if item.get("event_id") == event_id),
            None,
        )
        if existing is not None:
            existing_payload = existing.get("payload", {})
            if existing.get("event_type") != "world.district_effect_applied" or existing_payload.get("source_id") != source_id:
                raise PersistenceError("District-Command-ID wurde für eine andere Quelle verwendet")
            return DistrictCommitResult(current, (), True, True, deepcopy(existing_payload))

        save = deepcopy(self.persistence.load_state() or {})
        save["districts"] = updated.to_dict()
        payload = {
            "contract_version": self.version,
            "source_type": source_type,
            "source_id": source_id,
            "district_id": district_id,
            "old_metrics": before,
            "new_metrics": after,
            "deltas": applied,
            "district_state": updated.to_dict(),
        }
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:district-effect",
            events=[{
                "event_id": event_id,
                "event_type": "world.district_effect_applied",
                "payload": payload,
            }],
            derived_state=save,
            context=context,
        )
        return DistrictCommitResult(updated, receipt.event_ids, False, True, payload)

    def _no_location(self, source_id: str, source_type: str) -> DistrictCommitResult:
        current = self.current_state()
        return DistrictCommitResult(
            current,
            (),
            False,
            False,
            {"source_type": source_type, "source_id": source_id, "district_applied": False, "reason": "unmapped_location"},
        )

    def _district_for_event(self, event: EventState) -> str | None:
        if event.location is None:
            return None
        location_id = event.location.get("location_id")
        return self.location_to_district.get(location_id) if isinstance(location_id, str) else None

    def _validate_state_contract(self, state: DistrictState) -> None:
        if state.contract_version != self.version:
            raise PersistenceError("District-State verwendet einen anderen Vertragsstand")
        if set(state.metrics) != set(self.district_ids):
            raise PersistenceError("District-State passt nicht zum City-Map-Katalog")

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} muss nicht-leerer Text sein")
        return value.strip()

    @staticmethod
    def _metric(value: Any, field: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise ValueError(f"{field} muss Ganzzahl 0..100 sein")
        return value

    @staticmethod
    def _signed_int(value: Any, field: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field} muss Ganzzahl sein")
        return value

    def _deltas(self, value: Any, field: str) -> dict[str, int]:
        if not isinstance(value, Mapping) or set(value) != set(DISTRICT_METRICS):
            raise ValueError(f"{field} benötigt exakt {list(DISTRICT_METRICS)}")
        return {key: self._signed_int(value[key], f"{field}.{key}") for key in DISTRICT_METRICS}

    def _scaled(self, value: int, bps: Any) -> int:
        if isinstance(bps, bool) or not isinstance(bps, int) or bps < 0:
            raise ValueError("District-Skalierung benötigt nichtnegative Basispunkte")
        return int(round(value * bps / 10000))

    @staticmethod
    def _clamp(value: int) -> int:
        return min(100, max(0, value))
