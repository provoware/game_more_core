from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import random
from typing import Callable

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.progression import add_trait_evidence, apply_skill_xp, evaluate_specialization, specialization_xp_multiplier


@dataclass(frozen=True, slots=True)
class ResolvedAction:
    action_id: str
    action_instance_id: str
    outcome: str
    quality_multiplier: float
    xp_multiplier: float
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
        if any(skill not in character.skills for skill in skill_weights):
            unknown = sorted(skill for skill in skill_weights if skill not in character.skills)
            raise ValueError(f"Unbekannte Skills in Aktion: {', '.join(unknown)}")

        rng = _stable_random(world_seed, action_instance_id, server_sequence)
        competence = sum(character.skills[s] * w for s, w in skill_weights.items())
        competence_bonus = ((competence - 10.0) / 90.0) * 0.25
        roll = min(0.999999, max(0.0, rng.random() + competence_bonus - RISK_PENALTY.get(action.get("risk_profile", "medium"), 0.04)))
        outcome, quality, xp_mult = "success", 1.0, 1.0
        for limit, name, q, x in OUTCOMES:
            if roll < limit:
                outcome, quality, xp_mult = name, q, x
                break

        state = deepcopy(character)
        generated: list[dict] = []
        for skill_id, weight in skill_weights.items():
            amount = max(1, round(base_xp * weight * xp_mult * specialization_xp_multiplier(state, skill_id)))
            generated.append({"event_type": "character.skill_xp_gained", "payload": {"skill_id": skill_id, "amount": amount, "source_action": action["action_id"]}})
            generated.extend(apply_skill_xp(state, skill_id, amount))

        if evidence_source is None:
            evidence_source = {"training":"training", "crisis":"crisis", "exploration":"discovery", "research":"discovery", "social":"team"}.get(action.get("category"), "practice")
        source_multiplier = {"training":0.35, "practice":1.0, "crisis":1.25, "team":1.1, "discovery":1.1, "success":0.9, "failure":0.7}[evidence_source]
        trait_base = base_xp * quality * source_multiplier
        for family, weight in trait_weights.items():
            evidence = round(trait_base * weight, 6)
            generated.append({"event_type": "character.trait_evidence_gained", "payload": {"family": family, "amount": evidence, "source_action": action["action_id"], "evidence_source": evidence_source}})
            generated.extend(add_trait_evidence(state, family, evidence, evidence_source))

        generated.extend(evaluate_specialization(state))
        return ResolvedAction(
            action_id=action["action_id"], action_instance_id=action_instance_id,
            outcome=outcome, quality_multiplier=quality, xp_multiplier=xp_mult,
            journal_events=tuple(generated), character_after=state,
        )
