# Laienhilfe – Bankkonto, Sparen & Kontoauszug

## Was ist jetzt möglich?

Dein persönliches Geld besteht aus **Bargeld** und **Bankguthaben**. Beides gehört zum selben persönlichen `PlayerFinanceState` und zum selben bestätigten Finance-Ledger.

Seit 0.8.8-D kannst du Geld zwischen Bargeld und Bank verschieben. D2 ergänzt bestätigte Sparzinsen. FIN-STATEMENTS macht diese bereits bestätigten Geldbewegungen jetzt verständlich sichtbar.

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

## Warum steht dort „Buchung #…“ statt Datum und Uhrzeit?

Das persönliche Ledger enthält für diese Geldbewegungen derzeit **keinen kanonisch bestätigten Buchungszeitpunkt**. Deshalb erfindet das Spiel kein Datum und keine Uhrzeit.

`Buchung #12` bedeutet nur: Das war die zwölfte Ledgerposition. Sobald später ein bestätigter Zeitvertrag existiert, kann eine eigene Iteration echte Zeitangaben ergänzen. Rechnerzeit allein reicht dafür nicht.

## Was machen die Filter?

`ALLE`, `JOBLOHN`, `BANK` und `ZINSEN` ändern nur, welche bereits bestätigten Zeilen du gerade siehst. Der Filter wird nicht ins Journal geschrieben und verändert kein Geld.

Auch die angezeigten Summen werden ausschließlich aus den vorhandenen Ledgerzeilen berechnet. Der Browser erfindet keine Buchungen und keine Beträge.

## Was passiert mit späteren Geldarten wie Investments?

Unbekannte oder spätere Ledgerarten werden in diesem Slice **nicht gedeutet**. Der Kontoauszug weist nur darauf hin, dass weitere bestätigte Buchungen existieren. Damit kann eine spätere Investment-Iteration eigene Regeln hinzufügen, ohne dass FIN-STATEMENTS heute etwas Falsches behauptet.

## Kann der Browser Zinsen oder Kontoauszugsbuchungen auslösen?

Nein. Der Browser darf weder Finance-Perioden noch Zinsbeträge bestätigen. Für den Kontoauszug existiert außerdem **kein eigener Schreib-Command**: Er ist eine reine Anzeige des bestehenden bestätigten Ledgers.

## Ist das Eventbudget betroffen?

Nein. Persönliches Bargeld und Bankguthaben bleiben fachlich getrennt vom Eventbudget.

## Was kommt als Nächstes?

Nach validiertem FIN-STATEMENTS ist **0.8.8-F – Berlin Ops Map 2** der stärkste unabhängige Slice: lokaler Zoom/Pan, bessere Bezirks- und Objekthierarchie sowie fokussierte Details auf derselben read-only Map-Projection. C6 bleibt abhängig, bis ein echter kanonischer Rundenproduzent existiert.
