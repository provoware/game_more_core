from __future__ import annotations

from typing import Any, Mapping, Sequence

from ._shared import with_visible_keys


class SkillList:
    def build(
        self,
        skills: Sequence[Mapping[str, Any]],
        text_catalog: Mapping[str, str],
        local_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        local_state = local_state or {}
        return {
            "items": [with_visible_keys(skill, text_catalog) for skill in skills],
            "selected_skill_id": local_state.get("selected_skill_id"),
        }
