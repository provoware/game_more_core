from __future__ import annotations

from typing import Any, Mapping, Sequence

from ._shared import with_visible_keys


class BiographyTimeline:
    def build(
        self,
        biography: Sequence[Mapping[str, Any]],
        text_catalog: Mapping[str, str],
        local_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        category = (local_state or {}).get("category", "all")
        entries = biography if category == "all" else [entry for entry in biography if entry["category"] == category]
        return {
            "entries": [with_visible_keys(entry, text_catalog) for entry in entries],
            "category": category,
        }
