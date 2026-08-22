from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping

_METRICS = ("heat", "prestige", "police_pressure", "scene_activity")
_HOUSING = frozenset({"independent", "guest", "homeless"})
_XOXO_MARKS = frozenset({"", "X", "O"})


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} muss nicht leerer Text sein")
    return value.strip()


def _int(value: Any, name: str, *, minimum: int = 0, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} muss eine Ganzzahl >= {minimum} sein")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} muss <= {maximum} sein")
    return value


def _default_minigames() -> dict[str, Any]:
    return {
        "poker_score": 0,
        "slot_score": 0,
        "xoxo": {
            "board": ["" for _ in range(9)],
            "status": "ready",
            "round": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
        },
    }


@dataclass(slots=True)
class WorldState:
    world_id: str = "living_city"
    revision: int = 0
    next_booking_number: int = 1
    players: dict[str, dict[str, Any]] = field(default_factory=dict)
    positions: dict[str, dict[str, Any]] = field(default_factory=dict)
    housing: dict[str, dict[str, Any]] = field(default_factory=dict)
    districts: dict[str, dict[str, dict[str, int]]] = field(default_factory=dict)
    trust_blocks: list[dict[str, Any]] = field(default_factory=list)
    honors: dict[str, list[str]] = field(default_factory=dict)
    great_deeds: list[dict[str, Any]] = field(default_factory=list)
    party_modes: dict[str, str] = field(default_factory=dict)
    party_checks: dict[str, dict[str, Any]] = field(default_factory=dict)
    storefront_reads: dict[str, list[str]] = field(default_factory=dict)
    mini_games: dict[str, dict[str, Any]] = field(default_factory=dict)
    applied_settlements: list[str] = field(default_factory=list)

    def validate(self) -> None:
        _text(self.world_id, "world_id")
        _int(self.revision, "revision")
        _int(self.next_booking_number, "next_booking_number", minimum=1)
        if not all(isinstance(value, dict) for value in (self.players, self.positions, self.housing, self.districts)):
            raise ValueError("World-State besitzt ungültige Objektblöcke")

        booking_ids: list[str] = []
        for character_id, player in self.players.items():
            _text(character_id, "players.character_id")
            if set(player) != {"booking_id", "display_name", "intro_acknowledged"}:
                raise ValueError("Player-Registry besitzt ungültige Felder")
            booking_ids.append(_text(player["booking_id"], "booking_id"))
            _text(player["display_name"], "display_name")
            if not isinstance(player["intro_acknowledged"], bool):
                raise ValueError("intro_acknowledged muss bool sein")
        if len(booking_ids) != len(set(booking_ids)):
            raise ValueError("Einbuchungs-ID wurde doppelt vergeben")

        player_ids = set(self.players)
        if set(self.positions) != player_ids or set(self.housing) != player_ids:
            raise ValueError("Position/Housing muss exakt zu registrierten Spielern passen")

        for character_id, position in self.positions.items():
            if set(position) != {"city_id", "district_id", "location_id"}:
                raise ValueError("Position besitzt ungültige Felder")
            _text(position["city_id"], f"position.{character_id}.city_id")
            _text(position["district_id"], f"position.{character_id}.district_id")
            if position["location_id"] is not None:
                _text(position["location_id"], f"position.{character_id}.location_id")

        non_independent = 0
        for character_id, home in self.housing.items():
            if set(home) != {"status", "host_character_id"}:
                raise ValueError("Housing besitzt ungültige Felder")
            status = home["status"]
            if status not in _HOUSING:
                raise ValueError("Unbekannter Housing-Status")
            host = home["host_character_id"]
            if status == "guest":
                if host not in player_ids or host == character_id:
                    raise ValueError("Gast benötigt anderen registrierten Host")
            elif host is not None:
                raise ValueError("Nur Gaststatus darf host_character_id setzen")
            if status != "independent":
                non_independent += 1
        if player_ids and non_independent != 1:
            raise ValueError("Wohnungsregel verlangt exakt eine Person ohne unabhängiges Zuhause")

        for city_id, districts in self.districts.items():
            _text(city_id, "districts.city_id")
            if not isinstance(districts, dict) or not districts:
                raise ValueError("Stadt benötigt Bezirke")
            for district_id, metrics in districts.items():
                _text(district_id, "district_id")
                if set(metrics) != set(_METRICS):
                    raise ValueError("Bezirk besitzt falsche Metriken")
                for key in _METRICS:
                    _int(metrics[key], f"district.{key}", minimum=0, maximum=100)

        seen_pairs: set[tuple[str, str]] = set()
        for block in self.trust_blocks:
            required = {"offender_id", "target_id", "violation_type", "remaining_cycles"}
            if set(block) != required:
                raise ValueError("Trust-Block besitzt ungültige Felder")
            offender = _text(block["offender_id"], "offender_id")
            target = _text(block["target_id"], "target_id")
            if offender == target or offender not in player_ids or target not in player_ids:
                raise ValueError("Trust-Block benötigt zwei verschiedene registrierte Spieler")
            pair = (offender, target)
            if pair in seen_pairs:
                raise ValueError("Doppelter gerichteter Trust-Block")
            seen_pairs.add(pair)
            _text(block["violation_type"], "violation_type")
            _int(block["remaining_cycles"], "remaining_cycles", minimum=1, maximum=1000)

        for character_id, titles in self.honors.items():
            if character_id not in player_ids or not isinstance(titles, list):
                raise ValueError("Honor-Liste gehört zu unbekanntem Spieler")
            if len(titles) != len(set(titles)) or not all(isinstance(item, str) and item for item in titles):
                raise ValueError("Honor-Titel müssen eindeutige IDs sein")

        deed_ids: set[str] = set()
        for deed in self.great_deeds:
            required = {"record_id", "character_id", "deed_id", "source_event_id", "valence"}
            if set(deed) != required:
                raise ValueError("Great-Deed-Record besitzt ungültige Felder")
            record_id = _text(deed["record_id"], "record_id")
            if record_id in deed_ids:
                raise ValueError("Great-Deed-Record-ID doppelt")
            deed_ids.add(record_id)
            if deed["character_id"] not in player_ids:
                raise ValueError("Great Deed gehört zu unbekanntem Spieler")
            _text(deed["deed_id"], "deed_id")
            _text(deed["source_event_id"], "source_event_id")
            if deed["valence"] not in {"positive", "negative", "ambiguous"}:
                raise ValueError("Great-Deed-Valenz unbekannt")

        for event_id, mode in self.party_modes.items():
            _text(event_id, "party_modes.event_id")
            if mode not in {"official", "unofficial"}:
                raise ValueError("Party-Modus unbekannt")
        for event_id, check in self.party_checks.items():
            _text(event_id, "party_checks.event_id")
            if set(check) != {"triggered", "resolved", "choice_id"}:
                raise ValueError("Party-Check besitzt ungültige Felder")
            if not isinstance(check["triggered"], bool) or not isinstance(check["resolved"], bool):
                raise ValueError("Party-Check Flags müssen bool sein")
            if check["choice_id"] is not None:
                _text(check["choice_id"], "choice_id")
            if check["resolved"] and check["triggered"] and check["choice_id"] is None:
                raise ValueError("Aufgelöste Begegnung benötigt choice_id")

        for character_id, reads in self.storefront_reads.items():
            if character_id not in player_ids or not isinstance(reads, list):
                raise ValueError("Storefront-Reads gehören zu unbekanntem Spieler")
            if len(reads) != len(set(reads)) or not all(isinstance(item, str) and item for item in reads):
                raise ValueError("Storefront-Reads müssen eindeutige IDs sein")

        for character_id, games in self.mini_games.items():
            if character_id not in player_ids:
                raise ValueError("MiniGame-State gehört zu unbekanntem Spieler")
            if set(games) != {"poker_score", "slot_score", "xoxo"}:
                raise ValueError("MiniGame-State besitzt falsche Felder")
            _int(games["poker_score"], "poker_score")
            _int(games["slot_score"], "slot_score")
            xoxo = games["xoxo"]
            if set(xoxo) != {"board", "status", "round", "wins", "losses", "draws"}:
                raise ValueError("XOXO-State besitzt falsche Felder")
            board = xoxo["board"]
            if not isinstance(board, list) or len(board) != 9 or any(mark not in _XOXO_MARKS for mark in board):
                raise ValueError("XOXO-Board ist ungültig")
            if xoxo["status"] not in {"ready", "playing", "won", "lost", "draw"}:
                raise ValueError("XOXO-Status unbekannt")
            for key in ("round", "wins", "losses", "draws"):
                _int(xoxo[key], f"xoxo.{key}")

        if len(self.applied_settlements) != len(set(self.applied_settlements)):
            raise ValueError("Settlement wurde mehrfach als District-Folge registriert")
        for item in self.applied_settlements:
            _text(item, "applied_settlement")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "world_id": self.world_id,
            "revision": self.revision,
            "next_booking_number": self.next_booking_number,
            "players": deepcopy(self.players),
            "positions": deepcopy(self.positions),
            "housing": deepcopy(self.housing),
            "districts": deepcopy(self.districts),
            "trust_blocks": deepcopy(self.trust_blocks),
            "honors": deepcopy(self.honors),
            "great_deeds": deepcopy(self.great_deeds),
            "party_modes": deepcopy(self.party_modes),
            "party_checks": deepcopy(self.party_checks),
            "storefront_reads": deepcopy(self.storefront_reads),
            "mini_games": deepcopy(self.mini_games),
            "applied_settlements": list(self.applied_settlements),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WorldState":
        state = cls(
            world_id=data.get("world_id", "living_city"),
            revision=data.get("revision", 0),
            next_booking_number=data.get("next_booking_number", 1),
            players=deepcopy(data.get("players", {})),
            positions=deepcopy(data.get("positions", {})),
            housing=deepcopy(data.get("housing", {})),
            districts=deepcopy(data.get("districts", {})),
            trust_blocks=deepcopy(data.get("trust_blocks", [])),
            honors=deepcopy(data.get("honors", {})),
            great_deeds=deepcopy(data.get("great_deeds", [])),
            party_modes=deepcopy(data.get("party_modes", {})),
            party_checks=deepcopy(data.get("party_checks", {})),
            storefront_reads=deepcopy(data.get("storefront_reads", {})),
            mini_games=deepcopy(data.get("mini_games", {})),
            applied_settlements=list(data.get("applied_settlements", [])),
        )
        state.validate()
        return state

    @classmethod
    def empty_from_manifest(cls, manifest: Mapping[str, Any]) -> "WorldState":
        defaults = manifest.get("district_metric_defaults")
        cities = manifest.get("cities")
        if not isinstance(defaults, Mapping) or set(defaults) != set(_METRICS):
            raise ValueError("WORLD_MANIFEST district_metric_defaults ungültig")
        if not isinstance(cities, list) or not cities:
            raise ValueError("WORLD_MANIFEST cities fehlt")
        districts: dict[str, dict[str, dict[str, int]]] = {}
        for city in cities:
            if not isinstance(city, Mapping):
                raise ValueError("WORLD_MANIFEST city ungültig")
            city_id = _text(city.get("city_id"), "city.city_id")
            raw_districts = city.get("districts")
            if not isinstance(raw_districts, list) or not raw_districts:
                raise ValueError("WORLD_MANIFEST city benötigt districts")
            districts[city_id] = {
                _text(district_id, "district_id"): {key: int(defaults[key]) for key in _METRICS}
                for district_id in raw_districts
            }
        state = cls(world_id=str(manifest.get("world_id", "living_city")), districts=districts)
        state.validate()
        return state

    def clone(self) -> "WorldState":
        return WorldState.from_dict(self.to_dict())

    @staticmethod
    def default_minigames() -> dict[str, Any]:
        return _default_minigames()


WORLD_METRICS = _METRICS
