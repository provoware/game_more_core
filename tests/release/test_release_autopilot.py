from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from release_autopilot import (  # noqa: E402
    BLOCKED,
    QUARANTINE,
    READY,
    ReleaseInvalidError,
    ensure_frozen_source,
    evaluate_release_state,
    load_policy,
    load_subgate_evidence,
    promote_byte_exact,
)


class ReleaseAutopilotContractTests(unittest.TestCase):
    def test_policy_requires_future_pro_gates_and_source_binding(self):
        policy, digest = load_policy(ROOT / "manifests" / "RELEASE_POLICY.json")
        self.assertEqual(len(digest), 64)
        self.assertEqual(
            policy["public_promotion_required_subgates"],
            ["desktop_browser_e2e_pro", "failure_containment_pro"],
        )
        self.assertTrue(policy["build_isolation"]["clean_worktree_required"])
        self.assertTrue(policy["build_isolation"]["tracked_source_only"])
        self.assertEqual(policy["build_isolation"]["independent_build_directories"], 2)
        self.assertFalse(policy["promotion"]["rebuild_after_validation"])
        self.assertTrue(policy["promotion"]["copy_validated_candidate_only"])
        binding = policy["subgate_evidence_binding"]
        self.assertTrue(binding["source_commit_required"])
        self.assertTrue(binding["source_tree_required"])
        self.assertTrue(binding["pass_requires_evidence_sha256"])

    def test_source_freeze_checks_tracked_files_only_and_rejects_tracked_drift(self):
        with patch("release_autopilot._git") as git:
            git.side_effect = ["", "a" * 40, "b" * 40]
            self.assertEqual(ensure_frozen_source(), ("a" * 40, "b" * 40))
            git.assert_any_call("status", "--porcelain=v1", "--untracked-files=no")

        with patch("release_autopilot._git", return_value=" M tools/build_release.py"):
            with self.assertRaises(ReleaseInvalidError):
                ensure_frozen_source()

    def test_release_state_is_fail_closed_for_missing_flaky_or_failed_subgates(self):
        def gates(first: str, second: str):
            return {
                "desktop_browser_e2e_pro": {"status": first, "evidence_sha256": None},
                "failure_containment_pro": {"status": second, "evidence_sha256": None},
            }

        self.assertEqual(evaluate_release_state(gates("PASS", "PASS")), READY)
        self.assertEqual(evaluate_release_state(gates("NOT_RUN", "PASS")), QUARANTINE)
        self.assertEqual(evaluate_release_state(gates("FLAKY", "PASS")), QUARANTINE)
        self.assertEqual(evaluate_release_state(gates("PASS", "FAIL")), BLOCKED)

    def test_subgate_pass_is_bound_to_exact_source_and_evidence_hash(self):
        required = ["desktop_browser_e2e_pro", "failure_containment_pro"]
        source_commit = "a" * 40
        source_tree = "b" * 40
        evidence_hash = "c" * 64
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "subgates.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "source_commit": source_commit,
                        "source_tree": source_tree,
                        "gates": {
                            "desktop_browser_e2e_pro": {
                                "status": "PASS",
                                "evidence_sha256": evidence_hash,
                            },
                            "failure_containment_pro": {
                                "status": "PASS",
                                "evidence_sha256": "d" * 64,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            loaded = load_subgate_evidence(path, required, source_commit, source_tree)
            self.assertEqual(loaded["desktop_browser_e2e_pro"]["status"], "PASS")
            self.assertEqual(loaded["desktop_browser_e2e_pro"]["evidence_sha256"], evidence_hash)

            with self.assertRaises(ReleaseInvalidError):
                load_subgate_evidence(path, required, "e" * 40, source_tree)

            data = json.loads(path.read_text(encoding="utf-8"))
            data["gates"]["desktop_browser_e2e_pro"]["evidence_sha256"] = None
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ReleaseInvalidError):
                load_subgate_evidence(path, required, source_commit, source_tree)

    def test_missing_subgate_evidence_is_quarantine_not_implicit_pass(self):
        required = ["desktop_browser_e2e_pro", "failure_containment_pro"]
        loaded = load_subgate_evidence(None, required, "a" * 40, "b" * 40)
        self.assertEqual(evaluate_release_state(loaded), QUARANTINE)
        self.assertTrue(all(item["status"] == "NOT_RUN" for item in loaded.values()))

    def test_promotion_copies_already_validated_candidate_byte_exactly(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            candidate = root_path / "candidate.zip"
            candidate.write_bytes(b"validated-release-candidate\x00\x01")
            promoted = promote_byte_exact(candidate, root_path / "release")
            self.assertEqual(promoted.read_bytes(), candidate.read_bytes())
            sha_path = root_path / "release" / "candidate.zip.sha256"
            self.assertTrue(sha_path.is_file())
            self.assertIn("candidate.zip", sha_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
