from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from start_diagnosis import classify_failure, render_diagnosis_report, resolution_summary  # noqa: E402


class StartDiagnosisTests(unittest.TestCase):
    def test_known_failure_classes_are_stable(self):
        cases = (
            ("VORPRÜFUNG", "Pflichtdateien fehlen: web/a4/index.html", "release_integrity"),
            ("VORPRÜFUNG", "Python 3.9 ist zu alt.", "python_runtime"),
            ("ABHÄNGIGKEITEN", "Spielstandordner ist nicht beschreibbar: denied", "filesystem_permissions"),
            ("ABHÄNGIGKEITEN", "Ungültiger Port: 70000", "port_configuration"),
            ("SERVERSTART", "Server lieferte innerhalb von 1s keine Adresse", "server_start"),
            ("API-PRÜFUNG", "/api/health ist nicht sicher erreichbar", "api_health"),
            ("BROWSERPRÜFUNG", "UI-Reaktionsprüfung fehlgeschlagen", "browser_validation"),
            ("NACHVALIDIERUNG", "Server wurde unerwartet beendet", "post_validation"),
        )
        for label, reason, expected in cases:
            with self.subTest(label=label, reason=reason):
                self.assertEqual(classify_failure(label, reason).code, expected)

    def test_report_contains_now_fix_and_transparent_resolution_summary(self):
        report = render_diagnosis_report(
            label="API-PRÜFUNG",
            reason="/api/health oder /api/state ist nicht sicher erreichbar: timeout",
            actions=("Server neu starten.",),
            resolutions=(
                "Spielstandordner angelegt: /tmp/save",
                "Port 8044 war belegt; automatischer Wechsel auf freien Port.",
            ),
            project_root=ROOT,
            python_version="3.12-test",
            status_path=Path("/tmp/START_STATUS.txt"),
        )
        self.assertIn("FEHLERKLASSE: api_health", report)
        self.assertIn("JETZT BEHEBEN:", report)
        self.assertIn("AUTO-AUFLÖSUNGSBILANZ:", report)
        self.assertIn("2 Bedingung(en) automatisch gelöst", report)
        self.assertIn("TRANSPARENTES AUFLÖSUNGSPROTOKOLL:", report)
        self.assertIn("Port 8044 war belegt", report)
        self.assertIn("Der Diagnosehelfer führt selbst keine Reparatur", report)

    def test_resolution_summary_is_compact_and_deduplicated(self):
        self.assertEqual(resolution_summary(()), "0 Bedingungen automatisch gelöst.")
        summary = resolution_summary(("A", "A", "B"))
        self.assertEqual(summary, "2 Bedingung(en) automatisch gelöst: A | B")


if __name__ == "__main__":
    unittest.main()
