from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence

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


def build_scene_jobs_projection(
    state: Mapping[str, Any] | None,
    jobs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the read-only A4 Scene-Jobs/Wallet projection from confirmed state.

    `jobs` must come from the already validated SceneJobService catalog. The
    projection deliberately exposes display consequences, but no writable
    payout/effect authority.
    """
    raw = deepcopy(dict(state or {}))
    raw_finance = raw.get("finance")
    if raw_finance is not None and not isinstance(raw_finance, Mapping):
        raise ValueError("Persistierter Finance-State muss ein Mapping sein")
    finance = PlayerFinanceState.from_dict(dict(raw_finance) if isinstance(raw_finance, Mapping) else None)

    projected_jobs: list[dict[str, Any]] = []
    for index, raw_job in enumerate(jobs):
        if not isinstance(raw_job, Mapping):
            raise ValueError(f"Scene-Job-Projektion jobs[{index}] muss Mapping sein")
        missing = [field for field in _PUBLIC_JOB_FIELDS if field not in raw_job]
        if missing:
            raise ValueError(
                f"Scene-Job-Projektion jobs[{index}] fehlt: {', '.join(missing)}"
            )
        projected_jobs.append({field: deepcopy(raw_job[field]) for field in _PUBLIC_JOB_FIELDS})

    return {
        "available": isinstance(raw.get("character"), Mapping),
        "cash_cents": finance.cash_cents,
        "finance_revision": finance.revision,
        "ledger_entries": len(finance.ledger),
        "jobs": projected_jobs,
    }
