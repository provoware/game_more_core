import unittest
from unittest.mock import patch

from tools.github_merge_guard import Candidate, GuardError
from tools.github_merge_guard_retry import (
    PostMergeVerificationError,
    retry_verify_main,
    safe_merge_with_retry,
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


class TinyClient:
    repository = "provoware/game_more_core"
    owner = "provoware"
    name = "game_more_core"

    def __init__(self):
        self.put_calls = []
        self.comments = []

    def put(self, path, body):
        self.put_calls.append((path, body))
        return {"merged": True, "sha": MERGE}

    def post(self, path, body):
        self.comments.append((path, body))
        return {"ok": True}


class MergeRetryGuardTest(unittest.TestCase):
    def test_retry_verify_main_retries_reads_only_until_success(self):
        attempts = []
        sleeps = []

        def verify(client, manifest, sha):
            attempts.append(sha)
            if len(attempts) < 3:
                raise GuardError("GitHub association not visible yet")
            return {"merge_sha": sha, "pr_number": 36, "head_sha": HEAD}

        result = retry_verify_main(
            object(),
            MANIFEST,
            MERGE,
            delays=(0, 1, 2, 4),
            sleep_fn=sleeps.append,
            verify_fn=verify,
        )

        self.assertEqual(result["merge_sha"], MERGE)
        self.assertEqual(len(attempts), 3)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_retry_verify_main_is_bounded(self):
        attempts = []

        def verify(client, manifest, sha):
            attempts.append(sha)
            raise GuardError("still unavailable")

        with self.assertRaisesRegex(GuardError, "Nach 3 Versuchen"):
            retry_verify_main(
                object(),
                MANIFEST,
                MERGE,
                delays=(0, 0, 0),
                sleep_fn=lambda _: None,
                verify_fn=verify,
            )
        self.assertEqual(len(attempts), 3)

    def test_safe_merge_calls_merge_api_exactly_once(self):
        client = TinyClient()
        candidate = Candidate(
            pr_number=36,
            head_sha=HEAD,
            base_sha=BASE,
            base_ref="main",
            required_runs={
                "Runtime Core": 1,
                "Presentation Core": 2,
                "Repository Health": 3,
            },
        )

        with patch("tools.github_merge_guard_retry.verify_candidate", return_value=candidate), patch(
            "tools.github_merge_guard_retry.retry_verify_main",
            return_value={"merge_sha": MERGE, "pr_number": 36, "head_sha": HEAD},
        ):
            result = safe_merge_with_retry(client, MANIFEST, 36, actor="provoware")

        self.assertEqual(result, MERGE)
        self.assertEqual(len(client.put_calls), 1)
        self.assertEqual(client.put_calls[0][1]["sha"], HEAD)
        self.assertTrue(any("SAFE MERGE PASS" in body["body"] for _, body in client.comments))

    def test_post_merge_failure_is_not_reported_as_pre_merge_block(self):
        client = TinyClient()
        candidate = Candidate(
            pr_number=36,
            head_sha=HEAD,
            base_sha=BASE,
            base_ref="main",
            required_runs={
                "Runtime Core": 1,
                "Presentation Core": 2,
                "Repository Health": 3,
            },
        )

        with patch("tools.github_merge_guard_retry.verify_candidate", return_value=candidate), patch(
            "tools.github_merge_guard_retry.retry_verify_main",
            side_effect=GuardError("association still unavailable"),
        ):
            with self.assertRaises(PostMergeVerificationError) as raised:
                safe_merge_with_retry(client, MANIFEST, 36, actor="provoware")

        self.assertEqual(raised.exception.merge_sha, MERGE)
        self.assertEqual(len(client.put_calls), 1)
        bodies = [body["body"] for _, body in client.comments]
        self.assertTrue(any("SAFE MERGE COMMITTED" in body for body in bodies))
        self.assertFalse(any("SAFE MERGE BLOCKED" in body for body in bodies))


if __name__ == "__main__":
    unittest.main()
