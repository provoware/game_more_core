from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence


def iter_text_keys(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for field, child in value.items():
            if isinstance(field, str) and field.endswith("_key") and isinstance(child, str):
                yield child
            else:
                yield from iter_text_keys(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield from iter_text_keys(child)


def require_text_keys(
    value: Any,
    text_catalog: Mapping[str, str],
    *,
    context: str = "Presentation",
) -> None:
    missing = sorted({key for key in iter_text_keys(value) if key not in text_catalog})
    if missing:
        raise KeyError(f"Fehlende {context}-Textschlüssel: {', '.join(missing)}")
