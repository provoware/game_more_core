#!/usr/bin/env python3
"""Policy-driven release candidate validation and byte-exact promotion."""

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
DEFAULT_POLICY = ROOT / "manifests" / "RELEASE_POLICY.json"
READY = "RELEASE_READY"
QUARANTINE = "QUARANTINE"
BLOCKED = "RELEASE_BLOCKED"
INVALID = "RELEASE_INVALID"
ALLOWED_SUBGATE_STATES = {"PASS", "FAIL", "FLAKY", "NOT_RUN"}


class ReleaseAutopilotError(RuntimeError):
    """Controlled release-autopilot failure."""


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


def load_policy(path: Path) -> tuple[dict, str]:
    try:
        payload = path.read_bytes()
        policy = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseAutopilotError(f"Release-Policy ist nicht lesbar: {exc}") from exc
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise ReleaseAutopilotError("Release-Policy hat keine unterstützte schema_version=1")
    required_states = {READY, QUARANTINE, BLOCKED, INVALID}
    states = policy.get("release_states")
    if not isinstance(states, list) or set(states) != required_states:
        raise ReleaseAutopilotError("Release-Policy definiert die vier Release-Zustände nicht exakt")
    promotion = policy.get("promotion")
    if not isinstance(promotion, dict):
        raise ReleaseAutopilotError("Release-Policy enthält keinen Promotion-Vertrag")
    if promotion.get("rebuild_after_validation") is not False:
        raise ReleaseAutopilotError("Promotion darf keinen Rebuild nach der Validierung erlauben")
    if promotion.get("copy_validated_candidate_only") is not True:
        raise ReleaseAutopilotError("Promotion muss den validierten Kandidaten bytegenau übernehmen")
    subgates = policy.get("public_promotion_required_subgates")
    if not isinstance(subgates, list) or not subgates or not all(isinstance(item, str) for item in subgates):
        raise ReleaseAutopilotError("Release-Policy enthält keine gültigen Promotion-Subgates")
    return policy, _sha256_bytes(payload)


def load_subgate_evidence(path: Path | None, required: list[str]) -> dict[str, str]:
    result = {gate: "NOT_RUN" for gate in required}
    if path is None:
        return result
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseAutopilotError(f"Subgate-Evidence ist nicht lesbar: {exc}") from exc
    if not isinstance(data, dict):
        raise ReleaseAutopilotError("Subgate-Evidence muss ein JSON-Objekt sein")
    for gate in required:
        state = data.get(gate, "NOT_RUN")
        if state not in ALLOWED_SUBGATE_STATES:
            raise ReleaseAutopilotError(f"Ungültiger Subgate-Status für {gate}: {state!r}")
        result[gate] = state
    return result


def verify_embedded_manifest(zip_path: Path) -> tuple[str, int]:
    with zipfile.ZipFile(zip_path) as archive:
        roots = {name.split("/", 1)[0] for name in archive.namelist() if "/" in name}
        if len(roots) != 1:
            raise ReleaseAutopilotError("Release-ZIP besitzt keinen eindeutigen Paketwurzelordner")
        root = next(iter(roots))
        manifest_name = f"{root}/RELEASE_FILE_MANIFEST.json"
        info_name = f"{root}/RELEASE_INFO.json"
        try:
            manifest_bytes = archive.read(manifest_name)
            release_info = json.loads(archive.read(info_name).decode("utf-8"))
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReleaseAutopilotError(f"Release-Manifest ist ungültig: {exc}") from exc
        expected_manifest_hash = release_info.get("file_manifest_sha256")
        actual_manifest_hash = _sha256_bytes(manifest_bytes)
        if expected_manifest_hash != actual_manifest_hash:
            raise ReleaseAutopilotError("RELEASE_INFO und RELEASE_FILE_MANIFEST widersprechen sich")
        files = manifest.get("files") if isinstance(manifest, dict) else None
        if not isinstance(files, list) or not files:
            raise ReleaseAutopilotError("RELEASE_FILE_MANIFEST enthält keine Dateien")
        for entry in files:
            if not isinstance(entry, dict):
                raise ReleaseAutopilotError("RELEASE_FILE_MANIFEST enthält einen ungültigen Eintrag")
            path = entry.get("path")
            if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts:
                raise ReleaseAutopilotError(f"Ungültiger Release-Pfad im Manifest: {path!r}")
            archive_name = f"{root}/{path}"
            try:
                member = archive.getinfo(archive_name)
                payload = archive.read(archive_name)
            except KeyError as exc:
                raise ReleaseAutopilotError(f"Manifestdatei fehlt im ZIP: {path}") from exc
            if entry.get("size_bytes") != len(payload):
                raise ReleaseAutopilotError(f"Dateigröße stimmt nicht: {path}")
            if entry.get("sha256") != _sha256_bytes(payload):
                raise ReleaseAutopilotError(f"Dateihash stimmt nicht: {path}")
            archive_mode = (member.external_attr >> 16) & 0o777
            if entry.get("mode") != format(archive_mode, "04o"):
                raise ReleaseAutopilotError(f"Dateimodus stimmt nicht: {path}")
        return actual_manifest_hash, len(files)


def clean_room_validate(zip_path: Path, work_root: Path) -> dict[str, object]:
    clean_root = work_root / "clean-room"
    if clean_root.exists():
        shutil.rmtree(clean_root)
    clean_root.mkdir(parents=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(clean_root)
        roots = sorted(path for path in clean_root.iterdir() if path.is_dir())
    if len(roots) != 1:
        raise ReleaseAutopilotError("Clean-Room-Entpackung besitzt keinen eindeutigen Produktordner")
    product_root = roots[0]
    launcher = product_root / "START_BUNKERFREQUENZ.sh"
    if not launcher.is_file():
        raise ReleaseAutopilotError("Clean-Room enthält keinen START_BUNKERFREQUENZ.sh")
    launcher.chmod(launcher.stat().st_mode | 0o111)
    save_dir = work_root / "clean-save"
    state_dir = work_root / "clean-start-state"
    env = os.environ.copy()
    env["BUNKERFREQUENZ_START_STATE_DIR"] = str(state_dir)
    completed = subprocess.run(
        [
            str(launcher),
            "--port",
            "0",
            "--no-browser",
            "--save-dir",
            str(save_dir),
            "--exit-after-ready",
            "--startup-timeout",
            "15",
        ],
        cwd=product_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=45,
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise ReleaseAutopilotError(
            "Clean-Room-Start ist fehlgeschlagen: " + " | ".join(output.splitlines()[-10:])
        )
    if "[100%]" not in output or "BEREIT" not in output:
        raise ReleaseAutopilotError("Clean-Room-Start erreichte keinen bestätigten 100%-BEREIT-Zustand")
    status_path = state_dir / "START_STATUS.txt"
    if not status_path.is_file() or "BEREIT" not in status_path.read_text(encoding="utf-8"):
        raise ReleaseAutopilotError("Clean-Room-Statusbeleg fehlt oder ist unvollständig")
    if (state_dir / "START_DIAGNOSE.txt").exists():
        raise ReleaseAutopilotError("Clean-Room erzeugte trotz Erfolg eine Fehlerdiagnose")
    return {
        "exit_code": completed.returncode,
        "ready_marker": True,
        "status_receipt": True,
        "diagnosis_absent": True,
    }


def evaluate_release_state(subgates: dict[str, str]) -> str:
    values = set(subgates.values())
    if "FAIL" in values:
        return BLOCKED
    if "FLAKY" in values or "NOT_RUN" in values:
        return QUARANTINE
    return READY


def promote_byte_exact(candidate: Path, release_dir: Path) -> Path:
    release_dir.mkdir(parents=True, exist_ok=True)
    promoted = release_dir / candidate.name
    shutil.copyfile(candidate, promoted)
    if promoted.read_bytes() != candidate.read_bytes():
        promoted.unlink(missing_ok=True)
        raise ReleaseAutopilotError("Promotion ist nicht bytegenau")
    digest = _sha256_file(candidate)
    if _sha256_file(promoted) != digest:
        promoted.unlink(missing_ok=True)
        raise ReleaseAutopilotError("Promotion-Hash weicht vom validierten Kandidaten ab")
    (release_dir / f"{candidate.name}.sha256").write_text(
        f"{digest}  {candidate.name}\n", encoding="utf-8"
    )
    return promoted


def write_evidence(output_dir: Path, evidence: dict) -> tuple[Path, Path]:
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "RELEASE_EVIDENCE.json"
    payload = _canonical_json_bytes(evidence)
    evidence_path.write_bytes(payload)
    sha_path = evidence_dir / "RELEASE_EVIDENCE.json.sha256"
    sha_path.write_text(
        f"{_sha256_bytes(payload)}  {evidence_path.name}\n", encoding="utf-8"
    )
    return evidence_path, sha_path


def run_autopilot(
    output_dir: Path,
    policy_path: Path = DEFAULT_POLICY,
    subgate_evidence_path: Path | None = None,
) -> dict:
    policy, policy_sha256 = load_policy(policy_path)
    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    work_root = output_dir / "work"
    if work_root.exists():
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True)

    first_zip, _, first_summary = build(work_root / "build-a")
    second_zip, _, second_summary = build(work_root / "build-b")
    if first_zip.read_bytes() != second_zip.read_bytes() or first_summary != second_summary:
        raise ReleaseAutopilotError("Zwei unabhängige Builds sind nicht byte-reproduzierbar")
    if first_summary.get("source_commit") != source_commit or first_summary.get("source_tree") != source_tree:
        raise ReleaseAutopilotError("Build ist nicht an den eingefrorenen Source-Stand gebunden")

    manifest_sha256, manifest_file_count = verify_embedded_manifest(first_zip)
    clean_room = clean_room_validate(first_zip, work_root)
    candidate_dir = output_dir / "candidate"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    candidate = candidate_dir / first_zip.name
    shutil.copyfile(first_zip, candidate)
    candidate_sha256 = _sha256_file(candidate)

    required_subgates = list(policy["public_promotion_required_subgates"])
    subgates = load_subgate_evidence(subgate_evidence_path, required_subgates)
    release_state = evaluate_release_state(subgates)

    promoted_path: str | None = None
    promotion_hash_match = False
    if release_state == READY:
        promoted = promote_byte_exact(candidate, output_dir / "release")
        promoted_path = str(promoted.relative_to(output_dir))
        promotion_hash_match = _sha256_file(promoted) == candidate_sha256
    else:
        release_dir = output_dir / "release"
        if release_dir.exists():
            shutil.rmtree(release_dir)

    candidate_checks = {
        "source_tree_frozen": True,
        "reproducible_build": True,
        "file_manifest_verified": True,
        "clean_room_start": bool(clean_room["ready_marker"]),
        "clean_room_api_state": bool(clean_room["status_receipt"]),
        "byte_exact_promotion": promotion_hash_match if release_state == READY else "NOT_APPLICABLE",
    }
    evidence = {
        "schema_version": 1,
        "policy_id": policy["policy_id"],
        "policy_sha256": policy_sha256,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_file": str(candidate.relative_to(output_dir)),
        "candidate_sha256": candidate_sha256,
        "candidate_size_bytes": candidate.stat().st_size,
        "file_manifest_sha256": manifest_sha256,
        "file_manifest_file_count": manifest_file_count,
        "candidate_checks": candidate_checks,
        "subgates": subgates,
        "release_state": release_state,
        "promoted_file": promoted_path,
        "manual_technical_acceptance_required": release_state != READY,
        "rebuild_after_validation": False,
    }
    evidence_path, evidence_sha_path = write_evidence(output_dir, evidence)
    evidence["evidence_file"] = str(evidence_path.relative_to(output_dir))
    evidence["evidence_sha256_file"] = str(evidence_sha_path.relative_to(output_dir))
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BUNKERFREQUENZ Release Autopilot PRO – validieren, quarantänisieren oder bytegenau promoten"
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "autopilot-dist")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--subgate-evidence", type=Path)
    parser.add_argument(
        "--allow-quarantine",
        action="store_true",
        help="QUARANTINE als korrekt blockierten CI-Zustand mit Exit 0 akzeptieren",
    )
    args = parser.parse_args(argv)
    output_dir = args.output_dir.resolve()
    try:
        evidence = run_autopilot(
            output_dir,
            args.policy.resolve(),
            args.subgate_evidence.resolve() if args.subgate_evidence else None,
        )
    except ReleaseAutopilotError as exc:
        failure = {
            "schema_version": 1,
            "release_state": INVALID,
            "reason": str(exc),
            "manual_technical_acceptance_required": True,
        }
        write_evidence(output_dir, failure)
        print(f"{INVALID}: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
    state = evidence["release_state"]
    print(f"RELEASE_STATE: {state}")
    if state == READY:
        return 0
    if state == QUARANTINE and args.allow_quarantine:
        return 0
    return 3 if state == QUARANTINE else 1


if __name__ == "__main__":
    raise SystemExit(main())
