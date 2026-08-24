from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


RECOVERY_ACTIONS: tuple[dict[str, Any], ...] = (
    {
        "recovery_id": "recovery.koffein_kalte_luft",
        "label": "Koffein & kalte Luft",
        "description": "Ein kurzer kontrollierter Reset: du bekommst wieder Zug, bezahlst ihn aber mit zusätzlichem Stress.",
        "energy_delta": 20,
        "stress_delta": 12,
        "max_energy_before": 80,
        "max_stress_before": 88,
    },
    {
        "recovery_id": "recovery.mate_zucker_vollgas",
        "label": "Mate, Zucker & Vollgas",
        "description": "Mehr Reserve auf einen Schlag, aber deutlich teurer für den Kopf: der größere Energieschub kostet überproportional Stress.",
        "energy_delta": 30,
        "stress_delta": 20,
        "max_energy_before": 70,
        "max_stress_before": 80,
    },
)


def recovery_action_availability(action: Mapping[str, Any], character: CharacterState) -> dict[str, Any]:
    """Return the canonical read-only availability for one recovery action."""
    max_energy = action["max_energy_before"]
    max_stress = action["max_stress_before"]
    if character.energy > max_energy:
        return {"can_run": False, "blocker": "energy_above_recovery_threshold"}
    if character.stress > max_stress:
        return {"can_run": False, "blocker": "stress_above_recovery_threshold"}
    return {"can_run": True, "blocker": None}


@dataclass(frozen=True, slots=True)
class RecoveryActionResult:
    character: CharacterState
    action: dict[str, Any]
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class RecoveryActionService:
    """Apply small deterministic recovery trades to confirmed character resources."""

    def __init__(self, persistence: PersistenceKernel) -> None:
        self.persistence = persistence
        self.actions = tuple(deepcopy(action) for action in RECOVERY_ACTIONS)
        self.by_id = self._validate_actions()

    def run(self, recovery_id: str, *, context: JournalContext) -> RecoveryActionResult:
        if not isinstance(recovery_id, str) or not recovery_id.strip():
            raise ValueError("Regeneration benötigt recovery_id")
        recovery_id = recovery_id.strip()
        action = self.by_id.get(recovery_id)
        if action is None:
            raise ValueError("Unbekannte Regenerationsaktion")
        if context.entity_type != "character" or not context.entity_id or not context.command_id:
            raise ValueError("Regeneration benötigt bestätigten Character-Kontext")

        event_id = f"{context.command_id}:recovery"
        existing = next(
            (record for record in self.persistence.read_records() if record.get("event_id") == event_id),
            None,
        )
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("source_recovery_id") != recovery_id:
                raise PersistenceError("Command-ID wurde bereits für andere Regenerationsaktion verwendet")
            return self._current_result(action, replay=True)

        state = deepcopy(self.persistence.load_state() or {})
        raw_character = state.get("character")
        if not isinstance(raw_character, dict):
            raise PersistenceError("Regeneration benötigt bestätigten Character-State")
        character = CharacterState.from_dict(raw_character)
        if character.character_id != context.entity_id:
            raise ValueError("Regenerations-Kontext passt nicht zum Character")

        availability = recovery_action_availability(action, character)
        if availability["can_run"] is not True:
            raise ValueError(f"Regeneration aktuell nicht erlaubt: {availability['blocker']}")

        character_after = CharacterState.from_dict(character.to_dict())
        character_after.energy += action["energy_delta"]
        character_after.stress += action["stress_delta"]
        character_after.validate()

        derived = deepcopy(state)
        derived["character"] = character_after.to_dict()
        payload = {
            "source_recovery_id": recovery_id,
            "energy": {
                "old": character.energy,
                "delta": action["energy_delta"],
                "new": character_after.energy,
            },
            "stress": {
                "old": character.stress,
                "delta": action["stress_delta"],
                "new": character_after.stress,
            },
        }
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:recovery",
            events=[
                {
                    "event_id": event_id,
                    "event_type": "character.resources_changed",
                    "payload": payload,
                }
            ],
            derived_state=derived,
            context=context,
        )
        return RecoveryActionResult(character_after, deepcopy(action), receipt.event_ids, False)

    def _current_result(self, action: Mapping[str, Any], *, replay: bool) -> RecoveryActionResult:
        state = self.persistence.load_state() or {}
        raw_character = state.get("character")
        if not isinstance(raw_character, dict):
            raise PersistenceError("Regenerations-Replay verweist auf unvollständigen Character-State")
        return RecoveryActionResult(
            CharacterState.from_dict(raw_character),
            deepcopy(dict(action)),
            (),
            replay,
        )

    def _validate_actions(self) -> dict[str, dict[str, Any]]:
        by_id: dict[str, dict[str, Any]] = {}
        for index, raw in enumerate(self.actions):
            recovery_id = raw.get("recovery_id")
            if not isinstance(recovery_id, str) or not recovery_id.strip() or recovery_id in by_id:
                raise ValueError(f"Regenerationsaktion {index} benötigt eindeutige recovery_id")
            for field in ("label", "description"):
                value = raw.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"Regenerationsaktion {recovery_id} benötigt {field}")
            energy_delta = raw.get("energy_delta")
            stress_delta = raw.get("stress_delta")
            max_energy = raw.get("max_energy_before")
            max_stress = raw.get("max_stress_before")
            if isinstance(energy_delta, bool) or not isinstance(energy_delta, int) or energy_delta <= 0:
                raise ValueError("Regeneration benötigt positiven Energiedelta")
            if isinstance(stress_delta, bool) or not isinstance(stress_delta, int) or stress_delta <= 0:
                raise ValueError("Regeneration benötigt positiven Stresspreis")
            if isinstance(max_energy, bool) or not isinstance(max_energy, int) or not 0 <= max_energy <= 100:
                raise ValueError("Regeneration benötigt gültige Energiegrenze")
            if isinstance(max_stress, bool) or not isinstance(max_stress, int) or not 0 <= max_stress <= 100:
                raise ValueError("Regeneration benötigt gültige Stressgrenze")
            if max_energy + energy_delta > 100:
                raise ValueError("Regenerations-Energiegewinn darf an Zulässigkeitsgrenze nicht clampen")
            if max_stress + stress_delta > 100:
                raise ValueError("Regenerations-Stresspreis darf an Zulässigkeitsgrenze nicht clampen")
            by_id[recovery_id] = deepcopy(raw)
        return by_id
