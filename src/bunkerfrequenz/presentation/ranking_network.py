from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


_BASE_SORT_MODES = frozenset({"level", "reputation", "resonance", "skill", "events", "clubs"})
_EXPECTED_RANKING_STYLE = "competitive_displacement"


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} muss ein Mapping sein")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} muss ein nicht-leerer Text sein")
    return value


def _require_nonnegative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field} muss eine nichtnegative Ganzzahl sein")
    return value


def _require_positive_int(value: Any, field: str) -> int:
    result = _require_nonnegative_int(value, field)
    if result < 1:
        raise ValueError(f"{field} muss mindestens 1 sein")
    return result


def _require_positive_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{field} muss eine positive Zahl sein")
    return float(value)


def _manifest_contract(ranking_manifest: Mapping[str, Any], sync_manifest: Mapping[str, Any]) -> dict[str, Any]:
    sort_modes = ranking_manifest.get("sort_modes", ())
    if not isinstance(sort_modes, Sequence) or isinstance(sort_modes, (str, bytes)):
        raise ValueError("Ranking-Manifest enthält keine gültigen Sortiermodi")
    normalized_modes = frozenset(sort_modes)
    if normalized_modes != _BASE_SORT_MODES:
        raise ValueError("Ranking-Manifest und Runtime-Sortiervertrag weichen voneinander ab")

    default_top_limit = _require_positive_int(
        ranking_manifest.get("default_top_limit"),
        "default_top_limit",
    )
    competitive_top_limit = _require_positive_int(
        ranking_manifest.get("competitive_top_limit"),
        "competitive_top_limit",
    )
    top_pressure_factor = _require_positive_number(
        ranking_manifest.get("top_pressure_factor"),
        "top_pressure_factor",
    )
    outer_pressure_factor = _require_positive_number(
        ranking_manifest.get("outer_pressure_factor"),
        "outer_pressure_factor",
    )
    if outer_pressure_factor >= top_pressure_factor:
        raise ValueError("outer_pressure_factor muss kleiner als top_pressure_factor sein")
    if ranking_manifest.get("ranking_style") != _EXPECTED_RANKING_STYLE:
        raise ValueError("Ranking-Manifest besitzt nicht den Competitive-Displacement-Vertrag")
    if ranking_manifest.get("rank_numbers_unique") is not True:
        raise ValueError("Competitive Ranking benötigt eindeutige Rangnummern")

    authority = _require_text(
        sync_manifest.get("shared_resource_authority"),
        "SYNC_MANIFEST.shared_resource_authority",
    )
    metrics = ranking_manifest.get("confirmed_network_metrics", ())
    statuses = ranking_manifest.get("sync_statuses", ())
    if not isinstance(metrics, Sequence) or isinstance(metrics, (str, bytes)):
        raise ValueError("confirmed_network_metrics muss eine Liste sein")
    if not isinstance(statuses, Sequence) or isinstance(statuses, (str, bytes)):
        raise ValueError("sync_statuses muss eine Liste sein")
    return {
        "sort_modes": normalized_modes,
        "default_top_limit": default_top_limit,
        "competitive_top_limit": competitive_top_limit,
        "top_pressure_factor": top_pressure_factor,
        "outer_pressure_factor": outer_pressure_factor,
        "authority": authority,
        "network_metrics": frozenset(metrics),
        "sync_statuses": frozenset(statuses),
    }


def _skill_values(character_projection: Mapping[str, Any]) -> dict[str, int]:
    skills = character_projection.get("skills", ())
    if not isinstance(skills, Sequence) or isinstance(skills, (str, bytes)):
        raise ValueError("Character Projection skills muss eine Sequenz sein")
    values: dict[str, int] = {}
    for item in skills:
        if not isinstance(item, Mapping):
            continue
        skill_id = item.get("skill_id")
        value = item.get("value")
        if not isinstance(skill_id, str) or not skill_id:
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        values[skill_id] = value
    return values


def _participant(value: Mapping[str, Any]) -> dict[str, Any]:
    player_id = _require_text(value.get("player_id"), "participant.player_id")
    projection = _require_mapping(value.get("character"), f"participant[{player_id}].character")
    meta = _require_mapping(projection.get("meta"), f"participant[{player_id}].character.meta")
    overview = _require_mapping(projection.get("overview"), f"participant[{player_id}].character.overview")
    character_id = _require_text(meta.get("character_id"), f"participant[{player_id}].character_id")
    level = _require_nonnegative_int(overview.get("level"), f"participant[{player_id}].level")
    reputation = _require_nonnegative_int(overview.get("reputation"), f"participant[{player_id}].reputation")
    resonance_rank = _require_nonnegative_int(
        overview.get("resonance_rank"),
        f"participant[{player_id}].resonance_rank",
    )
    return {
        "player_id": player_id,
        "character_id": character_id,
        "display_name": overview.get("display_name"),
        "alias": overview.get("alias"),
        "level": level,
        "reputation": reputation,
        "resonance_rank": resonance_rank,
        "skills": _skill_values(projection),
    }


def _network_record(
    value: Mapping[str, Any],
    *,
    expected_authority: str,
    allowed_metrics: frozenset[str],
    allowed_statuses: frozenset[str],
) -> dict[str, Any]:
    player_id = _require_text(value.get("player_id"), "network.player_id")
    character_id = _require_text(value.get("character_id"), f"network[{player_id}].character_id")
    authority = _require_text(value.get("authority"), f"network[{player_id}].authority")
    if authority != expected_authority:
        raise ValueError(f"network[{player_id}] besitzt keine bestätigte Server-Autorität")
    version = _require_text(value.get("version"), f"network[{player_id}].version")
    sync_status = value.get("sync_status", "unknown")
    if sync_status not in allowed_statuses:
        raise ValueError(f"network[{player_id}].sync_status ist unbekannt")
    metrics = _require_mapping(value.get("metrics", {}), f"network[{player_id}].metrics")
    unknown_metrics = set(metrics) - allowed_metrics
    if unknown_metrics:
        raise ValueError(
            f"network[{player_id}] enthält nicht katalogisierte Metriken: "
            + ", ".join(sorted(unknown_metrics))
        )
    normalized_metrics = {
        metric: _require_nonnegative_int(metric_value, f"network[{player_id}].metrics.{metric}")
        for metric, metric_value in metrics.items()
    }
    return {
        "player_id": player_id,
        "character_id": character_id,
        "version": version,
        "sync_status": sync_status,
        "metrics": normalized_metrics,
    }


def _metric_label_key(sort_by: str, skill_id: str | None) -> str:
    if sort_by == "skill":
        if skill_id is None:
            raise ValueError("skill_id ist für Skill-Ranking erforderlich")
        return f"{skill_id}.label"
    return f"ui.ranking.metric.{sort_by}"


def _selected_metric(entry: Mapping[str, Any], sort_by: str, skill_id: str | None) -> tuple[bool, int | None]:
    if sort_by == "level":
        return True, int(entry["level"])
    if sort_by == "reputation":
        return True, int(entry["reputation"])
    if sort_by == "resonance":
        return True, int(entry["resonance_rank"])
    if sort_by == "skill":
        if skill_id is None:
            raise ValueError("skill_id ist für Skill-Ranking erforderlich")
        value = entry["skills"].get(skill_id)
        return value is not None, value
    value = entry["network_metrics"].get(sort_by)
    return value is not None, value


def _previous_cycle_entries(
    previous_cycle: Mapping[str, Any] | None,
    *,
    sort_by: str,
    skill_id: str | None,
) -> dict[str, dict[str, int]]:
    if previous_cycle is None:
        return {}
    cycle = _require_mapping(previous_cycle, "previous_cycle")
    if cycle.get("sort_by") != sort_by or cycle.get("skill_id") != skill_id:
        raise ValueError("previous_cycle gehört zu einem anderen Ranking-Modus")
    raw_entries = cycle.get("entries", ())
    if not isinstance(raw_entries, Sequence) or isinstance(raw_entries, (str, bytes)):
        raise ValueError("previous_cycle.entries muss eine Liste sein")
    result: dict[str, dict[str, int]] = {}
    used_ranks: set[int] = set()
    for raw in raw_entries:
        item = _require_mapping(raw, "previous_cycle.entry")
        character_id = _require_text(item.get("character_id"), "previous_cycle.character_id")
        rank = _require_positive_int(item.get("rank"), f"previous_cycle[{character_id}].rank")
        value = _require_nonnegative_int(item.get("value"), f"previous_cycle[{character_id}].value")
        if character_id in result:
            raise ValueError(f"previous_cycle enthält Character doppelt: {character_id}")
        if rank in used_ranks:
            raise ValueError("previous_cycle enthält doppelte Rangnummern")
        used_ranks.add(rank)
        result[character_id] = {"rank": rank, "value": value}
    return result


def _history_block(
    character_id: str,
    *,
    current_value: int | None,
    previous: Mapping[str, Mapping[str, int]],
    competitive_top_limit: int,
    top_pressure_factor: float,
    outer_pressure_factor: float,
) -> dict[str, Any]:
    old = previous.get(character_id)
    previous_rank = old["rank"] if old is not None else None
    previous_value = old["value"] if old is not None else None
    momentum_factor = (
        top_pressure_factor
        if previous_rank is not None and previous_rank <= competitive_top_limit
        else outer_pressure_factor
    )
    metric_delta = None if old is None or current_value is None else current_value - previous_value
    effective_momentum = 0.0 if metric_delta is None else round(metric_delta * momentum_factor, 6)
    return {
        "previous_rank": previous_rank,
        "previous_value": previous_value,
        "metric_delta": metric_delta,
        "momentum_factor": momentum_factor,
        "effective_momentum": effective_momentum,
        "movement": None,
        "rank_delta": None,
    }


def _assign_unique_ranks(
    entries: list[dict[str, Any]],
    *,
    competitive_top_limit: int,
    top_pressure_factor: float,
    outer_pressure_factor: float,
) -> None:
    next_rank = 1
    for entry in entries:
        if not entry["selected_metric"]["available"]:
            entry["rank"] = None
            entry["competition"] = {
                "zone": "unranked",
                "pressure_factor": None,
            }
            entry["history"]["movement"] = "unranked"
            continue
        rank = next_rank
        next_rank += 1
        entry["rank"] = rank
        entry["competition"] = {
            "zone": "top10" if rank <= competitive_top_limit else "open_field",
            "pressure_factor": top_pressure_factor if rank <= competitive_top_limit else outer_pressure_factor,
        }
        previous_rank = entry["history"]["previous_rank"]
        if previous_rank is None:
            movement = "new"
            rank_delta = None
        else:
            rank_delta = previous_rank - rank
            if rank_delta > 0:
                movement = "up"
            elif rank_delta < 0:
                movement = "down"
            else:
                movement = "same"
        entry["history"]["movement"] = movement
        entry["history"]["rank_delta"] = rank_delta


def _cycle_snapshot(entries: Sequence[Mapping[str, Any]], sort_by: str, skill_id: str | None) -> dict[str, Any]:
    return {
        "sort_by": sort_by,
        "skill_id": skill_id,
        "entries": [
            {
                "character_id": entry["character_id"],
                "rank": entry["rank"],
                "value": entry["selected_metric"]["value"],
            }
            for entry in entries
            if entry.get("rank") is not None
        ],
    }


def _require_text_catalog(projection: Mapping[str, Any], text_catalog: Mapping[str, str]) -> None:
    required = {
        projection["title_key"],
        projection["network_title_key"],
        projection["view"]["show_all_label_key"],
        projection["view"]["unavailable_label_key"],
        projection["sort"]["label_key"],
    }
    for entry in projection["entries"]:
        required.add(entry["sync"]["label_key"])
        required.add(entry["selected_metric"]["label_key"])
    missing = sorted(key for key in required if key not in text_catalog)
    if missing:
        raise KeyError(f"Fehlende Ranking-/Network-Textschlüssel: {', '.join(missing)}")


def build_ranking_network_projection(
    participants: Sequence[Mapping[str, Any]],
    confirmed_network_records: Sequence[Mapping[str, Any]],
    ranking_manifest: Mapping[str, Any],
    sync_manifest: Mapping[str, Any],
    text_catalog: Mapping[str, str],
    *,
    sort_by: str = "level",
    skill_id: str | None = None,
    show_all: bool = False,
    top_limit: int | None = None,
    previous_cycle: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic no-tie leaderboard from confirmed inputs only.

    Current metric values remain authoritative. If two players reach the same
    value, pressure-weighted momentum from the previous cycle decides who
    displaces whom. Outside the competitive top ten that momentum is reduced
    by the manifest's outer pressure factor.
    """
    contract = _manifest_contract(ranking_manifest, sync_manifest)
    if sort_by not in contract["sort_modes"]:
        raise ValueError(f"Unbekannter Ranking-Modus: {sort_by}")
    if sort_by == "skill":
        skill_id = _require_text(skill_id, "skill_id")
    elif skill_id is not None:
        raise ValueError("skill_id ist nur für sort_by=skill zulässig")
    if not isinstance(show_all, bool):
        raise ValueError("show_all muss bool sein")
    limit = contract["default_top_limit"] if top_limit is None else _require_positive_int(top_limit, "top_limit")
    previous = _previous_cycle_entries(previous_cycle, sort_by=sort_by, skill_id=skill_id)

    normalized_participants = [_participant(_require_mapping(item, "participant")) for item in participants]
    player_ids = [item["player_id"] for item in normalized_participants]
    character_ids = [item["character_id"] for item in normalized_participants]
    if len(set(player_ids)) != len(player_ids):
        raise ValueError("player_id darf nicht doppelt vorkommen")
    if len(set(character_ids)) != len(character_ids):
        raise ValueError("character_id darf nicht doppelt vorkommen")

    network_by_player: dict[str, dict[str, Any]] = {}
    for raw in confirmed_network_records:
        record = _network_record(
            _require_mapping(raw, "network_record"),
            expected_authority=contract["authority"],
            allowed_metrics=contract["network_metrics"],
            allowed_statuses=contract["sync_statuses"],
        )
        if record["player_id"] in network_by_player:
            raise ValueError(f"Doppelter bestätigter Network-Datensatz: {record['player_id']}")
        network_by_player[record["player_id"]] = record

    known_players = set(player_ids)
    unknown_network_players = set(network_by_player) - known_players
    if unknown_network_players:
        raise ValueError(
            "Network-Datensatz verweist auf unbekannte Spieler: "
            + ", ".join(sorted(unknown_network_players))
        )

    metric_label_key = _metric_label_key(sort_by, skill_id)
    entries: list[dict[str, Any]] = []
    for participant in normalized_participants:
        network = network_by_player.get(participant["player_id"])
        if network is not None and network["character_id"] != participant["character_id"]:
            raise ValueError(
                f"Network-Datensatz {participant['player_id']} gehört zu einem anderen Character"
            )
        network_metrics = deepcopy(network["metrics"]) if network is not None else {}
        entry = {
            **deepcopy(participant),
            "network_metrics": network_metrics,
            "sync": {
                "available": network is not None,
                "status": network["sync_status"] if network is not None else "unknown",
                "label_key": f"ui.sync.{network['sync_status'] if network is not None else 'unknown'}",
                "version": network["version"] if network is not None else None,
            },
        }
        available, value = _selected_metric(entry, sort_by, skill_id)
        entry["selected_metric"] = {
            "sort_by": sort_by,
            "skill_id": skill_id,
            "label_key": metric_label_key,
            "available": available,
            "value": value,
            "value_label_key": None if available else "ui.ranking.unavailable",
        }
        entry["history"] = _history_block(
            entry["character_id"],
            current_value=value if available else None,
            previous=previous,
            competitive_top_limit=contract["competitive_top_limit"],
            top_pressure_factor=contract["top_pressure_factor"],
            outer_pressure_factor=contract["outer_pressure_factor"],
        )
        entries.append(entry)

    entries.sort(
        key=lambda item: (
            not item["selected_metric"]["available"],
            -(item["selected_metric"]["value"] or 0),
            -item["history"]["effective_momentum"],
            item["history"]["previous_rank"] if item["history"]["previous_rank"] is not None else 10**12,
            item["character_id"],
        )
    )
    _assign_unique_ranks(
        entries,
        competitive_top_limit=contract["competitive_top_limit"],
        top_pressure_factor=contract["top_pressure_factor"],
        outer_pressure_factor=contract["outer_pressure_factor"],
    )

    availability = {
        "level": bool(entries),
        "reputation": bool(entries),
        "resonance": bool(entries),
        "skill": bool(entries),
        "events": any("events" in entry["network_metrics"] for entry in entries),
        "clubs": any("clubs" in entry["network_metrics"] for entry in entries),
    }
    visible_entries = entries if show_all else entries[:limit]
    projection = {
        "projection_version": "0.8.5-a",
        "title_key": "ui.ranking.title",
        "network_title_key": "ui.network.title",
        "sort": {
            "mode": sort_by,
            "skill_id": skill_id,
            "label_key": metric_label_key,
            "ranking_style": ranking_manifest.get("ranking_style"),
        },
        "view": {
            "show_all": show_all,
            "top_limit": limit,
            "competitive_top_limit": contract["competitive_top_limit"],
            "total_players": len(entries),
            "shown_players": len(visible_entries),
            "show_all_label_key": "ui.ranking.show_all",
            "unavailable_label_key": "ui.ranking.unavailable",
        },
        "competition_policy": {
            "shared_ranks_allowed": False,
            "top_pressure_factor": contract["top_pressure_factor"],
            "outer_pressure_factor": contract["outer_pressure_factor"],
            "equal_value_resolution": "effective_momentum_then_previous_rank_then_character_id",
        },
        "metric_availability": availability,
        "entries": deepcopy(visible_entries),
        "cycle_snapshot": _cycle_snapshot(entries, sort_by, skill_id),
        "network_policy": {
            "authority": contract["authority"],
            "unconfirmed_metrics_are_displayed": False,
            "online_presence_inferred": False,
        },
    }
    _require_text_catalog(projection, text_catalog)
    return projection
