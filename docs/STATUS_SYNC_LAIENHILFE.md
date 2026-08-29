# Status-Sync nach Safe Merge – Laienhilfe

## Was wird hier geprüft?

BUNKERFREQUENZ besitzt drei wichtige Projektübersichten: `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Sie sollen denselben zuletzt bestätigten fachlich relevanten `/safe-merge` nennen.

Der Status-Sync-Check liest dafür **nur** die Git-Historie und diese drei vorhandenen Dateien. Er ändert kein Spiel, keinen Spielstand und keine Gameplaywerte.

## Was bedeutet `STATUS SYNC PASS`?

- alle drei Statusdateien nennen denselben Safe-Merge-Anker,
- dieser Anker entspricht dem letzten fachlich relevanten `Safe merge PR #…` in der First-Parent-Historie,
- `PROJEKTSTATUS.json` bestätigt dazu weiterhin `SAFE MERGE PASS` und Main-Provenienz.

## Wichtig: Safe-Merge-Anker ist nicht immer eine neue Spielfunktion

Ein späterer Audit-, Test-, UX- oder Robustheits-PR kann der neueste fachlich relevante Safe Merge sein, obwohl er keine neue eigenständige Gameplayfunktion freigibt.

Die read-only Equipment-Handelshistorie wurde mit PR #238 als letzte vollständig abgeschlossene neue Spielfunktion geführt. Danach wechselte der Schwerpunkt zu eigenen Locations. Die Venue-Kette wurde schrittweise und ohne zweite Architektur gehärtet:

- PR #244 prüfte zulässige Venue Benefits. Ergebnis: read-only Betriebsprofil GO; Event-, Kosten-, Kapazitäts- und Ertragsboni ohne eigenen Fachvertrag NO-GO.
- PR #245 begrenzte das Profil auf fünf vorhandene Werte: **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen**.
- PR #247 machte diese Werte ausschließlich bei tatsächlich besessenen Locations sichtbar.
- PR #248 ersetzte kryptische Kürzel durch verständliche Bezeichnungen.
- PR #249 sicherte reine Textausgabe und exakt fünf erlaubte Felder.
- PR #250 verbot einen Browser-Rückfall auf die interne Ortswert-Karte, der die Eigentumsgrenze umgehen könnte.
- PR #251 bewies das Profil im echten Chromium bei **760×680**, **Großer Schrift** und **Hohem Kontrast**, einschließlich Eigentumsgrenze und horizontaler Überbreite.
- PR #252 verschärfte denselben Nachweis: Hinter jedem der fünf sichtbaren Begriffe muss tatsächlich ein endlicher numerischer Wert stehen.

Darum sind weiterhin zwei Aussagen gleichzeitig richtig:

- **letzte als vollständig abgeschlossene neue Spielfunktion geführte Stufe:** `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY` aus PR #238,
- **aktueller Status-Sync-Anker:** PR #252, weil dies der in den kanonischen Dateien zuletzt nachgezogene fachlich relevante Venue-/QA-Stand ist.

Diese Trennung verhindert, dass reine Vertrags-, Presentation- oder QA-Härtungen versehentlich als neue Gameplaymechanik bezeichnet werden.

## Was bedeutet `STATUS SYNC FAIL`?

Mindestens eine Projektübersicht hängt hinter der bereits gemergten Realität zurück oder widerspricht den anderen beiden Dateien. Der Fehler nennt die betroffene Datei sowie erwartete PR-/Merge-Referenz.

Das ist absichtlich ein **sichtbarer Qualitätsfehler**. Der Check repariert `main` nicht heimlich und führt keinen direkten Bot-Push aus. Die Statuskorrektur bleibt ein normal prüfbarer PR und wird anschließend wieder über `/safe-merge` abgeschlossen.

### Was macht `suggest`?

Wenn der Check Drift meldet, kann zusätzlich der rein lesende Befehl

```bash
python3 tools/status_sync.py suggest
```

verwendet werden. Er gibt als JSON den **exakt erkannten letzten fachlich relevanten Safe-Merge-Anker** sowie die dazu passenden Zielwerte für `TODO.md`, `FEATURE_POOL.md` und die beiden Ankerfelder in `PROJEKTSTATUS.json` aus.

Wichtig: `suggest` schreibt **keine Datei**. Es ist nur eine eindeutige Reparaturvorlage. Dadurch muss bei einer Statuskorrektur weder PR-Nummer noch Merge-SHA aus Fehlermeldungen abgeschrieben oder geraten werden, und die drei kanonischen Dateien bleiben weiterhin die einzigen Statusquellen.

### Warum war der Status-Sync auf PR #252 rot?

Der Feature-Head von PR #252 enthielt bereits den verschärften echten Chromium-Nachweis, während `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` weiterhin auf PR #245 zeigten. Der read-only Driftcheck meldete deshalb korrekt den vorhandenen Rückstand. Die für normale PRs vorgeschriebenen Required Checks waren auf dem geprüften Head grün; `/safe-merge` bestätigte anschließend den Merge samt Main-Provenienz. Die folgende Statusiteration zog die Projektübersichten auf diese bereits gemergte Realität nach.

## Warum erzeugt der Status-Sync-Merge nicht sofort wieder Drift?

Reine Status-Sync-Merges verändern mindestens gemeinsam `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json`. Optional dürfen nur die bereits katalogisierten Status-Sync-Helfer wie Checker, Tests, Workflow, README, Laienhilfe oder ein passender Changelog-Nachweis dazukommen.

Auch der kleinste Fall mit ausschließlich den drei kanonischen Statusdateien wird als reine Statuskorrektur erkannt. Solche Merges werden bei der Suche nach dem letzten **fachlich relevanten** Safe Merge übersprungen. Dadurch zeigt der Anker weiterhin auf den zuletzt bestätigten Spiel-/QA-/UX-/Story-Slice statt auf seine eigene Dokumentationsreparatur.

Ein beliebiger README-, Test- oder Dokumentations-Merge wird dadurch nicht versteckt: Ohne alle drei kanonischen Statusdateien bleibt er ein normaler relevanter Safe Merge.

## Praktisches Beispiel nach PR #252

Das Betriebsprofil ist jetzt nicht mehr nur ein Vertrag auf Papier. Bei einem wirklich besessenen Ort zeigt die vorhandene Property-/Location-Ansicht genau fünf bestätigte Werte:

- Prestige,
- Publikumskraft,
- Risiko,
- Underground-Faktor,
- Nutzen.

Ein fremder oder nicht gekaufter Ort bekommt kein eigenes Besitzprofil. Die Anzeige erfindet keine Werte und holt fehlende Besitzwerte auch nicht aus einer internen Hilfsmap zurück. Im echten Chromium wurde zusätzlich geprüft, dass alle fünf Werte als Zahlen sichtbar sind und die Zeile unter großer Schrift, hohem Kontrast und engem Fenster nicht horizontal überläuft.

### Sichtbarer Wert ist noch keine Spielwirkung

Ein Wert wie `Publikumskraft 74` bedeutet im Moment: **Dieser bestätigte Ortswert wird dir angezeigt.** Er bedeutet noch nicht automatisch „74 % mehr Besucher“, „mehr Events“ oder „höherer Gewinn“.

Für eine solche echte Wirkung braucht es zuerst einen klaren Spielvertrag: Welche Aktion verwendet den Wert? Wer berechnet den Effekt? Wie wird er gespeichert oder im Journal belegt? Was passiert bei Replay, Retry und Grenzwerten? Wie wird verhindert, dass ein Bonus doppelt angewendet wird?

Darum ist die nächste aktive Stufe ein enger **Venue-Benefit-Mechanik-Audit**. Genau ein vorhandener Wert wird gegen bestehende Domain-/Application-, Journal-/Replay- und Balanceverträge geprüft. Nur bei eindeutiger Autorität darf daraus später ein mechanischer Implementierungsslice entstehen. Sonst lautet das Ergebnis bewusst NO-GO.

### Merksatz für Laien

**Ein Ortswert zeigt, wie dein Ort bestätigt dasteht. Eine echte Spielwirkung entsteht erst, wenn dafür eine geprüfte Spielregel existiert.**

## Für Entwickler

Manuelle Prüfung vom Repository-Root:

```bash
python3 tools/status_sync.py check
```

Nur den erkannten Anker anzeigen:

```bash
python3 tools/status_sync.py anchor
```

Exakte read-only Reparaturvorlage anzeigen:

```bash
python3 tools/status_sync.py suggest
```

Die gezielte Regression liegt in `tests/quality/test_status_sync.py`. `tests/runtime/test_feature_status_consistency.py` stellt zusätzlich sicher, dass Feature-Stand, Safe-Merge-Anker, Feature-Pool und nächste aktive Arbeit konsistent bleiben, ohne reine Audit-/UX-/QA-Härtungen fälschlich als neue Gameplayfunktion zu klassifizieren.

Der Workflow `.github/workflows/status-sync.yml` führt Regression und Driftprüfung automatisch auf Pull Requests und nach Pushes auf `main` aus.

## Spätere Verbesserungsideen

**STATUS-SYNC-DRIFT-AGE:** Ein späterer rein diagnostischer Slice könnte bei `STATUS SYNC FAIL` zusätzlich ausgeben, wie viele fachlich relevante Safe Merges die Statusquellen hinter dem erkannten Anker liegen. Nutzen: Priorität und Alter einer Drift sind sofort sichtbar, ohne irgendeine Datei automatisch zu schreiben oder den `/safe-merge`-Schutz zu umgehen.

**STATUS-SYNC-PR-CHECKLIST:** `suggest` könnte später optional eine kurze Markdown-Checkliste für den Status-PR ausgeben. Nutzen: Die vier notwendigen Ankeränderungen und der anschließende `check`-Nachweis lassen sich direkt in die PR-Beschreibung übernehmen, weiterhin ohne automatische Schreibrechte.