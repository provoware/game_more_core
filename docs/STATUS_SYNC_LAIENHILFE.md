# Status-Sync nach Safe Merge – Laienhilfe

## Was wird hier geprüft?

BUNKERFREQUENZ besitzt drei wichtige Projektübersichten: `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Sie sollen denselben zuletzt bestätigten fachlich relevanten `/safe-merge` nennen.

Der Status-Sync-Check liest dafür **nur** die Git-Historie und diese drei vorhandenen Dateien. Er ändert kein Spiel, keinen Spielstand und keine Gameplaywerte.

## Was bedeutet `STATUS SYNC PASS`?

- alle drei Statusdateien nennen denselben Safe-Merge-Anker,
- dieser Anker entspricht dem letzten fachlich relevanten `Safe merge PR #…` in der First-Parent-Historie,
- `PROJEKTSTATUS.json` bestätigt dazu weiterhin `SAFE MERGE PASS` und Main-Provenienz.

## Wichtig: Safe-Merge-Anker ist nicht immer eine neue Spielfunktion

Ein späterer Audit-, Test-, UX- oder Robustheits-PR kann der neueste fachlich relevante Safe Merge sein, obwohl er **keine neue Spielfunktion** eingeführt hat.

Die read-only Equipment-Handelshistorie wurde mit PR #238 als Spielfunktion abgeschlossen. Danach wurde ihre Darstellung weiter geprüft. Anschließend wechselte der Fokus zu eigenen Locations:

- PR #244 prüfte, welche Venue Benefits überhaupt fachlich zulässig sind. Ergebnis: Ein read-only Betriebsprofil ist erlaubt; automatische Event-, Kosten-, Kapazitäts- oder Ertragsboni sind ohne eigenen Fachvertrag gesperrt.
- PR #245 begrenzte dieses Betriebsprofil noch genauer auf fünf bereits bestätigte Werte aus der vorhandenen Property-Upgrade-Projection: **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen**.

Darum sind zwei unterschiedliche Aussagen gleichzeitig richtig:

- **letzte validierte Spielfunktion:** `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY` aus PR #238,
- **aktueller Status-Sync-Anker:** PR #245, weil dies der neueste fachlich relevante und sicher gemergte Vertrags-/UX-Stand ist.

Diese Trennung verhindert, dass ein Audit oder Presentation-Vertrag fälschlich als neue Gameplayfunktion bezeichnet wird.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

### Warum war der Status-Sync auf PR #245 rot?

Der Feature-Head von PR #245 enthielt bereits den neuen Presentation-Vertrag, während die drei kanonischen Statusdateien noch auf PR #242 zeigten. Deshalb meldete der read-only Driftcheck korrekt einen bestehenden Rückstand. Die drei Required Checks für den Safe-Merge waren auf dem geprüften Head grün und `/safe-merge` bestätigte anschließend den Merge samt Main-Provenienz. Diese Statusiteration zieht nun die Projektübersichten auf die bereits gemergte Realität nach.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder passender Changelog-Nachweis dazukommen.

Auch der **kleinste Fall mit ausschließlich den drei kanonischen Statusdateien** wird ausdrücklich als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-/Story-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #245

PR #244 und PR #245 haben noch keine sichtbare Betriebsprofil-Karte gebaut. Sie haben zuerst festgelegt, **was die Oberfläche später sicher anzeigen darf**:

- nur für einen wirklich besessenen Ort,
- nur Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen,
- direkt aus den bereits bestätigten Ausbauwerten,
- keine zweite Berechnung im Browser,
- keine neue Speicherung,
- kein erfundener Bonus auf Events, Kosten, Kapazität oder Gewinn.

Damit gilt nach dieser Statuskorrektur:

- letzter validierter Feature-Stand bleibt `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY` aus PR #238,
- aktueller fachlich relevanter Status-Sync-Anker ist `PR #245 / f9357d16…`,
- nächster produktiver Slice ist `0.8.8-UX-VENUE-OPERATING-PROFILE-READONLY`.

### Was ist danach der echte nächste Inhaltsschritt?

In der bereits vorhandenen Property-/Location-Ansicht sollen die fünf bestätigten Ortswerte für **besessene Locations** verständlich gruppiert sichtbar werden. Ein fremder oder nicht gekaufter Ort darf kein eigenes Betriebsprofil vortäuschen.

Das Betriebsprofil ist zunächst nur eine bessere Lesebrille für bereits vorhandene Spieldaten. Erst ein späterer, eigener Fachvertrag darf entscheiden, ob beispielsweise Publikumskraft oder Nutzen tatsächlich eine neue mechanische Wirkung bekommt.

### Merksatz für Laien

**PR #238 ist weiterhin die letzte neue Spielfunktion. PR #245 ist der aktuelle geprüfte Repository-Anker. Als Nächstes werden fünf bereits bestätigte Werte sichtbar gemacht – ohne heimlich neue Spielregeln zu erfinden.**

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass Feature-Stand, Safe-Merge-Anker, Feature-Pool und nächste aktive Arbeit konsistent bleiben, ohne reine Audit-/UX-Härtungen fälschlich als neue Spielfunktion zu klassifizieren.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsidee

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.
