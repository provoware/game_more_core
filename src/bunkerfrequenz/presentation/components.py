from __future__ import annotations

from typing import Callable


COMPONENT_NAMES = (
    "CharacterHeader", "StatusSummary", "SkillList", "TraitList",
    "SpecializationCard", "BiographyTimeline", "ProfileEditor", "ProgressFeedback",
)


def _component(name: str, data, *, focusable: bool = False) -> dict:
    return {"component": name, "data": data, "focusable": focusable}


def build_components(projection: dict, biography_filter: str) -> dict[str, dict]:
    biography = projection["biography"]
    if biography_filter != "all":
        biography = [row for row in biography if row["category"] == biography_filter]
    builders: dict[str, Callable[[], dict]] = {
        "CharacterHeader": lambda: _component("CharacterHeader", projection["overview"]),
        "StatusSummary": lambda: _component("StatusSummary", projection["top_skills"]),
        "SkillList": lambda: _component("SkillList", projection["skills"]),
        "TraitList": lambda: _component("TraitList", projection["traits"]),
        "SpecializationCard": lambda: _component("SpecializationCard", projection["specialization"]),
        "BiographyTimeline": lambda: _component("BiographyTimeline", biography),
        "ProfileEditor": lambda: _component("ProfileEditor", projection["overview"], focusable=True),
        "ProgressFeedback": lambda: _component("ProgressFeedback", projection["feedback"], focusable=True),
    }
    return {name: builders[name]() for name in COMPONENT_NAMES}
