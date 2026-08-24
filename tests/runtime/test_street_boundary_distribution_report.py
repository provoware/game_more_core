from collections import Counter
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from street_boundary_matrix_report import build_rows, load_manifest, render_markdown  # noqa: E402


class StreetBoundaryDistributionReportTests(unittest.TestCase):
    def test_every_approach_maps_exactly_one_hundred_runtime_buckets_to_declared_weights(self):
        manifest = load_manifest()
        weight_total, rows = build_rows(manifest)
        self.assertEqual(weight_total, 100)

        by_approach: dict[str, list[dict[str, object]]] = {}
        for row in rows:
            by_approach.setdefault(str(row["approach_id"]), []).append(row)

        self.assertEqual(set(by_approach), {"balanced", "recovery", "network", "scout"})
        for approach_id, approach_rows in by_approach.items():
            with self.subTest(approach_id=approach_id):
                self.assertEqual(sum(int(row["declared_weight"]) for row in approach_rows), 100)
                self.assertEqual(sum(int(row["observed_buckets"]) for row in approach_rows), 100)
                self.assertEqual(
                    Counter({str(row["encounter_id"]): int(row["observed_buckets"]) for row in approach_rows}),
                    Counter({str(row["encounter_id"]): int(row["declared_weight"]) for row in approach_rows}),
                )

    def test_zero_weight_is_proven_unselectable_in_runtime_bucket_matrix(self):
        _, rows = build_rows(load_manifest())
        scout_detour = next(
            row
            for row in rows
            if row["approach_id"] == "scout" and row["encounter_id"] == "street.construction_detour"
        )
        self.assertEqual(scout_detour["declared_weight"], 0)
        self.assertEqual(scout_detour["observed_buckets"], 0)
        self.assertEqual(scout_detour["bucket_range"], "–")
        self.assertFalse(scout_detour["selectable"])

    def test_report_is_reproducible_and_documents_source_command_and_boundaries(self):
        manifest = load_manifest()
        first = render_markdown(manifest)
        second = render_markdown(manifest)
        self.assertEqual(first, second)
        for token in (
            "Street Boundary & Distribution Matrix",
            "manifests/STREET_ENCOUNTER_MANIFEST.json",
            "PYTHONPATH=src python3 tools/street_boundary_matrix_report.py",
            "Energie 100",
            "Energie 0",
            "Stress 100",
            "Stress 0",
            "`street.construction_detour`",
        ):
            with self.subTest(token=token):
                self.assertIn(token, first)


if __name__ == "__main__":
    unittest.main()
