from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from bunkerfrequenz.domain.character import CharacterState, RESOURCE_MAX, RESOURCE_MIN
from bunkerfrequenz.domain.finance import PlayerFinanceState
from bunkerfrequenz.infrastructure.persistence import JournalContext, PersistenceError, PersistenceKernel


def calculate_scene_job_payout_cents(job: Mapping[str, Any], pre_job_energy: int) -> int:
    """Return the canonical Anti-Grind payout for one confirmed pre-job energy value."""
    if isinstance(pre_job_energy, bool) or not isinstance(pre_job_energy, int) or not RESOURCE_MIN <= pre_job_energy <= RESOURCE_MAX:
        raise ValueError("Scene-Job-Lohnvorschau benötigt bestätigte Energie 0..100")
    energy_delta = job.get("energy_delta")
    base_payout = job.get("payout_cents")
    if isinstance(energy_delta, bool) or not isinstance(energy_delta, int) or not -100 <= energy_delta <= 100:
        raise ValueError("Scene Job benötigt gültigen Energieeffekt")
    if isinstance(base_payout, bool) or not isinstance(base_payout, int) or base_payout <= 0:
        raise ValueError("Scene Job benötigt positiven Basislohn")
    energy_cost = max(0, -energy_delta)
    if energy_cost == 0 or pre_job_energy >= energy_cost:
        return base_payout
    if pre_job_energy <= 0:
        return 0
    return base_payout * pre_job_energy // energy_cost


@dataclass(frozen=True, slots=True)
class SceneJobResult:
    character: CharacterState
    finance: PlayerFinanceState
    job: dict[str, Any]
    committed_event_ids: tuple[str, ...]
    idempotent_replay: bool


class SceneJobService:
    """Apply one catalogued always-available scene job atomically."""

    def __init__(self, persistence: PersistenceKernel, manifest: Mapping[str, Any]) -> None:
        self.persistence = persistence
        self.manifest = deepcopy(dict(manifest))
        self.version = self._text(self.manifest.get("version"), "SCENE_JOB_MANIFEST.version")
        policy = self.manifest.get("availability")
        if not isinstance(policy, Mapping):
            raise ValueError("Scene-Job-Manifest benötigt availability")
        if policy.get("always_available_with_character") is not True:
            raise ValueError("Scene Jobs müssen mit vorhandenem Character jederzeit verfügbar sein")
        if policy.get("requires_event_phase") is not False or policy.get("requires_system_time") is not False:
            raise ValueError("Scene Jobs dürfen weder Eventphase noch Systemzeit voraussetzen")
        if policy.get("client_can_supply_payout_or_effects") is not False:
            raise ValueError("Client darf Scene-Job-Auszahlungen oder Effekte nicht liefern")

        exhaustion_policy = self.manifest.get("exhaustion_policy")
        if not isinstance(exhaustion_policy, Mapping):
            raise ValueError("Scene-Job-Manifest benötigt exhaustion_policy")
        self.exhaustion_policy = deepcopy(dict(exhaustion_policy))
        self._validate_exhaustion_policy()

        assistant_policy = self.manifest.get("assistant_policy")
        if not isinstance(assistant_policy, Mapping):
            raise ValueError("Scene-Job-Manifest benötigt assistant_policy")
        self.assistant_policy = deepcopy(dict(assistant_policy))
        self._validate_assistant_policy()
        jobs = self.manifest.get("jobs")
        if not isinstance(jobs, list) or not jobs:
            raise ValueError("Scene-Job-Katalog ist leer")
        self.jobs = tuple(deepcopy(jobs))
        self.by_id = self._validate_jobs()

    def run(self, job_id: str, *, context: JournalContext) -> SceneJobResult:
        job_id = self._text(job_id, "job_id")
        if context.entity_type != "character" or not context.entity_id or not context.command_id:
            raise ValueError("Scene Job benötigt Character-Kontext")
        job = self.by_id.get(job_id)
        if job is None:
            raise ValueError("Unbekannter Scene Job")

        event_id = f"{context.command_id}:job"
        existing = next((record for record in self.persistence.read_records() if record.get("event_id") == event_id), None)
        if existing is not None:
            payload = existing.get("payload", {})
            if payload.get("job_id") != job_id:
                raise PersistenceError("Command-ID wurde bereits für anderen Scene Job verwendet")
            return self._current_result(job, replay=True)

        state = deepcopy(self.persistence.load_state() or {})
        raw_character = state.get("character")
        if not isinstance(raw_character, dict):
            raise PersistenceError("Scene Job benötigt bestätigten Character-State")
        character = CharacterState.from_dict(raw_character)
        if character.character_id != context.entity_id:
            raise ValueError("Scene-Job-Kontext passt nicht zum Character")
        finance = PlayerFinanceState.from_dict(state.get("finance") if isinstance(state.get("finance"), dict) else None)

        effective_payout_cents = calculate_scene_job_payout_cents(job, character.energy)
        energy_after = min(RESOURCE_MAX, max(RESOURCE_MIN, character.energy + job["energy_delta"]))
        stress_after = min(RESOURCE_MAX, max(RESOURCE_MIN, character.stress + job["stress_delta"]))
        character_after = CharacterState.from_dict(character.to_dict())
        character_after.energy = energy_after
        character_after.stress = stress_after
        character_after.validate()

        finance_after = PlayerFinanceState.from_dict(finance.to_dict())
        finance_after.cash_cents += effective_payout_cents
        finance_after.revision += 1
        finance_after.ledger.append({
            "transaction_id": f"job:{context.command_id}",
            "kind": "job_income",
            "amount_cents": effective_payout_cents,
            "cash_after_cents": finance_after.cash_cents,
            "bank_after_cents": finance_after.bank_cents,
            "asset_id": None,
            "units": 0,
            "unit_price_cents": 0,
            "source_id": job_id,
        })
        finance_after.validate()

        derived = deepcopy(state)
        derived["character"] = character_after.to_dict()
        derived["finance"] = finance_after.to_dict()
        resource_payload = {
            "energy": {"old": character.energy, "delta": job["energy_delta"], "new": energy_after},
            "stress": {"old": character.stress, "delta": job["stress_delta"], "new": stress_after},
        }
        job_payload = {
            "contract_version": self.version,
            "job_id": job_id,
            "duration_hours": job["duration_hours"],
            "payout_cents": effective_payout_cents,
            "finance": finance_after.to_dict(),
        }
        receipt = self.persistence.commit(
            transaction_id=f"tx:{context.command_id}:scene-job",
            events=[
                {
                    "event_id": f"{context.command_id}:resources",
                    "event_type": "character.resources_changed",
                    "payload": resource_payload,
                },
                {
                    "event_id": event_id,
                    "event_type": "finance.job_completed",
                    "payload": job_payload,
                },
            ],
            derived_state=derived,
            context=context,
        )
        return SceneJobResult(character_after, finance_after, deepcopy(job), receipt.event_ids, False)

    def _current_result(self, job: Mapping[str, Any], *, replay: bool) -> SceneJobResult:
        state = self.persistence.load_state() or {}
        raw_character = state.get("character")
        raw_finance = state.get("finance")
        if not isinstance(raw_character, dict) or not isinstance(raw_finance, dict):
            raise PersistenceError("Scene-Job-Replay verweist auf unvollständigen Zustand")
        return SceneJobResult(
            CharacterState.from_dict(raw_character),
            PlayerFinanceState.from_dict(raw_finance),
            deepcopy(dict(job)),
            (),
            replay,
        )

    def _validate_exhaustion_policy(self) -> None:
        policy = self.exhaustion_policy
        if policy.get("mode") != "pre_job_energy_proportional_payout":
            raise ValueError("Scene-Job-Erschöpfung benötigt proportionalen Energie-Lohnvertrag")
        if policy.get("jobs_remain_available") is not True:
            raise ValueError("Scene Jobs müssen auch bei Erschöpfung verfügbar bleiben")
        if policy.get("full_payout_requires_energy_cost") is not True:
            raise ValueError("Voller Scene-Job-Lohn muss den Energieverbrauch decken")
        if policy.get("zero_energy_payout_cents") != 0:
            raise ValueError("Scene Jobs dürfen bei 0 Energie keinen Joblohn erzeugen")
        if policy.get("requires_system_time") is not False:
            raise ValueError("Scene-Job-Erschöpfung darf keine Systemzeit voraussetzen")
        if policy.get("client_can_supply_modifier") is not False:
            raise ValueError("Client darf keinen Erschöpfungs-Lohnfaktor liefern")
        if policy.get("second_exhaustion_resource") is not False:
            raise ValueError("Scene Jobs dürfen keine zweite Erschöpfungsressource einführen")

    def _validate_assistant_policy(self) -> None:
        policy = self.assistant_policy
        if policy.get("task_source") != "scene_jobs":
            raise ValueError("Assistent muss den kanonischen Scene-Job-Katalog wiederverwenden")
        if policy.get("max_active_tasks") != 1:
            raise ValueError("Assistent erlaubt exakt eine aktive Aufgabe")
        if policy.get("requires_confirmed_round") is not True:
            raise ValueError("Assistent benötigt eine bestätigte Spielrunde")
        if policy.get("requires_system_time") is not False:
            raise ValueError("Systemzeit darf keine Assistenten-Autorität sein")
        if policy.get("client_can_supply_round_authority") is not False:
            raise ValueError("Client darf keine Assistenten-Rundenautorität liefern")
        if policy.get("client_can_supply_payout_or_effects") is not False:
            raise ValueError("Client darf keine Assistenten-Auszahlung oder Effekte liefern")
        if policy.get("stop_and_switch_required") is not True:
            raise ValueError("Assistent benötigt expliziten Stop und Aufgabenwechsel")

    def _validate_jobs(self) -> dict[str, dict[str, Any]]:
        by_id: dict[str, dict[str, Any]] = {}
        for index, raw in enumerate(self.jobs):
            if not isinstance(raw, Mapping):
                raise ValueError(f"jobs[{index}] muss Objekt sein")
            job = deepcopy(dict(raw))
            job_id = self._text(job.get("job_id"), f"jobs[{index}].job_id")
            if job_id in by_id:
                raise ValueError(f"Doppelte Scene-Job-ID: {job_id}")
            self._text(job.get("label"), f"jobs[{index}].label")
            self._text(job.get("description"), f"jobs[{index}].description")
            for key in ("duration_hours", "payout_cents"):
                value = job.get(key)
                if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                    raise ValueError(f"jobs[{index}].{key} muss positive Ganzzahl sein")
            for key in ("energy_delta", "stress_delta"):
                value = job.get(key)
                if isinstance(value, bool) or not isinstance(value, int) or not -100 <= value <= 100:
                    raise ValueError(f"jobs[{index}].{key} liegt außerhalb -100..100")
            by_id[job_id] = job
        return by_id

    @staticmethod
    def _text(value: Any, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} muss nicht-leerer Text sein")
        return value.strip()


def replay_finance_job_event(derived_state: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    if record.get("event_type") != "finance.job_completed":
        return derived_state
    payload = record.get("payload", {})
    raw_finance = payload.get("finance")
    if not isinstance(raw_finance, dict):
        raise ValueError("finance.job_completed benötigt Finance-Zielzustand")
    target = PlayerFinanceState.from_dict(raw_finance)
    state = deepcopy(derived_state)
    current = PlayerFinanceState.from_dict(state.get("finance") if isinstance(state.get("finance"), dict) else None)
    if target.revision < current.revision:
        raise ValueError("Finance-Replay würde Revision zurücksetzen")
    if target.revision == current.revision:
        if target.to_dict() != current.to_dict():
            raise ValueError("Finance-Replay kollidiert auf gleicher Revision")
        return state
    if target.revision != current.revision + 1:
        raise ValueError("Finance-Replay überspringt Revision")
    state["finance"] = target.to_dict()
    return state