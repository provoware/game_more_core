# Laienhilfe – Kontoauszug als TXT oder CSV exportieren

## Was ist neu?

Im Bereich **JOBS → Bankkonto → Deine Geldbewegungen** kannst du den bereits angezeigten Kontoauszug jetzt zusätzlich als **TXT** oder **CSV** herunterladen.

- **TXT** ist für Menschen gut lesbar und lässt sich mit jedem einfachen Texteditor öffnen.
- **CSV** ist praktisch für Tabellenprogramme wie LibreOffice Calc.

## Was wird exportiert?

Der Export verwendet ausschließlich den bereits bestätigten Kontoauszug, den das Spiel für die Anzeige bereitstellt. Er rechnet das Ledger nicht noch einmal aus und erzeugt keine neuen Geldwerte.

Exportiert werden die unterstützten bestätigten Buchungen:

- Joblohn
- Einzahlungen
- Auszahlungen
- Sparzinsen

Außerdem werden die bereits vorhandenen Summen und Metadaten des Kontoauszugs übernommen.

## Wichtig: Der Anzeigefilter verändert den Export nicht

Wenn du im Spiel zum Beispiel nur **ZINSEN** oder **BANK** eingeblendet hast, enthält die Exportdatei trotzdem den vollständigen unterstützten Kontoauszug. Der Filter ist nur eine lokale Ansichtshilfe.

## So geht es

1. Öffne im Control Deck den Bereich **JOBS**.
2. Gehe zum **Bankkonto** und zum Kontoauszug **Deine Geldbewegungen**.
3. Klicke auf **TXT EXPORT** oder **CSV EXPORT**.
4. Dein Browser lädt die Datei lokal herunter.

Die Dateinamen sind bewusst stabil:

- `bunkerfrequenz-kontoauszug.txt`
- `bunkerfrequenz-kontoauszug.csv`

## Was der Export ausdrücklich nicht macht

Der Export:

- verändert kein Bargeld und kein Bankguthaben,
- schreibt nichts ins Savegame oder Journal,
- sendet keinen neuen Finance-Befehl an die Runtime,
- berechnet keine Summen neu,
- erfindet kein Datum und keine Uhrzeit,
- legt kein zweites Ledger an.

Der Download ist damit eine reine lokale Kopie der bereits bestätigten FIN-STATEMENTS-Projection.

## Wenn keine Datei entsteht

Prüfe zuerst, ob dein Charakter und der Kontoauszug im Control Deck bereits verfügbar sind. Browser-Downloadregeln können außerdem verhindern, dass ein Download sichtbar startet. Das Spiel selbst wird dadurch nicht verändert.

## Spätere sinnvolle Erweiterung

Ein zukünftiger separater Slice könnte optional eine kleine Export-Prüfsumme oder ein maschinenlesbares Exportmanifest ergänzen. Das wäre nur ein Nachweis für die Datei und dürfte weiterhin keine neue Finanzlogik oder Buchhaltung einführen.
