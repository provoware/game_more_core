from __future__ import annotations

from typing import Any, Mapping, Sequence

from ._shared import with_visible_keys


class TraitList:
    def build(
        self,
        traits: Sequence[Mapping[str, Any]],
        text_catalog: Mapping[str, str],
        local_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        local_state = local_state or {}
        return {
            "items": [with_visible_keys(trait, text_catalog) for trait in traits],
            "selected_trait_id": local_state.get("selected_trait_id"),
        }
