# Equipment-Handelsverlauf – Contract Audit

## Ziel

Prüfen, ob der vorhandene Economy-Ledger bereits genug bestätigte Daten für einen read-only Handelsverlauf und eine belastbare Gewinn-/Verlust-Hilfe enthält.

## Befund

Der bestehende Ledger speichert pro bestätigter Economy-Transaktion:

- `transaction_id`
- `kind`
- `item_id`
- `quantity`
- `unit_price_cents`
- `budget_delta_cents`
- `compensates`

Damit ist eine **read-only Transaktionshistorie** fachlich tragfähig: Ein Kauf oder Verkauf kann mit tatsächlichem Ausführungspreis, Menge und Item eindeutig aus dem bestätigten Ledger dargestellt werden.

## Wichtige Grenze

Eine exakte realisierte Gewinn-/Verlustanzeige ist derzeit **nicht** eindeutig ableitbar.

Beispiel: Dasselbe Equipment wird einmal für 450,00 € und später für 475,00 € gekauft. Danach wird ein Stück für 500,00 € verkauft. Der Ledger sagt nicht, welches Kauflos beim Verkauf als Kostenbasis verwendet wurde. Je nach Zuordnung wären 50,00 € oder 25,00 € realisierter Gewinn korrekt.

Der aktuelle Vertrag besitzt dafür weder FIFO/LIFO-Regel noch gewichteten Einstand, Kauflos-ID oder allgemeine Sell→Buy-Zuordnung. `compensates` ist ausschließlich für eine explizite Rückbuchung einer bestätigten Kauf-/Verkaufstransaktion gedacht und darf nicht als allgemeine Kostenbasis interpretiert werden.

## Entscheidung

- **Freigegeben für späteren kleinen Presentation-Slice:** bestätigte Kauf-/Verkaufshistorie read-only anzeigen.
- **Nicht freigegeben:** realisierten Gewinn/Verlust aus historischen Käufen und Verkäufen berechnen.
- **Verboten:** Anschaffungskosten aus aktuellem Marktpreis zurückrechnen oder eine stille FIFO-/LIFO-Regel im Browser erfinden.

## Kleinster sinnvoller Folgeslice

Eine vorhandene Economy-Fläche darf die letzten bestätigten `buy`-/`sell`-Buchungen mit Item, Menge und tatsächlichem Stückpreis zeigen. Gewinn/Verlust bleibt ausgeblendet, bis ein eigener fachlicher Kostenbasisvertrag beschlossen und Runtime-seitig eindeutig getragen wird.

## Nicht-Ziele dieses Audits

Keine Runtime-, Markt-, Ledger-, Save-, Journal-, Projection- oder Browser-Produktlogik wird verändert. Keine neue Portfolioengine und keine nachträgliche Migration bestehender Buchungen.
