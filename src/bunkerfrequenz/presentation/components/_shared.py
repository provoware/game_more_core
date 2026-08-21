from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


def copied(value: Any) -> Any:
    """Trennt ein View-Modell von der schreibgeschützten Projektion."""
    return deepcopy(value)


def visible_text(key: str | None, text_catalog: Mapping[str, str]) -> str | None:
    """Lässt fehlende Schlüssel für die Entwicklungsansicht sichtbar."""
    if key is None:
        return None
    return text_catalog.get(key, key)


def with_visible_keys(item: Mapping[str, Any], text_catalog: Mapping[str, str]) -> dict[str, Any]:
    result = copied(dict(item))
    for field in ("label_key", "stage_label_key", "title_key", "body_key", "effect_key", "consequence_key"):
        if field in item:
            result[field.removesuffix("_key")] = visible_text(item[field], text_catalog)
    if "detail_keys" in item:
        result["details"] = [visible_text(key, text_catalog) for key in item["detail_keys"]]
    return result
