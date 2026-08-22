from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


DISTRICT_METRICS = ("heat", "prestige", "police_pressure", "scene_activity")


def _nonnegative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} muss eine nichtnegative Ganzzahl sein")
    return value


def _metric(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise ValueError(f"{field_name} muss eine Ganzzahl zwischen 0 und 100 sein")
    return value


def _text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} muss nicht-leerer Text sein")
    return value.strip()


@dataclass(slots=True)
class DistrictState:
    contract_version: str
    revision: int = 0
    metrics: dict[str, dict[str, int]] = field(default_factory=dict)
    applied_sources: list[str] = field(default_factory=list)
    last_change: dict[str, Any] | None = None

    def validate(self) -> None:
        _text(self.contract_version, "contract_version")
        _nonnegative_int(self.revision, "revision")
        if not isinstance(self.metrics, dict) or not self.metrics:
            raise ValueError("District-State benötigt mindestens einen Bezirk")
        for district_id, values in self.metrics.items():
            _text(district_id, "district_id")
            if not isinstance(values, dict) or set(values) != set(DISTRICT_METRICS):
                raise ValueError(f"Bezirk {district_id} besitzt falsche Metriken")
            for metric_name in DISTRICT_METRICS:
                _metric(values[metric_name], f"district.{district_id}.{metric_name}")

        if not isinstance(self.applied_sources, list):
            raise ValueError("applied_sources muss eine Liste sein")
        normalized = [_text(item, "applied_source") for item in self.applied_sources]
        if len(normalized) != len(set(normalized)):
            raise ValueError("District-Quelle wurde mehrfach angewendet")

        if self.last_change is not None:
            if not isinstance(self.last_change, dict):
                raise ValueError("last_change muss Objekt oder null sein")
            required = {"source_type", "source_id", "district_id", "deltas"}
            if set(self.last_change) != required:
                raise ValueError("last_change besitzt falsche Felder")
            _text(self.last_change["source_type"], "last_change.source_type")
            _text(self.last_change["source_id"], "last_change.source_id")
            district_id = _text(self.last_change["district_id"], "last_change.district_id")
            if district_id not in self.metrics:
                raise ValueError("last_change verweist auf unbekannten Bezirk")
            deltas = self.last_change["deltas"]
            if not isinstance(deltas, dict) or set(deltas) != set(DISTRICT_METRICS):
                raise ValueError("last_change.deltas besitzt falsche Metriken")
            for key, value in deltas.items():
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"last_change.deltas.{key} muss Ganzzahl sein")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "contract_version": self.contract_version,
            "revision": self.revision,
            "metrics": deepcopy(self.metrics),
            "applied_sources": list(self.applied_sources),
            "last_change": deepcopy(self.last_change),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DistrictState":
        state = cls(
            contract_version=data.get("contract_version", ""),
            revision=data.get("revision", 0),
            metrics=deepcopy(data.get("metrics", {})),
            applied_sources=list(data.get("applied_sources", [])),
            last_change=deepcopy(data.get("last_change")),
        )
        state.validate()
        return state

    @classmethod
    def from_city_map(
        cls,
        *,
        contract_version: str,
        district_ids: Sequence[str],
        defaults: Mapping[str, int],
    ) -> "DistrictState":
        ids = [_text(value, "district_id") for value in district_ids]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("District-IDs müssen nichtleer und eindeutig sein")
        if set(defaults) != set(DISTRICT_METRICS):
            raise ValueError("District-Defaults besitzen falsche Metriken")
        normalized_defaults = {
            key: _metric(defaults[key], f"defaults.{key}")
            for key in DISTRICT_METRICS
        }
        state = cls(
            contract_version=_text(contract_version, "contract_version"),
            metrics={district_id: dict(normalized_defaults) for district_id in ids},
        )
        state.validate()
        return state
