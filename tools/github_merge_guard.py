#!/usr/bin/env python3
"""Safe merge and main-integrity guard for BUNKERFREQUENZ.

The tool uses only the Python standard library and GitHub's REST/GraphQL APIs.
It is intentionally separate from gameplay/runtime code.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[1]
GUARD_MANIFEST = ROOT / "manifests" / "REPOSITORY_GUARD_MANIFEST.json"
API_ROOT = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"


class GuardError(RuntimeError):
    """Expected policy failure."""


@dataclass(frozen=True)
class Candidate:
    pr_number: int
    head_sha: str
    base_sha: str
    base_ref: str
    required_runs: Mapping[str, int]


class GitHubClient:
    def __init__(self, repository: str, token: str) -> None:
        if "/" not in repository:
            raise GuardError("GITHUB_REPOSITORY muss owner/repo enthalten")
        if not token:
            raise GuardError("GITHUB_TOKEN fehlt")
        self.repository = repository
        self.owner, self.name = repository.split("/", 1)
        self.token = token

    def _call(
        self,
        method: str,
        url: str,
        *,
        body: Mapping[str, Any] | None = None,
    ) -> Any:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "BUNKERFREQUENZ-repository-guard",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                payload = response.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GuardError(f"GitHub API {method} {url} -> HTTP {exc.code}: {detail[:500]}") from exc
        except error.URLError as exc:
            raise GuardError(f"GitHub API nicht erreichbar: {exc}") from exc
        if not payload:
            return None
        return json.loads(payload.decode("utf-8"))

    def get(self, path: str, *, params: Mapping[str, Any] | None = None) -> Any:
        url = f"{API_ROOT}{path}"
        if params:
            url += "?" + parse.urlencode(params)
        return self._call("GET", url)

    def post(self, path: str, body: Mapping[str, Any]) -> Any:
        return self._call("POST", f"{API_ROOT}{path}", body=body)

    def put(self, path: str, body: Mapping[str, Any]) -> Any:
        return self._call("PUT", f"{API_ROOT}{path}", body=body)

    def graphql(self, query: str, variables: Mapping[str, Any]) -> Any:
        result = self._call("POST", GRAPHQL_URL, body={"query": query, "variables": variables})
        if isinstance(result, Mapping) and result.get("errors"):
            raise GuardError(f"GitHub GraphQL Fehler: {result['errors']}")
        return result


def _load_manifest() -> dict[str, Any]:
    with GUARD_MANIFEST.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise GuardError("REPOSITORY_GUARD_MANIFEST.json muss ein JSON-Objekt sein")
    return value


def _merge_safety(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    value = manifest.get("merge_safety")
    if not isinstance(value, Mapping):
        raise GuardError("Guard-Manifest benötigt merge_safety")
    return value


def _workflow_names(manifest: Mapping[str, Any]) -> tuple[str, ...]:
    safety = _merge_safety(manifest)
    names = safety.get("required_workflow_names")
    if not isinstance(names, list) or not names or any(not isinstance(item, str) or not item for item in names):
        raise GuardError("merge_safety.required_workflow_names ist ungültig")
    return tuple(names)


def _allowed_permissions(manifest: Mapping[str, Any]) -> frozenset[str]:
    safety = _merge_safety(manifest)
    values = safety.get("allowed_actor_permissions")
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        raise GuardError("merge_safety.allowed_actor_permissions ist ungültig")
    return frozenset(values)


def _repo_path(client: GitHubClient, suffix: str) -> str:
    return f"/repos/{client.repository}{suffix}"


def _require_actor_permission(
    client: GitHubClient,
    manifest: Mapping[str, Any],
    actor: str | None,
) -> None:
    if not actor:
        return
    permission = client.get(_repo_path(client, f"/collaborators/{parse.quote(actor, safe='')}/permission"))
    level = permission.get("permission") if isinstance(permission, Mapping) else None
    if level not in _allowed_permissions(manifest):
        raise GuardError(f"{actor!r} besitzt keine Merge-Berechtigung: {level!r}")


def _latest_required_runs(
    runs: Sequence[Mapping[str, Any]],
    required_names: Sequence[str],
) -> dict[str, Mapping[str, Any]]:
    selected: dict[str, Mapping[str, Any]] = {}
    required = set(required_names)
    for run in runs:
        name = run.get("name")
        if name not in required:
            continue
        previous = selected.get(str(name))
        current_number = int(run.get("run_number") or 0)
        previous_number = int(previous.get("run_number") or 0) if previous else -1
        if previous is None or current_number > previous_number:
            selected[str(name)] = run
    return selected


def _require_green_runs(
    client: GitHubClient,
    manifest: Mapping[str, Any],
    head_sha: str,
) -> dict[str, int]:
    names = _workflow_names(manifest)
    payload = client.get(
        _repo_path(client, "/actions/runs"),
        params={"head_sha": head_sha, "event": "pull_request", "per_page": 100},
    )
    runs = payload.get("workflow_runs", []) if isinstance(payload, Mapping) else []
    if not isinstance(runs, list):
        raise GuardError("Workflow-Run-Antwort ist ungültig")
    selected = _latest_required_runs(
        [run for run in runs if isinstance(run, Mapping) and run.get("head_sha") in (None, head_sha)],
        names,
    )
    missing = [name for name in names if name not in selected]
    if missing:
        raise GuardError(f"Pflichtchecks fehlen auf Head {head_sha[:12]}: {', '.join(missing)}")

    failed: list[str] = []
    result: dict[str, int] = {}
    for name in names:
        run = selected[name]
        status = run.get("status")
        conclusion = run.get("conclusion")
        if status != "completed" or conclusion != "success":
            failed.append(f"{name}={status}/{conclusion}")
        result[name] = int(run.get("id") or 0)
    if failed:
        raise GuardError("Pflichtchecks nicht grün: " + ", ".join(failed))
    return result


def _unresolved_review_threads(client: GitHubClient, pr_number: int) -> int:
    query = """
query($owner:String!, $name:String!, $number:Int!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$cursor) {
        nodes { isResolved }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""
    cursor: str | None = None
    unresolved = 0
    while True:
        result = client.graphql(
            query,
            {
                "owner": client.owner,
                "name": client.name,
                "number": pr_number,
                "cursor": cursor,
            },
        )
        try:
            threads = result["data"]["repository"]["pullRequest"]["reviewThreads"]
        except (KeyError, TypeError) as exc:
            raise GuardError("Review-Threads konnten nicht gelesen werden") from exc
        nodes = threads.get("nodes", [])
        unresolved += sum(1 for node in nodes if isinstance(node, Mapping) and not node.get("isResolved"))
        page_info = threads.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            return unresolved
        cursor = page_info.get("endCursor")
        if not cursor:
            raise GuardError("Review-Thread-Pagination ohne Cursor")


def verify_candidate(
    client: GitHubClient,
    manifest: Mapping[str, Any],
    pr_number: int,
    *,
    actor: str | None = None,
) -> Candidate:
    _require_actor_permission(client, manifest, actor)
    protected_branch = manifest.get("protected_branch")
    if not isinstance(protected_branch, str) or not protected_branch:
        raise GuardError("protected_branch fehlt im Guard-Manifest")

    pr = client.get(_repo_path(client, f"/pulls/{pr_number}"))
    if not isinstance(pr, Mapping):
        raise GuardError("PR-Antwort ist ungültig")
    if pr.get("state") != "open":
        raise GuardError(f"PR #{pr_number} ist nicht offen")
    if pr.get("draft") is True:
        raise GuardError(f"PR #{pr_number} ist noch Draft")
    if not isinstance(pr.get("base"), Mapping) or pr["base"].get("ref") != protected_branch:
        raise GuardError(f"PR #{pr_number} zielt nicht auf {protected_branch}")
    if pr.get("mergeable") is False:
        raise GuardError(f"PR #{pr_number} ist nicht mergefähig")
    if pr.get("mergeable") is None:
        raise GuardError(f"PR #{pr_number}: GitHub berechnet Mergefähigkeit noch; /safe-merge erneut ausführen")

    head = pr.get("head") if isinstance(pr.get("head"), Mapping) else {}
    head_sha = head.get("sha")
    if not isinstance(head_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise GuardError("PR-Head-SHA ist ungültig")

    branch = client.get(_repo_path(client, f"/branches/{parse.quote(protected_branch, safe='')}"))
    try:
        base_sha = branch["commit"]["sha"]
    except (KeyError, TypeError) as exc:
        raise GuardError("Aktueller main-SHA konnte nicht gelesen werden") from exc

    comparison = client.get(_repo_path(client, f"/compare/{base_sha}...{head_sha}"))
    merge_base = comparison.get("merge_base_commit", {}) if isinstance(comparison, Mapping) else {}
    if merge_base.get("sha") != base_sha or int(comparison.get("behind_by") or 0) != 0:
        raise GuardError("PR-Branch enthält den aktuellen Stand von main nicht")

    required_runs = _require_green_runs(client, manifest, head_sha)
    unresolved = _unresolved_review_threads(client, pr_number)
    if unresolved:
        raise GuardError(f"PR #{pr_number} besitzt {unresolved} ungelöste Review-Threads")

    return Candidate(
        pr_number=pr_number,
        head_sha=head_sha,
        base_sha=base_sha,
        base_ref=protected_branch,
        required_runs=required_runs,
    )


def _comment_best_effort(client: GitHubClient, pr_number: int, body: str) -> None:
    try:
        client.post(_repo_path(client, f"/issues/{pr_number}/comments"), {"body": body})
    except GuardError as exc:
        print(f"Warnung: PR-Kommentar nicht möglich: {exc}", file=sys.stderr)


def merge_candidate(
    client: GitHubClient,
    manifest: Mapping[str, Any],
    pr_number: int,
    *,
    actor: str,
) -> str:
    candidate = verify_candidate(client, manifest, pr_number, actor=actor)
    result = client.put(
        _repo_path(client, f"/pulls/{pr_number}/merge"),
        {
            "sha": candidate.head_sha,
            "merge_method": "merge",
            "commit_title": f"Safe merge PR #{pr_number}",
            "commit_message": (
                "Automatisch über /safe-merge nach erfolgreicher Prüfung von "
                + ", ".join(f"{name} {run_id}" for name, run_id in candidate.required_runs.items())
            ),
        },
    )
    if not isinstance(result, Mapping) or result.get("merged") is not True:
        raise GuardError(f"GitHub hat PR #{pr_number} nicht gemergt: {result}")
    merge_sha = result.get("sha")
    if not isinstance(merge_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", merge_sha):
        raise GuardError("Merge erfolgreich, aber Merge-SHA fehlt")

    verify_main_commit(client, manifest, merge_sha)
    _comment_best_effort(
        client,
        pr_number,
        "✅ **SAFE MERGE PASS** – exakt geprüfter Head wurde gemergt. "
        f"Merge-Commit: `{merge_sha}`.",
    )
    return merge_sha


def _associated_merged_pr(client: GitHubClient, manifest: Mapping[str, Any], commit_sha: str) -> Mapping[str, Any]:
    protected_branch = manifest.get("protected_branch")
    pulls = client.get(_repo_path(client, f"/commits/{commit_sha}/pulls"), params={"per_page": 100})
    if not isinstance(pulls, list):
        raise GuardError("Associated-PR-Antwort ist ungültig")
    candidates = [
        pr
        for pr in pulls
        if isinstance(pr, Mapping)
        and pr.get("merged_at")
        and pr.get("merge_commit_sha") == commit_sha
        and isinstance(pr.get("base"), Mapping)
        and pr["base"].get("ref") == protected_branch
    ]
    if len(candidates) != 1:
        raise GuardError(
            f"Main-Commit {commit_sha[:12]} besitzt nicht exakt einen bestätigten Merge-PR auf {protected_branch}"
        )
    return candidates[0]


def verify_main_commit(client: GitHubClient, manifest: Mapping[str, Any], commit_sha: str) -> Mapping[str, Any]:
    commit = client.get(_repo_path(client, f"/commits/{commit_sha}"))
    parents = commit.get("parents", []) if isinstance(commit, Mapping) else []
    if not isinstance(parents, list) or len(parents) != 2:
        raise GuardError(
            f"Main-Commit {commit_sha[:12]} ist kein normaler Zwei-Eltern-PR-Merge; Direkt-/Rebase-/Squash-Push blockiert"
        )
    pr = _associated_merged_pr(client, manifest, commit_sha)
    pr_number = int(pr.get("number") or 0)
    head = pr.get("head") if isinstance(pr.get("head"), Mapping) else {}
    head_sha = head.get("sha")
    if not isinstance(head_sha, str):
        raise GuardError("Gemergter PR besitzt keinen Head-SHA")
    required_runs = _require_green_runs(client, manifest, head_sha)
    unresolved = _unresolved_review_threads(client, pr_number)
    if unresolved:
        raise GuardError(f"Gemergter PR #{pr_number} besitzt {unresolved} ungelöste Review-Threads")
    return {
        "pr_number": pr_number,
        "head_sha": head_sha,
        "merge_sha": commit_sha,
        "required_runs": required_runs,
    }


def create_integrity_incident(client: GitHubClient, commit_sha: str, run_url: str, reason: str) -> None:
    query = f"repo:{client.repository} is:issue is:open {commit_sha[:12]} main-integrity"
    existing = client.get("/search/issues", params={"q": query, "per_page": 10})
    if isinstance(existing, Mapping) and int(existing.get("total_count") or 0) > 0:
        return
    client.post(
        _repo_path(client, "/issues"),
        {
            "title": f"[MAIN-INTEGRITY] Prüfung fehlgeschlagen {commit_sha[:12]}",
            "body": (
                "Der kanonische `main`-Stand hat den Main-Integrity-Guard nicht bestanden.\n\n"
                f"- Commit: `{commit_sha}`\n"
                f"- Workflow: {run_url}\n"
                f"- Grund: `{reason}`\n\n"
                "Bis zur Klärung keinen weiteren Feature-Merge durchführen. "
                "Repository Health und die drei Pflichtchecks prüfen und bei Bedarf einen gezielten Revert-PR erstellen."
            ),
        },
    )


def _client_from_env() -> GitHubClient:
    return GitHubClient(
        os.environ.get("GITHUB_REPOSITORY", ""),
        os.environ.get("GITHUB_TOKEN", ""),
    )


def _cmd_check_pr(args: argparse.Namespace) -> int:
    client = _client_from_env()
    candidate = verify_candidate(client, _load_manifest(), args.pr, actor=args.actor or None)
    print(
        f"SAFE MERGE CANDIDATE PASS | PR #{candidate.pr_number} | "
        f"head {candidate.head_sha} | base {candidate.base_sha}"
    )
    for name, run_id in candidate.required_runs.items():
        print(f"{name}: {run_id}")
    return 0


def _cmd_merge_pr(args: argparse.Namespace) -> int:
    client = _client_from_env()
    manifest = _load_manifest()
    try:
        merge_sha = merge_candidate(client, manifest, args.pr, actor=args.actor)
    except GuardError as exc:
        _comment_best_effort(client, args.pr, f"⛔ **SAFE MERGE BLOCKED** – {exc}")
        raise
    print(f"SAFE MERGE PASS | PR #{args.pr} | merge {merge_sha}")
    return 0


def _cmd_verify_main(args: argparse.Namespace) -> int:
    client = _client_from_env()
    result = verify_main_commit(client, _load_manifest(), args.sha)
    print(
        f"MAIN INTEGRITY PASS | merge {result['merge_sha']} | PR #{result['pr_number']} | "
        f"head {result['head_sha']}"
    )
    return 0


def _cmd_incident(args: argparse.Namespace) -> int:
    client = _client_from_env()
    create_integrity_incident(client, args.sha, args.run_url, args.reason)
    print("MAIN INTEGRITY INCIDENT RECORDED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BUNKERFREQUENZ GitHub Merge Guard")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check-pr", help="PR ohne Merge validieren")
    check.add_argument("--pr", type=int, required=True)
    check.add_argument("--actor", default="")
    check.set_defaults(func=_cmd_check_pr)

    merge = sub.add_parser("merge-pr", help="PR nur nach vollständiger Prüfung mergen")
    merge.add_argument("--pr", type=int, required=True)
    merge.add_argument("--actor", required=True)
    merge.set_defaults(func=_cmd_merge_pr)

    verify = sub.add_parser("verify-main", help="Main-Merge nachträglich validieren")
    verify.add_argument("--sha", required=True)
    verify.set_defaults(func=_cmd_verify_main)

    incident = sub.add_parser("incident", help="Main-Integrity-Incident idempotent anlegen")
    incident.add_argument("--sha", required=True)
    incident.add_argument("--run-url", required=True)
    incident.add_argument("--reason", required=True)
    incident.set_defaults(func=_cmd_incident)

    args = parser.parse_args()
    try:
        return int(args.func(args))
    except GuardError as exc:
        print(f"MERGE GUARD FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
