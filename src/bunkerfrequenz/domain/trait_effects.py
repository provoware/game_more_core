from __future__ import annotations

from dataclasses import dataclass, field

from .character import CharacterState


# Mirrors manifests/TRAIT_ENGINE_MANIFEST.json. A regression test keeps both in sync.
TRAIT_EFFECTS: dict[str, tuple[str, tuple[int, ...], str, tuple[int, ...]]] = {
    "krisenfest": ("crisis_success_chance_pct", (3, 5, 8, 12, 16), "routine_xp_pct", (-1, -2, -3, -4, -5)),
    "vernetzer": ("contact_quality_pct", (3, 6, 9, 13, 18), "solo_xp_pct", (-1, -2, -3, -4, -6)),
    "klangfokus": ("audio_xp_pct", (4, 7, 10, 14, 18), "logistics_xp_pct", (-1, -2, -3, -4, -6)),
    "stromfokus": ("electrical_xp_pct", (4, 7, 10, 14, 18), "creativity_xp_pct", (-1, -2, -3, -4, -6)),
    "planer": ("reliability_pct", (3, 6, 9, 13, 18), "improvisation_xp_pct", (-1, -2, -3, -4, -6)),
    "scout": ("discovery_chance_pct", (3, 6, 9, 13, 18), "administration_speed_pct", (-1, -2, -3, -4, -6)),
    "improvisierer": ("alternative_solution_chance_pct", (4, 7, 10, 15, 20), "standardization_efficiency_pct", (-1, -2, -3, -5, -7)),
    "verhandler": ("negotiation_effect_pct", (2, 4, 7, 10, 14), "handwork_xp_pct", (-1, -2, -3, -4, -6)),
    "nachtmensch": ("night_performance_pct", (3, 6, 10, 14, 18), "early_day_performance_pct", (-2, -3, -5, -7, -9)),
    "ausdauer": ("fatigue_resistance_pct", (3, 6, 10, 14, 18), "recovery_speed_pct", (-1, -2, -3, -4, -6)),
    "kreativer": ("design_quality_pct", (3, 6, 10, 15, 20), "routine_reliability_pct", (-1, -2, -3, -5, -7)),
    "risikospieler": ("high_risk_reward_pct", (4, 8, 12, 18, 25), "consequence_severity_pct", (2, 4, 6, 9, 12)),
    "detailmensch": ("error_detection_pct", (4, 8, 12, 17, 22), "action_speed_pct", (-1, -2, -4, -6, -8)),
    "crew_anker": ("team_synergy_pct", (3, 6, 10, 14, 18), "solo_xp_pct", (-1, -2, -3, -4, -6)),
    "opportunist": ("rare_find_chance_pct", (2, 4, 7, 10, 15), "planning_predictability_pct", (-1, -2, -3, -5, -7)),
}

SOFT_CONFLICTS = (
    ("planer", "improvisierer", 3, 0.85),
    ("detailmensch", "opportunist", 4, 0.90),
)
POSITIVE_CAP = 35.0
NEGATIVE_CAP = -20.0

AUDIO_SKILLS = {"technik", "musik", "konzentration"}
LOGISTICS_SKILLS = {"logistik", "organisation", "orientierung"}
ELECTRICAL_SKILLS = {"technik", "handwerk"}
CREATIVE_SKILLS = {"kreativitaet", "musik"}


@dataclass(slots=True)
class ActionTraitModifiers:
    success_roll_delta: float = 0.0
    quality_multiplier: float = 1.0
    evidence_multiplier: float = 1.0
    consequence_multiplier: float = 1.0
    duration_multiplier: float = 1.0
    skill_xp_multipliers: dict[str, float] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)


def _tier_value(values: tuple[int, ...], tier: int) -> float:
    if tier <= 0:
        return 0.0
    return float(values[min(tier, len(values)) - 1])


def trait_metrics(state: CharacterState) -> dict[str, float]:
    metrics: dict[str, float] = {}
    positive_sources: dict[str, list[tuple[str, float]]] = {}
    negative_sources: dict[str, list[tuple[str, float]]] = {}

    for family, tier in state.traits.items():
        if family not in TRAIT_EFFECTS or tier <= 0:
            continue
        pos_metric, pos_values, trade_metric, trade_values = TRAIT_EFFECTS[family]
        positive_sources.setdefault(pos_metric, []).append((family, _tier_value(pos_values, tier)))
        trade_value = _tier_value(trade_values, tier)
        bucket = positive_sources if trade_value >= 0 else negative_sources
        bucket.setdefault(trade_metric, []).append((family, trade_value))

    conflict_multiplier: dict[str, float] = {family: 1.0 for family in state.traits}
    for left, right, min_tier, multiplier in SOFT_CONFLICTS:
        if state.traits.get(left, 0) >= min_tier and state.traits.get(right, 0) >= min_tier:
            conflict_multiplier[left] = min(conflict_multiplier.get(left, 1.0), multiplier)
            conflict_multiplier[right] = min(conflict_multiplier.get(right, 1.0), multiplier)

    for metric, sources in positive_sources.items():
        total = sum(value * conflict_multiplier.get(family, 1.0) for family, value in sources)
        metrics[metric] = min(POSITIVE_CAP, total)
    for metric, sources in negative_sources.items():
        total = sum(value for _family, value in sources)
        metrics[metric] = max(NEGATIVE_CAP, total)
    return metrics


def _add_success(mod: ActionTraitModifiers, pct: float, scale: float = 1.0) -> None:
    mod.success_roll_delta += (pct / 100.0) * scale


def action_trait_modifiers(state: CharacterState, action: dict, context: dict | None = None) -> ActionTraitModifiers:
    context = context or {}
    metrics = trait_metrics(state)
    mod = ActionTraitModifiers(metrics=metrics)
    category = action.get("category", "")
    risk = action.get("risk_profile", "medium")
    team_size = max(1, int(context.get("team_size", 1)))
    is_night = bool(context.get("is_night", False))
    is_early_day = bool(context.get("is_early_day", False))
    fatigue = min(1.0, max(0.0, float(context.get("fatigue", 0.0))))

    if category == "crisis":
        _add_success(mod, metrics.get("crisis_success_chance_pct", 0.0))
    if category in {"event", "booking", "club", "logistics"}:
        _add_success(mod, metrics.get("reliability_pct", 0.0), 0.55)
        _add_success(mod, metrics.get("routine_reliability_pct", 0.0), 0.35)
    if category in {"exploration", "research"}:
        _add_success(mod, metrics.get("discovery_chance_pct", 0.0))
        _add_success(mod, metrics.get("rare_find_chance_pct", 0.0), 0.45)
    if category in {"technical", "construction", "crisis"}:
        _add_success(mod, metrics.get("alternative_solution_chance_pct", 0.0), 0.55)
        _add_success(mod, metrics.get("error_detection_pct", 0.0), 0.35)
    if category in {"booking", "economy", "market", "social"}:
        _add_success(mod, metrics.get("negotiation_effect_pct", 0.0), 0.55)
        mod.quality_multiplier *= 1.0 + metrics.get("contact_quality_pct", 0.0) / 200.0
    if category in {"creative", "music"}:
        mod.quality_multiplier *= 1.0 + metrics.get("design_quality_pct", 0.0) / 100.0
    if is_night:
        _add_success(mod, metrics.get("night_performance_pct", 0.0), 0.6)
    if is_early_day:
        _add_success(mod, metrics.get("early_day_performance_pct", 0.0), 0.6)
    if team_size > 1:
        _add_success(mod, metrics.get("team_synergy_pct", 0.0), min(1.0, (team_size - 1) / 3.0) * 0.55)

    if fatigue > 0:
        resistance = metrics.get("fatigue_resistance_pct", 0.0) / 100.0
        mod.quality_multiplier *= 1.0 - max(0.0, fatigue * (0.18 - resistance * 0.12))

    if risk in {"medium_high", "high"}:
        reward = metrics.get("high_risk_reward_pct", 0.0) / 100.0
        mod.quality_multiplier *= 1.0 + reward
        mod.consequence_multiplier *= 1.0 + metrics.get("consequence_severity_pct", 0.0) / 100.0

    speed_pct = metrics.get("action_speed_pct", 0.0)
    if category in {"event", "booking", "club", "logistics", "construction"}:
        speed_pct += metrics.get("administration_speed_pct", 0.0)
    mod.duration_multiplier = max(0.65, min(1.35, 1.0 - speed_pct / 100.0))

    base_xp_multiplier = 1.0
    if action.get("risk_profile") == "low":
        base_xp_multiplier *= 1.0 + metrics.get("routine_xp_pct", 0.0) / 100.0
    if team_size <= 1:
        base_xp_multiplier *= 1.0 + metrics.get("solo_xp_pct", 0.0) / 100.0

    for skill in state.skills:
        multiplier = base_xp_multiplier
        if skill in AUDIO_SKILLS:
            multiplier *= 1.0 + metrics.get("audio_xp_pct", 0.0) / 100.0
        if skill in LOGISTICS_SKILLS:
            multiplier *= 1.0 + metrics.get("logistics_xp_pct", 0.0) / 100.0
        if skill in ELECTRICAL_SKILLS:
            multiplier *= 1.0 + metrics.get("electrical_xp_pct", 0.0) / 100.0
        if skill in CREATIVE_SKILLS:
            multiplier *= 1.0 + metrics.get("creativity_xp_pct", 0.0) / 100.0
        if skill == "improvisation":
            multiplier *= 1.0 + metrics.get("improvisation_xp_pct", 0.0) / 100.0
        if skill == "handwerk":
            multiplier *= 1.0 + metrics.get("handwork_xp_pct", 0.0) / 100.0
        mod.skill_xp_multipliers[skill] = max(0.5, min(1.5, multiplier))

    predictability = metrics.get("planning_predictability_pct", 0.0)
    standardization = metrics.get("standardization_efficiency_pct", 0.0)
    if category in {"event", "booking", "club", "logistics"}:
        _add_success(mod, predictability, 0.35)
        _add_success(mod, standardization, 0.25)

    return mod
