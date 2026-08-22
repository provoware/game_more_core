from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
from typing import Any, Mapping, Sequence

from bunkerfrequenz.application.state_blocks import merge_state_block
from bunkerfrequenz.domain.character import CharacterState, RESOURCE_MAX, RESOURCE_MIN
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_EFFECT_FIELDS = frozenset({"energy_delta", "stress_delta", "reputation_delta"})
_POLARITIES = frozenset({"neutral", "positive", "negative"})


@dataclass(frozen=True, slots=True)
class StreetEncounterResult:
    encounter_id: str
    polarity: str
    title_key: str
    body_key: str
    effects: dict[str, int]
    character_after: CharacterState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss ein nicht-leerer Text sein")
    return value.strip()


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} muss eine Ganzzahl sein")
    return value


def _validate_manifest(manifest: Mapping[str, Any]) -> tuple[str, int, tuple[dict[str, Any], ...]]:
    version = _require_text(manifest.get("version"), "STREET_ENCOUNTER_MANIFEST.version")
    selection = manifest.get("selection")
    policy = manifest.get("policy")
    encounters = manifest.get("encounters")
    if not isinstance(selection, Mapping) or not isinstance(policy, Mapping):
        raise ValueError("Street-Manifest benötigt selection und policy")
    if selection.get("method") != "sha256_stable_weighted":
        raise ValueError("Street-Manifest besitzt unbekannte Auswahlmethode")
    if selection.get("system_time_as_seed") is not False:
        raise ValueError("Systemzeit darf keine Street-Zufallsautorität sein")
    weight_total = _require_int(selection.get("weight_total"), "selection.weight_total")
    if weight_total < 1:
        raise ValueError("selection.weight_total muss positiv sein")
    if not isinstance(encounters, Sequence) or isinstance(encounters, (str, bytes)) or not encounters:
        raise ValueError("Street-Manifest benötigt Begegnungen")

    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    totals = {"neutral": 0, "positive": 0, "negative": 0}
    for raw in encounters:
        if not isinstance(raw, Mapping):
            raise ValueError("Street-Begegnung muss ein Mapping sein")
        encounter_id = _require_text(raw.get("encounter_id"), "encounter_id")
        if encounter_id in ids:
            raise ValueError(f"Doppelte Street-Begegnung: {encounter_id}")
        ids.add(encounter_id)
        polarity = _require_text(raw.get("polarity"), f"{encounter_id}.polarity")
        if polarity not in _POLARITIES:
            raise ValueError(f"{encounter_id}.polarity ist unbekannt")
        weight = _require_int(raw.get("weight"), f"{encounter_id}.weight")
        if weight < 1:
            raise ValueError(f"{encounter_id}.weight muss positiv sein")
        effects = raw.get("effects")
        if not isinstance(effects, Mapping) or set(effects) != _EFFECT_FIELDS:
            raise ValueError(f"{encounter_id}.effects benötigt exakt {sorted(_EFFECT_FIELDS)}")
        normalized_effects = {
            field: _require_int(effects[field], f"{encounter_id}.effects.{field}")
            for field in sorted(_EFFECT_FIELDS)
        }
        if any(abs(value) > 10 for value in normalized_effects.values()):
            raise ValueError(f"{encounter_id} überschreitet den kleinen Street-Effektbereich")
        if polarity == "positive" and not any(value > 0 for value in normalized_effects.values()) and not any(
            normalized_effects[field] < 0 for field in ("stress_delta",)
        ):
            raise ValueError(f"{encounter_id} ist positiv markiert, besitzt aber keinen positiven Effekt")
        if polarity == "negative" and not any(value < 0 for value in normalized_effects.values()) and not any(
            normalized_effects[field] > 0 for field in ("stress_delta",)
        ):
            raise ValueError(f"{encounter_id} ist negativ markiert, besitzt aber keinen negativen Effekt")
        totals[polarity] += weight
        normalized.append({
            "encounter_id": encounter_id,
            "polarity": polarity,
            "weight": weight,
            "title_key": _require_text(raw.get("title_key"), f"{encounter_id}.title_key"),
            "body_key": _require_text(raw.get("body_key"), f"{encounter_id}.body_key"),
            "effects": normalized_effects,
        })

    if sum(totals.values()) != weight_total:
        raise ValueError("Street-Gewichte entsprechen nicht selection.weight_total")
    for polarity in _POLARITIES:
        expected = _require_int(policy.get(f"{polarity}_weight"), f"policy.{polarity}_weight")
        if totals[polarity] != expected:
            raise ValueError(f"Street-{polarity}-Gewicht widerspricht policy")
    actual_weight = totals["positive"] + totals["negative"]
    expected_positive_share = policy.get("positive_share_of_actual_encounters")
    if isinstance(expected_positive_share, bool) or not isinstance(expected_positive_share, (int, float)):
        raise ValueError("positive_share_of_actual_encounters muss eine Zahl sein")
    if actual_weight <= 0 or abs((totals["positive"] / actual_weight) - float(expected_positive_share)) > 1e-9:
        raise ValueError("Street-Positivanteil widerspricht policy")
    if totals["positive"] <= totals["negative"]:
        raise ValueError("Street-Katalog muss überwiegend positive Begegnungen besitzen")
    return version, weight_total, tuple(normalized)


def _stable_bucket(world_seed: str, walk_instance_id: str, server_sequence: int | None, total: int) -> int:
    raw = f"{world_seed}|{walk_instance_id}|{server_sequence if server_sequence is not None else '-'}"
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % total


def _select(encounters: Sequence[Mapping[str, Any]], bucket: int) -> Mapping[str, Any]:
    cursor = 0
    for encounter in encounters:
        cursor += int(encounter["weight"])
        if bucket < cursor:
            return encounter
    raise RuntimeError("Street-Auswahl liegt außerhalb des Gewichtskatalogs")


def _clamp_resource(value: int) -> int:
    return min(RESOURCE_MAX, max(RESOURCE_MIN, value))


class StreetEncounterService:
    def __init__(self, persistence: PersistenceKernel, manifest: Mapping[str, Any]) -> None:
        self.persistence = persistence
        self.contract_version, self.weight_total, self.encounters = _validate_manifest(manifest)

    def walk(
        self,
        character: CharacterState,
        *,
        walk_instance_id: str,
        world_seed: str,
        journal_context: JournalContext,
        server_sequence: int | None = None,
    ) -> StreetEncounterResult:
        character.validate()
        walk_instance_id = _require_text(walk_instance_id, "walk_instance_id")
        world_seed = _require_text(world_seed, "world_seed")
        if journal_context.entity_type != "character" or journal_context.entity_id != character.character_id:
            raise ValueError("Street-Walk benötigt den bestätigten Character-Kontext")

        first_event_id = f"{walk_instance_id}:001"
        if self.persistence.has_event(first_event_id):
            return self._replay_result(character, first_event_id)

        bucket = _stable_bucket(world_seed, walk_instance_id, server_sequence, self.weight_total)
        selected = _select(self.encounters, bucket)
        state = deepcopy(character)
        requested = dict(selected["effects"])

        old_energy = state.energy
        old_stress = state.stress
        old_reputation = state.reputation
        new_energy = _clamp_resource(old_energy + requested["energy_delta"])
        new_stress = _clamp_resource(old_stress + requested["stress_delta"])
        new_reputation = max(0, old_reputation + requested["reputation_delta"])
        applied = {
            "energy_delta": new_energy - old_energy,
            "stress_delta": new_stress - old_stress,
            "reputation_delta": new_reputation - old_reputation,
        }
        state.energy = new_energy
        state.stress = new_stress
        state.reputation = new_reputation
        state.validate()

        generated: list[dict[str, Any]] = [{
            "event_type": "street.encounter_resolved",
            "payload": {
                "walk_instance_id": walk_instance_id,
                "encounter_id": selected["encounter_id"],
                "polarity": selected["polarity"],
                "title_key": selected["title_key"],
                "body_key": selected["body_key"],
                "effects": applied,
                "contract_version": self.contract_version,
            },
        }]
        if applied["energy_delta"] or applied["stress_delta"]:
            generated.append({
                "event_type": "character.resources_changed",
                "payload": {
                    "source_action": f"street.walk:{selected['encounter_id']}",
                    "energy": {
                        "old": old_energy,
                        "delta": applied["energy_delta"],
                        "new": new_energy,
                    },
                    "stress": {
                        "old": old_stress,
                        "delta": applied["stress_delta"],
                        "new": new_stress,
                    },
                },
            })
        if applied["reputation_delta"]:
            generated.append({
                "event_type": "character.reputation_changed",
                "payload": {
                    "old": old_reputation,
                    "delta": applied["reputation_delta"],
                    "new": new_reputation,
                    "reason": f"street.encounter:{selected['encounter_id']}",
                },
            })

        events = [
            {
                "event_id": f"{walk_instance_id}:{index:03d}",
                "event_type": event["event_type"],
                "payload": event["payload"],
            }
            for index, event in enumerate(generated, 1)
        ]
        receipt = self.persistence.commit(
            transaction_id=f"tx:street:{walk_instance_id}",
            events=events,
            derived_state=merge_state_block(self.persistence, "character", state.to_dict()),
            context=journal_context,
        )
        return StreetEncounterResult(
            encounter_id=str(selected["encounter_id"]),
            polarity=str(selected["polarity"]),
            title_key=str(selected["title_key"]),
            body_key=str(selected["body_key"]),
            effects=applied,
            character_after=state,
            committed_event_ids=receipt.event_ids,
            idempotent_replay=False,
        )

    def _replay_result(self, fallback: CharacterState, first_event_id: str) -> StreetEncounterResult:
        record = next(
            (item for item in self.persistence.read_records() if item.get("event_id") == first_event_id),
            None,
        )
        if record is None or record.get("event_type") != "street.encounter_resolved":
            raise PersistenceError("Street-Replay besitzt keinen gültigen Ausgangsrecord")
        payload = record.get("payload")
        if not isinstance(payload, Mapping):
            raise PersistenceError("Street-Replay besitzt keinen gültigen Payload")
        if payload.get("contract_version") != self.contract_version:
            raise PersistenceError("Street-Replay verwendet einen anderen Vertragsstand")
        persisted = self.persistence.load_state()
        state = fallback if persisted is None or not isinstance(persisted.get("character"), dict) else CharacterState.from_dict(persisted["character"])
        effects = payload.get("effects")
        if not isinstance(effects, Mapping) or set(effects) != _EFFECT_FIELDS:
            raise PersistenceError("Street-Replay besitzt ungültige Effekte")
        return StreetEncounterResult(
            encounter_id=_require_text(payload.get("encounter_id"), "replay.encounter_id"),
            polarity=_require_text(payload.get("polarity"), "replay.polarity"),
            title_key=_require_text(payload.get("title_key"), "replay.title_key"),
            body_key=_require_text(payload.get("body_key"), "replay.body_key"),
            effects={field: _require_int(effects[field], f"replay.effects.{field}") for field in sorted(_EFFECT_FIELDS)},
            character_after=state,
            committed_event_ids=(),
            idempotent_replay=True,
        )
