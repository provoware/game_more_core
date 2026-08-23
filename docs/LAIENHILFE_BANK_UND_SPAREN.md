# Laienhilfe – Bankkonto, Sparen, Kontoauszug & Export

## Was ist jetzt möglich?

Dein persönliches Geld besteht aus **Bargeld** und **Bankguthaben**. Beides gehört zum selben persönlichen `PlayerFinanceState` und zum selben bestätigten Finance-Ledger.

Seit 0.8.8-D kannst du Geld zwischen Bargeld und Bank verschieben. D2 ergänzt bestätigte Sparzinsen. FIN-STATEMENTS macht diese bereits bestätigten Geldbewegungen verständlich sichtbar. FIN-EXPORT ergänzt jetzt eine **lokale TXT- und CSV-Kopie genau dieses Kontoauszugs**.

## Wie funktionieren die Zinsen?

Eine Zinsbuchung passiert **nicht einfach, weil auf deinem Computer Zeit vergangen ist**. Die Runtime muss zuerst eine gültige, bereits bestätigte Finance-Periode erhalten.

Für jede bestätigte Periode gelten aktuell **1 % Zins** auf das gerade bestätigte Bankguthaben.

Beispiel:

- Start: 100,00 € auf der Bank
- erste bestätigte Periode: +1,00 € → 101,00 €
- zweite bestätigte Periode: +1,01 € → 102,01 €

Damit entsteht Zinseszins, ohne eine zweite Finanzlogik einzuführen.

## Warum kann eine Periode nicht doppelt zahlen?

Jede bestätigte Finance-Periode besitzt eine stabile ID und einen fortlaufenden Finance-Tick. Derselbe Tick darf nur einmal verarbeitet werden. Ein Retry oder Neustart zahlt deshalb nicht noch einmal.

Auch eine Periode mit 0 Cent Zins wird als verarbeitet markiert. Später eingezahltes Geld kann dadurch keine alte Periode rückwirkend verzinsen.

## Was zeigt der Kontoauszug?

Der Kontoauszug sitzt direkt beim vorhandenen **Bankkonto im JOBS-Bereich**. Er liest ausschließlich bereits vorhandene, bestätigte Ledgerbuchungen und verändert nichts.

Aktuell werden vier Arten verständlich dargestellt:

- **Joblohn** – Geld aus einem bestätigten Scene Job
- **Einzahlung** – Bargeld wurde auf die Bank verschoben
- **Auszahlung** – Bankguthaben wurde zu Bargeld
- **Sparzins** – bestätigter Zins wurde dem Bankkonto gutgeschrieben

Die neueste unterstützte Geldbewegung steht oben. Zusätzlich siehst du den Bargeld- und Bankstand **nach** der jeweiligen Buchung.

## Wie exportiere ich den Kontoauszug?

Im Kontoauszug erscheinen zwei zusätzliche Schalter:

- **TXT EXPORT** – gut lesbare Textdatei
- **CSV EXPORT** – tabellarische Datei für Tabellenprogramme oder weitere Auswertung

Beide Dateien heißen bewusst stabil:

- `bunkerfrequenz-kontoauszug.txt`
- `bunkerfrequenz-kontoauszug.csv`

Es wird **kein Datum im Dateinamen erfunden**, weil der Kontoauszug keinen kanonisch bestätigten Exportzeitpunkt besitzt.

## Exportiert der aktuelle Filter nur einen Teil?

Nein. Das ist absichtlich so.

Die Filter `ALLE`, `JOBLOHN`, `BANK` und `ZINSEN` sind nur eine lokale Anzeigehilfe. Beim Export wird immer der **vollständige bereits unterstützte FIN-STATEMENTS-Kontoauszug** verwendet. So kann ein versehentlich aktiver Filter keine Buchungen aus deiner Datei verschwinden lassen.

## Werden beim Export Summen neu berechnet?

Nein. Der Export übernimmt die bereits vorhandenen Felder der bestätigten Kontoauszug-Projection, einschließlich der dort vorhandenen Summen und Eintragszahlen.

Der Browser:

- liest kein `finance.ledger` direkt,
- erzeugt keine neuen Buchungen,
- berechnet keine neuen Salden,
- schreibt nichts in Save oder Journal zurück.

Die Exportdatei ist also eine **lokale Kopie zur Ansicht**, kein zweiter Finanzstand.

## Warum steht dort „Buchung #…“ statt Datum und Uhrzeit?

Das persönliche Ledger enthält für diese Geldbewegungen derzeit **keinen kanonisch bestätigten Buchungszeitpunkt**. Deshalb erfindet das Spiel kein Datum und keine Uhrzeit.

`Buchung #12` bedeutet nur: Das war die zwölfte Ledgerposition. Sobald später ein bestätigter Zeitvertrag existiert, kann eine eigene Iteration echte Zeitangaben ergänzen. Rechnerzeit allein reicht dafür nicht.

## Was machen die Filter?

`ALLE`, `JOBLOHN`, `BANK` und `ZINSEN` ändern nur, welche bereits bestätigten Zeilen du gerade siehst. Der Filter wird nicht ins Journal geschrieben und verändert kein Geld.

Die in der Projection gelieferten Summen stammen aus der validierten FIN-STATEMENTS-Schicht. FIN-EXPORT übernimmt sie nur und rechnet sie nicht ein zweites Mal.

## Was passiert mit späteren Geldarten wie Investments?

Unbekannte oder spätere Ledgerarten werden in diesem Slice **nicht gedeutet**. Der Kontoauszug weist nur darauf hin, dass weitere bestätigte Buchungen existieren. Damit kann eine spätere Investment-Iteration eigene Regeln hinzufügen, ohne dass FIN-STATEMENTS oder FIN-EXPORT heute etwas Falsches behauptet.

## Kann der Browser Zinsen oder Kontoauszugsbuchungen auslösen?

Nein. Der Browser darf weder Finance-Perioden noch Zinsbeträge bestätigen. Für Kontoauszug und Export existiert außerdem **kein eigener Schreib-Command**. Beides bleibt reine Anzeige beziehungsweise lokale Dateikopie der bestehenden bestätigten Projection.

## Ist das Eventbudget betroffen?

Nein. Persönliches Bargeld und Bankguthaben bleiben fachlich getrennt vom Eventbudget.

## Was kommt als Nächstes?

Nach FIN-EXPORT ist **0.8.8-ECON-ANTI-GRIND** der stärkste spielmechanische Slice: zuerst ein klarer Balancevertrag für sehr niedrige Energie, danach die kleinste Runtime-Regel, ohne phasenunabhängige Scene Jobs abzuschaffen. C6 bleibt abhängig, bis ein echter kanonischer Rundenproduzent existiert.
