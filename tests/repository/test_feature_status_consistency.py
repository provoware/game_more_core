import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]


class FeatureStatusConsistencyTests(unittest.TestCase):
    def test_last_validated_feature_is_consistent_across_status_todo_and_pool(self):
        status = json.loads((ROOT / "PROJEKTSTATUS.json").read_text(encoding="utf-8"))
        todo = (ROOT / "TODO.md").read_text(encoding="utf-8")
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")

        iteration = status["last_validated_feature_iteration"]
        validation = status["remote_validation"]
        merge_sha = validation["merged_commit"]
        pr_number = validation["pull_request"]

        self.assertIn(f"Zuletzt remote validierte Feature-Stufe:** `{iteration}", todo)
        self.assertIn(f"PR #{pr_number}", todo)
        self.assertIn(merge_sha, todo)
        self.assertIn(f"**{iteration}:** PR #{pr_number}", pool)
        self.assertIn(merge_sha, pool)
        self.assertEqual(validation["safe_merge_result"], "PASS")
        self.assertTrue(validation["main_provenance_confirmed"])

    def test_validated_control_deck_pool_items_are_not_left_pulled(self):
        pool = (ROOT / "FEATURE_POOL.md").read_text(encoding="utf-8")
        for pool_id in ("POOL-UX-001", "POOL-STREET-004", "POOL-CRISIS-002"):
            matching = [line for line in pool.splitlines() if f"`{pool_id}`" in line]
            self.assertEqual(len(matching), 1, pool_id)
            self.assertIn("`DONE`", matching[0], pool_id)


if __name__ == "__main__":
    unittest.main()
