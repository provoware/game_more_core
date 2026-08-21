from __future__ import annotations

from typing import Any, Mapping

from ._shared import copied


class CharacterHeader:
    def build(self, overview: Mapping[str, Any], local_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
        local_state = local_state or {}
        return {
            "display_name": overview["display_name"],
            "alias": overview.get("alias"),
            "additional_nicknames": copied(overview.get("additional_nicknames", [])),
            "motto": overview.get("motto"),
            "compact": bool(local_state.get("compact", False)),
        }
