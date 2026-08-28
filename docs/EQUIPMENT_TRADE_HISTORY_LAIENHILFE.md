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

## Wie wird das automatisch im echten Browser geprüft?

Die Release-Prüfung startet denselben lokalen A4-Server und einen echten Chromium-Browser in drei klar getrennten Zuständen:

1. Zuerst enthält der bestätigte Testspielstand nur ein rückgängig gemachtes Kauf-/Gegenbuchungspaar. Die sichtbare Historie muss deshalb eindeutig **leer** bleiben.
2. Danach werden über die echte Runtime ein Kauf und ein Verkauf bestätigt. Im Browser müssen genau diese wirksamen Trades als **GEKAUFT** und **VERKAUFT** mit dem gespeicherten Ausführungspreis erscheinen.
3. Für den Dichte-/Lesbarkeitscheck wird die echte Runtime-Historie bis zum vorgesehenen Maximum von **acht wirksamen Trades** gefüllt. Dann werden **Große Schrift**, **Hoher Kontrast** und das kleine 760×680-Fenster gemeinsam aktiviert. Zusätzlich ersetzt der Test ausschließlich zu Anzeigezwecken einen sichtbaren Equipment-Namen durch einen absichtlich langen Testnamen. Dadurch kann geprüft werden, ob Text sauber umbrechen kann, ohne Fachwerte oder Identifikatoren zu verändern.

Im Dichtefall werden die acht Zeilen, ihre Textbereiche und die gesamte Historie auf sichtbare Grenzen und horizontale Überbreite geprüft. Aktionsart, Mengen- und Preiszeile müssen weiterhin vorhanden und lesbar strukturiert bleiben. Der Browser-Test selbst sendet keine Handelsbefehle und berechnet weder Kostenbasis noch Gewinn oder Verlust.

## Was ändert dieser Dichte-Audit am Spiel?

Zunächst **gar nichts an der Darstellung**. Der Audit soll zuerst beweisen, ob überhaupt ein reproduzierbares Problem existiert. Ein CSS- oder Layout-Fix ist nur dann sinnvoll, wenn der echte Browserlauf einen konkreten Fehler zeigt. So bleibt das bestehende Design unangetastet, solange es die anspruchsvolle Anzeige bereits korrekt beherrscht.

## Später sinnvoll prüfen

Falls der Dichte-Audit grün bleibt, ist kein kosmetischer Patch nötig. Eine spätere Gewinn-/Verlustanzeige bleibt davon getrennt und braucht zuerst einen eigenen Kostenbasisvertrag in der Fachlogik.

**Merksatz:** Historie anzeigen = bestätigte Fakten sichtbar machen. Gewinn raten, Rückbuchungen als echte Trades zählen oder Layout ohne Befund ändern = verboten.
