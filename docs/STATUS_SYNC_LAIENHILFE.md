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

## Praktisches Beispiel nach PR #190

PR #190 prüfte den bereits gezogenen Map-Viewport-Audit. Der reale Randort `generator_ost` bleibt bei `AUSWAHL FOKUS` wegen der begrenzten Pan-Spanne deutlich außerhalb der Kartenmitte. Gleichzeitig stellt der vorhandene zugängliche **`1:1`-Button** Zoom und Verschiebung vollständig auf die Gesamtansicht zurück. Der Audit wurde deshalb bewusst **ohne zweite Mini-Map** abgeschlossen. Der fachliche Safe-Merge ist `3f4ac78912d8d7a3c79bda2d2e3d6aa6d5aea9db`.

Direkt danach standen die drei kanonischen Statusdateien noch auf PR #188 und führten `POOL-MAP-003` weiterhin als offene Arbeit. Genau diese Abweichung meldet der Status-Sync als Drift.

Die Statuskorrektur übernimmt deshalb PR #190 in alle drei Statusquellen, setzt `POOL-MAP-003` auf `DONE` und zieht als nächsten kleinen QA-Punkt `POOL-QA-017 – Avatar Context Text Clip E2E`.

Wichtig: Der Status-Sync implementiert **keinen** Clipping-Fix. Der nächste eigene Slice verwendet ausschließlich den bereits vorhandenen Chromium-/Firefox-Avatar-Harness und misst zuerst, ob die bestätigten Kurzmarken in HUD, Map oder Ranking tatsächlich abgeschnitten werden. CSS oder Markup darf erst bei einem reproduzierbaren Browserbefund verändert werden.

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass letzter validierter Feature-Stand, Feature-Pool, der abgeschlossene Map-Viewport-Audit und die nächste aktive Arbeit zusammenpassen.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.
