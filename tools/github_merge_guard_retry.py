#!/usr/bin/env python3
"""Retry adapter for GitHub merge verification.

GitHub's commit-to-pull-request association can become visible a few seconds
after the merge API already returned success. This adapter keeps the strict
merge policy but tolerates that bounded API propagation delay.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from typing import Any, Callable, Mapping, Sequence

try:
    from tools.github_merge_guard import (
        GitHubClient,
        GuardError,
        _client_from_env,
        _comment_best_effort,
        _load_manifest,
        _repo_path,
        verify_candidate,
        verify_main_commit,
    )
except ModuleNotFoundError:  # Direct execution from tools/.
    from github_merge_guard import (  # type: ignore
        GitHubClient,
        GuardError,
        _client_from_env,
        _comment_best_effort,
        _load_manifest,
        _repo_path,
        verify_candidate,
        verify_main_commit,
    )


DEFAULT_RETRY_DELAYS = (0.0, 1.0, 2.0, 4.0, 8.0)


class PostMergeVerificationError(GuardError):
    """Merge already happened but its post-verification could not be confirmed."""

    def __init__(self, merge_sha: str, reason: str) -> None:
        super().__init__(reason)
        self.merge_sha = merge_sha


def retry_verify_main(
    client: GitHubClient,
    manifest: Mapping[str, Any],
    commit_sha: str,
    *,
    delays: Sequence[float] = DEFAULT_RETRY_DELAYS,
    sleep_fn: Callable[[float], None] = time.sleep,
    verify_fn: Callable[[GitHubClient, Mapping[str, Any], str], Mapping[str, Any]] = verify_main_commit,
) -> Mapping[str, Any]:
    """Retry only the post-merge provenance read, never the merge operation."""
    if not delays:
        raise ValueError("Mindestens ein Verifikationsversuch ist erforderlich")

    last_error: GuardError | None = None
    for index, delay in enumerate(delays, start=1):
        if delay > 0:
            sleep_fn(float(delay))
        try:
            result = verify_fn(client, manifest, commit_sha)
        except GuardError as exc:
            last_error = exc
            print(
                f"POST-MERGE VERIFY RETRY {index}/{len(delays)}: {exc}",
                file=sys.stderr,
            )
            continue
        print(f"POST-MERGE VERIFY PASS {index}/{len(delays)} | {commit_sha}")
        return result

    raise GuardError(
        f"Nach {len(delays)} Versuchen keine bestätigte Main-Provenienz für "
        f"{commit_sha[:12]}: {last_error}"
    )


def safe_merge_with_retry(
    client: GitHubClient,
    manifest: Mapping[str, Any],
    pr_number: int,
    *,
    actor: str,
) -> str:
    """Validate once, merge once, then retry only the post-merge read."""
    candidate = verify_candidate(client, manifest, pr_number, actor=actor)
    result = client.put(
        _repo_path(client, f"/pulls/{pr_number}/merge"),
        {
            "sha": candidate.head_sha,
            "merge_method": "merge",
            "commit_title": f"Safe merge PR #{pr_number}",
            "commit_message": (
                "Automatisch über /safe-merge nach erfolgreicher Prüfung von "
                + ", ".join(
                    f"{name} {run_id}" for name, run_id in candidate.required_runs.items()
                )
            ),
        },
    )
    if not isinstance(result, Mapping) or result.get("merged") is not True:
        raise GuardError(f"GitHub hat PR #{pr_number} nicht gemergt: {result}")

    merge_sha = result.get("sha")
    if not isinstance(merge_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", merge_sha):
        raise PostMergeVerificationError("unknown", "Merge erfolgreich, aber Merge-SHA fehlt")

    try:
        retry_verify_main(client, manifest, merge_sha)
    except GuardError as exc:
        _comment_best_effort(
            client,
            pr_number,
            "⚠️ **SAFE MERGE COMMITTED – POST-VERIFY NICHT BESTÄTIGT** – "
            f"Merge-Commit: `{merge_sha}`. Grund: {exc}",
        )
        raise PostMergeVerificationError(merge_sha, str(exc)) from exc

    _comment_best_effort(
        client,
        pr_number,
        "✅ **SAFE MERGE PASS** – exakt geprüfter Head wurde gemergt und die "
        f"Main-Provenienz bestätigt. Merge-Commit: `{merge_sha}`.",
    )
    return merge_sha


def _cmd_merge(args: argparse.Namespace) -> int:
    client = _client_from_env()
    try:
        merge_sha = safe_merge_with_retry(
            client,
            _load_manifest(),
            args.pr,
            actor=args.actor,
        )
    except PostMergeVerificationError as exc:
        print(
            "SAFE MERGE POST-VERIFY FAIL: Der Merge wurde bereits geschrieben. "
            f"Commit {exc.merge_sha}. {exc}",
            file=sys.stderr,
        )
        return 2
    except GuardError as exc:
        _comment_best_effort(client, args.pr, f"⛔ **SAFE MERGE BLOCKED** – {exc}")
        print(f"SAFE MERGE BLOCKED: {exc}", file=sys.stderr)
        return 1

    print(f"SAFE MERGE PASS | PR #{args.pr} | merge {merge_sha}")
    return 0


def _cmd_verify_main(args: argparse.Namespace) -> int:
    client = _client_from_env()
    try:
        result = retry_verify_main(client, _load_manifest(), args.sha)
    except GuardError as exc:
        print(f"MAIN INTEGRITY FAIL: {exc}", file=sys.stderr)
        return 1
    print(
        f"MAIN INTEGRITY PASS | merge {result['merge_sha']} | PR #{result['pr_number']} | "
        f"head {result['head_sha']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ GitHub Merge Retry Guard")
    sub = parser.add_subparsers(dest="command", required=True)

    merge = sub.add_parser("merge-pr", help="Einmal mergen, Main-Provenienz begrenzt erneut lesen")
    merge.add_argument("--pr", type=int, required=True)
    merge.add_argument("--actor", required=True)
    merge.set_defaults(func=_cmd_merge)

    verify = sub.add_parser("verify-main", help="Main-Provenienz mit begrenztem Retry prüfen")
    verify.add_argument("--sha", required=True)
    verify.set_defaults(func=_cmd_verify_main)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
