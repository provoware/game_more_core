#!/usr/bin/env python3
"""Deterministic failure-containment evidence for BUNKERFREQUENZ releases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import zipfile

from build_release import build

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_NAME = "FAILURE_CONTAINMENT_EVIDENCE.json"
SUBGATE_NAME = "SUBGATE_EVIDENCE.json"
REQUIRED_SCENARIOS = (
    "path_locale_matrix",
    "process_ownership",
    "resource_stress",
    "port_collision",
    "fault_contract_regressions",
    "crash_save_upgrade_recovery",
)


def _canonical_json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def source_identity() -> tuple[str, str]:
    return _git("rev-parse", "HEAD"), _git("rev-parse", "HEAD^{tree}")


def _extract(zip_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = destination / member.filename
            resolved = target.resolve()
            if destination.resolve() not in resolved.parents and resolved != destination.resolve():
                raise RuntimeError(f"Unsicherer ZIP-Pfad: {member.filename}")
            archive.extract(member, destination)
            if not member.is_dir():
                mode = (member.external_attr >> 16) & 0o777
                target.chmod(mode or 0o644)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("Entpacktes Release besitzt keinen eindeutigen Produktordner")
    return roots[0]


def _limited_resources() -> None:
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    soft_as = 512 * 1024 * 1024
    hard_as = resource.getrlimit(resource.RLIMIT_AS)[1]
    if hard_as == resource.RLIM_INFINITY or hard_as > soft_as:
        resource.setrlimit(resource.RLIMIT_AS, (soft_as, soft_as))


def _run_launcher(
    product_root: Path,
    work_root: Path,
    *,
    port: int = 0,
    env_overrides: dict[str, str] | None = None,
    constrained: bool = False,
    timeout: float = 35.0,
) -> dict[str, object]:
    save_dir = work_root / "save"
    state_dir = work_root / "state"
    home_dir = work_root / "home"
    home_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home_dir),
            "PYTHONPATH": "",
            "BUNKERFREQUENZ_START_STATE_DIR": str(state_dir),
        }
    )
    if env_overrides:
        env.update(env_overrides)
    launcher = product_root / "START_BUNKERFREQUENZ.sh"
    completed = subprocess.run(
        [
            str(launcher),
            "--port",
            str(port),
            "--no-browser",
            "--save-dir",
            str(save_dir),
            "--exit-after-ready",
            "--startup-timeout",
            "12",
        ],
        cwd=product_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        preexec_fn=_limited_resources if constrained else None,
    )
    output = completed.stdout + completed.stderr
    status_path = state_dir / "START_STATUS.txt"
    status = status_path.read_text(encoding="utf-8") if status_path.is_file() else ""
    return {
        "exit_code": completed.returncode,
        "ready": completed.returncode == 0 and "[100%]" in output and "BEREIT" in output,
        "status_ready": "BEREIT" in status,
        "status_text": status,
        "output_tail": output.splitlines()[-12:],
        "save_dir": str(save_dir),
    }


def _scenario_path_locale(product_root: Path, root: Path) -> dict[str, object]:
    matrix = (
        ("C.UTF-8", "UTC", "Pfad mit Leerzeichen ÄÖÜ"),
        ("C", "Europe/Berlin", "sehr-langer-pfad-" + "x" * 80),
    )
    cases: list[dict[str, object]] = []
    for index, (lang, timezone, folder_name) in enumerate(matrix):
        case_root = root / f"case-{index}" / folder_name
        product_copy = case_root / product_root.name
        product_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(product_root, product_copy)
        result = _run_launcher(
            product_copy,
            case_root / "runtime",
            env_overrides={"LANG": lang, "LC_ALL": lang, "TZ": timezone, "PYTHONUTF8": "1"},
        )
        cases.append({"lang": lang, "tz": timezone, "path": folder_name, "pass": bool(result["ready"])})
        if not result["ready"]:
            raise RuntimeError(f"Pfad-/Locale-Fall fehlgeschlagen: {lang}/{timezone}/{folder_name}: {result['output_tail']}")
    return {"cases": cases}


def _scenario_process_ownership(product_root: Path, root: Path) -> dict[str, object]:
    sentinel = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        runtime_root = root / "owned-runtime"
        result = _run_launcher(product_root, runtime_root)
        if not result["ready"]:
            raise RuntimeError("Start für Process-Ownership-Test wurde nicht bereit")
        if sentinel.poll() is not None:
            raise RuntimeError("Fremder Sentinel-Prozess wurde vom Launcher beendet")
        marker = str(runtime_root / "save")
        time.sleep(0.15)
        ps = subprocess.run(["ps", "-eo", "pid=,args="], check=True, capture_output=True, text=True).stdout
        lingering = [line.strip() for line in ps.splitlines() if marker in line and str(os.getpid()) not in line]
        if lingering:
            raise RuntimeError("Eigener Serverprozess blieb nach Exit übrig: " + " | ".join(lingering[:3]))
        return {"foreign_process_survived": True, "owned_processes_remaining": 0}
    finally:
        if sentinel.poll() is None:
            sentinel.terminate()
            try:
                sentinel.wait(timeout=2)
            except subprocess.TimeoutExpired:
                sentinel.kill()
                sentinel.wait(timeout=2)


def _scenario_resource_stress(product_root: Path, root: Path) -> dict[str, object]:
    result = _run_launcher(product_root, root / "resource-runtime", constrained=True, timeout=40)
    if not result["ready"]:
        raise RuntimeError("Start unter begrenzten Ressourcen fehlgeschlagen: " + " | ".join(result["output_tail"]))
    return {"rlimit_nofile": 64, "rlimit_as_mib": 512, "ready": True}


def _scenario_port_collision(product_root: Path, root: Path) -> dict[str, object]:
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen(1)
    occupied_port = int(holder.getsockname()[1])
    try:
        result = _run_launcher(product_root, root / "port-runtime", port=occupied_port)
    finally:
        holder.close()
    if not result["ready"]:
        raise RuntimeError("Start mit belegtem Port wurde nicht recovered: " + " | ".join(result["output_tail"]))
    if f"Port {occupied_port} war belegt" not in str(result["status_text"]):
        raise RuntimeError("Belegter Port wurde nicht transparent als Auto-Auflösung protokolliert")
    return {"occupied_port": occupied_port, "auto_resolved": True}


def _run_unittest(targets: list[str], timeout: float = 90.0) -> dict[str, object]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src:."
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", *targets, "-v"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError("Regression fehlgeschlagen: " + " | ".join(output.splitlines()[-20:]))
    return {"targets": targets, "exit_code": 0}


def _scenario_fault_contracts() -> dict[str, object]:
    return _run_unittest(["tests.release.test_failure_containment_pro.FailureContainmentContractTests"])


def _scenario_crash_save_upgrade() -> dict[str, object]:
    return _run_unittest(
        [
            "tests.runtime.test_recovery",
            "tests.runtime.test_resource_recovery",
            "tests.release.test_failure_containment_pro.LegacyUpgradeRecoveryTests",
        ],
        timeout=120,
    )


def _single_run(candidate: Path, root: Path) -> dict[str, dict[str, object]]:
    product_root = _extract(candidate, root / "product")
    scenarios: dict[str, dict[str, object]] = {}
    scenario_calls = (
        ("path_locale_matrix", lambda: _scenario_path_locale(product_root, root / "paths")),
        ("process_ownership", lambda: _scenario_process_ownership(product_root, root / "process")),
        ("resource_stress", lambda: _scenario_resource_stress(product_root, root / "resources")),
        ("port_collision", lambda: _scenario_port_collision(product_root, root / "port")),
        ("fault_contract_regressions", _scenario_fault_contracts),
        ("crash_save_upgrade_recovery", _scenario_crash_save_upgrade),
    )
    for name, call in scenario_calls:
        try:
            detail = call()
        except Exception as exc:  # fail-closed evidence, not a hidden retry
            scenarios[name] = {"status": "FAIL", "reason": str(exc)}
        else:
            scenarios[name] = {"status": "PASS", "detail": detail}
    return scenarios


def _normalized_statuses(run: dict[str, dict[str, object]]) -> dict[str, str]:
    return {name: str(run[name]["status"]) for name in REQUIRED_SCENARIOS}


def evaluate_runs(first: dict[str, dict[str, object]], second: dict[str, dict[str, object]]) -> str:
    first_status = _normalized_statuses(first)
    second_status = _normalized_statuses(second)
    if first_status != second_status:
        return "FLAKY"
    return "PASS" if all(value == "PASS" for value in first_status.values()) else "FAIL"


def write_evidence(output_dir: Path, evidence: dict[str, object]) -> tuple[Path, Path, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / EVIDENCE_NAME
    payload = _canonical_json_bytes(evidence)
    digest = _sha256_bytes(payload)
    path.write_bytes(payload)
    sha_path = output_dir / f"{EVIDENCE_NAME}.sha256"
    sha_path.write_text(f"{digest}  {EVIDENCE_NAME}\n", encoding="utf-8")
    return path, sha_path, digest


def run(output_dir: Path) -> dict[str, object]:
    source_commit, source_tree = source_identity()
    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-failure-containment-") as temp:
        temp_root = Path(temp)
        candidate, _, summary = build(temp_root / "candidate")
        candidate_hash = _sha256_file(candidate)
        first = _single_run(candidate, temp_root / "run-a")
        second = _single_run(candidate, temp_root / "run-b")
    status = evaluate_runs(first, second)
    evidence: dict[str, object] = {
        "schema_version": 1,
        "gate": "failure_containment_pro",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_hash,
        "candidate_size_bytes": summary["size_bytes"],
        "anti_flake_runs": 2,
        "anti_flake_consistent": _normalized_statuses(first) == _normalized_statuses(second),
        "status": status,
        "coverage": [
            "resource_stress",
            "path_locale_matrix",
            "process_ownership",
            "port_race_and_collision",
            "disk_and_permission_fail_closed",
            "crash_save_recovery",
            "legacy_upgrade_recovery",
            "anti_flake_quarantine",
        ],
        "runs": [first, second],
    }
    _, _, evidence_hash = write_evidence(output_dir, evidence)
    subgate = {
        "schema_version": 1,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_hash,
        "gates": {
            "desktop_browser_e2e_pro": {"status": "NOT_RUN", "evidence_sha256": None},
            "failure_containment_pro": {"status": status, "evidence_sha256": evidence_hash},
        },
    }
    (output_dir / SUBGATE_NAME).write_bytes(_canonical_json_bytes(subgate))
    return {**evidence, "evidence_sha256": evidence_hash, "subgate_file": SUBGATE_NAME}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Failure Containment PRO")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "failure-containment-dist")
    args = parser.parse_args(argv)
    try:
        evidence = run(args.output_dir.resolve())
    except Exception as exc:
        print(f"FAILURE_CONTAINMENT_INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    print(f"FAILURE_CONTAINMENT_STATUS: {evidence['status']}")
    if evidence["status"] == "PASS":
        return 0
    return 3 if evidence["status"] == "FLAKY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
