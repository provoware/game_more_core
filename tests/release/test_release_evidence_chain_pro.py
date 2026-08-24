from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import release_evidence_chain_pro as chain  # noqa: E402


class ReleaseEvidenceChainContractTests(unittest.TestCase):
    def _write_json_with_sidecar(self, path: Path, payload: dict) -> str:
        data = chain._canonical_json_bytes(payload)
        path.write_bytes(data)
        digest = chain._sha256_bytes(data)
        Path(str(path) + ".sha256").write_text(f"{digest}  {path.name}\n", encoding="utf-8")
        return digest

    def test_chain_binds_all_evidence_and_promoted_zip(self):
        candidate = "a" * 64
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            failure_path = base / "FAILURE_CONTAINMENT_EVIDENCE.json"
            failure = {
                "source_commit": "commit",
                "source_tree": "tree",
                "candidate_sha256": candidate,
                "status": "PASS",
            }
            failure_sha = self._write_json_with_sidecar(failure_path, failure)

            browser_path = base / "DESKTOP_BROWSER_E2E_EVIDENCE.json"
            browser = {
                "source_commit": "commit",
                "source_tree": "tree",
                "candidate_sha256": candidate,
                "status": "PASS",
            }
            browser_sha = self._write_json_with_sidecar(browser_path, browser)

            release_path = base / "RELEASE_EVIDENCE.json"
            release = {
                "source_commit": "commit",
                "source_tree": "tree",
                "candidate_sha256": candidate,
                "release_state": "RELEASE_READY",
                "user_zip_available": True,
                "promoted_sha256": candidate,
                "subgates": {
                    "failure_containment_pro": {"status": "PASS", "evidence_sha256": failure_sha},
                    "desktop_browser_e2e_pro": {"status": "PASS", "evidence_sha256": browser_sha},
                },
            }
            release_sha = self._write_json_with_sidecar(release_path, release)

            promoted = base / "BUNKERFREQUENZ.zip"
            promoted.write_bytes(b"release-bytes")
            actual_zip_sha = chain._sha256_file(promoted)
            Path(str(promoted) + ".sha256").write_text(f"{actual_zip_sha}  {promoted.name}\n", encoding="utf-8")

            failure["candidate_sha256"] = actual_zip_sha
            browser["candidate_sha256"] = actual_zip_sha
            release["candidate_sha256"] = actual_zip_sha
            release["promoted_sha256"] = actual_zip_sha
            failure_sha = self._write_json_with_sidecar(failure_path, failure)
            browser_sha = self._write_json_with_sidecar(browser_path, browser)
            release["subgates"]["failure_containment_pro"]["evidence_sha256"] = failure_sha
            release["subgates"]["desktop_browser_e2e_pro"]["evidence_sha256"] = browser_sha
            release_sha = self._write_json_with_sidecar(release_path, release)

            result = chain.build_chain(failure_path, browser_path, release_path, promoted, base / "out")
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["candidate_sha256"], actual_zip_sha)
            self.assertEqual(result["links"][1]["previous_sha256"], failure_sha)
            self.assertEqual(result["links"][2]["previous_sha256"], browser_sha)
            self.assertEqual(result["links"][3]["previous_sha256"], release_sha)
            self.assertTrue(result["links"][3]["byte_exact_candidate"])

    def test_tampered_evidence_sidecar_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "evidence.json"
            path.write_text("{}\n", encoding="utf-8")
            Path(str(path) + ".sha256").write_text(f"{'0' * 64}  {path.name}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "widerspricht"):
                chain._declared_sidecar_hash(path)

    def test_mismatched_source_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Source Commit/Tree"):
            chain._same_source(
                {"source_commit": "a", "source_tree": "tree"},
                {"source_commit": "b", "source_tree": "tree"},
            )

    def test_chain_serialization_is_canonical(self):
        payload = {"b": 2, "a": 1}
        first = chain._canonical_json_bytes(payload)
        second = chain._canonical_json_bytes(json.loads(first.decode("utf-8")))
        self.assertEqual(first, second)
        self.assertEqual(chain._sha256_bytes(first), chain._sha256_bytes(second))


if __name__ == "__main__":
    unittest.main()
