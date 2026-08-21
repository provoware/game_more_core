from __future__ import annotations

from typing import Any, Mapping


class StatusSummary:
    def build(self, overview: Mapping[str, Any], local_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
        local_state = local_state or {}
        return {
            "level": overview["level"],
            "total_xp": overview["total_xp"],
            "resonance_xp": overview["resonance_xp"],
            "resonance_rank": overview["resonance_rank"],
            "energy": overview["energy"],
            "stress": overview["stress"],
            "reputation": overview["reputation"],
            "expanded": bool(local_state.get("expanded", False)),
        }
