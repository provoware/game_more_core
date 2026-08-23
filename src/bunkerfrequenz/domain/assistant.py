from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AssistantControlState:
    """Persisted user choice for the assistant; execution belongs to a later slice."""

    active_job_id: str | None = None
    revision: int = 0

    def validate(self) -> None:
        if self.active_job_id is not None and (
            not isinstance(self.active_job_id, str) or not self.active_job_id.strip()
        ):
            raise ValueError("assistant.active_job_id muss Text oder null sein")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("assistant.revision muss Ganzzahl >= 0 sein")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "active_job_id": self.active_job_id,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AssistantControlState":
        raw = data or {}
        state = cls(
            active_job_id=raw.get("active_job_id"),
            revision=raw.get("revision", 0),
        )
        state.validate()
        return state
