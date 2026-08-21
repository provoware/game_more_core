from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

START_SKILLS = (
    "technik", "musik", "organisation", "kreativitaet", "kommunikation",
    "menschenkenntnis", "orientierung", "handwerk", "logistik",
    "improvisation", "verhandlung", "szenewissen", "risikoeinschaetzung",
    "konzentration", "belastbarkeit", "instinkt",
)


def initial_skills(value: int = 10) -> dict[str, int]:
    return {skill: value for skill in START_SKILLS}


@dataclass(slots=True)
class CharacterState:
    character_id: str
    display_name: str
    alias: str = ""
    motto: str = ""
    level: int = 1
    total_xp: int = 0
    resonance_xp: int = 0
    resonance_rank: int = 0
    skills: dict[str, int] = field(default_factory=initial_skills)
    skill_xp: dict[str, int] = field(default_factory=dict)
    trait_evidence: dict[str, float] = field(default_factory=dict)
    trait_progress: dict[str, dict[str, Any]] = field(default_factory=dict)
    traits: dict[str, int] = field(default_factory=dict)
    specialization: dict[str, Any] | None = None
    energy: int = 100
    stress: int = 0
    reputation: int = 0

    def validate(self) -> None:
        if not self.character_id:
            raise ValueError("character_id fehlt")
        if set(self.skills) != set(START_SKILLS):
            raise ValueError("Skill-Satz ist unvollständig oder enthält unbekannte Skills")
        if any(not 10 <= value <= 100 for value in self.skills.values()):
            raise ValueError("Skillwert außerhalb 10..100")
        if self.level < 1 or self.total_xp < 0 or self.resonance_xp < 0 or self.resonance_rank < 0:
            raise ValueError("Ungültiger Fortschrittsstand")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "character_id": self.character_id,
            "display_name": self.display_name,
            "alias": self.alias,
            "motto": self.motto,
            "level": self.level,
            "total_xp": self.total_xp,
            "resonance_xp": self.resonance_xp,
            "resonance_rank": self.resonance_rank,
            "skills": dict(self.skills),
            "skill_xp": dict(self.skill_xp),
            "trait_evidence": dict(self.trait_evidence),
            "trait_progress": {k: dict(v) for k, v in self.trait_progress.items()},
            "traits": dict(self.traits),
            "specialization": self.specialization,
            "energy": self.energy,
            "stress": self.stress,
            "reputation": self.reputation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterState":
        state = cls(
            character_id=data["character_id"],
            display_name=data["display_name"],
            alias=data.get("alias", ""),
            motto=data.get("motto", ""),
            level=int(data.get("level", 1)),
            total_xp=int(data.get("total_xp", 0)),
            resonance_xp=int(data.get("resonance_xp", 0)),
            resonance_rank=int(data.get("resonance_rank", 0)),
            skills={k: int(v) for k, v in data.get("skills", initial_skills()).items()},
            skill_xp={k: int(v) for k, v in data.get("skill_xp", {}).items()},
            trait_evidence={k: float(v) for k, v in data.get("trait_evidence", {}).items()},
            trait_progress={k: dict(v) for k, v in data.get("trait_progress", {}).items()},
            traits={k: int(v) for k, v in data.get("traits", {}).items()},
            specialization=data.get("specialization"),
            energy=int(data.get("energy", 100)),
            stress=int(data.get("stress", 0)),
            reputation=int(data.get("reputation", 0)),
        )
        state.validate()
        return state
