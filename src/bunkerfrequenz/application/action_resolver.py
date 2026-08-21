from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import random
from typing import Callable

from bunkerfrequenz.domain.character import CharacterState, RESOURCE_MAX, RESOURCE_MIN
from bunkerfrequenz.domain.progression import add_trait_evidence, apply_skill_xp, evaluate_specialization, specialization_xp_multiplier
from bunkerfrequenz.domain.trait_effects import resolve_trait_modifiers


@dataclass(frozen=True, slots=True)
class ResolvedAction:
    action_id: str
    action_instance_id: str
    outcome: str
    quality_multiplier: float
    xp_multiplier: float
    trait_modifiers: dict[str, float]
    journal_events: tuple[dict, ...]
    character_after: CharacterState


OUTCOMES = (
    (0.10, "failed", 0.65, 0.70),
    (0.27, "partial", 0.85, 0.90),
    (0.80, "success", 1.00, 1.00),
    (0.96, "excellent", 1.15, 1.15),
    (1.01, "legendary", 1.30, 1.25),
)
RISK_PENALTY = {"low": 0.00, "low_medium": 0.02, "medium": 0.04, "medium_high": 0.07, "high": 0.10}
_RESOURCE_FIELDS = frozenset({"energy_delta", "stress_delta"})


def _stable_random(world_seed: str, action_instance_id: str, server_sequence: int | None) -> random.Random:
    raw = f"{world_seed}|{action_instance_id}|{server_sequence if server_sequence is not None else '-'}"
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _validate_weights(weights: dict[str, float], label: str) -> None:
    if not weights or any(value < 0 for value in weights.values()) or abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"{label} muss aus nicht-negativen Gewichten mit Summe 1.0 bestehen")


def _resolve_placeholder(weights: dict[str, float], placeholder: str, selected: str | None) -> dict[str, float]:
    result = dict(weights)
    if placeholder not in result:
        return result
    if not selected:
        raise ValueError(f"{placeholder} benötigt eine Auswahl")
    value = result.pop(placeholder)
    result[selected] = result.get(selected, 0.0) + value
    return result


def _resource_deltas(action: dict) -> tuple[int, int]:
    effects = action.get("resource_effects")
    if not isinstance(effects, dict) or set(effects) != _RESOURCE_FIELDS:
        raise ValueError("resource_effects benötigt exakt energy_delta und stress_delta")
    values = []
    for field in ("energy_delta", "stress_delta"):
        value = effects[field]
        if isinstance(value, bool) or not isinstance(value, int) or not -100 <= value <= 100:
            raise ValueError(f"resource_effects.{field} muss eine Ganzzahl zwischen -100 und 100 sein")
        values.append(value)
    return values[0], values[1]


def _clamp_resource(value: int) -> int:
    return min(RESOURCE_MAX, max(RESOURCE_MIN, value))


def _apply_resource_effects(state: CharacterState, action: dict) -> dict:
    energy_delta, stress_delta = _resource_deltas(action)
    old_energy = state.energy
    old_stress = state.stress
    new_energy = _clamp_resource(old_energy + energy_delta)
    new_stress = _clamp_resource(old_stress + stress_delta)
    state.energy = new_energy
    state.stress = new_stress
    return {
        "event_type": "character.resources_changed",
        "payload": {
            "source_action": action["action_id"],
            "energy": {"old": old_energy, "delta": energy_delta, "new": new_energy},
            "stress": {"old": old_stress, "delta": stress_delta, "new": new_stress},
        },
    }


class ActionResolver:
    def __init__(self, prerequisite_checker: Callable[[str, dict], bool] | None = None):
        self._check = prerequisite_checker or (lambda _rule, _ctx: True)

    def resolve(
        self,
        character: CharacterState,
        action: dict,
        *,
        action_instance_id: str,
        world_seed: str,
        server_sequence: int | None = None,
        context: dict | None = None,
        base_xp: int = 18,
        selected_skill: str | None = None,
        selected_trait_family: str | None = None,
        evidence_source: str | None = None,
    ) -> ResolvedAction:
        context = context or {}
        for rule in action.get("prerequisites", []):
            if not self._check(rule, context):
                raise ValueError(f"Voraussetzung nicht erfüllt: {rule}")

        skill_weights = _resolve_placeholder(action["skill_weights"], "selected_skill", selected_skill)
        trait_weights = _resolve_placeholder(action["trait_evidence_weights"], "selected_trait_family", selected_trait_family)
        _validate_weights(skill_weights, "skill_weights")
        _validate_weights(trait_weights, "trait_evidence_weights")
        _resource_deltas(action)
        if any(skill not in character.skills for skill in skill_weights):
            unknown = sorted(skill for skill in skill_weights if skill not in character.skills)
            raise ValueError(f"Unbekannte Skills in Aktion: {', '.join(unknown)}")

        rng = _stable_random(world_seed, action_instance_id, server_sequence)
        competence = sum(character.skills[s] * w for s, w in skill_weights.items())
        competence_bonus = ((competence - 10.0) / 90.0) * 0.25
        trait_modifiers = resolve_trait_modifiers(character, action, tuple(skill_weights))
        roll = min(
            0.999999,
            max(
                0.0,
                rng.random()
                + competence_bonus
                + trait_modifiers.outcome_pct / 100
                - RISK_PENALTY.get(action.get("risk_profile", "medium"), 0.04),
            ),
        )
        outcome, quality, xp_mult = "success", 1.0, 1.0
        for limit, name, q, x in OUTCOMES:
            if roll < limit:
                outcome, quality, xp_mult = name, q, x
                break
        quality = round(quality * (1 + trait_modifiers.quality_pct / 100), 6)

        state = deepcopy(character)
        generated: list[dict] = [_apply_resource_effects(state, action)]
        for skill_id, weight in skill_weights.items():
            trait_xp_multiplier = 1 + trait_modifiers.xp_pct_by_skill[skill_id] / 100
            amount = max(
                1,
                round(
                    base_xp
                    * weight
                    * xp_mult
                    * specialization_xp_multiplier(state, skill_id)
                    * trait_xp_multiplier
                ),
            )
            generated.append(
                {
                    "event_type": "character.skill_xp_gained",
                    "payload": {
                        "skill_id": skill_id,
                        "amount": amount,
                        "source_action": action["action_id"],
                    },
                }
            )
            generated.extend(apply_skill_xp(state, skill_id, amount))

        if evidence_source is None:
            evidence_source = {
                "training": "training",
                "crisis": "crisis",
                "exploration": "discovery",
                "research": "discovery",
                "social": "team",
            }.get(action.get("category"), "practice")
        source_multiplier = {
            "training": 0.35,
            "practice": 1.0,
            "crisis": 1.25,
            "team": 1.1,
            "discovery": 1.1,
            "success": 0.9,
            "failure": 0.7,
        }[evidence_source]
        trait_base = base_xp * quality * source_multiplier
        for family, weight in trait_weights.items():
            evidence = round(trait_base * weight, 6)
            generated.append(
                {
                    "event_type": "character.trait_evidence_gained",
                    "payload": {
                        "family": family,
                        "amount": evidence,
                        "source_action": action["action_id"],
                        "evidence_source": evidence_source,
                    },
                }
            )
            generated.extend(add_trait_evidence(state, family, evidence, evidence_source))

        generated.extend(evaluate_specialization(state))
        state.validate()
        return ResolvedAction(
            action_id=action["action_id"],
            action_instance_id=action_instance_id,
            outcome=outcome,
            quality_multiplier=quality,
            xp_multiplier=xp_mult,
            trait_modifiers=trait_modifiers.metrics,
            journal_events=tuple(generated),
            character_after=state,
        )
