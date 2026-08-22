from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.application.economy_service import EconomyService
from bunkerfrequenz.application.property_service import PropertyService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState, PROPERTY_UPGRADE_LEDGER_KIND
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.property import PropertyState
from bunkerfrequenz.domain.property_upgrade import (
    MAX_UPGRADE_LEVEL,
    PropertyUpgradeState,
    upgrade_cost_cents,
)
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


_VALUE_KEYS = {"prestige", "audience_pull", "risk", "underground_factor", "utility"}


@dataclass(frozen=True, slots=True)
class PropertyUpgradeCommitResult:
    property_upgrades: PropertyUpgradeState
    economy: EconomyState
    event: EventState
    location_id: str
    upgrade_id: str
    new_level: int
    upgrade_cost_cents: int
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class PropertyUpgradeService:
    """Upgrade already-owned City-Map properties with one atomic Economy commit."""

    def __init__(
        self,
        persistence: PersistenceKernel,
        upgrade_manifest: Mapping[str, Any],
        property_manifest: Mapping[str, Any],
        city_map_manifest: Mapping[str, Any],
    ) -> None:
        self.persistence = persistence
        self.economy = EconomyService(persistence)
        self.property = PropertyService(persistence, property_manifest, city_map_manifest)
        self.manifest = deepcopy(dict(upgrade_manifest))
        self.city_map = deepcopy(dict(city_map_manifest))
        self.version = self._text(self.manifest.get("version"), "PROPERTY_UPGRADE_MANIFEST.version")
        if self.version != "0.8.6-b1":
            raise ValueError("Property-Upgrade-Manifest besitzt unerwartete Version")
        if self.manifest.get("state_block") != "property_upgrades":
            raise ValueError("Property-Upgrade-Manifest besitzt falschen state_block")
        if self.manifest.get("property_manifest_version") != property_manifest.get("version"):
            raise ValueError("Property-Upgrade- und Property-Vertrag passen nicht zusammen")
        if self.manifest.get("city_map_manifest_version") != self.city_map.get("version"):
            raise ValueError("Property-Upgrade- und City-Map-Vertrag passen nicht zusammen")
        if self.manifest.get("max_level") != MAX_UPGRADE_LEVEL:
            raise ValueError("Property-Upgrade-Maxlevel weicht von der Domain ab")

        multipliers = self.manifest.get("level_cost_multipliers_bps")
        if not isinstance(multipliers, list) or len(multipliers) != MAX_UPGRADE_LEVEL:
            raise ValueError("Property-Upgrade benötigt drei Level-Kostenfaktoren")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in multipliers):
            raise ValueError("Level-Kostenfaktoren müssen positive Ganzzahlen sein")
        self.level_multipliers = tuple(multipliers)

        purchase = self.manifest.get("purchase")
        if not isinstance(purchase, Mapping):
            raise ValueError("Property-Upgrade-Manifest benötigt purchase-Vertrag")
        if purchase.get("economy_ledger_kind") != PROPERTY_UPGRADE_LEDGER_KIND:
            raise ValueError("Property-Upgrade- und Economy-Ledger-Vertrag widersprechen sich")
        if purchase.get("client_cost_authority") is not False or purchase.get("client_level_authority") is not False:
            raise ValueError("Client darf weder Ausbaukosten noch Level bestimmen")
        if purchase.get("atomic_with_economy") is not True:
            raise ValueError("Property-Ausbau muss atomar mit Economy sein")
        if purchase.get("market_tick_changes") is not False:
            raise ValueError("Property-Ausbau darf Equipment-Markt-Tick nicht verändern")

        catalog = self.manifest.get("catalog")
        if not isinstance(catalog, Mapping) or not catalog:
            raise ValueError("Property-Upgrade-Katalog fehlt")
        map_catalog = self.city_map.get("property_upgrade_catalog")
        if not isinstance(map_catalog, list):
            raise ValueError("City-Map besitzt keinen Property-Upgrade-Katalog")
        map_upgrade_ids = {
            item.get("upgrade_id")
            for item in map_catalog
            if isinstance(item, Mapping) and isinstance(item.get("upgrade_id"), str)
        }
        if set(catalog) != map_upgrade_ids:
            raise ValueError("Property-Upgrade-Katalog und City-Map-Slots weichen voneinander ab")
        self.catalog: dict[str, dict[str, Any]] = {}
        for upgrade_id, raw in catalog.items():
            upgrade_id = self._text(upgrade_id, "upgrade_id")
            if not isinstance(raw, Mapping):
                raise ValueError("Property-Upgrade-Katalogeintrag muss Mapping sein")
            cost_bps = raw.get("cost_bps")
            deltas = raw.get("value_delta_per_level")
            if isinstance(cost_bps, bool) or not isinstance(cost_bps, int) or cost_bps < 1:
                raise ValueError("Property-Upgrade cost_bps muss positive Ganzzahl sein")
            if not isinstance(deltas, Mapping) or set(deltas) != _VALUE_KEYS:
                raise ValueError("Property-Upgrade benötigt exakt die fünf Location-Wertedeltas")
            if any(isinstance(value, bool) or not isinstance(value, int) for value in deltas.values()):
                raise ValueError("Property-Upgrade-Wertedeltas müssen Ganzzahlen sein")
            self.catalog[upgrade_id] = {
                "cost_bps": cost_bps,
                "value_delta_per_level": dict(deltas),
            }

        raw_locations = self.city_map.get("locations")
        if not isinstance(raw_locations, list):
            raise ValueError("City-Map besitzt keine gültigen Locations")
        self.location_slots: dict[str, frozenset[str]] = {}
        for raw in raw_locations:
            if not isinstance(raw, Mapping):
                continue
            location_id = raw.get("location_id")
            if not isinstance(location_id, str) or not location_id:
                raise ValueError("City-Map besitzt ungültige Location-ID")
            slots = raw.get("upgrade_slots", [])
            if not isinstance(slots, list) or any(slot not in self.catalog for slot in slots):
                raise ValueError("City-Map-Location besitzt ungültige Upgrade-Slots")
            self.location_slots[location_id] = frozenset(slots)

    def current_state(self) -> PropertyUpgradeState:
        raw = (self.persistence.load_state() or {}).get("property_upgrades")
        if raw is None:
            return PropertyUpgradeState(contract_version=self.version)
        if not isinstance(raw, Mapping):
            raise PersistenceError("Property-Upgrade-State ist beschädigt")
        state = PropertyUpgradeState.from_dict(raw)
        if state.contract_version != self.version:
            raise PersistenceError("Property-Upgrade-State verwendet anderen Vertragsstand")
        ownership = self.property.current_state()
        for location_id, record in state.properties.items():
            if location_id not in ownership.owned:
                raise PersistenceError("Property-Upgrade-State verweist auf nicht besessene Location")
            slots = self.location_slots.get(location_id, frozenset())
            for upgrade_id in record["upgrades"]:
                if upgrade_id not in slots:
                    raise PersistenceError("Property-Upgrade-State verwendet nicht erlaubten Location-Slot")
        return state

    def upgrade(
        self,
        location_id: str,
        upgrade_id: str,
        *,
        context: JournalContext,
    ) -> PropertyUpgradeCommitResult:
        self._validate_context(context)
        location_id = self._text(location_id, "location_id")
        upgrade_id = self._text(upgrade_id, "upgrade_id")
        request = {
            "operation": "upgrade_property",
            "location_id": location_id,
            "upgrade_id": upgrade_id,
            "contract_version": self.version,
        }
        existing = self._existing(context.command_id)
        if existing is not None:
            if existing.get("payload", {}).get("request") != request:
                raise PersistenceError("Command-ID wurde mit anderem Property-Ausbau verwendet")
            return self._current_result(location_id, upgrade_id, context=context, replay=True)

        state = deepcopy(self.persistence.load_state() or {})
        required = {"event", "economy", "character", "properties"}
        missing = sorted(required - set(state))
        if missing:
            raise PersistenceError(f"Property-Ausbau benötigt Zustandsblöcke: {', '.join(missing)}")
        event = EventState.from_dict(state["event"])
        economy = EconomyState.from_dict(state["economy"])
        character = CharacterState.from_dict(state["character"])
        properties = PropertyState.from_dict(state["properties"])
        if event.event_id != context.entity_id:
            raise ValueError("Property-Ausbau gehört zu anderem Event-Kontext")
        if context.character_id is not None and context.character_id != character.character_id:
            raise ValueError("Property-Ausbau gehört zu anderem Character-Kontext")

        ownership = properties.owned.get(location_id)
        if ownership is None:
            raise ValueError("Location muss vor dem Ausbau im Besitz sein")
        if ownership["owner_character_id"] != character.character_id:
            raise ValueError("Location gehört nicht zum bestätigten Character")
        slots = self.location_slots.get(location_id)
        if slots is None or upgrade_id not in slots:
            raise ValueError("Ausbau ist für diese Location nicht katalogisiert")
        spec = self.catalog.get(upgrade_id)
        if spec is None:
            raise ValueError("Ausbauart ist nicht katalogisiert")

        upgrades = self.current_state()
        property_record = upgrades.properties.get(location_id)
        upgrade_record = None if property_record is None else property_record["upgrades"].get(upgrade_id)
        current_level = 0 if upgrade_record is None else upgrade_record["level"]
        if current_level >= MAX_UPGRADE_LEVEL:
            raise ValueError("Ausbau hat bereits das maximale Level erreicht")
        next_level = current_level + 1
        cost = upgrade_cost_cents(
            ownership["purchase_price_cents"],
            spec["cost_bps"],
            self.level_multipliers[next_level - 1],
        )
        economy_tx = f"property_upgrade:{context.command_id}"
        prepared = self.economy.prepare_property_upgrade(
            economy,
            event,
            location_id=location_id,
            upgrade_id=upgrade_id,
            next_level=next_level,
            upgrade_cost_cents=cost,
            transaction_id=economy_tx,
        )

        upgrade_data = upgrades.to_dict()
        target = upgrade_data["properties"].setdefault(
            location_id,
            {"location_id": location_id, "upgrades": {}},
        )
        target_upgrade = target["upgrades"].setdefault(
            upgrade_id,
            {"level": 0, "economy_transaction_ids": []},
        )
        target_upgrade["level"] = next_level
        target_upgrade["economy_transaction_ids"].append(economy_tx)
        upgrade_data["revision"] += 1
        upgrades_after = PropertyUpgradeState.from_dict(upgrade_data)

        derived = deepcopy(state)
        derived.update(
            economy=prepared.economy.to_dict(),
            event=prepared.event.to_dict(),
            property_upgrades=upgrades_after.to_dict(),
        )
        economy_payload = {
            "request": {
                "kind": PROPERTY_UPGRADE_LEDGER_KIND,
                "location_id": location_id,
                "upgrade_id": upgrade_id,
                "level": next_level,
                "item_id": prepared.item_id,
                "quantity": 1,
                "unit_price_cents": cost,
            },
            "economy": prepared.economy.to_dict(),
            "event": prepared.event.to_dict(),
        }
        upgrade_payload = {
            "request": request,
            "upgrade": {
                "location_id": location_id,
                "upgrade_id": upgrade_id,
                "previous_level": current_level,
                "new_level": next_level,
                "upgrade_cost_cents": cost,
                "economy_transaction_id": economy_tx,
                "owner_character_id": character.character_id,
                "event_id": event.event_id,
            },
            "property_upgrades": upgrades_after.to_dict(),
        }
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}",
            events=[
                {
                    "event_id": f"{context.command_id}:economy",
                    "event_type": "economy.transaction_posted",
                    "payload": economy_payload,
                },
                {
                    "event_id": f"{context.command_id}:property-upgrade",
                    "event_type": "world.property_upgraded",
                    "payload": upgrade_payload,
                },
            ],
            derived_state=derived,
            context=context,
        )
        return PropertyUpgradeCommitResult(
            upgrades_after,
            prepared.economy,
            prepared.event,
            location_id,
            upgrade_id,
            next_level,
            cost,
            receipt.event_ids,
            False,
        )

    def _current_result(
        self,
        location_id: str,
        upgrade_id: str,
        *,
        context: JournalContext,
        replay: bool,
    ) -> PropertyUpgradeCommitResult:
        state = self.persistence.load_state() or {}
        if not {"event", "economy", "properties", "property_upgrades"}.issubset(state):
            raise PersistenceError("Property-Ausbau-Replay verweist auf unvollständigen Zustand")
        event = EventState.from_dict(state["event"])
        if event.event_id != context.entity_id:
            raise ValueError("Property-Ausbau-Replay gehört zu anderem Event-Kontext")
        economy = EconomyState.from_dict(state["economy"])
        upgrades = PropertyUpgradeState.from_dict(state["property_upgrades"])
        record = upgrades.properties.get(location_id, {}).get("upgrades", {}).get(upgrade_id)
        if not isinstance(record, Mapping):
            raise PersistenceError("Property-Ausbau-Replay besitzt keinen bestätigten Ausbau")
        transaction_id = record["economy_transaction_ids"][-1]
        ledger = next((entry for entry in economy.ledger if entry["transaction_id"] == transaction_id), None)
        if ledger is None or ledger["kind"] != PROPERTY_UPGRADE_LEDGER_KIND:
            raise PersistenceError("Property-Ausbau-Replay besitzt keine passende Economy-Transaktion")
        return PropertyUpgradeCommitResult(
            upgrades,
            economy,
            event,
            location_id,
            upgrade_id,
            record["level"],
            ledger["unit_price_cents"],
            (),
            replay,
        )

    def _existing(self, command_id: str) -> dict[str, Any] | None:
        event_id = f"{command_id}:property-upgrade"
        return next((record for record in self.persistence.read_records() if record["event_id"] == event_id), None)

    @staticmethod
    def _validate_context(context: JournalContext) -> None:
        if context.entity_type != "event" or not context.entity_id or not context.command_id:
            raise ValueError("Property-Ausbau benötigt Event-Kontext mit entity_id und command_id")

    @staticmethod
    def _text(value: Any, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} muss nicht-leerer Text sein")
        return value.strip()


def replay_property_upgrade_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("event_type") != "world.property_upgraded":
        return derived_state
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Property-Ausbau-Replay benötigt Payload")
    raw_state = payload.get("property_upgrades")
    upgrade = payload.get("upgrade")
    request = payload.get("request")
    if not isinstance(raw_state, Mapping) or not isinstance(upgrade, Mapping) or not isinstance(request, Mapping):
        raise ValueError("Property-Ausbau-Replay benötigt bestätigten Ausbau-State und Request")
    upgrades = PropertyUpgradeState.from_dict(raw_state)
    location_id = request.get("location_id")
    upgrade_id = request.get("upgrade_id")
    if not isinstance(location_id, str) or not isinstance(upgrade_id, str):
        raise ValueError("Property-Ausbau-Replay besitzt ungültige IDs")
    state_record = upgrades.properties.get(location_id, {}).get("upgrades", {}).get(upgrade_id)
    if not isinstance(state_record, Mapping) or state_record.get("level") != upgrade.get("new_level"):
        raise ValueError("Property-Ausbau-Replay-State passt nicht zum bestätigten Ausbau")

    state = deepcopy(derived_state)
    if not {"economy", "event", "properties"}.issubset(state):
        raise ValueError("Property-Ausbau-Replay benötigt Economy, Event und Eigentum")
    economy = EconomyState.from_dict(state["economy"])
    event = EventState.from_dict(state["event"])
    properties = PropertyState.from_dict(state["properties"])
    ownership = properties.owned.get(location_id)
    if ownership is None or ownership.get("owner_character_id") != upgrade.get("owner_character_id"):
        raise ValueError("Property-Ausbau-Replay besitzt keine passende bestätigte Eigentümerschaft")
    transaction_id = upgrade.get("economy_transaction_id")
    ledger = next((entry for entry in economy.ledger if entry["transaction_id"] == transaction_id), None)
    if ledger is None or ledger.get("kind") != PROPERTY_UPGRADE_LEDGER_KIND:
        raise ValueError("Property-Ausbau-Replay findet keine passende Economy-Transaktion")
    if ledger.get("unit_price_cents") != upgrade.get("upgrade_cost_cents"):
        raise ValueError("Property-Ausbau-Replay-Kosten widersprechen Economy-Ledger")
    if event.event_id != upgrade.get("event_id"):
        raise ValueError("Property-Ausbau-Replay-Event widerspricht Ausbau")

    current = state.get("property_upgrades")
    if current is not None:
        current_state = PropertyUpgradeState.from_dict(current)
        if current_state.revision > upgrades.revision:
            return state
        if current_state.revision == upgrades.revision:
            if current_state.to_dict() != upgrades.to_dict():
                raise ValueError("Property-Ausbau-Replay kollidiert mit State derselben Revision")
            return state
    state["property_upgrades"] = upgrades.to_dict()
    return state
