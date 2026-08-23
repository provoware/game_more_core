# Laienhilfe – Bankkonto & Sparen

## Was ist jetzt möglich?

Dein persönliches Geld besteht aus **Bargeld** und **Bankguthaben**. Beides gehört zum selben persönlichen Finance-State und zum selben bestätigten Ledger.

Seit 0.8.8-D kannst du Geld zwischen Bargeld und Bank verschieben. D2 ergänzt darauf aufbauend Sparzinsen.

## Wie funktionieren die Zinsen?

Eine Zinsbuchung passiert **nicht einfach, weil auf deinem Computer Zeit vergangen ist**. Die Runtime muss zuerst eine gültige, bereits bestätigte Finance-Periode erhalten.

Für jede bestätigte Periode gelten aktuell **1 % Zins** auf das gerade bestätigte Bankguthaben.

Beispiel:

- Start: 100,00 € auf der Bank
- erste bestätigte Periode: +1,00 € → 101,00 €
- zweite bestätigte Periode: +1,01 € → 102,01 €

Damit entsteht echter Zinseszins, ohne eine zweite Finanzlogik einzuführen.

## Warum kann eine Periode nicht doppelt zahlen?

Jede bestätigte Finance-Periode besitzt eine stabile ID und einen fortlaufenden Finance-Tick. Derselbe Tick darf nur einmal verarbeitet werden.

Wird dieselbe Periode wegen Retry oder Neustart erneut geliefert, erkennt die Runtime die bereits bestätigte Buchung und zahlt **kein zweites Mal**.

## Was passiert bei 0 € Bankguthaben?

Auch eine Periode mit 0 Cent Zins wird als verarbeitet markiert. Das ist wichtig: Du kannst später nicht Geld einzahlen und eine alte, bereits vergangene Periode rückwirkend noch einmal verzinsen lassen.

## Kann der Browser Zinsen auslösen?

Nein.

Der Browser darf weder:

- eine Finance-Periode bestätigen,
- einen Finance-Tick erfinden,
- einen Zinsbetrag vorgeben,
- Rechnerzeit als Auslöser verwenden.

D2 besitzt außerdem bewusst **keinen eigenen Zeitproduzenten**. Es verarbeitet nur einen bereits autorisierten internen Periodentrigger.

## Ist das Eventbudget betroffen?

Nein. Persönliches Bargeld und Bankguthaben bleiben fachlich getrennt vom Eventbudget.

## Was kommt als Nächstes?

Als nächster unabhängiger Slice ist **0.8.8-E – Control Deck Focus** vorgesehen: weniger doppelte Informationen, lokal maximierbare Arbeitsbereiche und deutlichere nächste Aktionen. Der Round-Authority-Harness C6 bleibt abhängig, bis ein echter kanonischer Rundenproduzent vorhanden ist.
