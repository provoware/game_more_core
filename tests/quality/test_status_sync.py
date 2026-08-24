from pathlib import Path
import json
import subprocess
import tempfile
import unittest

from tools.status_sync import SafeMergeAnchor, check_status_sync, latest_relevant_safe_merge


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def write_status(root: Path, anchor: SafeMergeAnchor) -> None:
    marker = f"- **Status-Sync-Anker:** PR #{anchor.pull_request} · Merge `{anchor.merge_commit}`\n"
    (root / "TODO.md").write_text("# TODO\n\n" + marker, encoding="utf-8")
    (root / "FEATURE_POOL.md").write_text("# FEATURE-POOL\n\n" + marker, encoding="utf-8")
    (root / "PROJEKTSTATUS.json").write_text(
        json.dumps(
            {
                "status_sync": {
                    "anchor_pull_request": anchor.pull_request,
                    "anchor_merge_commit": anchor.merge_commit,
                },
                "remote_validation": {
                    "pull_request": anchor.pull_request,
                    "merged_commit": anchor.merge_commit,
                    "safe_merge_result": "PASS",
                    "main_provenance_confirmed": True,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class StatusSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, "init", "-b", "main")
        git(self.root, "config", "user.email", "status-sync@example.invalid")
        git(self.root, "config", "user.name", "Status Sync Test")
        write_status(self.root, SafeMergeAnchor(1, "0" * 40))
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "baseline")

    def tearDown(self):
        self.temp.cleanup()

    def merge_feature(self, pr_number: int = 173) -> SafeMergeAnchor:
        git(self.root, "checkout", "-b", f"feature-{pr_number}")
        path = self.root / "web" / "a4" / "app.js"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"// feature {pr_number}\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", f"feature {pr_number}")
        git(self.root, "checkout", "main")
        git(self.root, "merge", "--no-ff", f"feature-{pr_number}", "-m", f"Safe merge PR #{pr_number}")
        return SafeMergeAnchor(pr_number, git(self.root, "rev-parse", "HEAD"))

    def test_detects_drift_in_all_three_canonical_documents(self):
        expected = self.merge_feature()
        stale = SafeMergeAnchor(172, "1" * 40)
        write_status(self.root, stale)
        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertTrue(any("TODO.md" in error for error in errors))
        self.assertTrue(any("FEATURE_POOL.md" in error for error in errors))
        self.assertTrue(any("PROJEKTSTATUS.json" in error for error in errors))

    def test_synced_documents_match_latest_relevant_safe_merge(self):
        expected = self.merge_feature()
        write_status(self.root, expected)
        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertEqual(errors, [])

    def test_status_only_safe_merge_does_not_create_self_drift_loop(self):
        expected = self.merge_feature()
        git(self.root, "checkout", "-b", "status-sync")
        write_status(self.root, expected)
        tool = self.root / "tools" / "status_sync.py"
        tool.parent.mkdir(parents=True, exist_ok=True)
        tool.write_text("# status sync helper\n", encoding="utf-8")
        changelog = self.root / "CHANGELOG.d" / "0.8.8-STATUS-SYNC-AFTER-SAFE-MERGE.md"
        changelog.parent.mkdir(parents=True, exist_ok=True)
        changelog.write_text("status sync\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "status: sync canonical documents")
        git(self.root, "checkout", "main")
        git(self.root, "merge", "--no-ff", "status-sync", "-m", "Safe merge PR #174")

        self.assertEqual(latest_relevant_safe_merge(self.root), expected)
        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
