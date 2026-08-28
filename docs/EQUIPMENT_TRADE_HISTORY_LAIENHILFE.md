# Equipment-Handelsverlauf – einfache Erklärung

## Was ist sicher gespeichert?

Bei jedem bestätigten Kauf oder Verkauf merkt sich das Spiel bereits:

- welches Equipment betroffen war,
- wie viele Stücke gehandelt wurden,
- zu welchem tatsächlichen Stückpreis gehandelt wurde,
- ob Geld abgegangen oder hinzugekommen ist,
- welche bestätigte Transaktion dazu gehört.

Darum kann eine einfache Liste wie „gekauft / verkauft / Menge / Preis“ angezeigt werden, ohne etwas neu auszurechnen oder zu erfinden.

## Warum zeigt das Spiel noch keinen Gewinn oder Verlust?

Wenn du dasselbe Equipment mehrmals zu unterschiedlichen Preisen kaufst, ist noch nicht festgelegt, **welches gekaufte Stück** bei einem späteren Verkauf als Grundlage zählt.

Beispiel:

- Kauf 1: 450,00 €
- Kauf 2: 475,00 €
- Verkauf: 500,00 €

Je nachdem, welcher Kauf zum Verkauf gehört, wären 50,00 € oder 25,00 € Gewinn möglich. Das Spiel darf hier nicht raten.

## Was ist als Nächstes sicher möglich?

Der Audit aus PR #236 bestätigt: Der nächste kleine Ausbau darf ausschließlich die bereits bestätigten Käufe und Verkäufe **read-only** im bestehenden Economy-Bereich anzeigen. Sinnvoll sind Aktion, Equipment, Menge und tatsächlicher Stückpreis.

Die Liste darf nichts am Markt verändern und keinen Gewinn ausdenken. Eine spätere Gewinnanzeige braucht zuerst eine eindeutige Kostenbasisregel in der Fachlogik.

## Was bedeutet das für dich?

Du bekommst damit als nächsten sinnvollen Ausbau mehr Überblick über deine echten Handelsaktionen, ohne dass die Oberfläche aus alten Preisen neue Spielregeln erfindet.

**Merksatz:** Historie anzeigen = sicher. Kostenbasis raten = verboten.
