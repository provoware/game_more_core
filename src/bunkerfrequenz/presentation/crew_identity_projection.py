from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from bunkerfrequenz.domain.crew_identity import (
    CREW_IDENTITY_COLORS,
    CREW_IDENTITY_MODES,
    CREW_IDENTITY_STYLES,
    CREW_IDENTITY_SYMBOLS,
    normalize_crew_identity,
)


_MODE_LABELS = {"logo": "Logo", "flag": "Fahne"}
_STYLE_LABELS = {
    "solid": "Vollfläche",
    "split": "Geteilt",
    "band": "Balken",
    "diagonal": "Diagonal",
}
_SYMBOL_LABELS = {
    "bolt": "Blitz",
    "wave": "Welle",
    "speaker": "Box",
    "tower": "Turm",
    "star": "Stern",
}
_SYMBOL_GLYPHS = {
    "bolt": "ϟ",
    "wave": "≈",
    "speaker": "▣",
    "tower": "♜",
    "star": "★",
}
_COLOR_LABELS = {
    "concrete": "Beton",
    "black": "Schwarz",
    "signal_orange": "Signalorange",
    "acid_green": "Acidgrün",
    "electric_blue": "Elektroblau",
    "hot_pink": "Hot Pink",
    "warm_white": "Warmweiß",
    "warning_yellow": "Warnungsgelb",
}


def build_crew_identity_projection(identity: Mapping[str, Any] | None) -> dict[str, Any]:
    normalized = normalize_crew_identity(identity)
    return {
        "identity": deepcopy(normalized),
        "render": {
            "primary": CREW_IDENTITY_COLORS[normalized["primary_color_id"]],
            "secondary": CREW_IDENTITY_COLORS[normalized["secondary_color_id"]],
            "accent": CREW_IDENTITY_COLORS[normalized["accent_color_id"]],
            "symbol_glyph": _SYMBOL_GLYPHS[normalized["symbol"]],
        },
        "choices": {
            "modes": [{"id": item, "label": _MODE_LABELS[item]} for item in CREW_IDENTITY_MODES],
            "styles": [{"id": item, "label": _STYLE_LABELS[item]} for item in CREW_IDENTITY_STYLES],
            "symbols": [
                {"id": item, "label": _SYMBOL_LABELS[item], "glyph": _SYMBOL_GLYPHS[item]}
                for item in CREW_IDENTITY_SYMBOLS
            ],
            "colors": [
                {"id": item, "label": _COLOR_LABELS[item], "value": CREW_IDENTITY_COLORS[item]}
                for item in CREW_IDENTITY_COLORS
            ],
        },
        "sync_contract": {
            "image_blob_required": False,
            "stable_character_id_required": True,
            "field_set": sorted(normalized),
        },
    }
