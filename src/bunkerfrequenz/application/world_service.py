from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
from typing import Any, Mapping

from bunkerfrequenz.domain.character import CharacterState, RESOURCE_MAX, RESOURCE_MIN
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.domain.world import WORLD_METRICS, WorldState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class WorldCommitResult:
    world: WorldState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool
    metadata: dict[str, Any] | None = None


class WorldService:
    """Canonical persistent Living-City application boundary."""

    def __init__(self, persistence: PersistenceKernel, manifest: Mapping[str, Any]):
        self.persistence = persistence
        self.manifest = deepcopy(dict(manifest))
        self.version = self._require_text(self.manifest.get("version"), "WORLD_MANIFEST.version")
        self.seed = self._require_text(self.manifest.get("world_seed"), "WORLD_MANIFEST.world_seed")
        self._cities = self._build_city_catalog()
        self._locations = self._build_location_catalog()
        self._aliases = dict(self.manifest.get("legacy_location_aliases", {}))
        self._titles = {
            item["title_id"]: dict(item)
            for item in self.manifest.get("honor_titles", [])
            if isinstance(item, Mapping) and isinstance(item.get("title_id"), str)
        }
        self._deeds = {
            item["deed_id"]: dict(item)
            for item in self.manifest.get("great_deeds", [])
            if isinstance(item, Mapping) and isinstance(item.get("deed_id"), str)
        }
        self._storefronts = {
            item["location_id"]: tuple(item.get("note_keys", ()))
            for item in self.manifest.get("storefronts", [])
            if isinstance(item, Mapping) and isinstance(item.get("location_id"), str)
        }
        self._validate_manifest()

    def ensure_player(self, character: CharacterState, *, context: JournalContext) -> WorldCommitResult:
        character.validate()
        self._character_context(context, character.character_id)
        state = deepcopy(self.persistence.load_state() or {})
        world = self._world_or_empty(state)
        if character.character_id in world.players:
            return WorldCommitResult(world, (), True, {"booking_id": world.players[character.character_id]["booking_id"]})

        data = world.to_dict()
        number = data["next_booking_number"]
        booking = self._booking_id(number)
        used = {entry["booking_id"] for entry in data["players"].values()}
        while booking in used:
            number += 1
            booking = self._booking_id(number)
        data["next_booking_number"] = number + 1

        # Every new registration increases independent capacity by one, but the newcomer
        # becomes the single person without an independent home.
        for home in data["housing"].values():
            if home["status"] != "independent":
                home.update(status="independent", host_character_id=None)
        start = self._default_position()
        data["players"][character.character_id] = {
            "booking_id": booking,
            "display_name": character.display_name,
            "intro_acknowledged": False,
        }
        data["positions"][character.character_id] = start
        data["housing"][character.character_id] = {"status": "homeless", "host_character_id": None}
        data["honors"][character.character_id] = []
        data["storefront_reads"][character.character_id] = []
        data["mini_games"][character.character_id] = WorldState.default_minigames()
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        state["world"] = updated.to_dict()
        event_id = f"{context.command_id}:world-register"
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:world-register",
            events=[{
                "event_id": event_id,
                "event_type": "world.player_registered",
                "payload": {
                    "contract_version": self.version,
                    "character_id": character.character_id,
                    "booking_id": booking,
                    "world": updated.to_dict(),
                },
            }],
            derived_state=state,
            context=context,
        )
        return WorldCommitResult(updated, receipt.event_ids, False, {"booking_id": booking})

    def acknowledge_intro(self, character_id: str, *, context: JournalContext) -> WorldCommitResult:
        self._character_context(context, character_id)
        world, state = self._load_world()
        self._registered(world, character_id)
        if world.players[character_id]["intro_acknowledged"]:
            return WorldCommitResult(world, (), True)
        data = world.to_dict()
        data["players"][character_id]["intro_acknowledged"] = True
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        return self._commit_world(
            updated,
            state,
            context,
            suffix="intro",
            event_type="world.intro_acknowledged",
            payload={"character_id": character_id},
        )

    def move(
        self,
        character_id: str,
        *,
        city_id: str,
        district_id: str,
        location_id: str | None,
        context: JournalContext,
    ) -> WorldCommitResult:
        self._character_context(context, character_id)
        world, state = self._load_world()
        self._registered(world, character_id)
        city_id = self._require_text(city_id, "city_id")
        district_id = self._require_text(district_id, "district_id")
        if city_id not in self._cities or district_id not in self._cities[city_id]["districts"]:
            raise ValueError("Unbekannte Stadt-/Bezirk-Kombination")
        if location_id is not None:
            location_id = self._require_text(location_id, "location_id")
            location = self._locations.get(location_id)
            if location is None or location["city_id"] != city_id or location["district_id"] != district_id:
                raise ValueError("Ort gehört nicht zu gewählter Stadt/Bezirk")
        request = {"city_id": city_id, "district_id": district_id, "location_id": location_id}
        existing = self._record(f"{context.command_id}:move")
        if existing is not None:
            if existing.get("payload", {}).get("request") != request:
                raise PersistenceError("Command-ID wurde für andere Bewegung verwendet")
            return WorldCommitResult(world, (), True)
        data = world.to_dict()
        data["positions"][character_id] = request
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        return self._commit_world(
            updated,
            state,
            context,
            suffix="move",
            event_type="world.character_moved",
            payload={"character_id": character_id, "request": request},
        )

    def set_guest_housing(
        self, character_id: str, host_character_id: str | None, *, context: JournalContext
    ) -> WorldCommitResult:
        self._character_context(context, character_id)
        world, state = self._load_world()
        self._registered(world, character_id)
        if world.housing[character_id]["status"] == "independent":
            raise ValueError("Nur die Person ohne unabhängiges Zuhause kann Gaststatus ändern")
        data = world.to_dict()
        if host_character_id is None:
            data["housing"][character_id] = {"status": "homeless", "host_character_id": None}
        else:
            self._registered(world, host_character_id)
            if host_character_id == character_id:
                raise ValueError("Man kann nicht bei sich selbst unterkommen")
            data["housing"][character_id] = {"status": "guest", "host_character_id": host_character_id}
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        return self._commit_world(
            updated, state, context, suffix="housing", event_type="world.housing_changed",
            payload={"character_id": character_id, "host_character_id": host_character_id},
        )

    def record_trust_violation(
        self,
        offender_id: str,
        target_id: str,
        violation_type: str,
        *,
        context: JournalContext,
    ) -> WorldCommitResult:
        self._character_context(context, offender_id)
        world, state = self._load_world()
        self._registered(world, offender_id)
        self._registered(world, target_id)
        if offender_id == target_id:
            raise ValueError("Misstrauensfolge benötigt zwei verschiedene Spieler")
        allowed = set(self.manifest.get("trust", {}).get("violation_types", ()))
        if violation_type not in allowed:
            raise ValueError("Unbekannte Misstrauenstat")
        cycles = int(self.manifest["trust"]["block_cycles"])
        data = world.to_dict()
        data["trust_blocks"] = [
            block for block in data["trust_blocks"]
            if not (block["offender_id"] == offender_id and block["target_id"] == target_id)
        ]
        data["trust_blocks"].append({
            "offender_id": offender_id,
            "target_id": target_id,
            "violation_type": violation_type,
            "remaining_cycles": cycles,
        })
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        return self._commit_world(
            updated, state, context, suffix="trust", event_type="world.trust_violation_recorded",
            payload={"offender_id": offender_id, "target_id": target_id, "violation_type": violation_type, "cycles": cycles},
        )

    def effectiveness_bps(self, source_id: str, target_id: str) -> int:
        world, _ = self._load_world()
        self._registered(world, source_id)
        self._registered(world, target_id)
        for block in world.trust_blocks:
            if block["offender_id"] == source_id and block["target_id"] == target_id:
                return int(self.manifest["trust"]["blocked_direction_effectiveness_bps"])
        return int(self.manifest["trust"]["reverse_direction_effectiveness_bps"])

    def consume_trust_cycle(
        self, source_id: str, target_id: str, *, context: JournalContext
    ) -> WorldCommitResult:
        self._character_context(context, source_id)
        world, state = self._load_world()
        data = world.to_dict()
        matched = None
        remaining = []
        for block in data["trust_blocks"]:
            if block["offender_id"] == source_id and block["target_id"] == target_id:
                matched = block
                block = dict(block)
                block["remaining_cycles"] -= 1
                if block["remaining_cycles"] > 0:
                    remaining.append(block)
            else:
                remaining.append(block)
        if matched is None:
            return WorldCommitResult(world, (), True, {"effectiveness_bps": 10000})
        data["trust_blocks"] = remaining
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        result = self._commit_world(
            updated, state, context, suffix="trust-cycle", event_type="world.trust_cycle_consumed",
            payload={"source_id": source_id, "target_id": target_id},
        )
        return WorldCommitResult(
            result.world, result.committed_event_ids, result.idempotent_replay,
            {"effectiveness_bps": int(self.manifest["trust"]["blocked_direction_effectiveness_bps"])},
        )

    def city_price_multiplier_bps(self, character_id: str) -> int:
        world, _ = self._load_world()
        self._registered(world, character_id)
        city_id = world.positions[character_id]["city_id"]
        return int(self._cities[city_id]["price_multiplier_bps"])

    def set_party_mode(self, event_id: str, mode: str, *, context: JournalContext) -> WorldCommitResult:
        self._event_context(context, event_id)
        world, state = self._load_world()
        event = self._event(state, event_id)
        if event.phase not in {"draft", "planning", "procurement", "transport", "setup", "soundcheck"}:
            raise ValueError("Party-Modus kann nach LIVE nicht mehr geändert werden")
        if mode not in {"official", "unofficial"}:
            raise ValueError("Party-Modus muss official oder unofficial sein")
        data = world.to_dict()
        data["party_modes"][event_id] = mode
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        return self._commit_world(
            updated, state, context, suffix="party-mode", event_type="world.party_mode_changed",
            payload={"event_id": event_id, "mode": mode},
        )

    def check_party_encounter(self, event_id: str, *, context: JournalContext) -> WorldCommitResult:
        self._event_context(context, event_id)
        world, state = self._load_world()
        event = self._event(state, event_id)
        if event.phase != "live":
            raise ValueError("Behördenbegegnung wird nur während LIVE geprüft")
        if event_id in world.party_checks:
            return WorldCommitResult(world, (), True, deepcopy(world.party_checks[event_id]))
        if world.party_modes.get(event_id, "official") != "unofficial":
            raise ValueError("Behörden-Risikocheck ist nur für als unofficial bestätigte Party vorgesehen")
        location_id = self._canonical_event_location(event)
        location = self._locations.get(location_id)
        if location is None or not location.get("party_risk_eligible"):
            raise ValueError("Dieser Ort ist nicht für den Party-Risikocheck katalogisiert")
        metrics = world.districts[location["city_id"]][location["district_id"]]
        config = self.manifest["party_encounter"]
        threshold = min(
            int(config["max_trigger_percent"]),
            int(config["base_trigger_percent"]) + metrics["heat"] // 2 + metrics["police_pressure"] // 3,
        )
        roll = self._percent("party-check", event_id, location_id)
        triggered = roll < threshold
        data = world.to_dict()
        data["party_checks"][event_id] = {"triggered": triggered, "resolved": not triggered, "choice_id": None}
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        result = self._commit_world(
            updated, state, context, suffix="party-check", event_type="world.party_encounter_checked",
            payload={"event_id": event_id, "location_id": location_id, "roll": roll, "threshold": threshold, "triggered": triggered},
        )
        metadata = {"triggered": triggered, "roll": roll, "threshold": threshold, "choices": self.party_choices() if triggered else []}
        return WorldCommitResult(result.world, result.committed_event_ids, False, metadata)

    def resolve_party_encounter(
        self, event_id: str, choice_id: str, *, context: JournalContext
    ) -> WorldCommitResult:
        self._event_context(context, event_id)
        world, state = self._load_world()
        event = self._event(state, event_id)
        check = world.party_checks.get(event_id)
        if check is None or not check["triggered"] or check["resolved"]:
            raise ValueError("Keine offene Behördenbegegnung vorhanden")
        choice = next((item for item in self.manifest["party_encounter"]["choices"] if item["choice_id"] == choice_id), None)
        if choice is None:
            raise ValueError("Unbekannte Behördenentscheidung")
        character_raw = state.get("character")
        if not isinstance(character_raw, dict):
            raise PersistenceError("Behördenbegegnung benötigt Character-State")
        character = CharacterState.from_dict(character_raw)
        if context.character_id is not None and context.character_id != character.character_id:
            raise ValueError("JournalContext.character_id passt nicht zum Character")
        location = self._locations[self._canonical_event_location(event)]
        effects = dict(choice["effects"])

        world_data = world.to_dict()
        metrics = world_data["districts"][location["city_id"]][location["district_id"]]
        for key in ("heat", "police_pressure", "scene_activity"):
            delta = int(effects[f"{key}_delta"])
            metrics[key] = self._clamp(metrics[key] + delta)
        world_data["party_checks"][event_id] = {"triggered": True, "resolved": True, "choice_id": choice_id}
        world_data["revision"] += 1
        world_after = WorldState.from_dict(world_data)

        character_data = character.to_dict()
        character_data["stress"] = self._clamp_resource(character.stress + int(effects["stress_delta"]))
        character_data["reputation"] = max(0, character.reputation + int(effects["reputation_delta"]))
        character_after = CharacterState.from_dict(character_data)
        state["world"] = world_after.to_dict()
        state["character"] = character_after.to_dict()
        events = [
            {
                "event_id": f"{context.command_id}:party-resolve",
                "event_type": "world.party_encounter_resolved",
                "payload": {"event_id": event_id, "choice_id": choice_id, "effects": effects, "world": world_after.to_dict(), "character": character_after.to_dict()},
            },
            {
                "event_id": f"{context.command_id}:party-resources",
                "event_type": "character.resources_changed",
                "payload": {
                    "energy": {"old": character.energy, "delta": 0, "new": character.energy},
                    "stress": {"old": character.stress, "delta": int(effects["stress_delta"]), "new": character_after.stress},
                },
            },
            {
                "event_id": f"{context.command_id}:party-reputation",
                "event_type": "character.reputation_changed",
                "payload": {"old": character.reputation, "delta": int(effects["reputation_delta"]), "new": character_after.reputation, "reason": "party_authority_encounter"},
            },
        ]
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:party-resolve",
            events=events,
            derived_state=state,
            context=context,
        )
        return WorldCommitResult(world_after, receipt.event_ids, False, {"choice_id": choice_id, "effects": effects})

    def inspect_storefront(self, character_id: str, *, context: JournalContext) -> WorldCommitResult:
        self._character_context(context, character_id)
        world, state = self._load_world()
        self._registered(world, character_id)
        location_id = world.positions[character_id]["location_id"]
        if location_id not in self._storefronts:
            raise ValueError("Am aktuellen Ort gibt es kein katalogisiertes Schaufenster")
        notes = list(self._storefronts[location_id])
        data = world.to_dict()
        if location_id not in data["storefront_reads"][character_id]:
            data["storefront_reads"][character_id].append(location_id)
            data["revision"] += 1
            updated = WorldState.from_dict(data)
            result = self._commit_world(
                updated, state, context, suffix="storefront", event_type="world.storefront_inspected",
                payload={"character_id": character_id, "location_id": location_id, "note_keys": notes},
            )
            return WorldCommitResult(result.world, result.committed_event_ids, False, {"note_keys": notes})
        return WorldCommitResult(world, (), True, {"note_keys": notes})

    def play_minigame(
        self,
        character_id: str,
        game_id: str,
        *,
        cell: int | None,
        context: JournalContext,
    ) -> WorldCommitResult:
        self._character_context(context, character_id)
        world, state = self._load_world()
        self._registered(world, character_id)
        location_id = world.positions[character_id]["location_id"]
        location = self._locations.get(location_id or "")
        if location is None or game_id not in location.get("mini_games", []):
            raise ValueError("Dieses Minispiel ist am aktuellen Ort nicht verfügbar")
        if game_id not in {"poker", "slot", "xoxo"}:
            raise ValueError("Unbekanntes Minispiel")
        existing = self._record(f"{context.command_id}:minigame")
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("request") != {"game_id": game_id, "cell": cell}:
                raise PersistenceError("Command-ID wurde für anderes Minispiel verwendet")
            return WorldCommitResult(world, (), True, deepcopy(payload.get("result")))

        data = world.to_dict()
        games = data["mini_games"][character_id]
        if game_id == "poker":
            result = self._poker(character_id, context.command_id)
            games["poker_score"] += result["points"]
        elif game_id == "slot":
            result = self._slot(character_id, context.command_id)
            games["slot_score"] += result["points"]
        else:
            result = self._xoxo(games["xoxo"], character_id, context.command_id, cell)
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        return self._commit_world(
            updated, state, context, suffix="minigame", event_type="world.minigame_played",
            payload={"character_id": character_id, "request": {"game_id": game_id, "cell": cell}, "result": result},
            metadata=result,
        )

    def apply_confirmed_settlement(self, *, context: JournalContext) -> WorldCommitResult:
        if context.entity_type != "event" or not context.entity_id:
            raise ValueError("District-Settlement benötigt Event-Kontext")
        state = deepcopy(self.persistence.load_state() or {})
        raw_event = state.get("event")
        raw_settlement = state.get("settlement")
        raw_character = state.get("character")
        if not all(isinstance(item, dict) for item in (raw_event, raw_settlement, raw_character)):
            raise PersistenceError("District-Folge benötigt bestätigtes Event, Settlement und Character")
        event = EventState.from_dict(raw_event)
        settlement = SettlementState.from_dict(raw_settlement)
        character = CharacterState.from_dict(raw_character)
        if event.event_id != context.entity_id or settlement.event_id != event.event_id or event.phase != "completed":
            raise ValueError("District-Folge benötigt passendes abgeschlossenes Event")
        world = self._world_or_empty(state)
        if character.character_id not in world.players:
            # Legacy save: register deterministically inside the same resulting world snapshot.
            world = self._register_without_commit(world, character)
        if settlement.settlement_id in world.applied_settlements:
            return WorldCommitResult(world, (), True)

        data = world.to_dict()
        location_id = self._canonical_event_location(event)
        location = self._locations.get(location_id)
        if location is not None:
            metrics = data["districts"][location["city_id"]][location["district_id"]]
            effects = settlement.effects
            config = self.manifest["settlement_to_district"]
            metrics["heat"] = self._clamp(metrics["heat"] + int(effects["heat_delta"]))
            metrics["prestige"] = self._clamp(metrics["prestige"] + self._scaled(int(effects["reputation_delta"]), int(config["prestige_from_reputation_bps"])))
            metrics["police_pressure"] = self._clamp(
                metrics["police_pressure"]
                + self._scaled(max(0, int(effects["heat_delta"])), int(config["police_from_heat_bps"]))
                - self._scaled(max(0, int(effects["stability_delta"])), int(config["police_relief_from_stability_bps"]))
            )
            metrics["scene_activity"] = self._clamp(
                metrics["scene_activity"]
                + self._scaled(int(effects["reputation_delta"]), int(config["scene_from_reputation_bps"]))
                + self._scaled(int(effects["stability_delta"]), int(config["scene_from_stability_bps"]))
            )
        self._award_deeds(data, settlement, character.character_id, context.command_id)
        data["applied_settlements"].append(settlement.settlement_id)
        data["revision"] += 1
        updated = WorldState.from_dict(data)
        state["world"] = updated.to_dict()
        event_id = f"{context.command_id}:world-settlement"
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:world-settlement",
            events=[{
                "event_id": event_id,
                "event_type": "world.settlement_applied",
                "payload": {
                    "contract_version": self.version,
                    "settlement_id": settlement.settlement_id,
                    "location_id": location_id,
                    "world": updated.to_dict(),
                },
            }],
            derived_state=state,
            context=context,
        )
        return WorldCommitResult(updated, receipt.event_ids, False)

    def party_choices(self) -> list[dict[str, Any]]:
        return [
            {"choice_id": item["choice_id"], "label_key": item["label_key"]}
            for item in self.manifest["party_encounter"]["choices"]
        ]

    def _register_without_commit(self, world: WorldState, character: CharacterState) -> WorldState:
        if character.character_id in world.players:
            return world
        data = world.to_dict()
        for home in data["housing"].values():
            if home["status"] != "independent":
                home.update(status="independent", host_character_id=None)
        booking = self._booking_id(data["next_booking_number"])
        used = {entry["booking_id"] for entry in data["players"].values()}
        while booking in used:
            data["next_booking_number"] += 1
            booking = self._booking_id(data["next_booking_number"])
        data["next_booking_number"] += 1
        data["players"][character.character_id] = {"booking_id": booking, "display_name": character.display_name, "intro_acknowledged": False}
        data["positions"][character.character_id] = self._default_position()
        data["housing"][character.character_id] = {"status": "homeless", "host_character_id": None}
        data["honors"][character.character_id] = []
        data["storefront_reads"][character.character_id] = []
        data["mini_games"][character.character_id] = WorldState.default_minigames()
        return WorldState.from_dict(data)

    def _award_deeds(self, data: dict[str, Any], settlement: SettlementState, character_id: str, source: str) -> None:
        existing = {item["deed_id"] for item in data["great_deeds"] if item["character_id"] == character_id}
        candidates = ["first_completed_event"]
        if settlement.incident_ids:
            candidates.append("crisis_survivor")
        if int(settlement.effects["heat_delta"]) >= 8:
            candidates.append("high_heat_finish")
        if int(settlement.effects["reputation_delta"]) >= 5:
            candidates.append("prestige_night")
        for deed_id in candidates:
            if deed_id in existing or deed_id not in self._deeds:
                continue
            deed = self._deeds[deed_id]
            data["great_deeds"].append({
                "record_id": f"deed:{source}:{deed_id}",
                "character_id": character_id,
                "deed_id": deed_id,
                "source_event_id": settlement.event_id,
                "valence": deed["valence"],
            })
            title_id = deed.get("title_id")
            if title_id in self._titles and title_id not in data["honors"][character_id]:
                data["honors"][character_id].append(title_id)

    def _poker(self, character_id: str, command_id: str) -> dict[str, Any]:
        deck = [f"{rank}{suit}" for suit in "CDHS" for rank in "23456789TJQKA"]
        ordered = sorted(deck, key=lambda card: self._hash("poker", character_id, command_id, card))
        player = ordered[:5]
        house = ordered[5:10]
        player_rank = self._poker_rank(player)
        house_rank = self._poker_rank(house)
        outcome = "win" if player_rank > house_rank else "draw" if player_rank == house_rank else "loss"
        config = self.manifest["mini_games"]["poker"]
        points = int(config["win_points"]) if outcome == "win" else int(config["draw_points"]) if outcome == "draw" else 0
        return {"game_id": "poker", "player_hand": player, "house_hand": house, "outcome": outcome, "points": points}

    @staticmethod
    def _poker_rank(hand: list[str]) -> tuple[int, list[int]]:
        values = "23456789TJQKA"
        ranks = sorted((values.index(card[0]) + 2 for card in hand), reverse=True)
        counts = {rank: ranks.count(rank) for rank in set(ranks)}
        groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
        if groups[0][0] == 4:
            category = 7
        elif [g[0] for g in groups[:2]] == [3, 2]:
            category = 6
        elif groups[0][0] == 3:
            category = 3
        elif [g[0] for g in groups[:2]] == [2, 2]:
            category = 2
        elif groups[0][0] == 2:
            category = 1
        else:
            category = 0
        return category, [rank for count, rank in groups for _ in range(count)]

    def _slot(self, character_id: str, command_id: str) -> dict[str, Any]:
        symbols = ("BASS", "BETON", "BLITZ", "KABEL", "KRONE")
        reels = [symbols[self._number("slot", character_id, command_id, str(index)) % len(symbols)] for index in range(3)]
        config = self.manifest["mini_games"]["slot"]
        if len(set(reels)) == 1:
            outcome, points = "jackpot", int(config["jackpot_points"])
        elif len(set(reels)) == 2:
            outcome, points = "pair", int(config["pair_points"])
        else:
            outcome, points = "miss", 0
        return {"game_id": "slot", "reels": reels, "outcome": outcome, "points": points}

    def _xoxo(self, xoxo: dict[str, Any], character_id: str, command_id: str, cell: int | None) -> dict[str, Any]:
        if isinstance(cell, bool) or not isinstance(cell, int) or not 0 <= cell <= 8:
            raise ValueError("XOXO benötigt cell 0..8")
        if xoxo["status"] in {"won", "lost", "draw"}:
            xoxo.update(board=["" for _ in range(9)], status="ready")
        board = xoxo["board"]
        if board[cell]:
            raise ValueError("XOXO-Feld ist bereits belegt")
        if xoxo["status"] == "ready":
            xoxo["round"] += 1
            xoxo["status"] = "playing"
        board[cell] = "X"
        status = self._xoxo_status(board)
        if status is None:
            open_cells = [index for index, mark in enumerate(board) if not mark]
            ai_cell = min(open_cells, key=lambda index: self._hash("xoxo-ai", character_id, str(xoxo["round"]), "".join(board), str(index)))
            board[ai_cell] = "O"
            status = self._xoxo_status(board)
        if status == "X":
            xoxo["status"] = "won"
            xoxo["wins"] += 1
            points = int(self.manifest["mini_games"]["xoxo"]["win_points"])
        elif status == "O":
            xoxo["status"] = "lost"
            xoxo["losses"] += 1
            points = 0
        elif status == "draw":
            xoxo["status"] = "draw"
            xoxo["draws"] += 1
            points = int(self.manifest["mini_games"]["xoxo"]["draw_points"])
        else:
            points = 0
        return {"game_id": "xoxo", "board": list(board), "status": xoxo["status"], "points": points}

    @staticmethod
    def _xoxo_status(board: list[str]) -> str | None:
        lines = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
        for a, b, c in lines:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return "draw" if all(board) else None

    def _commit_world(
        self,
        updated: WorldState,
        state: dict[str, Any],
        context: JournalContext,
        *,
        suffix: str,
        event_type: str,
        payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> WorldCommitResult:
        event_id = f"{context.command_id}:{suffix}"
        existing = self._record(event_id)
        if existing is not None:
            return WorldCommitResult(self._load_world()[0], (), True, deepcopy(metadata))
        state["world"] = updated.to_dict()
        body = deepcopy(payload)
        body["world"] = updated.to_dict()
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:{suffix}",
            events=[{"event_id": event_id, "event_type": event_type, "payload": body}],
            derived_state=state,
            context=context,
        )
        return WorldCommitResult(updated, receipt.event_ids, False, deepcopy(metadata))

    def _load_world(self) -> tuple[WorldState, dict[str, Any]]:
        state = deepcopy(self.persistence.load_state() or {})
        raw = state.get("world")
        if not isinstance(raw, dict):
            raise PersistenceError("World-State ist noch nicht initialisiert")
        return WorldState.from_dict(raw), state

    def _world_or_empty(self, state: dict[str, Any]) -> WorldState:
        raw = state.get("world")
        return WorldState.from_dict(raw) if isinstance(raw, dict) else WorldState.empty_from_manifest(self.manifest)

    def _event(self, state: dict[str, Any], event_id: str) -> EventState:
        raw = state.get("event")
        if not isinstance(raw, dict):
            raise PersistenceError("Bestätigter Event-State fehlt")
        event = EventState.from_dict(raw)
        if event.event_id != event_id:
            raise ValueError("Event-Kontext passt nicht")
        return event

    def _default_position(self) -> dict[str, Any]:
        preferred = self._locations.get("concrete_orbit")
        if preferred is None:
            preferred = next(iter(self._locations.values()))
        return {"city_id": preferred["city_id"], "district_id": preferred["district_id"], "location_id": preferred["location_id"]}

    def _canonical_event_location(self, event: EventState) -> str:
        if event.location is None:
            raise ValueError("Event besitzt keinen Ort")
        location_id = event.location["location_id"]
        return str(self._aliases.get(location_id, location_id))

    def _build_city_catalog(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for city in self.manifest.get("cities", []):
            if not isinstance(city, Mapping):
                raise ValueError("WORLD_MANIFEST city ungültig")
            city_id = self._require_text(city.get("city_id"), "city_id")
            if city_id in result:
                raise ValueError("Doppelte city_id")
            districts = city.get("districts")
            if not isinstance(districts, list) or not districts:
                raise ValueError("City benötigt districts")
            result[city_id] = {**dict(city), "districts": tuple(str(item) for item in districts)}
        return result

    def _build_location_catalog(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for location in self.manifest.get("locations", []):
            if not isinstance(location, Mapping):
                raise ValueError("WORLD_MANIFEST location ungültig")
            location_id = self._require_text(location.get("location_id"), "location_id")
            if location_id in result:
                raise ValueError("Doppelte location_id")
            result[location_id] = dict(location)
        return result

    def _validate_manifest(self) -> None:
        if not self._cities or not self._locations:
            raise ValueError("WORLD_MANIFEST benötigt Städte und Orte")
        for location in self._locations.values():
            city_id = location.get("city_id")
            district_id = location.get("district_id")
            if city_id not in self._cities or district_id not in self._cities[city_id]["districts"]:
                raise ValueError("WORLD_MANIFEST Location verweist auf unbekannten Bezirk")
        trust = self.manifest.get("trust")
        if not isinstance(trust, Mapping) or int(trust.get("block_cycles", 0)) < 1:
            raise ValueError("WORLD_MANIFEST Trust-Vertrag ungültig")
        party = self.manifest.get("party_encounter")
        if not isinstance(party, Mapping) or len(party.get("choices", ())) != 3:
            raise ValueError("Party-Encounter muss exakt drei Entscheidungen besitzen")
        for deed in self._deeds.values():
            if deed.get("title_id") not in self._titles:
                raise ValueError("Great Deed verweist auf unbekannten Titel")

    def _booking_id(self, number: int) -> str:
        config = self.manifest["booking_id"]
        return f"{config['prefix']}-{number:0{int(config['digits'])}d}"

    def _record(self, event_id: str) -> dict[str, Any] | None:
        return next((record for record in self.persistence.read_records() if record["event_id"] == event_id), None)

    @staticmethod
    def _registered(world: WorldState, character_id: str) -> None:
        if character_id not in world.players:
            raise ValueError("Spieler ist nicht im World-State registriert")

    @staticmethod
    def _require_text(value: Any, name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} fehlt")
        return value.strip()

    @staticmethod
    def _character_context(context: JournalContext, character_id: str) -> None:
        if context.entity_type != "character" or context.entity_id != character_id or not context.command_id:
            raise ValueError("World-Character-Command benötigt passenden Character-Kontext")

    @staticmethod
    def _event_context(context: JournalContext, event_id: str) -> None:
        if context.entity_type != "event" or context.entity_id != event_id or not context.command_id:
            raise ValueError("World-Event-Command benötigt passenden Event-Kontext")

    @staticmethod
    def _clamp(value: int) -> int:
        return min(100, max(0, int(value)))

    @staticmethod
    def _clamp_resource(value: int) -> int:
        return min(RESOURCE_MAX, max(RESOURCE_MIN, int(value)))

    @staticmethod
    def _scaled(value: int, bps: int) -> int:
        sign = -1 if value < 0 else 1
        return sign * ((abs(value) * bps + 5000) // 10000)

    def _hash(self, *parts: str) -> str:
        joined = "\x1f".join((self.seed, *parts)).encode("utf-8")
        return hashlib.sha256(joined).hexdigest()

    def _number(self, *parts: str) -> int:
        return int(self._hash(*parts)[:16], 16)

    def _percent(self, *parts: str) -> int:
        return self._number(*parts) % 100


def replay_world_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if not str(record.get("event_type", "")).startswith("world."):
        return derived_state
    payload = record.get("payload", {})
    raw_world = payload.get("world")
    if not isinstance(raw_world, dict):
        return derived_state
    target = WorldState.from_dict(raw_world)
    state = deepcopy(derived_state)
    current_raw = state.get("world")
    if isinstance(current_raw, dict):
        current = WorldState.from_dict(current_raw)
        if current.revision > target.revision:
            return state
        if current.revision == target.revision:
            if current.to_dict() != target.to_dict():
                raise ValueError("World-Replay kollidiert mit Zustand derselben Revision")
            return state
    state["world"] = target.to_dict()
    raw_character = payload.get("character")
    if isinstance(raw_character, dict):
        state["character"] = CharacterState.from_dict(raw_character).to_dict()
    return state
