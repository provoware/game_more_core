# AVATAR-CONTEXT-E2E – Laienhilfe

## Was wird geprüft?

Der Release-Browser-Test öffnet BUNKERFREQUENZ in echten Browsern mit kleiner Arbeitsfläche. Für den detaillierten Identitätslauf erzeugt er **immer einen eigenen temporären Test-Spielstand**. Darin legt er genau über den vorhandenen Button ein lokales Spiel an, ändert die Crew-Kurzmarke im normalen Profil-Editor auf `E2E` und speichert sie über den vorhandenen `PROFIL SPEICHERN`-Pfad.

Der identische vorhandene Test-Harness läuft jetzt sowohl im Chromium-Acceptance-Pfad als auch im bereits vorhandenen nativen Firefox-/Geckodriver-Pfad. Es gibt dafür kein zweites Browserframework und keine zweite Avatar-Testlogik.

Danach muss dieselbe bestätigte Kurzmarke sichtbar bleiben in:

- der Profilvorschau,
- dem Live-HUD,
- dem eigenen Ranking-Eintrag,
- dem vorhandenen Map-Crew-Klonvertrag.

Zusätzlich wird der bestehende Modus `Hoher Kontrast` eingeschaltet. Der Test prüft nicht nur, ob Text vorhanden ist, sondern auch, ob `crew_identity.css` im echten Browser erfolgreich geladen wurde, die Crew-Marke sichtbare Geometrie besitzt und die weiße High-Contrast-Kante tatsächlich berechnet wird.

## Was wurde beim kleinen Fenster verbessert?

Der Chromium-Browserlauf hat einen echten Schwachpunkt sichtbar gemacht: unter 1100 px wurde die bestätigte Crew-Marke im HUD bisher vollständig ausgeblendet. Das widersprach dem Ziel, die bestätigte Identität durchgehend wiederzuerkennen.

Der HUD-Avatar bleibt deshalb jetzt auch in kompakteren Fenstern sichtbar, wird dort aber kleiner dargestellt. Der neue Firefox-Nachweis verwendet denselben 900 × 760 Browserrahmen und denselben 760 px breiten Testinhalt. Es entsteht keine zweite Identitätsquelle; weiterhin wird ausschließlich die bereits bestätigte HUD-Marke verwendet.

## Was beweist Firefox zusätzlich?

Der vorhandene Release-Nachweis startete Firefox bereits nativ über Geckodriver, prüfte dort bisher aber nur `BEREIT`, DOM-Reaktion und `/api/health`. Jetzt muss Firefox zusätzlich denselben ausgeführten `AVATAR_CONTEXT_E2E: PASS` liefern wie Chromium.

Damit ist im zweiten Browser konkret abgesichert:

- Profiländerung über die echte Oberfläche,
- bestätigte Crew-Marke im HUD,
- eigener Ranking-Eintrag,
- derselbe klar abgegrenzte Map-Presentation-Fixture,
- Hoher Kontrast,
- kleines Fenster.

Ein bloß geladener Scripttext reicht nicht: Erst der tatsächlich ausgeführte PASS beendet den Firefox-Slice erfolgreich. Meldet der Harness `FAIL`, wird der Release-Browser-Nachweis sofort rot.

## Warum ist der Map-Punkt ein Test-Fixture?

Ein frisch angelegtes Testspiel startet mit 1.000 EUR Eventbudget, während die günstigste kaufbare Immobilie 31.000 EUR kostet. Der Browser-Test darf deshalb weder Geld erfinden noch die Property-Runtime umgehen. Für den reinen Presentation-Vertrag wird nach bestätigtem Profil-Save kurzfristig ein DOM-Marker mit der bereits verwendeten Klasse `.owned` eingesetzt. Der vorhandene Map-Usability-Code muss daran dieselbe bestätigte HUD-Marke klonen. Der Marker wird danach wieder entfernt.

Damit prüft dieser Slice nur die Darstellungskette. Kaufpreis, Besitz und Persistenz bleiben vollständig bei den bestehenden Runtime- und Property-Tests.

## Schutz echter Spielstände

Wird `start_a4_acceptance.py` mit `--address` gegen eine bereits laufende Session verwendet, läuft **nur der bisherige read-only Browsercheck**. In diesem Modus wird keine E2E-Testseite erzeugt, kein Profilfeld verändert, kein `PROFIL SPEICHERN` ausgelöst und kein Testcharakter angelegt. Der schreibende Identitätslauf ist ausschließlich an den intern erzeugten temporären Save gebunden.

Auch der Firefox-Release-Pfad startet einen eigenen paketierten Server mit eigenem temporären Save-Verzeichnis. Die Testseite wird im entpackten temporären Release erzeugt und im `finally`-Pfad wieder gelöscht.

## Sicherheitsgrenzen

- kein direkter `/api/command`-Aufruf aus dem Test-Harness,
- kein künstlicher Property-Kauf,
- keine Änderung an echten oder per `--address` übergebenen Spielständen,
- keine Änderung an Journalverträgen oder Gameplaywerten,
- keine neue Avatar-, Map- oder Ranking-Datenquelle,
- Chromium und Firefox verwenden denselben vorhandenen Avatar-Context-Harness,
- die temporäre HTML-Testseite wird nur für den temporären Test-Spielstand erzeugt und nach dem Browserlauf wieder gelöscht,
- fehlender `AVATAR_CONTEXT_E2E: PASS` blockiert den detaillierten Browser-Acceptance-Test,
- fehlendes oder wirkungsloses `crew_identity.css` blockiert den visuellen PASS ebenfalls.

## Spätere sinnvolle Erweiterung

Wenn künftig ein eigener kanonischer Testspielstand mit bestätigtem Eigentum existiert, kann der temporäre `.owned`-DOM-Fixture entfallen und durch einen vollständig runtime-erzeugten Property-Kontext ersetzt werden. Bis dahin bleibt die Trennung zwischen Besitzautorität und Presentation-Test ausdrücklich sichtbar.
