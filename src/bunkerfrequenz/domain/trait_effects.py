from __future__ import annotations

from dataclasses import dataclass

from .character import CharacterState


POSITIVE_CAP = 35
NEGATIVE_CAP = -20

# Kept numeric and text-free; the manifest remains the public balance contract.
EFFECTS = {
    "krisenfest": ((3, 5, 8, 12, 16), "crisis_success_chance_pct", (-1, -2, -3, -4, -5), "routine_xp_pct"),
    "vernetzer": ((3, 6, 9, 13, 18), "contact_quality_pct", (-1, -2, -3, -4, -6), "solo_xp_pct"),
    "klangfokus": ((4, 7, 10, 14, 18), "audio_xp_pct", (-1, -2, -3, -4, -6), "logistics_xp_pct"),
    "stromfokus": ((4, 7, 10, 14, 18), "electrical_xp_pct", (-1, -2, -3, -4, -6), "creativity_xp_pct"),
    "planer": ((3, 6, 9, 13, 18), "reliability_pct", (-1, -2, -3, -4, -6), "improvisation_xp_pct"),
    "scout": ((3, 6, 9, 13, 18), "discovery_chance_pct", (-1, -2, -3, -4, -6), "administration_speed_pct"),
    "improvisierer": ((4, 7, 10, 15, 20), "alternative_solution_chance_pct", (-1, -2, -3, -5, -7), "standardization_efficiency_pct"),
    "verhandler": ((2, 4, 7, 10, 14), "negotiation_effect_pct", (-1, -2, -3, -4, -6), "handwork_xp_pct"),
    "nachtmensch": ((3, 6, 10, 14, 18), "night_performance_pct", (-2, -3, -5, -7, -9), "early_day_performance_pct"),
    "ausdauer": ((3, 6, 10, 14, 18), "fatigue_resistance_pct", (-1, -2, -3, -4, -6), "recovery_speed_pct"),
    "kreativer": ((3, 6, 10, 15, 20), "design_quality_pct", (-1, -2, -3, -5, -7), "routine_reliability_pct"),
    "risikospieler": ((4, 8, 12, 18, 25), "high_risk_reward_pct", (2, 4, 6, 9, 12), "consequence_severity_pct"),
    "detailmensch": ((4, 8, 12, 17, 22), "error_detection_pct", (-1, -2, -4, -6, -8), "action_speed_pct"),
    "crew_anker": ((3, 6, 10, 14, 18), "team_synergy_pct", (-1, -2, -3, -4, -6), "solo_xp_pct"),
    "opportunist": ((2, 4, 7, 10, 15), "rare_find_chance_pct", (-1, -2, -3, -5, -7), "planning_predictability_pct"),
}
SOFT_CONFLICTS = (("planer", "improvisierer", 3, 0.85), ("detailmensch", "opportunist", 4, 0.9))

XP_SKILLS = {
    "audio_xp_pct": {"musik"}, "logistics_xp_pct": {"logistik"},
    "electrical_xp_pct": {"technik"}, "creativity_xp_pct": {"kreativitaet"},
    "improvisation_xp_pct": {"improvisation"}, "handwork_xp_pct": {"handwerk"},
}
QUALITY_METRICS = {"contact_quality_pct", "negotiation_effect_pct", "design_quality_pct", "high_risk_reward_pct"}
XP_ALL_METRICS = {"routine_xp_pct", "solo_xp_pct"}


def _cap(value: float) -> float:
    return max(NEGATIVE_CAP, min(POSITIVE_CAP, value))


@dataclass(frozen=True, slots=True)
class TraitModifiers:
    outcome_pct: float
    quality_pct: float
    xp_pct_by_skill: dict[str, float]
    metrics: dict[str, float]


def resolve_trait_modifiers(state: CharacterState, action: dict, skill_ids: tuple[str, ...]) -> TraitModifiers:
    relevant = set(action.get("trait_evidence_weights", ()))
    active = {family: tier for family, tier in state.traits.items() if family in relevant and family in EFFECTS}
    conflict_factor = {family: 1.0 for family in active}
    for left, right, min_tier, factor in SOFT_CONFLICTS:
        if active.get(left, 0) >= min_tier and active.get(right, 0) >= min_tier:
            conflict_factor[left] *= factor
            conflict_factor[right] *= factor

    metrics: dict[str, float] = {}
    for family, tier in active.items():
        positive, positive_metric, tradeoff, tradeoff_metric = EFFECTS[family]
        metrics[positive_metric] = metrics.get(positive_metric, 0.0) + positive[tier - 1] * conflict_factor[family]
        tradeoff_value = -tradeoff[tier - 1] if tradeoff_metric == "consequence_severity_pct" else tradeoff[tier - 1]
        metrics[tradeoff_metric] = metrics.get(tradeoff_metric, 0.0) + tradeoff_value
    metrics = {metric: _cap(value) for metric, value in metrics.items()}

    quality = _cap(sum(value for metric, value in metrics.items() if metric in QUALITY_METRICS))
    outcome = _cap(sum(value for metric, value in metrics.items() if metric not in QUALITY_METRICS and metric not in XP_ALL_METRICS and metric not in XP_SKILLS))
    xp = {}
    for skill_id in skill_ids:
        value = sum(metrics.get(metric, 0.0) for metric in XP_ALL_METRICS)
        value += sum(metrics.get(metric, 0.0) for metric, skills in XP_SKILLS.items() if skill_id in skills)
        xp[skill_id] = _cap(value)
    return TraitModifiers(outcome, quality, xp, metrics)
