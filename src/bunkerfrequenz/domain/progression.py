from __future__ import annotations

from .character import CharacterState


class ProgressionRules:
    skill_min = 10
    skill_max = 100
    total_xp_from_skill_xp_multiplier = 1.15
    trait_tiers = (
        (1, 220.0, 3, 12, 1),
        (2, 480.0, 8, 25, 1),
        (3, 850.0, 15, 45, 2),
        (4, 1300.0, 25, 70, 2),
        (5, 1900.0, 40, 110, 3),
    )

    @staticmethod
    def xp_to_next_skill(value: int) -> int:
        return round(70 + 5.5 * max(0, value - 10) ** 1.28)

    @staticmethod
    def total_xp_for_level(level: int) -> int:
        if level <= 1:
            return 0
        return round(120 * (level - 1) ** 1.62 + 80 * (level - 1))


def level_for_total_xp(total_xp: int) -> int:
    level = 1
    while level < 50 and total_xp >= ProgressionRules.total_xp_for_level(level + 1):
        level += 1
    return level


def resonance_cost_for_rank(rank: int) -> int:
    if rank < 1:
        raise ValueError("Resonanzrang beginnt bei 1")
    return round(5000 + 1800 * (rank - 1) ** 1.22)


def resonance_rank_for_xp(resonance_xp: int) -> int:
    if resonance_xp < 0:
        raise ValueError("Resonanz-XP darf nicht negativ sein")
    rank = 0
    spent = 0
    while resonance_xp >= spent + resonance_cost_for_rank(rank + 1):
        spent += resonance_cost_for_rank(rank + 1)
        rank += 1
    return rank


def resonance_title(rank: int) -> str:
    titles = (
        "Verdächtig erfahren",
        "Akustisch auffällig",
        "Strukturell bedenklich",
        "Szenetechnisch unvermeidbar",
        "Amtlich nicht vorgesehen",
        "Physikalisch fragwürdig",
        "Betonhistorisch relevant",
        "Frequenztechnisch unvernünftig",
        "Legendenstatus",
        "Mythos",
    )
    if rank <= 0:
        return "Noch ohne Resonanz"
    if rank <= len(titles):
        return titles[rank - 1]
    return f"Mythos +{rank - 10}"


def apply_skill_xp(state: CharacterState, skill_id: str, amount: int) -> list[dict]:
    if skill_id not in state.skills:
        raise ValueError(f"Unbekannter Skill: {skill_id}")
    if amount < 0:
        raise ValueError("XP darf nicht negativ sein")

    events: list[dict] = []
    current_value = state.skills[skill_id]
    current_xp = state.skill_xp.get(skill_id, 0) + amount

    while current_value < ProgressionRules.skill_max:
        required = ProgressionRules.xp_to_next_skill(current_value)
        if current_xp < required:
            break
        current_xp -= required
        old = current_value
        current_value += 1
        events.append({"event_type": "character.skill_level_up", "payload": {"skill_id": skill_id, "old": old, "new": current_value}})

    state.skills[skill_id] = current_value
    state.skill_xp[skill_id] = current_xp
    state.total_xp += round(amount * ProgressionRules.total_xp_from_skill_xp_multiplier)
    old_level = state.level
    state.level = level_for_total_xp(state.total_xp)
    if state.level != old_level:
        events.append({"event_type": "character.level_up", "payload": {"old": old_level, "new": state.level}})

    level_50_xp = ProgressionRules.total_xp_for_level(50)
    old_resonance_rank = state.resonance_rank
    state.resonance_xp = max(0, state.total_xp - level_50_xp)
    state.resonance_rank = resonance_rank_for_xp(state.resonance_xp)
    if state.resonance_rank > old_resonance_rank:
        events.append({
            "event_type": "character.resonance_rank_up",
            "payload": {
                "old": old_resonance_rank,
                "new": state.resonance_rank,
                "resonance_xp": state.resonance_xp,
                "title": resonance_title(state.resonance_rank),
            },
        })
    return events


def add_trait_evidence(state: CharacterState, family: str, amount: float, source: str) -> list[dict]:
    if amount < 0:
        raise ValueError("Trait-Evidenz darf nicht negativ sein")
    if not source:
        raise ValueError("Trait-Evidenz benötigt eine Quelle")
    progress = state.trait_progress.setdefault(family, {"evidence": 0.0, "qualifying_events": 0, "sources": []})
    progress["evidence"] = round(float(progress["evidence"]) + amount, 6)
    progress["qualifying_events"] = int(progress["qualifying_events"]) + 1
    sources = set(progress.get("sources", []))
    sources.add(source)
    progress["sources"] = sorted(sources)
    state.trait_evidence[family] = progress["evidence"]

    old_tier = int(state.traits.get(family, 0))
    new_tier = old_tier
    for tier, min_evidence, min_level, min_events, min_sources in ProgressionRules.trait_tiers:
        if (
            progress["evidence"] >= min_evidence
            and state.level >= min_level
            and progress["qualifying_events"] >= min_events
            and len(progress["sources"]) >= min_sources
        ):
            new_tier = tier
    if new_tier <= old_tier:
        return []
    state.traits[family] = new_tier
    event_type = "character.trait_unlocked" if old_tier == 0 else "character.trait_tier_up"
    return [{"event_type": event_type, "payload": {"family": family, "old_tier": old_tier, "new_tier": new_tier}}]


SPECIALIZATIONS = {
    "spec.klangarchitektur": ("technik", "musik", "konzentration"),
    "spec.einsatzleitung": ("organisation", "logistik", "risikoeinschaetzung", "kommunikation"),
    "spec.szenenetzwerk": ("kommunikation", "menschenkenntnis", "verhandlung", "szenewissen"),
    "spec.spurensuche": ("orientierung", "instinkt", "risikoeinschaetzung"),
    "spec.impro_werkstatt": ("handwerk", "improvisation", "kreativitaet", "technik"),
    "spec.crew_stabilitaet": ("belastbarkeit", "menschenkenntnis", "kommunikation", "konzentration"),
}

SPECIALIZATION_STAGES = (
    ("meisterschaft", 42, 50.0, 8.0),
    ("identitaet", 30, 36.0, 6.0),
    ("profil", 18, 26.0, 4.0),
    ("tendenz", 10, 18.0, 2.0),
)


def evaluate_specialization(state: CharacterState) -> list[dict]:
    all_average = sum(state.skills.values()) / len(state.skills)
    candidates: list[tuple[float, str, str]] = []
    for spec_id, focus_skills in SPECIALIZATIONS.items():
        focus_average = sum(state.skills[s] for s in focus_skills) / len(focus_skills)
        advantage = focus_average - all_average
        stage = None
        for stage_name, min_level, min_focus, min_advantage in SPECIALIZATION_STAGES:
            if state.level >= min_level and focus_average >= min_focus and advantage >= min_advantage:
                stage = stage_name
                break
        if stage:
            candidates.append((focus_average, spec_id, stage))

    new_value = None
    if candidates:
        _, spec_id, stage = max(candidates)
        new_value = {"specialization_id": spec_id, "stage": stage}
    if new_value == state.specialization:
        return []
    old = state.specialization
    state.specialization = new_value
    if old is None and new_value is None:
        return []
    return [{"event_type": "character.specialization_changed", "payload": {"old": old, "new": new_value}}]


SPECIALIZATION_XP_EFFECTS = {
    "tendenz": (0.02, 0.0),
    "profil": (0.05, -0.01),
    "identitaet": (0.08, -0.03),
    "meisterschaft": (0.12, -0.05),
}


def specialization_xp_multiplier(state: CharacterState, skill_id: str) -> float:
    if not state.specialization:
        return 1.0
    spec_id = state.specialization.get("specialization_id")
    stage = state.specialization.get("stage")
    if spec_id not in SPECIALIZATIONS or stage not in SPECIALIZATION_XP_EFFECTS:
        return 1.0
    focus_bonus, outside_penalty = SPECIALIZATION_XP_EFFECTS[stage]
    return 1.0 + (focus_bonus if skill_id in SPECIALIZATIONS[spec_id] else outside_penalty)
