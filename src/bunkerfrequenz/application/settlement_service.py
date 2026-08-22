from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from bunkerfrequenz.domain.character import CharacterState, RESOURCE_MAX, RESOURCE_MIN
from bunkerfrequenz.domain.economy import EconomyState
from bunkerfrequenz.domain.event import EventState
from bunkerfrequenz.domain.incident import IncidentState
from bunkerfrequenz.domain.settlement import SettlementState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel

SETTLEMENT_LEDGER_ITEM_ID = "__event_settlement__"
_EFFECT_KEYS = (
    "budget_delta_cents",
    "reputation_delta",
    "crew_stress_delta",
    "stability_delta",
    "heat_delta",
)


@dataclass(frozen=True, slots=True)
class SettlementCommitResult:
    event: EventState
    economy: EconomyState
    character: CharacterState
    incidents: IncidentState
    settlement: SettlementState
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class SettlementService:
    """Finalize one event atomically from already confirmed event/economy/incident state."""

    def __init__(self, persistence: PersistenceKernel, *, contract_version: str = "0.8.3-c1"):
        self.persistence = persistence
        self.contract_version = contract_version

    def complete(self, *, context: JournalContext) -> SettlementCommitResult:
        self._validate_context(context)
        request = {"operation": "complete_settlement", "contract_version": self.contract_version}
        existing = self._existing(context.command_id)
        if existing is not None:
            if existing.get("payload", {}).get("request") != request:
                raise PersistenceError("Command-ID wurde mit anderem Settlement verwendet")
            return self._current_result(context, replay=True)

        event, economy, character, incidents, state = self._load(context)
        if event.phase != "settlement":
            raise ValueError("Settlement kann nur aus Eventphase settlement abgeschlossen werden")
        if incidents.active is not None:
            raise ValueError("Settlement ist mit aktivem Incident nicht erlaubt")
        if "settlement" in state:
            raise PersistenceError("Settlement-State existiert ohne passenden idempotenten Abschlussrecord")
        if not any(member["character_id"] == character.character_id for member in event.crew):
            raise ValueError("Settlement-Character ist dem Event nicht als Crew zugeordnet")

        effects = {key: incidents.pending_settlement[key] for key in _EFFECT_KEYS}
        budget_after = event.budget_cents + effects["budget_delta_cents"]
        if budget_after < 0:
            raise ValueError("Settlement würde Event-Budget negativ machen; Defizitregel fehlt")

        economy_after = self._apply_economy_settlement(
            economy,
            transaction_id=f"settlement:{context.command_id}",
            budget_delta_cents=effects["budget_delta_cents"],
        )
        budget_event = self._apply_budget_to_event(event, budget_after)
        character_after = self._apply_character_effects(character, effects)
        final_event = budget_event.transition_to("completed")
        incidents_after = self._consume_pending_incidents(incidents)

        settlement = SettlementState(
            event_id=event.event_id,
            settlement_id=f"settlement:{context.command_id}",
            contract_version=self.contract_version,
            incident_ids=[item["incident_id"] for item in incidents.history],
            effects=effects,
            budget={"old": event.budget_cents, "delta": effects["budget_delta_cents"], "new": budget_after},
            character_id=character.character_id,
            stress={
                "old": character.stress,
                "delta": effects["crew_stress_delta"],
                "new": character_after.stress,
            },
            reputation={
                "old": character.reputation,
                "delta": effects["reputation_delta"],
                "new": character_after.reputation,
            },
            event_revision={"old": event.revision, "new": final_event.revision},
            economy_revision={"old": economy.revision, "new": economy_after.revision},
            incident_revision={"old": incidents.revision, "new": incidents_after.revision},
        )
        settlement.validate()

        derived = deepcopy(state)
        derived.update(
            event=final_event.to_dict(),
            economy=economy_after.to_dict(),
            character=character_after.to_dict(),
            incidents=incidents_after.to_dict(),
            settlement=settlement.to_dict(),
        )

        resource_payload = {
            "energy": {"old": character.energy, "delta": 0, "new": character.energy},
            "stress": {
                "old": character.stress,
                "delta": effects["crew_stress_delta"],
                "new": character_after.stress,
            },
        }
        reputation_payload = {
            "old": character.reputation,
            "delta": effects["reputation_delta"],
            "new": character_after.reputation,
            "reason": "event_settlement",
        }
        phase_payload = {
            "event_id": event.event_id,
            "old_phase": budget_event.phase,
            "new_phase": final_event.phase,
            "old_revision": budget_event.revision,
            "new_revision": final_event.revision,
            "reason": "event_settlement:complete",
        }
        completed_payload = {
            "request": request,
            "event": final_event.to_dict(),
            "incidents": incidents_after.to_dict(),
            "settlement": settlement.to_dict(),
        }
        economy_payload = {
            "request": {
                "kind": "settlement",
                "settlement_id": settlement.settlement_id,
                "budget_delta_cents": effects["budget_delta_cents"],
            },
            "economy": economy_after.to_dict(),
            "event": budget_event.to_dict(),
        }
        biography_payload = {
            "entry_id": f"bio:{settlement.settlement_id}",
            "category": "event",
            "title_key": "biography.action.event.title",
            "body_key": "biography.action.event.body",
            "placeholders": {
                "event_id": event.event_id,
                "incident_count": len(settlement.incident_ids),
                "budget_delta_cents": effects["budget_delta_cents"],
                "reputation_delta": effects["reputation_delta"],
                "stability_delta": effects["stability_delta"],
                "heat_delta": effects["heat_delta"],
            },
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
                    "event_id": f"{context.command_id}:resources",
                    "event_type": "character.resources_changed",
                    "payload": resource_payload,
                },
                {
                    "event_id": f"{context.command_id}:reputation",
                    "event_type": "character.reputation_changed",
                    "payload": reputation_payload,
                },
                {
                    "event_id": f"{context.command_id}:biography",
                    "event_type": "character.biography_entry_added",
                    "payload": biography_payload,
                },
                {
                    "event_id": f"{context.command_id}:event",
                    "event_type": "event.phase_changed",
                    "payload": phase_payload,
                },
                {
                    "event_id": f"{context.command_id}:completed",
                    "event_type": "event.completed",
                    "payload": completed_payload,
                },
            ],
            derived_state=derived,
            context=context,
        )
        return SettlementCommitResult(
            final_event,
            economy_after,
            character_after,
            incidents_after,
            settlement,
            receipt.event_ids,
            False,
        )

    @staticmethod
    def _apply_economy_settlement(
        economy: EconomyState,
        *,
        transaction_id: str,
        budget_delta_cents: int,
    ) -> EconomyState:
        data = economy.to_dict()
        if any(entry["transaction_id"] == transaction_id for entry in data["ledger"]):
            raise PersistenceError("Settlement-Transaktion existiert bereits im Economy-Ledger")
        data["ledger"].append({
            "transaction_id": transaction_id,
            "kind": "settlement",
            "item_id": SETTLEMENT_LEDGER_ITEM_ID,
            "quantity": 1,
            "unit_price_cents": 0,
            "budget_delta_cents": budget_delta_cents,
            "compensates": None,
        })
        data["revision"] += 1
        return EconomyState.from_dict(data)

    @staticmethod
    def _apply_budget_to_event(event: EventState, budget_after: int) -> EventState:
        data = event.to_dict()
        data["budget_cents"] = budget_after
        data["revision"] += 1
        return EventState.from_dict(data)

    @staticmethod
    def _apply_character_effects(character: CharacterState, effects: dict[str, int]) -> CharacterState:
        data = character.to_dict()
        data["stress"] = min(
            RESOURCE_MAX,
            max(RESOURCE_MIN, character.stress + effects["crew_stress_delta"]),
        )
        data["reputation"] = character.reputation + effects["reputation_delta"]
        return CharacterState.from_dict(data)

    @staticmethod
    def _consume_pending_incidents(incidents: IncidentState) -> IncidentState:
        data = incidents.to_dict()
        data["pending_settlement"] = {key: 0 for key in _EFFECT_KEYS}
        data["revision"] += 1
        return IncidentState.from_dict(data)

    def _load(
        self,
        context: JournalContext,
    ) -> tuple[EventState, EconomyState, CharacterState, IncidentState, dict[str, Any]]:
        state = deepcopy(self.persistence.load_state() or {})
        required = {"event", "economy", "character", "incidents"}
        missing = sorted(required - set(state))
        if missing:
            raise PersistenceError(f"Settlement benötigt Zustandsblöcke: {', '.join(missing)}")
        event = EventState.from_dict(state["event"])
        if context.entity_id != event.event_id:
            raise ValueError("JournalContext.entity_id passt nicht zum bestätigten Event")
        economy = EconomyState.from_dict(state["economy"])
        character = CharacterState.from_dict(state["character"])
        incidents = IncidentState.from_dict(state["incidents"])
        if incidents.event_id != event.event_id:
            raise PersistenceError("Incident-State gehört zu anderem Event")
        return event, economy, character, incidents, state

    def _existing(self, command_id: str) -> dict[str, Any] | None:
        event_id = f"{command_id}:completed"
        return next((record for record in self.persistence.read_records() if record["event_id"] == event_id), None)

    def _current_result(self, context: JournalContext, *, replay: bool) -> SettlementCommitResult:
        state = self.persistence.load_state() or {}
        required = {"event", "economy", "character", "incidents", "settlement"}
        if not required.issubset(state):
            raise PersistenceError("Settlement-Replay verweist auf unvollständigen Zustand")
        event = EventState.from_dict(state["event"])
        if context.entity_id != event.event_id:
            raise ValueError("JournalContext.entity_id passt nicht zum bestätigten Event")
        settlement = SettlementState.from_dict(state["settlement"])
        if settlement.event_id != event.event_id:
            raise PersistenceError("Settlement-State gehört zu anderem Event")
        return SettlementCommitResult(
            event,
            EconomyState.from_dict(state["economy"]),
            CharacterState.from_dict(state["character"]),
            IncidentState.from_dict(state["incidents"]),
            settlement,
            (),
            replay,
        )

    @staticmethod
    def _validate_context(context: JournalContext) -> None:
        if context.entity_type != "event" or not context.entity_id or not context.command_id:
            raise ValueError("Settlement benötigt Event-Kontext mit entity_id und command_id")


def replay_settlement_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record["event_type"] != "event.completed":
        return derived_state

    payload = record.get("payload", {})
    target_event = EventState.from_dict(payload["event"])
    target_incidents = IncidentState.from_dict(payload["incidents"])
    target_settlement = SettlementState.from_dict(payload["settlement"])
    if target_event.event_id != target_settlement.event_id or target_incidents.event_id != target_event.event_id:
        raise ValueError("Settlement-Replay verweist auf widersprüchliche Event-IDs")

    state = deepcopy(derived_state)
    existing = state.get("settlement")
    if existing is not None:
        current_settlement = SettlementState.from_dict(existing)
        if (
            current_settlement.to_dict() != target_settlement.to_dict()
            or state.get("event") != target_event.to_dict()
            or state.get("incidents") != target_incidents.to_dict()
        ):
            raise ValueError("event.completed kollidiert mit vorhandenem Settlement")
        return state

    required = {"event", "economy", "character", "incidents"}
    if not required.issubset(state):
        raise ValueError("event.completed benötigt Event-, Economy-, Character- und Incident-State")

    current_event = EventState.from_dict(state["event"])
    current_economy = EconomyState.from_dict(state["economy"])
    current_character = CharacterState.from_dict(state["character"])
    current_incidents = IncidentState.from_dict(state["incidents"])

    if current_event.to_dict() != target_event.to_dict():
        raise ValueError("event.completed passt nicht zum zuvor bestätigten Phasenwechsel")
    if current_event.budget_cents != target_settlement.budget["new"]:
        raise ValueError("Settlement-Replay besitzt falsches Event-Budget")
    if current_economy.revision != target_settlement.economy_revision["new"]:
        raise ValueError("Settlement-Replay besitzt falsche Economy-Revision")
    if current_character.character_id != target_settlement.character_id:
        raise ValueError("Settlement-Replay verweist auf anderen Character")
    if current_character.stress != target_settlement.stress["new"]:
        raise ValueError("Settlement-Replay besitzt falschen Stress-Zielwert")
    if current_character.reputation != target_settlement.reputation["new"]:
        raise ValueError("Settlement-Replay besitzt falschen Ruf-Zielwert")
    if current_incidents.active is not None:
        raise ValueError("Settlement-Replay ist mit aktivem Incident unzulässig")
    if current_incidents.revision != target_settlement.incident_revision["old"]:
        raise ValueError("Settlement-Replay besitzt falsche Incident-Ausgangsrevision")
    if current_incidents.pending_settlement != target_settlement.effects:
        raise ValueError("Settlement-Replay-Effekte stimmen nicht mit pending_settlement überein")
    if target_incidents.revision != current_incidents.revision + 1:
        raise ValueError("Settlement-Replay besitzt falsche Incident-Zielrevision")
    if target_incidents.history != current_incidents.history or target_incidents.active is not None:
        raise ValueError("Settlement-Replay darf Incident-Historie nicht verändern")
    if any(target_incidents.pending_settlement.values()):
        raise ValueError("Settlement-Replay muss pending_settlement vollständig leeren")

    state["incidents"] = target_incidents.to_dict()
    state["settlement"] = target_settlement.to_dict()
    return state
