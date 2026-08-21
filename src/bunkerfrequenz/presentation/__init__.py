"""Read-only presentation projections."""

from bunkerfrequenz.presentation.biography_projection import build_biography_projection

__all__ = ["build_biography_projection"]
"""Read-only presentation projections for shared user interfaces."""

from .character_projection import build_character_projection

__all__ = ["build_character_projection"]
