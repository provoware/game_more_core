from __future__ import annotations

from typing import Any, Mapping, Sequence

from ._shared import with_visible_keys


class ProgressFeedback:
    def build(
        self,
        feedback: Sequence[Mapping[str, Any]],
        text_catalog: Mapping[str, str],
        local_state: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        dismissed = set((local_state or {}).get("dismissed_feedback_ids", []))
        return {
            "items": [
                with_visible_keys(item, text_catalog)
                for item in feedback
                if item["feedback_id"] not in dismissed
            ]
        }
