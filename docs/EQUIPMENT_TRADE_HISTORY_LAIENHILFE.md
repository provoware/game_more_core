# Equipment-Handelsverlauf – einfache Erklärung

## Was ist jetzt sichtbar?

Im bestehenden Bereich **Equipment & Economy** erscheint unter dem Markt eine kleine Liste **„Letzte Käufe & Verkäufe“**.

Sie zeigt höchstens die letzten acht wirksamen bestätigten Handelsbuchungen. Pro Eintrag siehst du:

- **GEKAUFT** oder **VERKAUFT**,
- das betroffene Equipment,
- die gehandelte Menge,
- den tatsächlichen Stückpreis dieser bestätigten Buchung,
- die Buchungsnummer als einfache Reihenfolge im vorhandenen Ledger.

Die Liste ist **nur Anzeige**. Sie startet keinen Kauf, keinen Verkauf und verändert weder Markt noch Inventar.

## Woher kommen die Angaben?

Das Spiel verwendet ausschließlich Daten, die der vorhandene Economy-Ledger bereits nach einer bestätigten Transaktion speichert: Equipment-ID, Menge und tatsächlichen Ausführungspreis. Die Anzeige berechnet keinen historischen Preis nach und verwendet nicht den heutigen Marktpreis als Ersatz.

## Was ist mit rückgängig gemachten Geschäften?

Eine technische Rückbuchung kann ebenfalls wie ein Kauf oder Verkauf im Ledger stehen. Das Feld `compensates` zeigt, dass diese Buchung eine frühere Transaktion rückgängig macht.

Damit ein rückgängig gemachter Vorgang nicht wie zwei echte Handelsentscheidungen aussieht, blendet die normale Handelsliste **beide Seiten dieses Paares** aus: die ursprüngliche Buchung und ihre bestätigte Gegenbuchung.

`compensates` sagt dabei nur: **Diese Buchung macht eine frühere Buchung rückgängig.** Es sagt nicht, welcher Einkauf später die Kostenbasis eines echten Verkaufs sein soll.

## Warum zeigt das Spiel keinen Gewinn oder Verlust?

Wenn du dasselbe Equipment mehrmals zu unterschiedlichen Preisen kaufst, ist noch nicht festgelegt, **welches gekaufte Stück** bei einem späteren Verkauf als Grundlage zählt.

Beispiel:

- Kauf 1: 450,00 €
- Kauf 2: 475,00 €
- Verkauf: 500,00 €

Je nach Zuordnung wären 50,00 € oder 25,00 € Gewinn möglich. Das Spiel darf hier nicht raten. Deshalb zeigt dieser Ausbau bewusst nur bestätigte Handelsfakten und **keine erfundene Rendite**.

## Warum nur acht Einträge?

Die Liste soll im Control Deck schnell lesbar bleiben und keine zweite Kontoauszugs- oder Portfoliooberfläche werden. Die vollständigen Ledgerdaten bleiben unverändert im bestehenden Spielstand; die Projection wählt nur die jüngsten acht wirksamen Käufe/Verkäufe zur Anzeige aus.

## Später sinnvoll prüfen

Als nächster Qualitätsausbau kann ein echter Browser-E2E beweisen, dass leere Historie, reale Käufe/Verkäufe und kompensierte Paare auch im gerenderten Control Deck korrekt erscheinen. Eine Gewinn-/Verlustanzeige bleibt davon getrennt und braucht zuerst einen eigenen Kostenbasisvertrag in der Fachlogik.

**Merksatz:** Historie anzeigen = bestätigte Fakten sichtbar machen. Gewinn raten oder Rückbuchungen als echte Trades zählen = verboten.
