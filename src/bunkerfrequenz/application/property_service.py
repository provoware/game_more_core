from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.application.economy_service import EconomyService
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.economy import EconomyState, PROPERTY_PURCHASE_LEDGER_KIND
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.property import PropertyState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


@dataclass(frozen=True, slots=True)
class PropertyCommitResult:
    properties: PropertyState
    economy: EconomyState
    event: EventState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class PropertyService:
    """Purchase catalogued City-Map properties with one atomic Economy commit."""

    def __init__(
        self,
        persistence: PersistenceKernel,
        property_manifest: Mapping[str, Any],
        city_map_manifest: Mapping[str, Any],
    ) -> None:
        self.persistence = persistence
        self.economy = EconomyService(persistence)
        self.manifest = deepcopy(dict(property_manifest))
        self.city_map = deepcopy(dict(city_map_manifest))
        self.version = self._text(self.manifest.get("version"), "PROPERTY_MANIFEST.version")
        if self.version != "0.8.6-a1":
            raise ValueError("Property-Manifest besitzt unerwartete Version")
        if self.manifest.get("state_block") != "properties":
            raise ValueError("Property-Manifest besitzt falschen state_block")
        if self.manifest.get("city_map_manifest_version") != self.city_map.get("version"):
            raise ValueError("Property- und City-Map-Vertrag passen nicht zusammen")
        purchase = self.manifest.get("purchase")
        if not isinstance(purchase, Mapping):
            raise ValueError("Property-Manifest benötigt purchase-Vertrag")
        if purchase.get("client_price_authority") is not False:
            raise ValueError("Client darf keinen Property-Kaufpreis bestimmen")
        if purchase.get("atomic_with_economy") is not True:
            raise ValueError("Property-Kauf muss atomar mit Economy sein")
        if purchase.get("economy_ledger_kind") != PROPERTY_PURCHASE_LEDGER_KIND:
            raise ValueError("Property- und Economy-Ledger-Vertrag widersprechen sich")

        raw_locations = self.city_map.get("locations")
        if not isinstance(raw_locations, list) or not raw_locations:
            raise ValueError("City-Map besitzt keine Locations")
        self.locations: dict[str, dict[str, Any]] = {}
        for raw in raw_locations:
            if not isinstance(raw, Mapping):
                raise ValueError("City-Map-Location muss Mapping sein")
            location_id = self._text(raw.get("location_id"), "location_id")
            if location_id in self.locations:
                raise ValueError("City-Map besitzt doppelte Location-ID")
            self.locations[location_id] = deepcopy(dict(raw))

    def current_state(self) -> PropertyState:
        raw = (self.persistence.load_state() or {}).get("properties")
        if raw is None:
            return PropertyState(contract_version=self.version)
        if not isinstance(raw, Mapping):
            raise PersistenceError("Property-State ist beschädigt")
        state = PropertyState.from_dict(raw)
        if state.contract_version != self.version:
            raise PersistenceError("Property-State verwendet anderen Vertragsstand")
        unknown = set(state.owned) - set(self.locations)
        if unknown:
            raise PersistenceError("Property-State verweist auf unbekannte Location")
        for location_id in state.owned:
            if self.locations[location_id].get("purchasable") is not True:
                raise PersistenceError("Property-State besitzt nicht kaufbare Location")
        return state

    def purchase(self, location_id: str, *, context: JournalContext) -> PropertyCommitResult:
        self._validate_context(context)
        location_id = self._text(location_id, "location_id")
        request = {
            "operation": "purchase_property",
            "location_id": location_id,
            "contract_version": self.version,
        }
        existing = self._existing(context.command_id)
        if existing is not None:
            if existing.get("payload", {}).get("request") != request:
                raise PersistenceError("Command-ID wurde mit anderem Property-Kauf verwendet")
            return self._current_result(location_id, context=context, replay=True)

        state = deepcopy(self.persistence.load_state() or {})
        required = {"event", "economy", "character"}
        missing = sorted(required - set(state))
        if missing:
            raise PersistenceError(f"Property-Kauf benötigt Zustandsblöcke: {', '.join(missing)}")
        event = EventState.from_dict(state["event"])
        economy = EconomyState.from_dict(state["economy"])
        character = CharacterState.from_dict(state["character"])
        if event.event_id != context.entity_id:
            raise ValueError("Property-Kauf gehört zu anderem Event-Kontext")
        if context.character_id is not None and context.character_id != character.character_id:
            raise ValueError("Property-Kauf gehört zu anderem Character-Kontext")

        properties = self.current_state()
        if location_id in properties.owned:
            raise ValueError("Location ist bereits im Besitz")
        location = self.locations.get(location_id)
        if location is None:
            raise ValueError("Location ist nicht katalogisiert")
        if location.get("purchasable") is not True:
            raise ValueError("Location ist nicht kaufbar")
        purchase_price = location.get("purchase_price_cents")
        if isinstance(purchase_price, bool) or not isinstance(purchase_price, int) or purchase_price < 1:
            raise ValueError("Kaufbare Location besitzt keinen gültigen Kaufpreis")

        economy_tx = f"property:{context.command_id}"
        prepared = self.economy.prepare_property_purchase(
            economy,
            event,
            location_id=location_id,
            purchase_price_cents=purchase_price,
            transaction_id=economy_tx,
        )

        property_data = properties.to_dict()
        property_data["owned"][location_id] = {
            "location_id": location_id,
            "owner_character_id": character.character_id,
            "purchase_price_cents": purchase_price,
            "economy_transaction_id": economy_tx,
            "event_id": event.event_id,
        }
        property_data["revision"] += 1
        properties_after = PropertyState.from_dict(property_data)

        derived = deepcopy(state)
        derived.update(
            economy=prepared.economy.to_dict(),
            event=prepared.event.to_dict(),
            properties=properties_after.to_dict(),
        )
        economy_payload = {
            "request": {
                "kind": PROPERTY_PURCHASE_LEDGER_KIND,
                "location_id": location_id,
                "item_id": prepared.item_id,
                "quantity": 1,
                "unit_price_cents": purchase_price,
            },
            "economy": prepared.economy.to_dict(),
            "event": prepared.event.to_dict(),
        }
        ownership = deepcopy(properties_after.owned[location_id])
        property_payload = {
            "request": request,
            "ownership": ownership,
            "properties": properties_after.to_dict(),
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
                    "event_id": f"{context.command_id}:property",
                    "event_type": "world.property_purchased",
                    "payload": property_payload,
                },
            ],
            derived_state=derived,
            context=context,
        )
        return PropertyCommitResult(
            properties_after,
            prepared.economy,
            prepared.event,
            receipt.event_ids,
            False,
        )

    def _current_result(
        self,
        location_id: str,
        *,
        context: JournalContext,
        replay: bool,
    ) -> PropertyCommitResult:
        state = self.persistence.load_state() or {}
        if not {"event", "economy", "properties"}.issubset(state):
            raise PersistenceError("Property-Replay verweist auf unvollständigen Zustand")
        event = EventState.from_dict(state["event"])
        if event.event_id != context.entity_id:
            raise ValueError("Property-Replay gehört zu anderem Event-Kontext")
        economy = EconomyState.from_dict(state["economy"])
        properties = PropertyState.from_dict(state["properties"])
        ownership = properties.owned.get(location_id)
        if ownership is None:
            raise PersistenceError("Property-Replay besitzt keinen bestätigten Eigentumsrecord")
        transaction_id = ownership["economy_transaction_id"]
        ledger = next((entry for entry in economy.ledger if entry["transaction_id"] == transaction_id), None)
        if ledger is None or ledger["kind"] != PROPERTY_PURCHASE_LEDGER_KIND:
            raise PersistenceError("Property-Replay besitzt keine passende Economy-Transaktion")
        if ledger["unit_price_cents"] != ownership["purchase_price_cents"]:
            raise PersistenceError("Property-Replay besitzt widersprüchlichen Kaufpreis")
        return PropertyCommitResult(properties, economy, event, (), replay)

    def _existing(self, command_id: str) -> dict[str, Any] | None:
        event_id = f"{command_id}:property"
        return next((record for record in self.persistence.read_records() if record["event_id"] == event_id), None)

    @staticmethod
    def _validate_context(context: JournalContext) -> None:
        if context.entity_type != "event" or not context.entity_id or not context.command_id:
            raise ValueError("Property-Kauf benötigt Event-Kontext mit entity_id und command_id")

    @staticmethod
    def _text(value: Any, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} muss nicht-leerer Text sein")
        return value.strip()


def replay_property_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("event_type") != "world.property_purchased":
        return derived_state
    payload = record.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Property-Replay benötigt Payload")
    raw_properties = payload.get("properties")
    ownership = payload.get("ownership")
    request = payload.get("request")
    if not isinstance(raw_properties, Mapping) or not isinstance(ownership, Mapping) or not isinstance(request, Mapping):
        raise ValueError("Property-Replay benötigt bestätigten Property-State und Request")
    properties = PropertyState.from_dict(raw_properties)
    location_id = request.get("location_id")
    if not isinstance(location_id, str) or location_id not in properties.owned:
        raise ValueError("Property-Replay verweist auf unbekannten Eigentumsrecord")
    if properties.owned[location_id] != dict(ownership):
        raise ValueError("Property-Replay-Ownership passt nicht zum bestätigten State")

    state = deepcopy(derived_state)
    if "economy" not in state or "event" not in state:
        raise ValueError("Property-Replay benötigt zuvor bestätigte Economy-/Event-Transaktion")
    economy = EconomyState.from_dict(state["economy"])
    event = EventState.from_dict(state["event"])
    transaction_id = ownership.get("economy_transaction_id")
    ledger = next((entry for entry in economy.ledger if entry["transaction_id"] == transaction_id), None)
    if ledger is None or ledger.get("kind") != PROPERTY_PURCHASE_LEDGER_KIND:
        raise ValueError("Property-Replay findet keine passende Economy-Transaktion")
    if ledger.get("unit_price_cents") != ownership.get("purchase_price_cents"):
        raise ValueError("Property-Replay-Kaufpreis widerspricht Economy-Ledger")
    if event.event_id != ownership.get("event_id"):
        raise ValueError("Property-Replay-Event widerspricht Ownership")

    current = state.get("properties")
    if current is not None:
        current_properties = PropertyState.from_dict(current)
        if current_properties.revision > properties.revision:
            return state
        if current_properties.revision == properties.revision:
            if current_properties.to_dict() != properties.to_dict():
                raise ValueError("Property-Replay kollidiert mit State derselben Revision")
            return state
    state["properties"] = properties.to_dict()
    return state
