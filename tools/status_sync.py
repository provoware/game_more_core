#!/usr/bin/env python3
"""Detect drift between canonical project status files and safe-merge history.

The checker is intentionally read-only. It never writes to ``main`` and does not
create a second project-status source. The three existing canonical documents
remain authoritative; Git history only supplies the latest confirmed merge
anchor they must agree on.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
TODO_PATH = "TODO.md"
FEATURE_POOL_PATH = "FEATURE_POOL.md"
PROJECT_STATUS_PATH = "PROJEKTSTATUS.json"
CANONICAL_STATUS_PATHS = (TODO_PATH, FEATURE_POOL_PATH, PROJECT_STATUS_PATH)
SAFE_MERGE_RE = re.compile(r"^Safe merge PR #(\d+)$")
MARKER_RE = re.compile(
    r"Status-Sync-Anker:\*\*\s*PR #(\d+)\s*·\s*Merge `([0-9a-f]{40})`"
)


@dataclass(frozen=True)
class SafeMergeAnchor:
    pull_request: int
    merge_commit: str


def _run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise RuntimeError(f"Git-Aufruf fehlgeschlagen: git {' '.join(args)}: {detail.strip()}") from exc
    return result.stdout


def _is_status_sync_path(path: str) -> bool:
    if path in {
        TODO_PATH,
        FEATURE_POOL_PATH,
        PROJECT_STATUS_PATH,
        "README.md",
        "tools/status_sync.py",
        "tests/quality/test_status_sync.py",
        "tests/runtime/test_feature_status_consistency.py",
        ".github/workflows/status-sync.yml",
        "docs/STATUS_SYNC_LAIENHILFE.md",
    }:
        return True
    if path.startswith("docs/STATUS_SYNC_") and path.endswith(".md"):
        return True
    if path.startswith("CHANGELOG.d/") and "STATUS-SYNC" in Path(path).name.upper():
        return True
    return False


def _changed_paths(root: Path, merge_commit: str) -> tuple[str, ...]:
    parents = _run_git(root, "rev-list", "--parents", "-n", "1", merge_commit).strip().split()
    if len(parents) < 3:
        return ()
    first_parent = parents[1]
    output = _run_git(root, "diff", "--name-only", first_parent, merge_commit)
    return tuple(line.strip() for line in output.splitlines() if line.strip())


def _is_status_only_safe_merge(root: Path, merge_commit: str) -> bool:
    paths = set(_changed_paths(root, merge_commit))
    # README, Status-Regressionen und versionsbezogene Status-Laienhilfen dürfen
    # wegen der Repository-Health-/Konsistenzverträge Teil eines Status-Syncs
    # sein. Ein beliebiger Doku-/Test-Merge darf aber niemals als Status-Sync
    # verschwinden: alle drei kanonischen Statusdateien müssen gemeinsam
    # enthalten sein. Eine reine PROJEKTSTATUS-Korrektur ist ebenfalls nur
    # Statuspflege und darf keinen neuen fachlichen Anker erzeugen.
    if paths == {PROJECT_STATUS_PATH}:
        return True
    return (
        set(CANONICAL_STATUS_PATHS).issubset(paths)
        and all(_is_status_sync_path(path) for path in paths)
    )


def latest_relevant_safe_merge(root: Path = ROOT, history_ref: str = "HEAD") -> SafeMergeAnchor:
    output = _run_git(root, "log", "--first-parent", "--format=%H%x09%s", history_ref)
    for line in output.splitlines():
        if "\t" not in line:
            continue
        commit, subject = line.split("\t", 1)
        match = SAFE_MERGE_RE.fullmatch(subject.strip())
        if match is None:
            continue
        if _is_status_only_safe_merge(root, commit):
            continue
        return SafeMergeAnchor(int(match.group(1)), commit)
    raise RuntimeError(
        f"Kein fachlich relevanter 'Safe merge PR #…'-Commit in der First-Parent-Historie von {history_ref} gefunden"
    )


def build_sync_suggestion(anchor: SafeMergeAnchor) -> dict:
    """Return exact read-only replacement values for the three canonical files."""
    marker = f"- **Status-Sync-Anker:** PR #{anchor.pull_request} · Merge `{anchor.merge_commit}`"
    return {
        "anchor": {
            "pull_request": anchor.pull_request,
            "merge_commit": anchor.merge_commit,
        },
        "canonical_updates": {
            TODO_PATH: {
                "status_sync_anchor": marker,
            },
            FEATURE_POOL_PATH: {
                "status_sync_anchor": marker,
            },
            PROJECT_STATUS_PATH: {
                "status_sync.anchor_pull_request": anchor.pull_request,
                "status_sync.anchor_merge_commit": anchor.merge_commit,
                "remote_validation.pull_request": anchor.pull_request,
                "remote_validation.merged_commit": anchor.merge_commit,
            },
        },
        "write_mode": "read_only",
    }


def _markdown_anchor(path: Path) -> SafeMergeAnchor | None:
    text = path.read_text(encoding="utf-8")
    match = MARKER_RE.search(text)
    if match is None:
        return None
    return SafeMergeAnchor(int(match.group(1)), match.group(2))


def _project_status_anchor(path: Path) -> tuple[SafeMergeAnchor | None, dict]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    sync = data.get("status_sync")
    if not isinstance(sync, dict):
        return None, data
    pull_request = sync.get("anchor_pull_request")
    merge_commit = sync.get("anchor_merge_commit")
    if not isinstance(pull_request, int) or not isinstance(merge_commit, str):
        return None, data
    if not re.fullmatch(r"[0-9a-f]{40}", merge_commit):
        return None, data
    return SafeMergeAnchor(pull_request, merge_commit), data


def check_status_sync(
    root: Path = ROOT,
    history_ref: str = "HEAD",
) -> tuple[SafeMergeAnchor, list[str]]:
    expected = latest_relevant_safe_merge(root, history_ref)
    errors: list[str] = []

    markdown_anchors = {
        TODO_PATH: _markdown_anchor(root / TODO_PATH),
        FEATURE_POOL_PATH: _markdown_anchor(root / FEATURE_POOL_PATH),
    }
    for path, anchor in markdown_anchors.items():
        if anchor is None:
            errors.append(f"{path}: Status-Sync-Anker fehlt oder ist ungültig")
        elif anchor != expected:
            errors.append(
                f"{path}: Anker PR #{anchor.pull_request} / {anchor.merge_commit[:12]} != "
                f"letzter relevanter Safe-Merge PR #{expected.pull_request} / {expected.merge_commit[:12]}"
            )

    project_anchor, project_status = _project_status_anchor(root / PROJECT_STATUS_PATH)
    if project_anchor is None:
        errors.append("PROJEKTSTATUS.json: status_sync-Anker fehlt oder ist ungültig")
    elif project_anchor != expected:
        errors.append(
            "PROJEKTSTATUS.json: status_sync-Anker "
            f"PR #{project_anchor.pull_request} / {project_anchor.merge_commit[:12]} != "
            f"PR #{expected.pull_request} / {expected.merge_commit[:12]}"
        )

    remote = project_status.get("remote_validation")
    if not isinstance(remote, dict):
        errors.append("PROJEKTSTATUS.json: remote_validation fehlt")
    else:
        if remote.get("pull_request") != expected.pull_request:
            errors.append(
                "PROJEKTSTATUS.json: remote_validation.pull_request stimmt nicht mit dem Status-Sync-Anker überein"
            )
        if remote.get("merged_commit") != expected.merge_commit:
            errors.append(
                "PROJEKTSTATUS.json: remote_validation.merged_commit stimmt nicht mit dem Status-Sync-Anker überein"
            )
        if remote.get("safe_merge_result") != "PASS" or remote.get("main_provenance_confirmed") is not True:
            errors.append("PROJEKTSTATUS.json: Remote-Validierung besitzt keinen bestätigten SAFE MERGE PASS")

    declared = [anchor for anchor in (*markdown_anchors.values(), project_anchor) if anchor is not None]
    if declared and len(set(declared)) != 1:
        errors.append("TODO.md, FEATURE_POOL.md und PROJEKTSTATUS.json verwenden unterschiedliche Status-Sync-Anker")

    return expected, errors


def _print_result(expected: SafeMergeAnchor, errors: Iterable[str]) -> int:
    errors = list(errors)
    if errors:
        print("STATUS SYNC FAIL", file=sys.stderr)
        print(
            f"Erwarteter Anker: PR #{expected.pull_request} / {expected.merge_commit}",
            file=sys.stderr,
        )
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1
    print("STATUS SYNC PASS")
    print(f"Anker: PR #{expected.pull_request} / {expected.merge_commit}")
    print("Kanonische Dateien: " + ", ".join(CANONICAL_STATUS_PATHS))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ Status-Sync nach Safe Merge")
    parser.add_argument("command", choices=("check", "anchor", "suggest"), nargs="?", default="check")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository-Root für Tests/Diagnose")
    parser.add_argument(
        "--history-ref",
        default="HEAD",
        help="Git-Ref, dessen First-Parent-Historie den erwarteten Safe-Merge-Anker liefert",
    )
    args = parser.parse_args()

    try:
        expected = latest_relevant_safe_merge(args.root, args.history_ref)
        if args.command == "anchor":
            print(json.dumps({"pull_request": expected.pull_request, "merge_commit": expected.merge_commit}))
            return 0
        if args.command == "suggest":
            print(json.dumps(build_sync_suggestion(expected), indent=2, ensure_ascii=False))
            return 0
        checked, errors = check_status_sync(args.root, args.history_ref)
        return _print_result(checked, errors)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"STATUS SYNC FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())