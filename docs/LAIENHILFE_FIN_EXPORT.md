# Laienhilfe – Kontoauszug prüfen und als TXT oder CSV exportieren

## Was ist neu?

Im Bereich **JOBS → Bankkonto → Deine Geldbewegungen** kannst du den Export jetzt **vor dem Download lokal prüfen**.

- **TXT PRÜFEN** zeigt exakt den TXT-Inhalt, der heruntergeladen würde.
- **CSV PRÜFEN** zeigt exakt den CSV-Inhalt, der heruntergeladen würde.
- **VORSCHAU KOPIEREN** kopiert den gerade geprüften Inhalt in die Zwischenablage, sofern der Browser das erlaubt.
- Eine kleine **Prüfsumme** hilft dir zu erkennen, ob zwei exakt gleiche Exportinhalte auch dieselbe Kennung haben.
- **TXT DOWNLOAD** und **CSV DOWNLOAD** laden anschließend denselben serialisierten Inhalt herunter.

## Was bedeutet die Prüfsumme?

Die angezeigte achtstellige Kennung ist eine kleine deterministische **32-Bit-FNV-1a-Prüfsumme**. Gleicher Exportinhalt ergibt dieselbe Kennung. Schon eine Änderung am Exportinhalt führt normalerweise zu einer anderen Kennung.

Wichtig: Diese Prüfsumme ist **kein kryptografischer Sicherheitsnachweis und keine digitale Signatur**. Sie dient nur als schnelle lokale Vergleichshilfe.

## Was wird exportiert?

Der Export verwendet ausschließlich den bereits bestätigten Kontoauszug, den das Spiel für die Anzeige bereitstellt. Er rechnet das Ledger nicht noch einmal aus und erzeugt keine neuen Geldwerte.

Exportiert werden die unterstützten bestätigten Buchungen:

- Joblohn
- Einzahlungen
- Auszahlungen
- Sparzinsen

Außerdem werden die bereits vorhandenen Summen und Metadaten des Kontoauszugs übernommen.

## Wichtig: Der Anzeigefilter verändert den Export nicht

Wenn du im Spiel zum Beispiel nur **ZINSEN** oder **BANK** eingeblendet hast, enthält Vorschau und Exportdatei trotzdem den vollständigen unterstützten Kontoauszug. Der Filter ist nur eine lokale Ansichtshilfe.

## So geht es

1. Öffne im Control Deck den Bereich **JOBS**.
2. Gehe zum **Bankkonto** und zu **Deine Geldbewegungen**.
3. Klicke zuerst auf **TXT PRÜFEN** oder **CSV PRÜFEN**.
4. Lies die Vorschau und merke dir bei Bedarf die angezeigte Prüfsumme.
5. Optional: **VORSCHAU KOPIEREN**.
6. Klicke auf den passenden **DOWNLOAD**-Button.
7. Der Download verwendet exakt dieselbe Serialisierung wie die Vorschau.

Die Dateinamen bleiben stabil:

- `bunkerfrequenz-kontoauszug.txt`
- `bunkerfrequenz-kontoauszug.csv`

## Was Vorschau und Export ausdrücklich nicht machen

Sie:

- verändern kein Bargeld und kein Bankguthaben,
- schreiben nichts ins Savegame oder Journal,
- senden keinen neuen Finance-Befehl an die Runtime,
- berechnen keine Summen neu,
- erfinden kein Datum und keine Uhrzeit,
- legen kein zweites Ledger an,
- verwenden die Prüfsumme nicht für Gameplay oder Finanzentscheidungen.

## Wenn Kopieren nicht funktioniert

Manche Browser blockieren die Zwischenablage. Dann bleibt der gesamte Exportinhalt in der Vorschau sichtbar und kann manuell markiert und kopiert werden. Das Spiel und dein Geldstand werden dadurch nicht verändert.

## Spätere sinnvolle Erweiterung

Ein eigener späterer Release-/Archiv-Slice könnte bei Bedarf eine **kryptografische SHA-256-Dateiprüfung** ergänzen. Das wäre ein stärkerer Integritätsnachweis, gehört aber bewusst nicht in diese kleine lokale UX-Iteration.
