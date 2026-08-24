#!/usr/bin/env python3
"""Source-bound desktop/browser E2E evidence for BUNKERFREQUENZ releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

from build_release import build

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_NAME = "DESKTOP_BROWSER_E2E_EVIDENCE.json"
SUBGATE_NAME = "SUBGATE_EVIDENCE.json"
REQUIRED_SCENARIOS = (
    "desktop_launcher_contract",
    "clickstart_orchestrator",
    "chromium_dom_ready",
)


def _canonical_json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def source_identity() -> tuple[str, str]:
    dirty_tracked = _git("status", "--porcelain", "--untracked-files=no")
    if dirty_tracked:
        raise RuntimeError("Desktop-Browser-Evidence darf keine geänderten versionierten Quelldateien verwenden")
    return _git("rev-parse", "HEAD"), _git("rev-parse", "HEAD^{tree}")


def _extract(zip_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    root_resolved = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = destination / member.filename
            resolved = target.resolve()
            if resolved != root_resolved and root_resolved not in resolved.parents:
                raise RuntimeError(f"Unsicherer ZIP-Pfad: {member.filename}")
            archive.extract(member, destination)
            if not member.is_dir():
                mode = (member.external_attr >> 16) & 0o777
                target.chmod(mode or 0o644)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("Entpacktes Release besitzt keinen eindeutigen Produktordner")
    return roots[0]


def _load_prior_subgate(path: Path, source_commit: str, source_tree: str, candidate_sha256: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failure-Containment-Subgate ist nicht lesbar: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise RuntimeError("Failure-Containment-Subgate benötigt schema_version=1")
    if data.get("source_commit") != source_commit or data.get("source_tree") != source_tree:
        raise RuntimeError("Failure-Containment-Subgate gehört nicht zur aktuellen Source")
    if data.get("candidate_sha256") != candidate_sha256:
        raise RuntimeError("Failure-Containment-Subgate gehört nicht zu denselben Release-Bytes")
    gates = data.get("gates")
    if not isinstance(gates, dict):
        raise RuntimeError("Failure-Containment-Subgate besitzt kein gates-Objekt")
    failure = gates.get("failure_containment_pro")
    if not isinstance(failure, dict) or failure.get("status") != "PASS":
        raise RuntimeError("failure_containment_pro muss vor Desktop-Browser-E2E PASS sein")
    evidence_sha = failure.get("evidence_sha256")
    if not isinstance(evidence_sha, str) or len(evidence_sha) != 64:
        raise RuntimeError("failure_containment_pro besitzt keinen gültigen Evidence-SHA-256")
    return data


def _scenario_desktop_launcher_contract(product_root: Path) -> dict[str, object]:
    launcher = product_root / "START_BUNKERFREQUENZ.sh"
    desktop = product_root / "BUNKERFREQUENZ.desktop"
    orchestrator = product_root / "tools" / "start_orchestrator.py"
    for path in (launcher, desktop, orchestrator):
        if not path.is_file():
            raise RuntimeError(f"Pflichtdatei fehlt: {path.name}")
    if not os.access(launcher, os.X_OK):
        raise RuntimeError("START_BUNKERFREQUENZ.sh ist im Release nicht ausführbar")
    if not os.access(desktop, os.X_OK):
        raise RuntimeError("BUNKERFREQUENZ.desktop ist im Release nicht ausführbar")
    desktop_text = desktop.read_text(encoding="utf-8")
    exec_lines = [line for line in desktop_text.splitlines() if line.startswith("Exec=")]
    if len(exec_lines) != 1 or "START_BUNKERFREQUENZ.sh" not in exec_lines[0]:
        raise RuntimeError("Desktop-Datei verweist nicht eindeutig auf START_BUNKERFREQUENZ.sh")
    launcher_text = launcher.read_text(encoding="utf-8")
    if "tools/start_orchestrator.py" not in launcher_text:
        raise RuntimeError("Startskript delegiert nicht an den kanonischen Orchestrator")
    return {"launcher_executable": True, "desktop_executable": True, "single_orchestrator_path": True}


def _scenario_clickstart(product_root: Path, root: Path) -> dict[str, object]:
    save_dir = root / "save"
    state_dir = root / "state"
    env = os.environ.copy()
    env.update(
        {
            "BUNKERFREQUENZ_START_STATE_DIR": str(state_dir),
            "PYTHONPATH": "",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    completed = subprocess.run(
        [
            str(product_root / "START_BUNKERFREQUENZ.sh"),
            "--no-browser",
            "--exit-after-ready",
            "--port",
            "0",
            "--save-dir",
            str(save_dir),
        ],
        cwd=product_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=35,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError("Klickstart scheiterte: " + " | ".join(output.splitlines()[-12:]))
    status_path = state_dir / "START_STATUS.txt"
    if not status_path.is_file():
        raise RuntimeError("Klickstart erzeugte keinen START_STATUS-Nachweis")
    status = status_path.read_text(encoding="utf-8")
    if "[100%]" not in status or "BEREIT" not in status:
        raise RuntimeError("Klickstart erreichte keinen vollständigen BEREIT-Zustand")
    return {"exit_code": 0, "ready_100_percent": True, "server_shutdown_after_acceptance": True}


def _scenario_chromium_dom(product_root: Path) -> dict[str, object]:
    env = os.environ.copy()
    env.update({"PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"})
    completed = subprocess.run(
        [sys.executable, str(product_root / "tools" / "start_a4_acceptance.py"), "--require-browser"],
        cwd=product_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=40,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError("Browser-Acceptance scheiterte: " + " | ".join(output.splitlines()[-12:]))
    if "BROWSER OK" not in output or "UI reaktionsfähig" not in output:
        raise RuntimeError("Browser-Acceptance lieferte keinen bestätigten DOM/BEREIT-Nachweis")
    return {"real_browser_required": True, "dom_ready": True, "ui_responsive": True}


def _single_run(candidate: Path, root: Path) -> dict[str, dict[str, object]]:
    product_root = _extract(candidate, root / "product")
    calls = (
        ("desktop_launcher_contract", lambda: _scenario_desktop_launcher_contract(product_root)),
        ("clickstart_orchestrator", lambda: _scenario_clickstart(product_root, root / "clickstart")),
        ("chromium_dom_ready", lambda: _scenario_chromium_dom(product_root)),
    )
    scenarios: dict[str, dict[str, object]] = {}
    for name, call in calls:
        try:
            detail = call()
        except Exception as exc:
            scenarios[name] = {"status": "FAIL", "reason": str(exc)}
        else:
            scenarios[name] = {"status": "PASS", "detail": detail}
    return scenarios


def _statuses(run: dict[str, dict[str, object]]) -> dict[str, str]:
    return {name: str(run[name]["status"]) for name in REQUIRED_SCENARIOS}


def evaluate_runs(first: dict[str, dict[str, object]], second: dict[str, dict[str, object]]) -> str:
    first_status = _statuses(first)
    second_status = _statuses(second)
    if first_status != second_status:
        return "FLAKY"
    return "PASS" if all(value == "PASS" for value in first_status.values()) else "FAIL"


def run(output_dir: Path, prior_subgate: Path) -> dict[str, object]:
    source_commit, source_tree = source_identity()
    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-desktop-browser-e2e-") as temp:
        temp_root = Path(temp)
        candidate, _, summary = build(temp_root / "candidate")
        candidate_sha = _sha256_file(candidate)
        prior = _load_prior_subgate(prior_subgate, source_commit, source_tree, candidate_sha)
        first = _single_run(candidate, temp_root / "run-a")
        second = _single_run(candidate, temp_root / "run-b")
    status = evaluate_runs(first, second)
    evidence = {
        "schema_version": 1,
        "gate": "desktop_browser_e2e_pro",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_sha,
        "candidate_size_bytes": summary["size_bytes"],
        "anti_flake_runs": 2,
        "anti_flake_consistent": _statuses(first) == _statuses(second),
        "status": status,
        "coverage": ["packaged_desktop_contract", "real_clickstart_orchestrator", "real_chromium_dom_ready", "post_start_shutdown", "anti_flake_quarantine"],
        "runs": [first, second],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = output_dir / EVIDENCE_NAME
    payload = _canonical_json_bytes(evidence)
    evidence_sha = _sha256_bytes(payload)
    evidence_path.write_bytes(payload)
    (output_dir / f"{EVIDENCE_NAME}.sha256").write_text(f"{evidence_sha}  {EVIDENCE_NAME}\n", encoding="utf-8")
    gates = dict(prior["gates"])
    gates["desktop_browser_e2e_pro"] = {"status": status, "evidence_sha256": evidence_sha}
    combined = {
        "schema_version": 1,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_sha,
        "gates": gates,
    }
    (output_dir / SUBGATE_NAME).write_bytes(_canonical_json_bytes(combined))
    return {**evidence, "evidence_sha256": evidence_sha, "subgate_file": SUBGATE_NAME}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Desktop Browser E2E PRO")
    parser.add_argument("--prior-subgate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "desktop-browser-e2e-dist")
    args = parser.parse_args(argv)
    try:
        evidence = run(args.output_dir.resolve(), args.prior_subgate.resolve())
    except Exception as exc:
        print(f"DESKTOP_BROWSER_E2E_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    print(f"DESKTOP_BROWSER_E2E_STATUS: {evidence['status']}")
    if evidence["status"] == "PASS":
        return 0
    return 3 if evidence["status"] == "FLAKY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
