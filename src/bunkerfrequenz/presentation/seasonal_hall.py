from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Mapping


_EXPECTED_CYCLE_TYPES = ("weekly", "monthly")
_EXPECTED_MODES = ("reputation", "level", "resonance")


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss nicht-leerer Text sein")
    return value.strip()


def _aware_datetime(value: Any, field: str) -> datetime:
    text = _text(value, field)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{field} muss gültiges ISO-8601 sein") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} benötigt einen UTC-Offset")
    return parsed


def _manifest_contract(
    season_manifest: Mapping[str, Any],
    hall_manifest: Mapping[str, Any],
    ranking_manifest: Mapping[str, Any],
    zeit_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    if season_manifest.get("version") != "0.8.7-a1":
        raise ValueError("Hall-Saison-Manifest besitzt unerwartete Version")
    if season_manifest.get("hall_manifest_version") != hall_manifest.get("version"):
        raise ValueError("Hall-Saison- und Hall-Vertrag passen nicht zusammen")
    if season_manifest.get("ranking_manifest_version") != ranking_manifest.get("version"):
        raise ValueError("Hall-Saison- und Ranking-Vertrag passen nicht zusammen")
    if season_manifest.get("zeit_manifest_version") != zeit_manifest.get("version"):
        raise ValueError("Hall-Saison- und Zeit-Vertrag passen nicht zusammen")
    if zeit_manifest.get("system_time_is_sole_authority") is not False:
        raise ValueError("Zeitvertrag muss Systemzeit als alleinige Autorität verbieten")
    if season_manifest.get("system_time_is_sole_authority") is not False:
        raise ValueError("Hall-Saison darf Systemzeit nicht als alleinige Autorität nutzen")

    cycle_types = season_manifest.get("cycle_types")
    if cycle_types != list(_EXPECTED_CYCLE_TYPES):
        raise ValueError("Hall-Saison benötigt weekly und monthly als Zyklustypen")
    if season_manifest.get("default_cycle_type") not in _EXPECTED_CYCLE_TYPES:
        raise ValueError("Hall-Saison besitzt ungültigen Default-Zyklus")

    allowed_authorities = season_manifest.get("allowed_authorities")
    if not isinstance(allowed_authorities, list) or not allowed_authorities:
        raise ValueError("Hall-Saison benötigt bestätigte Zeitautoritäten")
    allowed = frozenset(_text(value, "allowed_authority") for value in allowed_authorities)
    if "system_time" in allowed:
        raise ValueError("system_time darf keine bestätigte Saisonautorität sein")
    zeit_sources = zeit_manifest.get("sources")
    if not isinstance(zeit_sources, list) or not allowed.issubset(set(zeit_sources)):
        raise ValueError("Hall-Saison verwendet eine nicht katalogisierte Zeitquelle")

    title_policy = season_manifest.get("title_policy")
    if not isinstance(title_policy, Mapping):
        raise ValueError("Hall-Saison benötigt title_policy")
    if title_policy.get("requires_closed_cycle") is not True:
        raise ValueError("Saisontitel dürfen nur aus geschlossenem Zyklus entstehen")
    if title_policy.get("requires_confirmed_competition") is not True:
        raise ValueError("Saisontitel benötigen bestätigte Konkurrenz")
    minimum = title_policy.get("minimum_confirmed_participants")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 2:
        raise ValueError("Saisontitel benötigen mindestens zwei bestätigte Teilnehmer")
    if title_policy.get("rank_required") != 1:
        raise ValueError("Saisontitel benötigen Rang 1")

    titles = title_policy.get("titles")
    if not isinstance(titles, Mapping) or set(titles) != set(_EXPECTED_CYCLE_TYPES):
        raise ValueError("Saisontitel müssen weekly und monthly abdecken")
    normalized_titles: dict[str, dict[str, str]] = {}
    for cycle_type in _EXPECTED_CYCLE_TYPES:
        cycle_titles = titles.get(cycle_type)
        if not isinstance(cycle_titles, Mapping) or set(cycle_titles) != set(_EXPECTED_MODES):
            raise ValueError("Saisontitel müssen alle Hall-Modi abdecken")
        normalized_titles[cycle_type] = {
            mode: _text(cycle_titles[mode], f"title.{cycle_type}.{mode}")
            for mode in _EXPECTED_MODES
        }

    grand = title_policy.get("grand_title")
    if not isinstance(grand, Mapping):
        raise ValueError("Hall-Saison benötigt grand_title-Vertrag")
    if grand.get("cycle_type") != "monthly":
        raise ValueError("Grand Title ist an Monatszyklus gebunden")
    if grand.get("requires_first_place_in_modes") != list(_EXPECTED_MODES):
        raise ValueError("Grand Title benötigt Rang 1 in allen drei Hall-Modi")
    grand_title = _text(grand.get("title"), "grand_title.title")

    return {
        "allowed_authorities": allowed,
        "minimum_participants": minimum,
        "titles": normalized_titles,
        "grand_title": grand_title,
        "default_cycle_type": season_manifest["default_cycle_type"],
    }


def _cycle_id(cycle_type: str, anchor: datetime) -> str:
    if cycle_type == "weekly":
        iso_year, iso_week, _ = anchor.isocalendar()
        return f"week:{iso_year}-W{iso_week:02d}"
    if cycle_type == "monthly":
        return f"month:{anchor.year:04d}-{anchor.month:02d}"
    raise ValueError("Unbekannter Hall-Saison-Zyklustyp")


def _normalize_cycle_context(
    raw: Mapping[str, Any],
    *,
    allowed_authorities: frozenset[str],
) -> dict[str, Any]:
    expected_fields = {
        "cycle_id", "cycle_type", "authority", "anchor_at", "closed", "confirmation_id"
    }
    if set(raw) != expected_fields:
        raise ValueError("Bestätigter Saisonkontext besitzt unerwartete Felder")
    cycle_type = _text(raw.get("cycle_type"), "cycle_type")
    if cycle_type not in _EXPECTED_CYCLE_TYPES:
        raise ValueError("cycle_type muss weekly oder monthly sein")
    authority = _text(raw.get("authority"), "authority")
    if authority not in allowed_authorities:
        raise ValueError("Saisonkontext besitzt keine bestätigte Zeitautorität")
    anchor = _aware_datetime(raw.get("anchor_at"), "anchor_at")
    cycle_id = _text(raw.get("cycle_id"), "cycle_id")
    if cycle_id != _cycle_id(cycle_type, anchor):
        raise ValueError("cycle_id passt nicht zum bestätigten Zyklusanker")
    closed = raw.get("closed")
    if not isinstance(closed, bool):
        raise ValueError("closed muss bool sein")
    confirmation_id = _text(raw.get("confirmation_id"), "confirmation_id")
    return {
        "cycle_id": cycle_id,
        "cycle_type": cycle_type,
        "authority": authority,
        "anchor_at": anchor.isoformat(),
        "closed": closed,
        "confirmation_id": confirmation_id,
    }


def derive_cycle_contexts_from_completed_event(
    event: Mapping[str, Any] | None,
    *,
    season_manifest: Mapping[str, Any],
    hall_manifest: Mapping[str, Any],
    ranking_manifest: Mapping[str, Any],
    zeit_manifest: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    """Derive stable local cycle anchors from a confirmed completed event.

    No wall clock is read. The persisted event time window is the game-world
    authority. Locally derived cycles are deliberately not marked closed.
    """
    contract = _manifest_contract(season_manifest, hall_manifest, ranking_manifest, zeit_manifest)
    if event is None:
        return {}
    if not isinstance(event, Mapping):
        raise ValueError("Event für Hall-Saison muss Mapping sein")
    anchor_policy = season_manifest.get("local_event_anchor")
    if not isinstance(anchor_policy, Mapping) or anchor_policy.get("allowed") is not True:
        return {}
    if event.get("phase") != anchor_policy.get("requires_event_phase"):
        return {}
    window = event.get("time_window")
    if not isinstance(window, Mapping):
        raise ValueError("Abgeschlossenes Event benötigt Zeitfenster für Saisonanker")
    anchor = _aware_datetime(window.get("start_local"), "event.time_window.start_local")
    event_id = _text(event.get("event_id"), "event.event_id")
    revision = event.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError("event.revision muss nichtnegative Ganzzahl sein")
    authority = anchor_policy.get("authority")
    if authority not in contract["allowed_authorities"]:
        raise ValueError("Lokaler Event-Anker besitzt keine erlaubte Zeitautorität")
    closed = anchor_policy.get("cycle_closed")
    if closed is not False:
        raise ValueError("Lokaler Event-Anker darf Zyklus nicht selbst schließen")
    confirmation_id = f"event:{event_id}:revision:{revision}"
    return {
        cycle_type: {
            "cycle_id": _cycle_id(cycle_type, anchor),
            "cycle_type": cycle_type,
            "authority": authority,
            "anchor_at": anchor.isoformat(),
            "closed": False,
            "confirmation_id": confirmation_id,
        }
        for cycle_type in _EXPECTED_CYCLE_TYPES
    }


def _leader(board: Mapping[str, Any]) -> dict[str, Any] | None:
    entries = board.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Hall-Board benötigt entries")
    first = next((entry for entry in entries if entry.get("rank") == 1), None)
    if first is None:
        return None
    metric = first.get("selected_metric")
    if not isinstance(metric, Mapping) or metric.get("available") is not True:
        return None
    return {
        "character_id": _text(first.get("character_id"), "leader.character_id"),
        "display_name": first.get("display_name"),
        "alias": first.get("alias"),
        "value": metric.get("value"),
        "rank": 1,
    }


def build_seasonal_hall_projection(
    hall_projection: Mapping[str, Any] | None,
    *,
    season_manifest: Mapping[str, Any],
    hall_manifest: Mapping[str, Any],
    ranking_manifest: Mapping[str, Any],
    zeit_manifest: Mapping[str, Any],
    confirmed_cycle_contexts: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any] | None:
    """Decorate existing Hall boards with confirmed season metadata and titles."""
    contract = _manifest_contract(season_manifest, hall_manifest, ranking_manifest, zeit_manifest)
    if hall_projection is None:
        return None
    if not isinstance(hall_projection, Mapping):
        raise ValueError("Hall-Projection muss Mapping sein")
    boards = hall_projection.get("boards")
    if not isinstance(boards, Mapping) or set(boards) != set(_EXPECTED_MODES):
        raise ValueError("Hall-Saison benötigt die drei kanonischen Hall-Boards")
    local_character_id = _text(hall_projection.get("local_character_id"), "local_character_id")
    participant_count = hall_projection.get("confirmed_participant_count")
    if isinstance(participant_count, bool) or not isinstance(participant_count, int) or participant_count < 1:
        raise ValueError("Hall-Saison benötigt bestätigte Teilnehmerzahl")

    raw_contexts = confirmed_cycle_contexts or {}
    if not isinstance(raw_contexts, Mapping):
        raise ValueError("confirmed_cycle_contexts muss Mapping sein")
    unknown = set(raw_contexts) - set(_EXPECTED_CYCLE_TYPES)
    if unknown:
        raise ValueError("Bestätigte Saisonkontexte enthalten unbekannten Zyklustyp")

    normalized: dict[str, dict[str, Any]] = {}
    seen_cycle_ids: set[str] = set()
    for cycle_type in _EXPECTED_CYCLE_TYPES:
        raw = raw_contexts.get(cycle_type)
        if raw is None:
            continue
        context = _normalize_cycle_context(
            raw,
            allowed_authorities=contract["allowed_authorities"],
        )
        if context["cycle_type"] != cycle_type:
            raise ValueError("Saisonkontext ist unter falschem Zyklustyp abgelegt")
        if context["cycle_id"] in seen_cycle_ids:
            raise ValueError("cycle_id darf nicht doppelt verwendet werden")
        seen_cycle_ids.add(context["cycle_id"])
        normalized[cycle_type] = context

    cycles: dict[str, Any] = {}
    local_titles: list[dict[str, Any]] = []
    for cycle_type in _EXPECTED_CYCLE_TYPES:
        context = normalized.get(cycle_type)
        if context is None:
            continue
        title_allowed = (
            context["closed"]
            and participant_count >= contract["minimum_participants"]
        )
        mode_results: dict[str, Any] = {}
        awarded_leaders: dict[str, str] = {}
        for mode in _EXPECTED_MODES:
            board = boards[mode]
            leader = _leader(board)
            title = contract["titles"][cycle_type][mode]
            awarded = title if title_allowed and leader is not None else None
            mode_results[mode] = {
                "leader": deepcopy(leader),
                "title_candidate": title if leader is not None else None,
                "awarded_title": awarded,
                "cycle_snapshot": deepcopy(board.get("cycle_snapshot")),
            }
            if awarded is not None and leader is not None:
                awarded_leaders[mode] = leader["character_id"]
                if leader["character_id"] == local_character_id:
                    local_titles.append({
                        "cycle_id": context["cycle_id"],
                        "cycle_type": cycle_type,
                        "mode": mode,
                        "title": awarded,
                    })

        grand_title = None
        if cycle_type == "monthly" and set(awarded_leaders) == set(_EXPECTED_MODES):
            winners = set(awarded_leaders.values())
            if len(winners) == 1:
                winner = next(iter(winners))
                grand_title = {
                    "character_id": winner,
                    "title": contract["grand_title"],
                }
                if winner == local_character_id:
                    local_titles.append({
                        "cycle_id": context["cycle_id"],
                        "cycle_type": cycle_type,
                        "mode": "grand",
                        "title": contract["grand_title"],
                    })

        cycles[cycle_type] = {
            **deepcopy(context),
            "confirmed_competition": participant_count >= contract["minimum_participants"],
            "titles_final": title_allowed,
            "modes": mode_results,
            "grand_title": grand_title,
        }

    return {
        "projection_version": season_manifest["version"],
        "available": bool(cycles),
        "unavailable_reason": None if cycles else "no_confirmed_cycle",
        "default_cycle_type": contract["default_cycle_type"],
        "cycle_types": list(_EXPECTED_CYCLE_TYPES),
        "cycles": cycles,
        "local_titles": local_titles,
        "time_policy": {
            "system_time_is_sole_authority": False,
            "allowed_authorities": sorted(contract["allowed_authorities"]),
        },
        "competition_policy": {
            "minimum_confirmed_participants_for_title": contract["minimum_participants"],
            "invented_competitors": False,
            "titles_require_closed_cycle": True,
        },
    }
