# Status-Sync nach Safe Merge – Laienhilfe

## Was wird hier geprüft?

BUNKERFREQUENZ besitzt drei wichtige Projektübersichten: `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Sie sollen denselben zuletzt bestätigten fachlichen `/safe-merge` nennen.

Der Status-Sync-Check liest dafür **nur** die Git-Historie und diese drei vorhandenen Dateien. Er ändert kein Spiel, keinen Spielstand und keine Gameplaywerte.

## Was bedeutet `STATUS SYNC PASS`?

- alle drei Statusdateien nennen denselben Safe-Merge-Anker,
- dieser Anker entspricht dem letzten fachlich relevanten `Safe merge PR #…` in der First-Parent-Historie,
- `PROJEKTSTATUS.json` bestätigt dazu weiterhin `SAFE MERGE PASS` und Main-Provenienz.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder passender Changelog-Nachweis dazukommen.

Auch der **kleinste Fall mit ausschließlich den drei kanonischen Statusdateien** wird ausdrücklich als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #177

PR #177 hat den echten Chromium-Pfad **Profil → HUD → Map → eigener Ranking-Eintrag** sicher gemergt. Direkt danach hing der dokumentierte Status noch bei PR #175. Der Status-Sync erkennt genau diese Situation als Drift.

Die Korrektur übernimmt deshalb den bestätigten Merge `bb8d083061fb83453547d0ba4238c6eaeea8afc7` in alle drei kanonischen Statusdateien, setzt den erledigten Browser-E2E-Punkt auf `DONE` und benennt erst danach den nächsten unabhängigen Prüfpunkt. Die Korrektur verändert dabei weder CSS noch Browserlogik noch Spielzustand.

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. Sie prüft neben Drift und erweiterten Status-Sync-Slices auch den minimalen Drei-Dateien-Fall. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass letzter validierter Feature-Stand, Feature-Pool und nächste aktive Arbeit zusammenpassen.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

Falls die Driftprüfung sich im Alltag weiter bewährt, kann ein späterer eigener Automations-Slice bei einem roten Main-Check **einen vorbereiteten Status-Sync-PR eröffnen**, aber weiterhin niemals direkt in `main` schreiben. Das hält Auditierbarkeit und `/safe-merge`-Policy erhalten.
