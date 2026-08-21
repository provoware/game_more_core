from __future__ import annotations

from typing import Any, Protocol


class PresentationAdapter(Protocol):
    """Zentrale Schreibgrenze zwischen Presentation und Application."""

    def dispatch(self, command: dict[str, Any]) -> Any:
        ...
