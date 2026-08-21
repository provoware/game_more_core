"""Shared presentation boundary for Character Forge layouts."""

from .a4_ops_deck import build_a4_ops_deck
from .command_adapter import PresentationCommandAdapter
from .projection import build_character_projection
from .state import PresentationState

__all__ = (
    "PresentationCommandAdapter",
    "PresentationState",
    "build_a4_ops_deck",
    "build_character_projection",
)
