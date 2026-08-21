"""Shared read-only presentation contracts for Character Forge layouts."""

from .character_projection import build_character_projection
from .character_views import build_character_view

__all__ = ["build_character_projection", "build_character_view"]
