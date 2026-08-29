from pathlib import Path
import json
import subprocess
import tempfile
import unittest

from tools.status_sync import (
    SafeMergeAnchor,
    build_sync_suggestion,
    check_status_sync,
    latest_relevant_safe_merge,
)


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
        (self.root / "README.md").write_text("# Project\n", encoding="utf-8")
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

    def test_suggestion_names_exact_read_only_updates_for_all_canonical_documents(self):
        expected = self.merge_feature(174)
        suggestion = build_sync_suggestion(expected)
        marker = f"- **Status-Sync-Anker:** PR #174 · Merge `{expected.merge_commit}`"

        self.assertEqual(
            suggestion["anchor"],
            {"pull_request": 174, "merge_commit": expected.merge_commit},
        )
        self.assertEqual(suggestion["write_mode"], "read_only")
        self.assertEqual(
            suggestion["canonical_updates"]["TODO.md"]["status_sync_anchor"],
            marker,
        )
        self.assertEqual(
            suggestion["canonical_updates"]["FEATURE_POOL.md"]["status_sync_anchor"],
            marker,
        )
        project_updates = suggestion["canonical_updates"]["PROJEKTSTATUS.json"]
        self.assertEqual(project_updates["status_sync.anchor_pull_request"], 174)
        self.assertEqual(project_updates["status_sync.anchor_merge_commit"], expected.merge_commit)
        self.assertEqual(project_updates["remote_validation.pull_request"], 174)
        self.assertEqual(project_updates["remote_validation.merged_commit"], expected.merge_commit)

    def test_applying_suggested_anchor_values_clears_status_drift(self):
        expected = self.merge_feature(176)
        suggestion = build_sync_suggestion(expected)
        suggested_anchor = SafeMergeAnchor(
            suggestion["anchor"]["pull_request"],
            suggestion["anchor"]["merge_commit"],
        )
        write_status(self.root, suggested_anchor)

        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertEqual(errors, [])

    def test_synced_documents_match_latest_relevant_safe_merge(self):
        expected = self.merge_feature()
        write_status(self.root, expected)
        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertEqual(errors, [])

    def test_minimal_three_file_status_safe_merge_does_not_create_self_drift(self):
        expected = self.merge_feature(175)
        git(self.root, "checkout", "-b", "minimal-status-sync")
        write_status(self.root, expected)
        git(self.root, "add", "TODO.md", "FEATURE_POOL.md", "PROJEKTSTATUS.json")
        git(self.root, "commit", "-m", "status: sync canonical documents only")
        git(self.root, "checkout", "main")
        git(self.root, "merge", "--no-ff", "minimal-status-sync", "-m", "Safe merge PR #176")

        self.assertEqual(latest_relevant_safe_merge(self.root), expected)
        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertEqual(errors, [])

    def test_project_status_only_correction_does_not_create_new_feature_anchor(self):
        expected = self.merge_feature(185)
        write_status(self.root, expected)
        git(self.root, "add", "TODO.md", "FEATURE_POOL.md", "PROJEKTSTATUS.json")
        git(self.root, "commit", "-m", "status after feature")

        git(self.root, "checkout", "-b", "project-status-correction")
        status_path = self.root / "PROJEKTSTATUS.json"
        data = json.loads(status_path.read_text(encoding="utf-8"))
        data["history_label"] = "read_only"
        status_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        git(self.root, "add", "PROJEKTSTATUS.json")
        git(self.root, "commit", "-m", "status: restore historical label")
        git(self.root, "checkout", "main")
        git(self.root, "merge", "--no-ff", "project-status-correction", "-m", "Safe merge PR #187")

        self.assertEqual(latest_relevant_safe_merge(self.root), expected)
        checked, errors = check_status_sync(self.root)
        self.assertEqual(checked, expected)
        self.assertEqual(errors, [])

    def test_status_only_safe_merge_with_readme_does_not_create_self_drift_loop(self):
        expected = self.merge_feature()
        git(self.root, "checkout", "-b", "status-sync")
        write_status(self.root, expected)
        (self.root / "README.md").write_text("# Project\n\nActive status synchronized.\n", encoding="utf-8")
        tool = self.root / "tools" / "status_sync.py"
        tool.parent.mkdir(parents=True, exist_ok=True)
        tool.write_text("# status sync helper\n", encoding="utf-8")
        runtime_test = self.root / "tests" / "runtime" / "test_feature_status_consistency.py"
        runtime_test.parent.mkdir(parents=True, exist_ok=True)
        runtime_test.write_text("# status consistency\n", encoding="utf-8")
        status_help = self.root / "docs" / "STATUS_SYNC_AFTER_PR173_LAIENHILFE.md"
        status_help.parent.mkdir(parents=True, exist_ok=True)
        status_help.write_text("# Status-Sync Hilfe\n", encoding="utf-8")
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

    def test_readme_only_safe_merge_is_still_a_relevant_merge(self):
        previous = self.merge_feature()
        git(self.root, "checkout", "-b", "readme-only")
        (self.root / "README.md").write_text("# Project\n\nDocumentation changed.\n", encoding="utf-8")
        git(self.root, "add", "README.md")
        git(self.root, "commit", "-m", "docs: update readme")
        git(self.root, "checkout", "main")
        git(self.root, "merge", "--no-ff", "readme-only", "-m", "Safe merge PR #175")
        latest = latest_relevant_safe_merge(self.root)
        self.assertEqual(latest.pull_request, 175)
        self.assertNotEqual(latest, previous)

    def test_current_base_history_wins_when_main_is_merged_into_stale_pr_branch(self):
        first = self.merge_feature(173)
        write_status(self.root, first)
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "status after 173")

        git(self.root, "checkout", "-b", "stale-pr")
        (self.root / "branch.txt").write_text("feature branch\n", encoding="utf-8")
        git(self.root, "add", "branch.txt")
        git(self.root, "commit", "-m", "branch work")

        git(self.root, "checkout", "main")
        second = self.merge_feature(174)
        write_status(self.root, second)
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "status after 174")

        git(self.root, "checkout", "stale-pr")
        git(self.root, "merge", "--no-ff", "main", "-m", "Merge main into stale PR")

        self.assertEqual(latest_relevant_safe_merge(self.root, "main"), second)
        checked, errors = check_status_sync(self.root, "main")
        self.assertEqual(checked, second)
        self.assertEqual(errors, [])
        self.assertNotEqual(latest_relevant_safe_merge(self.root, "HEAD"), second)


if __name__ == "__main__":
    unittest.main()
