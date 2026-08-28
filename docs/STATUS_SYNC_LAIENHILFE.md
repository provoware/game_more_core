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

Die read-only Equipment-Handelshistorie wurde mit PR #238 als Spielfunktion abgeschlossen. PR #240 hat dieselbe Funktion anschließend im echten Chromium für leeren Zustand, realen Kauf und Verkauf, Compensation-Filter, Hohen Kontrast und kleines Fenster geprüft. PR #242 ging noch einen Schritt weiter und hat den **Maximalfall mit acht wirksamen Trades**, langem Anzeigenamen, Großer Schrift, Hohem Kontrast und kleinem Fenster geprüft.

Darum sind zwei unterschiedliche Aussagen gleichzeitig richtig:

- **letzte validierte Spielfunktion:** `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY` aus PR #238,
- **aktueller Status-Sync-Anker:** PR #242, weil dies der neueste relevante und sicher gemergte UX-/QA-Stand ist.

Diese Trennung verhindert, dass ein reiner Dichte-/Browser-Audit fälschlich als neue Gameplayfunktion bezeichnet wird. Gleichzeitig bleibt die Projektübersicht technisch auf dem neuesten bestätigten Repository-Stand.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder passender Changelog-Nachweis dazukommen.

Auch der **kleinste Fall mit ausschließlich den drei kanonischen Statusdateien** wird ausdrücklich als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-/Story-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #242

PR #242 hat keine neue Economy- oder Gameplayfunktion eingeführt. Der vorhandene Chromium-Harness wurde nur auf den maximalen Dichtefall erweitert. Acht reale wirksame Trades wurden gemeinsam mit einem langen Anzeigenamen, Großer Schrift, Hohem Kontrast und einem 760×680-Fenster geprüft.

Der Befund war grün: **kein reproduzierbares Clipping, keine horizontale Überbreite und kein CSS-Fix nötig.**

Damit gilt nach dieser Statuskorrektur:

- letzter validierter Feature-Stand bleibt `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY` aus PR #238,
- aktueller fachlich relevanter Status-Sync-Anker ist `PR #242 / 5e112a6c…`.

### Was ist danach der echte nächste Inhaltsschritt?

Nach der langen Economy-/QA-Kette wird mit `POOL-PROPERTY-003` wieder ein sichtbarer Gameplay-Bereich geöffnet – aber zuerst nur als **Venue-Benefits-/Betriebsprofil-Contract-Audit**.

Das bedeutet in einfacher Sprache: Bevor ein eigener Ort später einen echten Vorteil bekommt, wird zuerst geprüft, **welcher bestehende Spielvertrag dafür zuständig sein darf**. Ein Vorteil darf nicht einfach im Browser erfunden werden. Event-Verfügbarkeit, Kosten-/Kapazitätswirkung oder eine rein narrative Venue-Identität müssen auf vorhandene Property-, Event-, Availability- und Projection-Verträge zurückgeführt werden können oder einen einzelnen klaren neuen Fachvertrag erhalten.

Noch nicht Teil dieses Audits sind Miete, Verkauf, laufende Betriebsökonomie oder frei erfundene Bonuswerte.

### Merksatz für Laien

**PR #238 ist weiterhin die letzte neue Spielfunktion. PR #242 ist der aktuelle geprüfte Repository-Anker. Der nächste Schritt prüft erst den Vertrag für Venue Benefits – gebaut wird erst danach, wenn klar ist, wer im Spiel dafür zuständig ist.**

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass Feature-Stand, Safe-Merge-Anker, Feature-Pool und nächste aktive Arbeit konsistent bleiben, ohne reine QA-/UX-Härtungen fälschlich als neue Spielfunktion zu klassifizieren.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.
