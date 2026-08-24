#!/usr/bin/env python3
"""Verify and emit an explicit SHA-256 chain from release subgates to promoted ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

CHAIN_NAME = "RELEASE_EVIDENCE_CHAIN.json"


def _canonical_json_bytes(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{label} ist nicht lesbar: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} ist kein JSON-Objekt")
    return value


def _declared_sidecar_hash(path: Path) -> str:
    sidecar = Path(str(path) + ".sha256")
    try:
        fields = sidecar.read_text(encoding="utf-8").strip().split()
    except OSError as exc:
        raise RuntimeError(f"SHA-256-Sidecar fehlt für {path.name}: {exc}") from exc
    if len(fields) < 2 or not _is_sha256(fields[0]) or fields[-1] != path.name:
        raise RuntimeError(f"SHA-256-Sidecar ist ungültig für {path.name}")
    actual = _sha256_file(path)
    if actual != fields[0]:
        raise RuntimeError(f"SHA-256-Sidecar widerspricht den Bytes von {path.name}")
    return actual


def _same_source(*items: dict) -> tuple[str, str]:
    commits = {item.get("source_commit") for item in items}
    trees = {item.get("source_tree") for item in items}
    if len(commits) != 1 or len(trees) != 1:
        raise RuntimeError("Evidence-Stufen gehören nicht zum selben Source Commit/Tree")
    commit = next(iter(commits))
    tree = next(iter(trees))
    if not isinstance(commit, str) or not commit or not isinstance(tree, str) or not tree:
        raise RuntimeError("Source Commit/Tree fehlt in der Evidence-Kette")
    return commit, tree


def _candidate_hash(*items: dict) -> str:
    values = {item.get("candidate_sha256") for item in items}
    if len(values) != 1:
        raise RuntimeError("Evidence-Stufen beziehen sich nicht auf denselben Candidate-SHA-256")
    candidate = next(iter(values))
    if not _is_sha256(candidate):
        raise RuntimeError("Candidate-SHA-256 fehlt oder ist ungültig")
    return candidate


def build_chain(
    failure_path: Path,
    browser_path: Path,
    release_path: Path,
    promoted_zip: Path,
    output_dir: Path,
) -> dict[str, object]:
    failure = _load_json(failure_path, "Failure-Containment-Evidence")
    browser = _load_json(browser_path, "Multi-Browser-Evidence")
    release = _load_json(release_path, "Release-Evidence")

    failure_sha = _declared_sidecar_hash(failure_path)
    browser_sha = _declared_sidecar_hash(browser_path)
    release_sha = _declared_sidecar_hash(release_path)
    promoted_sha = _declared_sidecar_hash(promoted_zip)

    if failure.get("status") != "PASS" or browser.get("status") != "PASS":
        raise RuntimeError("Failure-Containment und Multi-Browser müssen PASS sein")
    if release.get("release_state") != "RELEASE_READY" or release.get("user_zip_available") is not True:
        raise RuntimeError("Release-Evidence ist nicht RELEASE_READY")

    source_commit, source_tree = _same_source(failure, browser, release)
    candidate_sha = _candidate_hash(failure, browser, release)

    if promoted_sha != candidate_sha:
        raise RuntimeError("Promoviertes Benutzer-ZIP ist nicht bytegleich zum validierten Candidate")
    if release.get("promoted_sha256") != promoted_sha:
        raise RuntimeError("Release-Evidence bindet nicht exakt das tatsächlich promovierte ZIP")

    subgates = release.get("subgates")
    if not isinstance(subgates, dict):
        raise RuntimeError("Release-Evidence enthält kein subgates-Objekt")
    failure_gate = subgates.get("failure_containment_pro")
    browser_gate = subgates.get("desktop_browser_e2e_pro")
    if not isinstance(failure_gate, dict) or failure_gate.get("status") != "PASS" or failure_gate.get("evidence_sha256") != failure_sha:
        raise RuntimeError("Release-Evidence bindet den Failure-Containment-Hash nicht exakt")
    if not isinstance(browser_gate, dict) or browser_gate.get("status") != "PASS" or browser_gate.get("evidence_sha256") != browser_sha:
        raise RuntimeError("Release-Evidence bindet den Multi-Browser-Hash nicht exakt")

    links = [
        {
            "stage": "failure_containment_pro",
            "file": failure_path.name,
            "sha256": failure_sha,
            "previous_sha256": None,
            "candidate_sha256": candidate_sha,
        },
        {
            "stage": "multi_browser_e2e_pro",
            "file": browser_path.name,
            "sha256": browser_sha,
            "previous_sha256": failure_sha,
            "candidate_sha256": candidate_sha,
        },
        {
            "stage": "release_evidence",
            "file": release_path.name,
            "sha256": release_sha,
            "previous_sha256": browser_sha,
            "candidate_sha256": candidate_sha,
        },
        {
            "stage": "promoted_user_zip",
            "file": promoted_zip.name,
            "sha256": promoted_sha,
            "previous_sha256": release_sha,
            "candidate_sha256": candidate_sha,
            "byte_exact_candidate": True,
        },
    ]
    terminal_descriptor = {
        "previous_sha256": release_sha,
        "promoted_zip_sha256": promoted_sha,
        "candidate_sha256": candidate_sha,
    }
    chain = {
        "schema_version": 1,
        "chain_id": "bunkerfrequenz.release-evidence-chain-pro.v1",
        "status": "PASS",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "candidate_sha256": candidate_sha,
        "links": links,
        "terminal_descriptor_sha256": _sha256_bytes(_canonical_json_bytes(terminal_descriptor)),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    chain_path = output_dir / CHAIN_NAME
    payload = _canonical_json_bytes(chain)
    chain_sha = _sha256_bytes(payload)
    chain_path.write_bytes(payload)
    (output_dir / f"{CHAIN_NAME}.sha256").write_text(f"{chain_sha}  {CHAIN_NAME}\n", encoding="utf-8")
    return {**chain, "chain_sha256": chain_sha}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Release Evidence Chain PRO")
    parser.add_argument("--failure-evidence", type=Path, required=True)
    parser.add_argument("--browser-evidence", type=Path, required=True)
    parser.add_argument("--release-evidence", type=Path, required=True)
    parser.add_argument("--promoted-zip", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = build_chain(
            args.failure_evidence.resolve(),
            args.browser_evidence.resolve(),
            args.release_evidence.resolve(),
            args.promoted_zip.resolve(),
            args.output_dir.resolve(),
        )
    except Exception as exc:
        print(f"RELEASE_EVIDENCE_CHAIN_INVALID: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("RELEASE_EVIDENCE_CHAIN_STATUS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
