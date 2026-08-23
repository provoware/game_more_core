from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AssistantState:
    active_task_id: str | None = None
    last_completed_round_id: str | None = None
    completed_rounds: int = 0
    revision: int = 0

    def validate(self) -> None:
        for name, value in (
            ("active_task_id", self.active_task_id),
            ("last_completed_round_id", self.last_completed_round_id),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} muss nicht-leerer Text oder null sein")
        for name, value in (("completed_rounds", self.completed_rounds), ("revision", self.revision)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} muss Ganzzahl >= 0 sein")
        if self.completed_rounds > self.revision:
            raise ValueError("completed_rounds darf Revision nicht übersteigen")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "active_task_id": self.active_task_id,
            "last_completed_round_id": self.last_completed_round_id,
            "completed_rounds": self.completed_rounds,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AssistantState":
        raw = data or {}
        state = cls(
            active_task_id=raw.get("active_task_id"),
            last_completed_round_id=raw.get("last_completed_round_id"),
            completed_rounds=raw.get("completed_rounds", 0),
            revision=raw.get("revision", 0),
        )
        state.validate()
        return state
