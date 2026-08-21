from __future__ import annotations

from typing import Any, Mapping

from ._shared import with_visible_keys


class SpecializationCard:
    def build(
        self,
        specialization: Mapping[str, Any] | None,
        text_catalog: Mapping[str, str],
        local_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "specialization": with_visible_keys(specialization, text_catalog) if specialization else None,
            "expanded": bool((local_state or {}).get("expanded", False)),
        }
