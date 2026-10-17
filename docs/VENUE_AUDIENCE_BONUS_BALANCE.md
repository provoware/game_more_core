# Publikumskraft: begrenzter Rufbonus als geprüfter Vorschlag

## Status und Scope

**Nur definiert und lokal getestet, nicht aktiviert.** Verbindliche Parameter stehen ausschließlich in `manifests/VENUE_AUDIENCE_BONUS_PROPOSAL.json`; die folgenden Zahlen erklären diesen Vertrag. Die aktuelle Abrechnung und alle fünf bestehenden Effekte bleiben unverändert. Eine Aktivierung braucht einen eigenen versionierten Effect-/Receipt-/Replay-Vertrag und grüne Remote-Gates.

Geplanter Lesesatz: vorhandener Venue-Belegvertrag, Settlement-Effekte, `INCIDENT_MANIFEST.json` sowie deren direkte Tests. Die Anzeige wurde davor in einem getrennten lokalen Commit abgeschlossen. Die GitHub-API bleibt durch die verwaltete Netzpolicy gesperrt; der bereits hochgeladene Evidence-Branch ist kein CI- oder Merge-PASS.

## Auswahl und Abwägung

Der aktuelle Incident-Katalog besitzt 18 Antworten: Geldfolgen liegen zwischen −12.000 und 0 Cent, Ruffolgen zwischen −12 und +4. Ein prozentualer Einnahmebonus hätte keine positive bestehende Einnahmequelle. Einen Bonus auf das gesamte Eventbudget zu berechnen, würde dagegen Startkapital, Einlagen und Besitzkäufe als vermeintlichen Gewinn belohnen.

Deshalb wird genau **ein Rufpunkt pro bestätigtem Eventabschluss** vorgeschlagen. Verlustausgleich, Geldbonus, freie Regeneration und Stapeln mehrerer Immobilien werden verworfen. Es entsteht keine generische Bonusengine.

## Exakte vorgeschlagene Regel

Der Kandidat liefert **+1 Ruf** nur, wenn alle folgenden Bedingungen gemeinsam gelten:

1. neuer, gültiger und abgeschlossener Settlement-Beleg mit bestätigtem eigenem Event-Ort;
2. gespeicherte Publikumskraft mindestens **50/100**;
3. der ohne Bonus bestätigte Eventausgang hat mindestens **+2 Ruf**;
4. bestätigte Incident-Kosten betragen mindestens **1.000 Cent (10 Euro)**.

Sonst lautet der Bonus **0**. Alter Beleg, fehlende Evidence, fremder Besitz, null/negativer Rufausgang und kostenfreie Wiederholungen sind nicht bonusfähig. Derselbe Eventabschluss besitzt genau einen Schlüssel `settlement.event_id`; ein späterer Ausbau darf einen abgeschlossenen Beleg nicht neu bewerten.

Damit ist die Verstärkung auf **einen Punkt absolut und höchstens 50 % des positiven Basis-Rufgewinns** begrenzt. Beispiel: Basis +2 und Publikumskraft 94 bei 10 Euro bestätigten Kosten ergäben zukünftig insgesamt +3. Basis +1, Basis −3 oder Kosten 0 ergeben keinen Bonus. Der Vorschlag gibt **kein Geld** zurück und erzeugt keine Zinsen oder dauernden Erträge.

## Nachweise und Grenzen

`PYTHONPATH=src:. python3 -m unittest tests.runtime.test_venue_bonus_balance_proposal -v` prüft fünf Testfälle mit **16.665 Grenzkombinationen**: Basis-Ruf −12 bis +20, Publikumskraft 0 bis 100 und Kosten-/Einnahmegrenzen 0, −999, −1.000, −12.000 sowie +1.000 Cent. Dabei gilt immer 0 ≤ Bonus ≤ 1 und die relative Grenze von 50 %.

Weitere Fälle prüfen manipulierte Typen und Besitzer, zusätzliche Venue-Felder, falsche Event-ID und alte Belege. Die bestehende öffentliche Command-Grenze weist clientseitige Bonus-, Ruf- und Publikumskraftparameter ohne State-/Journalschreibvorgang ab. Retry und erneutes Lesen verändern den bestehenden Spielstand nicht.

Die kleine Referenzberechnung liegt ausschließlich im Audit-Test und ist kein neuer Runtime-Calculator. Ein aktueller erfolgreicher Abschluss erhält weiterhin nur seinen ursprünglichen Rufgewinn; der Vorschlag schaltet keinen heimlichen Bonus frei. Die Tests beweisen Vertragsgrenzen und die bestehende Abschottung, **keine aktive Bonusbuchung**.

Lokale Abschlussprüfung des Drei-Schritte-Arbeitsstands am 17.10.2026:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests/runtime -q`: **319 bestanden**.
- `BUNKER_PLAYWRIGHT_MODULE=/workspace/GAME_HTML_2026/node_modules/playwright PYTHONPATH=src:. python3 -m unittest discover -s tests/presentation -q`: **293 bestanden**, einschließlich echtem Chromium-Nachweis; kein Browser-Skip in diesem Lauf.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -q`: **22 bestanden**.
- `PYTHONPATH=src python3 tools/repository_health.py`, `python3 tools/status_sync.py check`, `node --check web/a4/app.js`, `git diff --check`: **PASS**.

Insgesamt **634 lokale Tests**. Die fünf neuen Proposal-Tests enthalten zusätzlich die genannte 16.665er-Matrix; diese Kombinationen werden nicht als 16.665 einzelne Runner-Tests ausgegeben. Der vorhandene Cloud-Playwright-Treiber ist nur eine optionale Testabhängigkeit. Keine Remote-Prüfung, kein Merge und keine aktive Bonusvergabe aus diesen Nachweisen ableiten.

Vor einer Aktivierung müssen insbesondere `effects == pending_settlement`, die zugehörigen angewandten Ruf-Triplets, historische Belege, Exactly-once nach Crash und eine sichtbare bestätigte Bonusursache ausdrücklich in einem neuen Vertrag zusammenpassen. Der alte Receipt-Vertrag wird nicht still umgedeutet.

## Sinnvolle nächste drei Schritte

1. `api.github.com` in den Umgebungseinstellungen freigeben, speichern/veröffentlichen; anschließend die vorbereiteten Commits über passende PRs, grüne Remote-Gates und `/safe-merge` übernehmen.
2. Den geprüften Bonusvorschlag in einen eigenen versionierten Anwendungs-/Receipt-/Recovery-Vertrag überführen, einschließlich Roh-Ausgang und angewandtem Bonus; noch kein Schreibpfad vor diesem Vertrag.
3. Erst danach denselben Settlement-Pfad um die einmalige Anwendung erweitern und mit realem Eventablauf, Crash/Reload und sichtbarer Ursache prüfen; Produktrelease gesondert abnehmen.
