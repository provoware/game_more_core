# Status-Sync nach Safe Merge – Laienhilfe

## Was wird hier geprüft?

BUNKERFREQUENZ besitzt drei wichtige Projektübersichten: `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Sie sollen denselben zuletzt bestätigten fachlich relevanten `/safe-merge` nennen.

Der Status-Sync-Check liest dafür **nur** die Git-Historie und diese drei vorhandenen Dateien. Er ändert kein Spiel, keinen Spielstand und keine Gameplaywerte.

## Was bedeutet `STATUS SYNC PASS`?

- alle drei Statusdateien nennen denselben Safe-Merge-Anker,
- dieser Anker entspricht dem letzten fachlich relevanten `Safe merge PR #…` in der First-Parent-Historie,
- `PROJEKTSTATUS.json` bestätigt dazu weiterhin `SAFE MERGE PASS` und Main-Provenienz.

## Wichtig: Safe-Merge-Anker ist nicht immer eine neue Spielfunktion

Ein späterer QA-, Test- oder Robustheits-PR kann der neueste fachlich relevante Safe Merge sein, obwohl er **keine neue Spielfunktion** eingeführt hat.

Beispiel: Der Job-Lohn-Kontexthinweis wurde mit PR #231 als Spielfunktion abgeschlossen. PR #232 hat denselben bereits vorhandenen Hinweis im echten Chromium-Browser geprüft. PR #234 hat anschließend nur die Lade-Reihenfolge dieses Browsertests stabilisiert.

Darum dürfen zwei Aussagen gleichzeitig richtig sein:

- **letzte validierte Spielfunktion:** `0.8.8-UX-JOB-PAYOUT-CONTEXT-CLARITY` aus PR #231,
- **aktueller Status-Sync-Anker:** PR #234, weil dies der neueste relevante und sicher gemergte QA-Stand ist.

Diese Trennung verhindert, dass eine reine Testhärtung fälschlich als neue Gameplayfunktion bezeichnet wird. Gleichzeitig bleibt die Projektübersicht technisch auf dem neuesten bestätigten Repository-Stand.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder passender Changelog-Nachweis dazukommen.

Auch der **kleinste Fall mit ausschließlich den drei kanonischen Statusdateien** wird ausdrücklich als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-/Story-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #234

PR #231 führte den verständlichen Hinweis für reduzierten Joblohn ein. PR #232 bewies ihn im echten Chromium-Pfad mit Voll- und Teillohnfällen, `aria-label`, Hohem Kontrast und kleinem Fenster. PR #234 beseitigte anschließend eine konkrete Race-Condition im Acceptance-Harness, indem erst nach vollständiger `payoutReducedByEnergy`-Dekoration klassifiziert wird.

Die drei Statusdateien standen danach noch auf PR #229. Das Spiel und seine QA-Evidenz waren also weiter als die Projektübersichten. Der Status-Sync zieht deshalb den technischen Anker auf PR #234, lässt den letzten Feature-Stand aber korrekt auf PR #231.

### Was ist danach der echte nächste Inhaltsschritt?

`POOL-ECON-010` wird zunächst nur als **Equipment-Handelsverlauf-Audit** gezogen. Dabei wird geprüft, ob das vorhandene Ledger historische Kauf-/Verkaufspreise und Item-Identitäten bereits zuverlässig genug speichert.

Erst wenn diese Evidenz ausreicht, darf ein späterer Presentation-Slice Gewinn oder Verlust read-only erklären. Es werden keine alten Preise aus dem aktuellen Marktpreis zurückgerechnet und keine zweite Marktengine erfunden.

### Merksatz für Laien

**Der Status-Sync sagt, bis wohin das Repository sicher geprüft ist. Der Feature-Stand sagt, welche Spielfunktion zuletzt wirklich hinzugekommen ist. Beides kann auf unterschiedliche PRs zeigen und trotzdem korrekt sein.**

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass Feature-Stand, Safe-Merge-Anker, Feature-Pool und nächste aktive Arbeit konsistent bleiben, ohne QA-Härtungen fälschlich als neue Spielfunktion zu klassifizieren.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.