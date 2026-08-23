from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


CREW_IDENTITY_MODES = ("logo", "flag")
CREW_IDENTITY_STYLES = ("solid", "split", "band", "diagonal")
CREW_IDENTITY_SYMBOLS = ("bolt", "wave", "speaker", "tower", "star")
CREW_IDENTITY_COLORS = {
    "concrete": "#5e6670",
    "black": "#101114",
    "signal_orange": "#ff5a1f",
    "acid_green": "#a8ff3e",
    "electric_blue": "#35b8ff",
    "hot_pink": "#ff4fa3",
    "warm_white": "#f2eee3",
    "warning_yellow": "#ffd447",
}
CREW_IDENTITY_MARK_MAX_LENGTH = 4

_DEFAULT_CREW_IDENTITY = {
    "mode": "flag",
    "style": "split",
    "symbol": "wave",
    "primary_color_id": "black",
    "secondary_color_id": "concrete",
    "accent_color_id": "signal_orange",
    "mark": "",
}


def default_crew_identity() -> dict[str, str]:
    return deepcopy(_DEFAULT_CREW_IDENTITY)


def normalize_crew_identity(value: Mapping[str, Any] | None) -> dict[str, str]:
    if value is None:
        return default_crew_identity()
    if not isinstance(value, Mapping):
        raise ValueError("Crew-Identität muss ein Objekt sein")

    expected = set(_DEFAULT_CREW_IDENTITY)
    unknown = set(value) - expected
    missing = expected - set(value)
    if unknown:
        raise ValueError(f"Unbekannte Crew-Identitätsfelder: {', '.join(sorted(str(item) for item in unknown))}")
    if missing:
        raise ValueError(f"Fehlende Crew-Identitätsfelder: {', '.join(sorted(missing))}")

    result: dict[str, str] = {}
    for key in expected:
        raw = value.get(key)
        if not isinstance(raw, str):
            raise ValueError(f"Crew-Identitätsfeld {key} muss Text sein")
        result[key] = raw.strip()

    if result["mode"] not in CREW_IDENTITY_MODES:
        raise ValueError("Unbekannter Crew-Identitätsmodus")
    if result["style"] not in CREW_IDENTITY_STYLES:
        raise ValueError("Unbekannter Crew-Identitätsstil")
    if result["symbol"] not in CREW_IDENTITY_SYMBOLS:
        raise ValueError("Unbekanntes Crew-Identitätssymbol")
    for key in ("primary_color_id", "secondary_color_id", "accent_color_id"):
        if result[key] not in CREW_IDENTITY_COLORS:
            raise ValueError(f"Unbekannte Crew-Identitätsfarbe in {key}")

    mark = result["mark"].upper()
    if len(mark) > CREW_IDENTITY_MARK_MAX_LENGTH:
        raise ValueError(f"Crew-Kurzmarke darf höchstens {CREW_IDENTITY_MARK_MAX_LENGTH} Zeichen lang sein")
    if mark and not all(character.isalnum() or character in {"-", "+"} for character in mark):
        raise ValueError("Crew-Kurzmarke erlaubt nur Buchstaben, Zahlen, - und +")
    result["mark"] = mark
    return result
