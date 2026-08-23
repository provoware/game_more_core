from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

from bunkerfrequenz.application.scene_job_service import calculate_scene_job_payout_cents
from bunkerfrequenz.domain.assistant import AssistantControlState
from bunkerfrequenz.domain.character import CharacterState
from bunkerfrequenz.domain.finance import PlayerFinanceState


_PUBLIC_JOB_FIELDS = (
    "job_id",
    "label",
    "description",
    "duration_hours",
    "payout_cents",
    "energy_delta",
    "stress_delta",
)

_STATEMENT_KIND_META = {
    "job_income": {"label": "Joblohn", "group": "jobs"},
    "bank_deposit": {"label": "Einzahlung", "group": "bank"},
    "bank_withdrawal": {"label": "Auszahlung", "group": "bank"},
    "savings_interest": {"label": "Sparzins", "group": "interest"},
}


def _build_finance_statement_projection(
    finance: PlayerFinanceState,
    projected_jobs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Project supported personal ledger rows without inventing time or balances."""
    job_labels = {job["job_id"]: job["label"] for job in projected_jobs}
    totals = {
        "job_income_cents": 0,
        "bank_deposit_cents": 0,
        "bank_withdrawal_cents": 0,
        "savings_interest_cents": 0,
    }
    entries: list[dict[str, Any]] = []
    other_entries = 0

    for index, raw_entry in enumerate(finance.ledger):
        kind = raw_entry["kind"]
        meta = _STATEMENT_KIND_META.get(kind)
        if meta is None:
            other_entries += 1
            continue

        amount_cents = raw_entry["amount_cents"]
        totals[f"{kind}_cents"] += amount_cents
        if kind == "job_income":
            source_label = job_labels.get(raw_entry["source_id"], "Scene Job")
        elif kind in {"bank_deposit", "bank_withdrawal"}:
            source_label = "Persönliche Bank"
        else:
            source_label = "Bestätigte Sparperiode"

        entries.append({
            "sequence": index + 1,
            "transaction_id": raw_entry["transaction_id"],
            "kind": kind,
            "group": meta["group"],
            "label": meta["label"],
            "amount_cents": amount_cents,
            "cash_after_cents": raw_entry["cash_after_cents"],
            "bank_after_cents": raw_entry["bank_after_cents"],
            "source_label": source_label,
        })

    entries.reverse()
    return {
        "available": True,
        "entries": entries,
        "supported_entries": len(entries),
        "other_entries": other_entries,
        "totals": totals,
        "filters": ["all", "jobs", "bank", "interest"],
    }


def build_scene_jobs_projection(
    state: Mapping[str, Any] | None,
    jobs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the read-only A4 Scene-Jobs/Wallet/Bank/Assistant projection.

    `jobs` must come from the already validated SceneJobService catalog. The
    projection exposes confirmed personal finance balances and assistant state,
    but no writable payout/effect, target balance or round authority.
    """
    raw = deepcopy(dict(state or {}))
    raw_character = raw.get("character")
    if raw_character is not None and not isinstance(raw_character, Mapping):
        raise ValueError("Persistierter Character-State muss ein Mapping sein")
    character = CharacterState.from_dict(dict(raw_character)) if isinstance(raw_character, Mapping) else None

    raw_finance = raw.get("finance")
    if raw_finance is not None and not isinstance(raw_finance, Mapping):
        raise ValueError("Persistierter Finance-State muss ein Mapping sein")
    finance = PlayerFinanceState.from_dict(dict(raw_finance) if isinstance(raw_finance, Mapping) else None)

    raw_assistant = raw.get("assistant")
    if raw_assistant is not None and not isinstance(raw_assistant, Mapping):
        raise ValueError("Persistierter Assistant-State muss ein Mapping sein")
    assistant = AssistantControlState.from_dict(
        dict(raw_assistant) if isinstance(raw_assistant, Mapping) else None
    )

    projected_jobs: list[dict[str, Any]] = []
    for index, raw_job in enumerate(jobs):
        if not isinstance(raw_job, Mapping):
            raise ValueError(f"Scene-Job-Projektion jobs[{index}] muss Mapping sein")
        missing = [field for field in _PUBLIC_JOB_FIELDS if field not in raw_job]
        if missing:
            raise ValueError(
                f"Scene-Job-Projektion jobs[{index}] fehlt: {', '.join(missing)}"
            )
        projected = {field: deepcopy(raw_job[field]) for field in _PUBLIC_JOB_FIELDS}
        if character is None:
            projected["effective_payout_cents"] = None
            projected["payout_reduced_by_energy"] = False
        else:
            effective = calculate_scene_job_payout_cents(projected, character.energy)
            projected["effective_payout_cents"] = effective
            projected["payout_reduced_by_energy"] = effective < projected["payout_cents"]
        projected_jobs.append(projected)

    active_job = next(
        (job for job in projected_jobs if job["job_id"] == assistant.active_job_id),
        None,
    )
    if assistant.active_job_id is not None and active_job is None:
        raise ValueError("Assistant-State verweist auf unbekannten Scene Job")

    return {
        "available": character is not None,
        "cash_cents": finance.cash_cents,
        "bank_cents": finance.bank_cents,
        "finance_revision": finance.revision,
        "ledger_entries": len(finance.ledger),
        "finance_statement": _build_finance_statement_projection(finance, projected_jobs),
        "assistant": {
            "enabled": assistant.active_job_id is not None,
            "active_job_id": assistant.active_job_id,
            "active_job_label": active_job["label"] if active_job is not None else None,
            "revision": assistant.revision,
        },
        "jobs": projected_jobs,
    }