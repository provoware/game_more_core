# AVATAR-CONTEXT-E2E – Laienhilfe

## Was wird geprüft?

Der Release-Browser-Test öffnet BUNKERFREQUENZ in einem echten Chromium-Fenster mit kleiner Arbeitsfläche. Für den detaillierten Identitätslauf erzeugt er **immer einen eigenen temporären Test-Spielstand**. Darin legt er genau über den vorhandenen Button ein lokales Spiel an, ändert die Crew-Kurzmarke im normalen Profil-Editor auf `E2E` und speichert sie über den vorhandenen `PROFIL SPEICHERN`-Pfad.

Danach muss dieselbe bestätigte Kurzmarke sichtbar bleiben in:

- der Profilvorschau,
- dem Live-HUD,
- dem eigenen Ranking-Eintrag,
- dem vorhandenen Map-Crew-Klonvertrag.

Zusätzlich wird der bestehende Modus `Hoher Kontrast` eingeschaltet und geprüft, dass die Marke in allen vier Kontexten eine sichtbare Geometrie behält.

## Warum ist der Map-Punkt ein Test-Fixture?

Ein frisch angelegtes Testspiel startet mit 1.000 EUR Eventbudget, während die günstigste kaufbare Immobilie 31.000 EUR kostet. Der Browser-Test darf deshalb weder Geld erfinden noch die Property-Runtime umgehen. Für den reinen Presentation-Vertrag wird nach bestätigtem Profil-Save kurzfristig ein DOM-Marker mit der bereits verwendeten Klasse `.owned` eingesetzt. Der vorhandene Map-Usability-Code muss daran dieselbe bestätigte HUD-Marke klonen. Der Marker wird danach wieder entfernt.

Damit prüft dieser Slice nur die Darstellungskette. Kaufpreis, Besitz und Persistenz bleiben vollständig bei den bestehenden Runtime- und Property-Tests.

## Schutz echter Spielstände

Wird `start_a4_acceptance.py` mit `--address` gegen eine bereits laufende Session verwendet, läuft **nur der bisherige read-only Browsercheck**. In diesem Modus wird keine E2E-Testseite erzeugt, kein Profilfeld verändert, kein `PROFIL SPEICHERN` ausgelöst und kein Testcharakter angelegt. Der schreibende Identitätslauf ist ausschließlich an den intern erzeugten temporären Save gebunden.

## Sicherheitsgrenzen

- kein direkter `/api/command`-Aufruf aus dem Test-Harness,
- kein künstlicher Property-Kauf,
- keine Änderung an echten oder per `--address` übergebenen Spielständen,
- keine Änderung an Journalverträgen oder Gameplaywerten,
- keine neue Avatar-, Map- oder Ranking-Datenquelle,
- die temporäre HTML-Testseite wird nur für den temporären Test-Spielstand erzeugt und nach dem Browserlauf wieder gelöscht,
- fehlender `AVATAR_CONTEXT_E2E: PASS` blockiert den detaillierten Browser-Acceptance-Test.

## Spätere sinnvolle Erweiterung

Wenn künftig ein eigener kanonischer Testspielstand mit bestätigtem Eigentum existiert, kann der temporäre `.owned`-DOM-Fixture entfallen und durch einen vollständig runtime-erzeugten Property-Kontext ersetzt werden. Bis dahin bleibt die Trennung zwischen Besitzautorität und Presentation-Test ausdrücklich sichtbar.
