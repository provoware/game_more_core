import unittest

from tools.github_merge_guard import (
    GuardError,
    _latest_required_runs,
    merge_candidate,
    verify_candidate,
    verify_main_commit,
)


HEAD = "1" * 40
BASE = "2" * 40
MERGE = "3" * 40


MANIFEST = {
    "protected_branch": "main",
    "merge_safety": {
        "required_workflow_names": ["Runtime Core", "Presentation Core", "Repository Health"],
        "allowed_actor_permissions": ["admin", "maintain", "write"],
    },
}


class FakeClient:
    repository = "provoware/game_more_core"
    owner = "provoware"
    name = "game_more_core"

    def __init__(self):
        self.permission = "admin"
        self.pr = {
            "number": 99,
            "state": "open",
            "draft": False,
            "mergeable": True,
            "head": {"sha": HEAD},
            "base": {"ref": "main", "sha": BASE},
            "merged_at": None,
            "merge_commit_sha": None,
        }
        self.behind_by = 0
        self.merge_base_sha = BASE
        self.unresolved = 0
        self.run_conclusions = {
            "Runtime Core": "success",
            "Presentation Core": "success",
            "Repository Health": "success",
        }
        self.put_calls = []
        self.comments = []
        self.merge_result = {"merged": True, "sha": MERGE}
        self.main_commit_parents = [{"sha": BASE}, {"sha": HEAD}]

    def _runs(self):
        return [
            {
                "id": index,
                "name": name,
                "run_number": index,
                "status": "completed",
                "conclusion": conclusion,
                "head_sha": HEAD,
            }
            for index, (name, conclusion) in enumerate(self.run_conclusions.items(), start=10)
        ]

    def get(self, path, *, params=None):
        if "/collaborators/" in path:
            return {"permission": self.permission}
        if path.endswith("/pulls/99"):
            return dict(self.pr)
        if path.endswith("/branches/main"):
            return {"commit": {"sha": BASE}}
        if "/compare/" in path:
            return {
                "merge_base_commit": {"sha": self.merge_base_sha},
                "behind_by": self.behind_by,
            }
        if path.endswith("/actions/runs"):
            return {"workflow_runs": self._runs()}
        if path.endswith(f"/commits/{MERGE}"):
            return {"parents": list(self.main_commit_parents)}
        if path.endswith(f"/commits/{MERGE}/pulls"):
            merged_pr = dict(self.pr)
            merged_pr["merged_at"] = "2026-08-21T20:00:00Z"
            merged_pr["merge_commit_sha"] = MERGE
            return [merged_pr]
        if path == "/search/issues":
            return {"total_count": 0, "items": []}
        raise AssertionError(f"unexpected GET {path} {params}")

    def graphql(self, query, variables):
        return {
            "data": {
                "repository": {
                    "pullRequest": {
                        "reviewThreads": {
                            "nodes": [{"isResolved": False} for _ in range(self.unresolved)],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        }

    def put(self, path, body):
        self.put_calls.append((path, body))
        return dict(self.merge_result)

    def post(self, path, body):
        self.comments.append((path, body))
        return {"ok": True}


class MergeGuardTest(unittest.TestCase):
    def test_latest_required_runs_selects_newest_attempt_per_workflow(self):
        runs = [
            {"name": "Runtime Core", "run_number": 1, "conclusion": "failure"},
            {"name": "Runtime Core", "run_number": 2, "conclusion": "success"},
            {"name": "Other", "run_number": 99, "conclusion": "success"},
        ]
        selected = _latest_required_runs(runs, ["Runtime Core"])
        self.assertEqual(selected["Runtime Core"]["run_number"], 2)

    def test_green_current_candidate_passes(self):
        client = FakeClient()
        candidate = verify_candidate(client, MANIFEST, 99, actor="provoware")
        self.assertEqual(candidate.head_sha, HEAD)
        self.assertEqual(candidate.base_sha, BASE)
        self.assertEqual(set(candidate.required_runs), set(MANIFEST["merge_safety"]["required_workflow_names"]))

    def test_stale_branch_is_blocked(self):
        client = FakeClient()
        client.merge_base_sha = "4" * 40
        with self.assertRaisesRegex(GuardError, "aktuellen Stand von main"):
            verify_candidate(client, MANIFEST, 99, actor="provoware")

    def test_red_required_check_is_blocked(self):
        client = FakeClient()
        client.run_conclusions["Repository Health"] = "failure"
        with self.assertRaisesRegex(GuardError, "Pflichtchecks nicht grün"):
            verify_candidate(client, MANIFEST, 99, actor="provoware")

    def test_missing_required_check_is_blocked(self):
        client = FakeClient()
        del client.run_conclusions["Presentation Core"]
        with self.assertRaisesRegex(GuardError, "Pflichtchecks fehlen"):
            verify_candidate(client, MANIFEST, 99, actor="provoware")

    def test_unresolved_review_thread_is_blocked(self):
        client = FakeClient()
        client.unresolved = 1
        with self.assertRaisesRegex(GuardError, "ungelöste Review-Threads"):
            verify_candidate(client, MANIFEST, 99, actor="provoware")

    def test_actor_without_write_permission_is_blocked(self):
        client = FakeClient()
        client.permission = "read"
        with self.assertRaisesRegex(GuardError, "keine Merge-Berechtigung"):
            verify_candidate(client, MANIFEST, 99, actor="visitor")

    def test_draft_and_conflicted_pr_are_blocked(self):
        client = FakeClient()
        client.pr["draft"] = True
        with self.assertRaisesRegex(GuardError, "noch Draft"):
            verify_candidate(client, MANIFEST, 99)

        client = FakeClient()
        client.pr["mergeable"] = False
        with self.assertRaisesRegex(GuardError, "nicht mergefähig"):
            verify_candidate(client, MANIFEST, 99)

    def test_safe_merge_uses_expected_head_and_revalidates_merge_commit(self):
        client = FakeClient()
        merge_sha = merge_candidate(client, MANIFEST, 99, actor="provoware")
        self.assertEqual(merge_sha, MERGE)
        self.assertEqual(len(client.put_calls), 1)
        _, payload = client.put_calls[0]
        self.assertEqual(payload["sha"], HEAD)
        self.assertEqual(payload["merge_method"], "merge")
        self.assertTrue(any("SAFE MERGE PASS" in call[1]["body"] for call in client.comments))

    def test_main_integrity_accepts_only_two_parent_green_pr_merge(self):
        client = FakeClient()
        result = verify_main_commit(client, MANIFEST, MERGE)
        self.assertEqual(result["pr_number"], 99)
        self.assertEqual(result["head_sha"], HEAD)

    def test_direct_push_or_squash_style_main_commit_is_blocked(self):
        client = FakeClient()
        client.main_commit_parents = [{"sha": BASE}]
        with self.assertRaisesRegex(GuardError, "kein normaler Zwei-Eltern-PR-Merge"):
            verify_main_commit(client, MANIFEST, MERGE)

    def test_main_integrity_rejects_red_original_pr_head(self):
        client = FakeClient()
        client.run_conclusions["Runtime Core"] = "failure"
        with self.assertRaisesRegex(GuardError, "Pflichtchecks nicht grün"):
            verify_main_commit(client, MANIFEST, MERGE)


if __name__ == "__main__":
    unittest.main()
