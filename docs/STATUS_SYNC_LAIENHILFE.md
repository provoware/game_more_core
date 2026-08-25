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

## Praktisches Beispiel nach PR #185

PR #185 änderte genau einen reproduzierten Presentation-Befund: Die kompakte Kurzmarke im eigenen Ranking-Eintrag wurde von `0.30rem` auf den bereits im kleinen HUD verwendeten Lesbarkeitsboden `0.34rem` angehoben. Der fachliche Safe-Merge ist `22d2774a8a0f55c645d5eb97141099b8f0ae7433`.

Direkt danach standen die drei kanonischen Statusdateien noch auf PR #183 und führten `POOL-UX-009 – Crew Identity Micro Polish Audit` weiter als offene Arbeit. Genau diese Abweichung meldet der Status-Sync als Drift.

Die Statuskorrektur übernimmt deshalb PR #185 in alle drei Statusquellen, setzt `POOL-UX-009` auf `DONE` und zieht als nächsten kleinen QA-Punkt `POOL-QA-016 – Avatar Context Computed Size E2E`.

Wichtig: Der Status-Sync verändert dabei **keine CSS-Regel und keinen Browser-Harness**. Er dokumentiert nur den bestätigten Zustand. Erst der nächste eigene Slice darf den bereits vorhandenen Chromium-/Firefox-Harness um die tatsächlich berechnete `font-size` erweitern.

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass letzter validierter Feature-Stand, Feature-Pool, Micro-Polish-Vertrag und nächste aktive Arbeit zusammenpassen.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-PR-AUTOPREP:** Falls die Driftprüfung sich weiter bewährt, kann ein späterer eigener Automations-Slice bei einem roten Main-Check einen normalen Status-Sync-PR **vorbereiten**, aber weiterhin niemals direkt `main` beschreiben. Nutzen: weniger manuelle Statuspflege bei unverändertem Review- und `/safe-merge`-Schutz.
