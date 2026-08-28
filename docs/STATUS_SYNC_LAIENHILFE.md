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
- **damaliger Status-Sync-Anker:** PR #234, weil dies zu diesem Zeitpunkt der neueste relevante und sicher gemergte QA-Stand war.

Diese Trennung verhindert, dass eine reine Testhärtung fälschlich als neue Gameplayfunktion bezeichnet wird. Gleichzeitig bleibt die Projektübersicht technisch auf dem neuesten bestätigten Repository-Stand.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder passender Changelog-Nachweis dazukommen.

Auch der **kleinste Fall mit ausschließlich den drei kanonischen Statusdateien** wird ausdrücklich als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-/Story-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #238

PR #236 bestätigte zunächst nur, dass das vorhandene Economy-Ledger eine sichere read-only Handelshistorie tragen kann. PR #238 hat diese Funktion anschließend wirklich umgesetzt: Im bestehenden Equipment-Bereich werden jetzt die letzten acht wirksamen bestätigten Käufe und Verkäufe mit Aktion, Equipment, Menge und tatsächlichem Stückpreis angezeigt. Kompensierte Original-/Gegenbuchungspaare werden aus der normalen Historie ausgeblendet, Gewinn oder Kostenbasis werden nicht erfunden.

Damit ist PR #238 wieder **beides zugleich**:

- letzter validierter Feature-Stand `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY`,
- aktueller fachlich relevanter Status-Sync-Anker `PR #238 / 52934e08…`.

Der vor dieser Statuskorrektur rote Status-Sync bedeutet deshalb nicht, dass die Handelsfunktion fehlerhaft ist. Er bedeutet nur: Die drei Projektübersichten standen noch auf dem früheren Audit PR #236 und müssen auf den bereits sicher gemergten Produktstand nachgezogen werden.

### Was ist danach der echte nächste Inhaltsschritt?

Als nächster kleiner Qualitäts-Slice wird ein **echter Browser-E2E für die Handelshistorie** gezogen. Er soll im vorhandenen Chromium-Acceptance-Pfad vier Dinge beweisen: leere Historie, bestätigten Kauf, bestätigten Verkauf und korrekt ausgeblendete Kompensationspaare. Kleines Fenster und Hoher Kontrast sollen dabei mitgeprüft werden.

Dieser nächste Test darf keine neue Markt-, Ledger- oder Gewinnlogik einführen. Eine spätere Gewinn-/Verlustanzeige bleibt weiterhin getrennt und braucht zuerst einen eindeutigen Kostenbasisvertrag.

### Merksatz für Laien

**Der Status-Sync sagt, bis wohin das Repository sicher geprüft ist. Der Feature-Stand sagt, welche Spielfunktion zuletzt wirklich hinzugekommen ist. Nach PR #238 zeigen beide wieder auf denselben produktiven Stand.**

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass Feature-Stand, Safe-Merge-Anker, Feature-Pool und nächste aktive Arbeit konsistent bleiben, ohne reine QA-Härtungen fälschlich als neue Spielfunktion zu klassifizieren.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.
