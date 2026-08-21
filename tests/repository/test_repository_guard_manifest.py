import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class RepositoryGuardManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROOT / "manifests/REPOSITORY_GUARD_MANIFEST.json").read_text(encoding="utf-8")
        )

    def test_required_check_ids_remain_canonical(self):
        self.assertEqual(
            self.manifest["target_branch_policy"]["required_status_checks"],
            ["runtime-core", "presentation-core", "repository-health"],
        )
        self.assertEqual(
            set(self.manifest["required_workflows"]),
            {"runtime-core", "presentation-core", "repository-health"},
        )

    def test_safe_merge_contract_exists_and_is_owner_authorized(self):
        safety = self.manifest["merge_safety"]
        self.assertEqual(safety["safe_merge_command"], "/safe-merge")
        self.assertEqual(safety["merge_method"], "merge")
        self.assertFalse(safety["direct_push_to_main_valid"])
        self.assertFalse(safety["unresolved_review_threads_valid"])
        self.assertEqual(
            safety["required_workflow_names"],
            ["Runtime Core", "Presentation Core", "Repository Health"],
        )
        self.assertEqual(set(safety["allowed_actor_permissions"]), {"admin", "maintain", "write"})

    def test_safe_merge_protects_its_own_security_boundary(self):
        safety = self.manifest["merge_safety"]
        protected = set(safety["protected_guard_paths"])
        self.assertTrue(
            {
                ".github/workflows/runtime-core.yml",
                ".github/workflows/presentation-core.yml",
                ".github/workflows/repository-health.yml",
                ".github/workflows/safe-merge.yml",
                ".github/workflows/main-integrity.yml",
                "tools/repository_health.py",
                "tools/github_merge_guard.py",
                "manifests/REPOSITORY_GUARD_MANIFEST.json",
                "tests/repository/",
            }.issubset(protected)
        )

    def test_safe_merge_workflow_uses_trusted_main_and_exact_command(self):
        safety = self.manifest["merge_safety"]
        text = (ROOT / safety["safe_merge_workflow"]).read_text(encoding="utf-8")
        self.assertIn("issue_comment:", text)
        self.assertIn("github.event.comment.body == '/safe-merge'", text)
        self.assertIn("ref: main", text)
        self.assertIn("tools/github_merge_guard.py merge-pr", text)
        self.assertIn("Block self-modifying guard changes", text)
        self.assertIn("protected_guard_paths", text)
        self.assertIn("pull-requests: write", text)
        self.assertNotIn("pull_request_target:", text)

    def test_main_integrity_workflow_checks_every_main_push(self):
        safety = self.manifest["merge_safety"]
        text = (ROOT / safety["main_integrity_workflow"]).read_text(encoding="utf-8")
        self.assertIn("push:", text)
        self.assertIn("branches: [main]", text)
        self.assertIn("tools/repository_health.py", text)
        self.assertIn("tools/github_merge_guard.py verify-main", text)
        self.assertIn("tools/github_merge_guard.py incident", text)
        self.assertIn("issues: write", text)

    def test_merge_guard_tool_is_standard_library_source(self):
        safety = self.manifest["merge_safety"]
        path = ROOT / safety["merge_guard_tool"]
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        for forbidden in ("requests", "httpx", "PyGithub"):
            self.assertNotIn(f"import {forbidden}", text)
            self.assertNotIn(f"from {forbidden}", text)


if __name__ == "__main__":
    unittest.main()
