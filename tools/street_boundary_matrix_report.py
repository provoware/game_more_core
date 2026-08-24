#!/usr/bin/env python3
"""Generate a deterministic Street approach/distribution matrix from the canonical manifest.

The report is read-only. It reuses the runtime selector to prove that every bucket maps
exactly to the weight declared for each approach; it does not simulate gameplay state.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from bunkerfrequenz.application.street_encounter_service import _select, _validate_manifest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "STREET_ENCOUNTER_MANIFEST.json"


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Street-Manifest muss ein JSON-Objekt sein")
    return value


def boundary_labels(effects: dict[str, int]) -> str:
    labels: list[str] = []
    if effects["energy_delta"] > 0:
        labels.append("Energie 100")
    elif effects["energy_delta"] < 0:
        labels.append("Energie 0")
    if effects["stress_delta"] > 0:
        labels.append("Stress 100")
    elif effects["stress_delta"] < 0:
        labels.append("Stress 0")
    if effects["reputation_delta"] < 0:
        labels.append("Ruf 0")
    return ", ".join(labels) if labels else "kein Klemmgrenz-Effekt"


def build_rows(manifest: dict) -> tuple[int, list[dict[str, object]]]:
    _, weight_total, encounters, _, approaches, _ = _validate_manifest(manifest)
    rows: list[dict[str, object]] = []

    for approach_id, approach in approaches.items():
        weights = approach["weights"]
        observed = Counter(
            str(_select(encounters, weights, bucket)["encounter_id"])
            for bucket in range(weight_total)
        )
        cursor = 0
        for encounter in encounters:
            encounter_id = str(encounter["encounter_id"])
            weight = int(weights[encounter_id])
            start = cursor if weight else None
            end = cursor + weight - 1 if weight else None
            rows.append({
                "approach_id": approach_id,
                "encounter_id": encounter_id,
                "polarity": encounter["polarity"],
                "declared_weight": weight,
                "observed_buckets": observed[encounter_id],
                "bucket_range": "–" if start is None else f"{start}–{end}",
                "boundary": boundary_labels(dict(encounter["effects"])),
                "selectable": weight > 0,
            })
            cursor += weight

        if cursor != weight_total:
            raise AssertionError(f"{approach_id}: Gewichte enden bei {cursor}, erwartet {weight_total}")
        declared = Counter({key: int(value) for key, value in weights.items()})
        if observed != declared:
            raise AssertionError(
                f"{approach_id}: Runtime-Bucketverteilung {dict(observed)} != Manifest {dict(declared)}"
            )

    return weight_total, rows


def render_markdown(manifest: dict) -> str:
    weight_total, rows = build_rows(manifest)
    lines = [
        "# Street Boundary & Distribution Matrix",
        "",
        f"Quelle: `manifests/STREET_ENCOUNTER_MANIFEST.json` · Version `{manifest['version']}` · {weight_total} deterministische Buckets je Ansatz.",
        "",
        "Erzeugung: `PYTHONPATH=src python3 tools/street_boundary_matrix_report.py`",
        "",
        "| Ansatz | Begegnung | Polarität | Gewicht | Runtime-Buckets | Bucketbereich | relevante Klemmgrenze |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['approach_id']} | `{row['encounter_id']}` | {row['polarity']} | "
            f"{row['declared_weight']} | {row['observed_buckets']} | {row['bucket_range']} | {row['boundary']} |"
        )
    lines.extend((
        "",
        "**Nachweis:** Für jeden Ansatz werden alle Bucketwerte `0..weight_total-1` durch denselben Runtime-Selektor `_select` geführt. Die beobachtete Häufigkeit muss exakt dem deklarierten Gewicht entsprechen; Gewicht `0` muss exakt `0` auswählbare Buckets ergeben.",
    ))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Street Boundary/Distribution Report")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = render_markdown(load_manifest(args.manifest))
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(args.output)
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
