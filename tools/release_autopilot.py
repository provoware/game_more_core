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
    state = INVALID


class ReleaseInvalidError(ReleaseAutopilotError):
    state = INVALID


class ReleaseBlockedError(ReleaseAutopilotError):
    state = BLOCKED


def _canonical_json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseInvalidError("Git-Quelle ist für den Release-Nachweis nicht lesbar") from exc
    return completed.stdout.strip()


def source_identity() -> tuple[str, str]:
    return _git("rev-parse", "HEAD"), _git("rev-parse", "HEAD^{tree}")


def ensure_frozen_source() -> tuple[str, str]:
    dirty = _git("status", "--porcelain=v1", "--untracked-files=all")
    if dirty:
        preview = " | ".join(dirty.splitlines()[:8])
        raise ReleaseInvalidError(
            "Arbeitsbaum ist nicht eingefroren; Release-Inhalt wäre nicht eindeutig an HEAD gebunden: " + preview
        )
    return source_identity()


def load_policy(path: Path) -> tuple[dict, str]:
    try:
        payload = path.read_bytes()
        policy = json.loads(payload.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseInvalidError(f"Release-Policy ist nicht lesbar: {exc}") from exc
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise ReleaseInvalidError("Release-Policy hat keine unterstützte schema_version=1")
    states = policy.get("release_states")
    required_states = [READY, QUARANTINE, BLOCKED, INVALID]
    if not isinstance(states, list) or sorted(states) != sorted(required_states) or len(states) != 4:
        raise ReleaseInvalidError("Release-Policy definiert die vier Release-Zustände nicht exakt")
    isolation = policy.get("build_isolation")
    if not isinstance(isolation, dict) or isolation.get("clean_worktree_required") is not True:
        raise ReleaseInvalidError("Release-Policy verlangt keinen sauberen eingefrorenen Arbeitsbaum")
    if isolation.get("independent_build_directories") != 2:
        raise ReleaseInvalidError("Release-Policy muss exakt zwei unabhängige Reproduzierbarkeits-Builds verlangen")
    promotion = policy.get("promotion")
    if not isinstance(promotion, dict):
        raise ReleaseInvalidError("Release-Policy enthält keinen Promotion-Vertrag")
    if promotion.get("rebuild_after_validation") is not False:
        raise ReleaseInvalidError("Promotion darf keinen Rebuild nach der Validierung erlauben")
    if promotion.get("copy_validated_candidate_only") is not True:
        raise ReleaseInvalidError("Promotion muss den validierten Kandidaten bytegenau übernehmen")
    required_subgates = policy.get("public_promotion_required_subgates")
    if (
        not isinstance(required_subgates, list)
        or not required_subgates
        or len(required_subgates) != len(set(required_subgates))
        or not all(isinstance(item, str) and item for item in required_subgates)
    ):
        raise ReleaseInvalidError("Release-Policy enthält keine eindeutigen Promotion-Subgates")
    binding = policy.get("subgate_evidence_binding")
    if not isinstance(binding, dict):
        raise ReleaseInvalidError("Release-Policy enthält keinen Subgate-Bindungsvertrag")
    if not all(
        binding.get(key) is True
        for key in ("source_commit_required", "source_tree_required", "pass_requires_evidence_sha256")
    ):
        raise ReleaseInvalidError("Subgate-PASS muss an Source und Evidence-SHA gebunden sein")
    return policy, _sha256_bytes(payload)


def _empty_subgates(required: list[str]) -> dict[str, dict[str, str | None]]:
    return {gate: {"status": "NOT_RUN", "evidence_sha256": None} for gate in required}


def load_subgate_evidence(
    path: Path | None,
    required: list[str],
    source_commit: str,
    source_tree: str,
) -> dict[str, dict[str, str | None]]:
    if path is None:
        return _empty_subgates(required)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseInvalidError(f"Subgate-Evidence ist nicht lesbar: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ReleaseInvalidError("Subgate-Evidence benötigt schema_version=1")
    if data.get("source_commit") != source_commit or data.get("source_tree") != source_tree:
        raise ReleaseInvalidError("Subgate-Evidence gehört nicht zum aktuellen Source Commit/Tree")
    gates = data.get("gates")
    if not isinstance(gates, dict):
        raise ReleaseInvalidError("Subgate-Evidence enthält kein gates-Objekt")
    result = _empty_subgates(required)
    for gate in required:
        item = gates.get(gate)
        if item is None:
            continue
        if not isinstance(item, dict):
            raise ReleaseInvalidError(f"Subgate-Evidence für {gate} ist kein Objekt")
        status = item.get("status")
        evidence_sha256 = item.get("evidence_sha256")
        if status not in ALLOWED_SUBGATE_STATES:
            raise ReleaseInvalidError(f"Ungültiger Subgate-Status für {gate}: {status!r}")
        if status == "PASS" and not _is_sha256(evidence_sha256):
            raise ReleaseInvalidError(f"PASS für {gate} besitzt keinen gültigen Evidence-SHA-256")
        if evidence_sha256 is not None and not _is_sha256(evidence_sha256):
            raise ReleaseInvalidError(f"Ungültiger Evidence-SHA-256 für {gate}")
        result[gate] = {"status": status, "evidence_sha256": evidence_sha256}
    return result


def verify_embedded_manifest(
    zip_path: Path,
    expected_policy_sha256: str,
    expected_source_commit: str,
    expected_source_tree: str,
) -> tuple[str, int]:
    try:
        archive = zipfile.ZipFile(zip_path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise ReleaseInvalidError(f"Release-ZIP ist nicht lesbar: {exc}") from exc
    with archive:
        names = archive.namelist()
        roots = {name.split("/", 1)[0] for name in names if "/" in name}
        if len(roots) != 1:
            raise ReleaseInvalidError("Release-ZIP besitzt keinen eindeutigen Paketwurzelordner")
        root = next(iter(roots))
        manifest_name = f"{root}/RELEASE_FILE_MANIFEST.json"
        info_name = f"{root}/RELEASE_INFO.json"
        policy_name = f"{root}/manifests/RELEASE_POLICY.json"
        try:
            manifest_bytes = archive.read(manifest_name)
            release_info = json.loads(archive.read(info_name).decode("utf-8"))
            manifest = json.loads(manifest_bytes.decode("utf-8"))
            embedded_policy = archive.read(policy_name)
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ReleaseInvalidError(f"Release-Manifest/Policy ist ungültig: {exc}") from exc
        if release_info.get("source_commit") != expected_source_commit:
            raise ReleaseInvalidError("RELEASE_INFO ist nicht an den eingefrorenen Source Commit gebunden")
        if release_info.get("source_tree") != expected_source_tree:
            raise ReleaseInvalidError("RELEASE_INFO ist nicht an den eingefrorenen Source Tree gebunden")
        if _sha256_bytes(embedded_policy) != expected_policy_sha256:
            raise ReleaseInvalidError("Im Kandidaten steckt nicht exakt die validierte Release-Policy")
        actual_manifest_hash = _sha256_bytes(manifest_bytes)
        if release_info.get("file_manifest_sha256") != actual_manifest_hash:
            raise ReleaseInvalidError("RELEASE_INFO und RELEASE_FILE_MANIFEST widersprechen sich")
        files = manifest.get("files") if isinstance(manifest, dict) else None
        if not isinstance(files, list) or not files:
            raise ReleaseInvalidError("RELEASE_FILE_MANIFEST enthält keine Dateien")
        seen: set[str] = set()
        for entry in files:
            if not isinstance(entry, dict):
                raise ReleaseInvalidError("RELEASE_FILE_MANIFEST enthält einen ungültigen Eintrag")
            path = entry.get("path")
            if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts:
                raise ReleaseInvalidError(f"Ungültiger Release-Pfad im Manifest: {path!r}")
            if path in seen:
                raise ReleaseInvalidError(f"Doppelter Release-Pfad im Manifest: {path}")
            seen.add(path)
            archive_name = f"{root}/{path}"
            try:
                member = archive.getinfo(archive_name)
                payload = archive.read(archive_name)
            except KeyError as exc:
                raise ReleaseInvalidError(f"Manifestdatei fehlt im ZIP: {path}") from exc
            if entry.get("size_bytes") != len(payload):
                raise ReleaseInvalidError(f"Dateigröße stimmt nicht: {path}")
            if entry.get("sha256") != _sha256_bytes(payload):
                raise ReleaseInvalidError(f"Dateihash stimmt nicht: {path}")
            archive_mode = (member.external_attr >> 16) & 0o777
            if entry.get("mode") != format(archive_mode, "04o"):
                raise ReleaseInvalidError(f"Dateimodus stimmt nicht: {path}")
        required_paths = {
            "START_BUNKERFREQUENZ.sh",
            "BUNKERFREQUENZ.desktop",
            "manifests/RELEASE_POLICY.json",
            "tools/build_release.py",
            "tools/release_autopilot.py",
        }
        missing = sorted(required_paths - seen)
        if missing:
            raise ReleaseInvalidError("Pflichtdateien fehlen im Release-Manifest: " + ", ".join(missing))
        return actual_manifest_hash, len(files)


def _extract_preserving_modes(zip_path: Path, destination: Path) -> Path:
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = destination / member.filename
            resolved = target.resolve()
            if destination.resolve() not in resolved.parents and resolved != destination.resolve():
                raise ReleaseInvalidError(f"Unsicherer ZIP-Pfad: {member.filename}")
            archive.extract(member, destination)
            if not member.is_dir():
                mode = (member.external_attr >> 16) & 0o777
                target.chmod(mode or 0o644)
    roots = sorted(path for path in destination.iterdir() if path.is_dir())
    if len(roots) != 1:
        raise ReleaseInvalidError("Clean-Room-Entpackung besitzt keinen eindeutigen Produktordner")
    return roots[0]


def clean_room_validate(zip_path: Path, work_root: Path) -> dict[str, object]:
    clean_root = work_root / "clean-room"
    clean_root.mkdir(parents=True, exist_ok=True)
    product_root = _extract_preserving_modes(zip_path, clean_root)
    launcher = product_root / "START_BUNKERFREQUENZ.sh"
    if not launcher.is_file() or not os.access(launcher, os.X_OK):
        raise ReleaseBlockedError("Clean-Room-Launcher fehlt oder ist nicht ausführbar")
    save_dir = work_root / "clean-save"
    state_dir = work_root / "clean-start-state"
    clean_home = work_root / "clean-home"
    clean_home.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = str(clean_home)
    env["PYTHONPATH"] = ""
    env["BUNKERFREQUENZ_START_STATE_DIR"] = str(state_dir)
    try:
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
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReleaseBlockedError(f"Clean-Room-Start konnte nicht sicher abgeschlossen werden: {exc}") from exc
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise ReleaseBlockedError(
            "Clean-Room-Start ist fehlgeschlagen: " + " | ".join(output.splitlines()[-10:])
        )
    if "[100%]" not in output or "BEREIT" not in output:
        raise ReleaseBlockedError("Clean-Room-Start erreichte keinen bestätigten 100%-BEREIT-Zustand")
    status_path = state_dir / "START_STATUS.txt"
    if not status_path.is_file() or "BEREIT" not in status_path.read_text(encoding="utf-8"):
        raise ReleaseBlockedError("Clean-Room-Statusbeleg fehlt oder ist unvollständig")
    if (state_dir / "START_DIAGNOSE.txt").exists():
        raise ReleaseBlockedError("Clean-Room erzeugte trotz Erfolg eine Fehlerdiagnose")
    return {
        "exit_code": completed.returncode,
        "ready_marker": True,
        "status_receipt": True,
        "diagnosis_absent": True,
        "source_pythonpath_cleared": True,
        "isolated_home": True,
    }


def evaluate_release_state(subgates: dict[str, dict[str, str | None]]) -> str:
    statuses = {item["status"] for item in subgates.values()}
    if "FAIL" in statuses:
        return BLOCKED
    if "FLAKY" in statuses or "NOT_RUN" in statuses:
        return QUARANTINE
    return READY


def promote_byte_exact(candidate: Path, release_dir: Path) -> Path:
    release_dir.mkdir(parents=True, exist_ok=True)
    promoted = release_dir / candidate.name
    shutil.copyfile(candidate, promoted)
    candidate_hash = _sha256_file(candidate)
    if _sha256_file(promoted) != candidate_hash or promoted.read_bytes() != candidate.read_bytes():
        promoted.unlink(missing_ok=True)
        raise ReleaseInvalidError("Promotion ist nicht bytegenau zum validierten Kandidaten")
    (release_dir / f"{candidate.name}.sha256").write_text(
        f"{candidate_hash}  {candidate.name}\n", encoding="utf-8"
    )
    return promoted


def write_evidence(output_dir: Path, evidence: dict) -> tuple[Path, Path, str]:
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "RELEASE_EVIDENCE.json"
    payload = _canonical_json_bytes(evidence)
    digest = _sha256_bytes(payload)
    evidence_path.write_bytes(payload)
    sha_path = evidence_dir / "RELEASE_EVIDENCE.json.sha256"
    sha_path.write_text(f"{digest}  {evidence_path.name}\n", encoding="utf-8")
    return evidence_path, sha_path, digest


def _failure_evidence(state: str, reason: str, policy_path: Path) -> dict:
    try:
        source_commit, source_tree = source_identity()
    except ReleaseAutopilotError:
        source_commit, source_tree = None, None
    try:
        policy_sha256 = _sha256_file(policy_path)
    except OSError:
        policy_sha256 = None
    return {
        "schema_version": 1,
        "policy_sha256": policy_sha256,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": None,
        "candidate_size_bytes": None,
        "file_manifest_sha256": None,
        "candidate_checks": {"completed": False},
        "subgates": {},
        "release_state": state,
        "reason": reason,
        "user_zip_available": False,
        "manual_user_technical_validation_required": False,
        "release_operator_action_required": True,
    }


def run_autopilot(
    output_dir: Path,
    policy_path: Path = DEFAULT_POLICY,
    subgate_evidence_path: Path | None = None,
) -> dict:
    policy, policy_sha256 = load_policy(policy_path)
    source_commit, source_tree = ensure_frozen_source()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="bunkerfrequenz-release-autopilot-") as temp:
        work_root = Path(temp)
        first_zip, _, first_summary = build(work_root / "build-a")
        second_zip, _, second_summary = build(work_root / "build-b")
        if first_zip.read_bytes() != second_zip.read_bytes() or first_summary != second_summary:
            raise ReleaseBlockedError("Zwei unabhängige Builds sind nicht byte-reproduzierbar")
        if first_summary.get("source_commit") != source_commit or first_summary.get("source_tree") != source_tree:
            raise ReleaseInvalidError("Build ist nicht an den eingefrorenen Source-Stand gebunden")
        manifest_sha256, manifest_file_count = verify_embedded_manifest(
            first_zip,
            policy_sha256,
            source_commit,
            source_tree,
        )
        clean_room = clean_room_validate(first_zip, work_root)
        candidate_dir = output_dir / "candidate"
        if candidate_dir.exists():
            shutil.rmtree(candidate_dir)
        candidate_dir.mkdir(parents=True)
        candidate = candidate_dir / first_zip.name
        shutil.copyfile(first_zip, candidate)

    candidate_sha256 = _sha256_file(candidate)
    required_subgates = list(policy["public_promotion_required_subgates"])
    subgates = load_subgate_evidence(
        subgate_evidence_path,
        required_subgates,
        source_commit,
        source_tree,
    )
    release_state = evaluate_release_state(subgates)

    release_dir = output_dir / "release"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    promoted_path: str | None = None
    promoted_sha256: str | None = None
    if release_state == READY:
        promoted = promote_byte_exact(candidate, release_dir)
        promoted_path = str(promoted.relative_to(output_dir))
        promoted_sha256 = _sha256_file(promoted)

    candidate_checks = {
        "source_tree_frozen": True,
        "reproducible_build": True,
        "file_manifest_verified": True,
        "embedded_policy_verified": True,
        "clean_room_start": bool(clean_room["ready_marker"]),
        "clean_room_api_state": bool(clean_room["status_receipt"]),
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
        "promoted_sha256": promoted_sha256,
        "rebuild_after_validation": False,
        "user_zip_available": release_state == READY,
        "manual_user_technical_validation_required": False,
        "release_operator_action_required": release_state != READY,
        "evidence_file": "evidence/RELEASE_EVIDENCE.json",
        "evidence_sha256_file": "evidence/RELEASE_EVIDENCE.json.sha256",
    }
    required_fields = policy["evidence"]["required_fields"]
    missing_fields = [field for field in required_fields if field not in evidence]
    if missing_fields:
        raise ReleaseInvalidError("Evidence Root verfehlt Policy-Felder: " + ", ".join(missing_fields))
    _, _, evidence_sha256 = write_evidence(output_dir, evidence)
    return {**evidence, "evidence_root_sha256": evidence_sha256}


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
    policy_path = args.policy.resolve()
    try:
        evidence = run_autopilot(
            output_dir,
            policy_path,
            args.subgate_evidence.resolve() if args.subgate_evidence else None,
        )
    except ReleaseAutopilotError as exc:
        failure = _failure_evidence(exc.state, str(exc), policy_path)
        write_evidence(output_dir, failure)
        print(f"{exc.state}: {exc}", file=sys.stderr)
        return 2 if exc.state == INVALID else 1

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
