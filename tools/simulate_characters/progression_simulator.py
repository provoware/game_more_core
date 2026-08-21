#!/usr/bin/env python3
"""Deterministischer Progression-Simulator für BUNKERFREQUENZ 0.4.1.

Nur Standardbibliothek. Keine Spiel-Runtime.
Zweck: Balancing-Regeln reproduzierbar prüfen, bevor Character-Core-Code entsteht.
"""

from __future__ import annotations
import argparse
import collections
import json
import random
import statistics
from pathlib import Path

SKILLS = [
    "technik","musik","organisation","kreativitaet","kommunikation","menschenkenntnis",
    "orientierung","handwerk","logistik","improvisation","verhandlung","szenewissen",
    "risikoeinschaetzung","konzentration","belastbarkeit","instinkt",
]

ARCHETYPES = {
    "generalist": {"skills": SKILLS, "traits": []},
    "audio": {"skills": ["technik","musik","konzentration"], "traits": ["klangfokus","detailmensch","nachtmensch","ausdauer"]},
    "organisation": {"skills": ["organisation","logistik","risikoeinschaetzung","kommunikation"], "traits": ["planer","verhandler","detailmensch","crew_anker"]},
    "netzwerk": {"skills": ["kommunikation","menschenkenntnis","verhandlung","szenewissen"], "traits": ["vernetzer","verhandler","crew_anker","opportunist"]},
    "erkundung": {"skills": ["orientierung","instinkt","risikoeinschaetzung"], "traits": ["scout","opportunist","nachtmensch","risikospieler"]},
    "impro": {"skills": ["handwerk","improvisation","kreativitaet","technik"], "traits": ["improvisierer","kreativer","risikospieler","ausdauer"]},
    "stabilitaet": {"skills": ["belastbarkeit","menschenkenntnis","kommunikation","konzentration"], "traits": ["krisenfest","ausdauer","crew_anker","detailmensch"]},
}

SOURCE_PROBABILITIES = [
    ("practice", 0.44), ("training", 0.20), ("team", 0.10), ("crisis", 0.08),
    ("discovery", 0.07), ("success", 0.08), ("failure", 0.03),
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def level_threshold(level: int) -> float:
    if level <= 1:
        return 0.0
    return 120 * (level - 1) ** 1.62 + 80 * (level - 1)


def level_for_xp(total_xp: float) -> int:
    level = 1
    while level < 50 and total_xp >= level_threshold(level + 1):
        level += 1
    return level


def xp_to_next(value: int) -> int:
    return round(70 + 5.5 * max(0, value - 10) ** 1.28)


def weighted_choice(rng: random.Random, pairs: list[tuple[str, float]]) -> str:
    roll = rng.random()
    cumulative = 0.0
    for name, probability in pairs:
        cumulative += probability
        if roll <= cumulative:
            return name
    return pairs[-1][0]


def choose_focus(rng: random.Random, focus: list[str], all_items: list[str], focus_probability: float) -> str:
    if focus and rng.random() < focus_probability:
        return rng.choice(focus)
    return rng.choice(all_items)


def trait_tier(evidence: float, events: int, distinct_sources: int, level: int, engine: dict) -> int:
    tier = 0
    for rule in engine["tier_rules"]:
        if (
            evidence >= rule["min_evidence"]
            and events >= rule["min_qualifying_events"]
            and distinct_sources >= rule["min_distinct_sources"]
            and level >= rule["min_character_level"]
        ):
            tier = rule["tier"]
    return tier


def specialization(skill_values: dict[str, int], level: int, progression: dict) -> dict | None:
    model = progression["specialization_model"]
    all_average = statistics.fmean(skill_values.values())
    candidates = []
    for spec in model["specializations"]:
        focus_average = statistics.fmean(skill_values[s] for s in spec["focus_skills"])
        advantage = focus_average - all_average
        stage = None
        for rule in model["stages"]:
            if (
                level >= rule["min_level"]
                and focus_average >= rule["min_focus_average"]
                and advantage >= rule["min_advantage_over_all_average"]
            ):
                stage = rule["stage"]
        if stage:
            score = focus_average + advantage * 1.5
            candidates.append((score, spec["specialization_id"], stage, focus_average, advantage))
    if not candidates:
        return None
    score, spec_id, stage, focus_average, advantage = max(candidates)
    return {
        "specialization_id": spec_id,
        "stage": stage,
        "score": round(score, 3),
        "focus_average": round(focus_average, 3),
        "advantage": round(advantage, 3),
    }


def simulate_character(rng: random.Random, days: int, engine: dict, progression: dict, archetype: str) -> dict:
    templates = [e["effect_template_id"].split(".")[-1] for e in engine["effect_templates"]]
    focus = ARCHETYPES[archetype]
    trait_focus = focus["traits"] or templates

    skill_values = {skill: 10 for skill in SKILLS}
    skill_xp = {skill: 0.0 for skill in SKILLS}
    trait_evidence = {name: 0.0 for name in templates}
    trait_events = {name: 0 for name in templates}
    trait_sources = {name: set() for name in templates}
    total_xp = 0.0

    source_factors = engine["evidence_sources"]
    repeat = engine["same_day_repetition_factors"]
    training_effectiveness = progression["action_xp"]["training_daily_effectiveness"]
    source_skill_mult = progression["action_xp"]["source_multipliers"]
    total_xp_mult = progression["action_xp"]["total_character_xp_from_skill_xp_multiplier"]

    for _day in range(days):
        day_trait_count = collections.Counter()
        training_count = 0
        for _action in range(3):
            source = weighted_choice(rng, SOURCE_PROBABILITIES)
            if source == "training":
                training_count += 1

            skill = choose_focus(rng, focus["skills"], SKILLS, 0.80)
            template = choose_focus(rng, trait_focus, templates, 0.80 if archetype != "generalist" else 0.0)

            repeat_factor = repeat[min(day_trait_count[template], len(repeat) - 1)]
            day_trait_count[template] += 1

            quality = rng.uniform(0.85, 1.15)
            difficulty = rng.uniform(0.85, 1.20)
            novelty = rng.uniform(0.75, 1.05)

            evidence = 5.0 * source_factors[source] * quality * difficulty * novelty * repeat_factor
            trait_evidence[template] += evidence
            trait_events[template] += 1
            trait_sources[template].add(source)

            skill_gain = rng.uniform(*progression["action_xp"]["base_range"]) * difficulty * quality
            if source == "training":
                effectiveness = training_effectiveness[min(training_count - 1, len(training_effectiveness) - 1)]
                skill_gain *= effectiveness
            else:
                skill_gain *= source_skill_mult[source]

            skill_xp[skill] += skill_gain
            while skill_values[skill] < progression["skill_value"]["max"] and skill_xp[skill] >= xp_to_next(skill_values[skill]):
                skill_xp[skill] -= xp_to_next(skill_values[skill])
                skill_values[skill] += 1

            total_xp += skill_gain * total_xp_mult

        if rng.random() < 0.10:
            total_xp += rng.uniform(60, 180)

    level = level_for_xp(total_xp)
    tiers = {
        name: trait_tier(trait_evidence[name], trait_events[name], len(trait_sources[name]), level, engine)
        for name in templates
    }
    return {
        "archetype": archetype,
        "level": level,
        "active_traits": sum(t > 0 for t in tiers.values()),
        "tier3_plus": sum(t >= 3 for t in tiers.values()),
        "tier5": sum(t >= 5 for t in tiers.values()),
        "tiers": tiers,
        "skill_values": skill_values,
        "specialization": specialization(skill_values, level, progression),
    }


def run_simulation(runs: int, days: int, seed: int, engine: dict, progression: dict) -> dict:
    results = []
    archetype_names = list(ARCHETYPES)
    for index in range(runs):
        rng = random.Random(seed + index)
        archetype = archetype_names[index % len(archetype_names)]
        results.append(simulate_character(rng, days, engine, progression, archetype))

    grouped = collections.defaultdict(list)
    for result in results:
        grouped[result["archetype"]].append(result)

    groups = {}
    for name, rows in grouped.items():
        groups[name] = {
            "runs": len(rows),
            "mean_level": round(statistics.fmean(r["level"] for r in rows), 3),
            "mean_active_traits": round(statistics.fmean(r["active_traits"] for r in rows), 3),
            "mean_tier3_plus": round(statistics.fmean(r["tier3_plus"] for r in rows), 3),
            "mean_tier5": round(statistics.fmean(r["tier5"] for r in rows), 3),
            "specialization_rate": round(sum(r["specialization"] is not None for r in rows) / len(rows), 4),
        }

    overall = {
        "runs": runs,
        "days": days,
        "seed": seed,
        "mean_level": round(statistics.fmean(r["level"] for r in results), 3),
        "min_level": min(r["level"] for r in results),
        "max_level": max(r["level"] for r in results),
        "mean_active_traits": round(statistics.fmean(r["active_traits"] for r in results), 3),
        "mean_tier3_plus": round(statistics.fmean(r["tier3_plus"] for r in results), 3),
        "mean_tier5": round(statistics.fmean(r["tier5"] for r in results), 3),
    }

    checks = {
        "generalist_has_no_forced_specialization": groups["generalist"]["specialization_rate"] <= 0.05,
        "specialists_form_specialization": min(data["specialization_rate"] for key, data in groups.items() if key != "generalist") >= 0.90,
        "specialists_develop_deep_traits": min(data["mean_tier3_plus"] for key, data in groups.items() if key != "generalist") >= 3.0,
        "generalist_stays_broad_not_deep": groups["generalist"]["mean_tier3_plus"] <= 1.0,
        "tier5_not_mass_unlocked": overall["mean_tier5"] <= 2.0,
        "level_progression_not_capped": overall["max_level"] < 50,
    }
    return {"version": "0.4.1-alpha.1", "overall": overall, "groups": groups, "checks": checks, "passed": all(checks.values())}


def validate_manifests(engine: dict, progression: dict) -> list[str]:
    errors = []
    templates = engine["effect_templates"]
    ids = [row["effect_template_id"] for row in templates]
    if len(ids) != 15 or len(ids) != len(set(ids)):
        errors.append("Es müssen exakt 15 eindeutige Trait-Effektvorlagen vorhanden sein.")
    thresholds = [row["min_evidence"] for row in engine["tier_rules"]]
    if thresholds != sorted(thresholds) or len(thresholds) != 5:
        errors.append("Trait-Evidenzschwellen müssen fünf strikt aufsteigende Stufen bilden.")
    if progression["skill_value"]["min"] != 10 or progression["skill_value"]["max"] != 100:
        errors.append("Skillbereich muss für 0.4.1 bei 10 bis 100 liegen.")
    if not progression["specialization_model"]["specializations"]:
        errors.append("Mindestens eine Spezialisierung muss definiert sein.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Progression 0.4.1 simulieren")
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--days", type=int, default=720)
    parser.add_argument("--seed", type=int, default=90409)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    engine = load_json(args.repo_root / "manifests" / "TRAIT_ENGINE_MANIFEST.json")
    progression = load_json(args.repo_root / "manifests" / "PROGRESSION_MANIFEST.json")

    errors = validate_manifests(engine, progression)
    if errors:
        print(json.dumps({"passed": False, "manifest_errors": errors}, ensure_ascii=False, indent=2))
        return 2

    report = run_simulation(args.runs, args.days, args.seed, engine, progression)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
