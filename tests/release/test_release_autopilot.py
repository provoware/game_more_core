from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from release_autopilot import (  # noqa: E402
    BLOCKED,
    QUARANTINE,
    READY,
    evaluate_release_state,
    load_policy,
    promote_byte_exact,
)


class ReleaseAutopilotContractTests(unittest.TestCase):
    def test_policy_requires_future_pro_gates_before_public_promotion(self):
        policy, digest = load_policy(ROOT / "manifests" / "RELEASE_POLICY.json")
        self.assertEqual(len(digest), 64)
        self.assertEqual(
            policy["public_promotion_required_subgates"],
            ["desktop_browser_e2e_pro", "failure_containment_pro"],
        )
        self.assertFalse(policy["promotion"]["rebuild_after_validation"])
        self.assertTrue(policy["promotion"]["copy_validated_candidate_only"])
        self.assertTrue(policy["promotion"]["sha256_must_match_candidate"])

    def test_release_state_is_fail_closed_for_missing_flaky_or_failed_subgates(self):
        self.assertEqual(
            evaluate_release_state(
                {"desktop_browser_e2e_pro": "PASS", "failure_containment_pro": "PASS"}
            ),
            READY,
        )
        self.assertEqual(
            evaluate_release_state(
                {"desktop_browser_e2e_pro": "NOT_RUN", "failure_containment_pro": "PASS"}
            ),
            QUARANTINE,
        )
        self.assertEqual(
            evaluate_release_state(
                {"desktop_browser_e2e_pro": "FLAKY", "failure_containment_pro": "PASS"}
            ),
            QUARANTINE,
        )
        self.assertEqual(
            evaluate_release_state(
                {"desktop_browser_e2e_pro": "PASS", "failure_containment_pro": "FAIL"}
            ),
            BLOCKED,
        )

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

    def test_policy_json_is_canonical_data_not_executable_configuration(self):
        policy_path = ROOT / "manifests" / "RELEASE_POLICY.json"
        data = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(data["product"], "BUNKERFREQUENZ")
        self.assertEqual(
            set(data["release_states"]),
            {"RELEASE_READY", "QUARANTINE", "RELEASE_BLOCKED", "RELEASE_INVALID"},
        )
        boundaries = data["automatic_repair_boundaries"]
        self.assertFalse(boundaries["sudo"])
        self.assertFalse(boundaries["system_package_install"])
        self.assertFalse(boundaries["user_data_delete"])
        self.assertFalse(boundaries["gameplay_state_mutation"])


if __name__ == "__main__":
    unittest.main()
