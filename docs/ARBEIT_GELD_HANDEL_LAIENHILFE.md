# Arbeit, Geld und Handel – einfache Spielhilfe

## Der kurze Weg

1. **Job wählen.** Vergleiche Stundenlohn, Energie und Stress. Ein höherer Gesamtlohn ist nicht automatisch der beste Job.
2. **Auf Erschöpfung achten.** Bei wenig Energie kann der tatsächlich bestätigte Lohn sinken. Die Jobkarte zeigt dir deshalb den aktuellen Betrag zusätzlich zum normalen Lohn.
3. **Bargeld und Bank trennen.** Joblohn landet als persönliches Bargeld. Du kannst Geld auf die Bank legen oder wieder abheben. Bankbewegungen ändern kein Event-Budget.
4. **Equipment handeln.** Im Equipment-Bereich siehst du den aktuell bestätigten Marktpreis. Du kannst kaufen und freien, nicht reservierten Bestand wieder verkaufen.
5. **Reservierungen verstehen.** Reservierte Ausrüstung ist für dein Event gebunden. Sie kann nicht gleichzeitig verkauft werden. Mit **FREIGEBEN** löst du die Reservierung zuerst.
6. **Erst dann investieren.** Orte, Ausbauten und Eventkosten sind größere Ausgaben. Ein Geldpolster verhindert, dass du dich durch einen einzelnen Kauf festfährst.

## Was bedeutet der Marktpreis?

Der Markt läuft in einem kleinen deterministischen Preiszyklus. Das bedeutet: Der angezeigte Preis wird nicht im Browser erfunden und nicht durch deine Rechneruhr bestimmt. Kauf und Verkauf verwenden dieselbe bestätigte Preisregel aus dem Spiel.

- **Markt über Basis:** aktuell teurer als der normale Grundpreis.
- **Markt unter Basis:** aktuell günstiger als der Grundpreis.
- **Auf Basispreis:** aktuell keine Abweichung.

Ein Kauf oder Verkauf kann den Marktstand weiterschalten. Darum kann der nächste Preis anders aussehen.

## Welcher Job ist gut?

Es gibt nicht nur eine richtige Antwort:

- **Stundenlohn** zeigt, wie viel der normale Lohn pro Stunde entspricht.
- **Jetzt** zeigt den aktuell für deinen Energiezustand erwarteten Lohn.
- **Energie** zeigt deine körperliche Belastung.
- **Stress** zeigt die mentale Belastung.

Wenn zwei Jobs ähnlich bezahlen, kann der Job mit weniger Energie- oder Stresskosten langfristig sinnvoller sein. Wenn du schnell Bargeld brauchst, kann dagegen ein belastenderer Job trotzdem die bessere Entscheidung sein.

## Warum gibt es Kaufen, Verkaufen, Reservieren und Freigeben?

- **KAUFEN:** ein Stück zum aktuell bestätigten Marktpreis erwerben.
- **VERKAUFEN:** ein freies eigenes Stück zum aktuell bestätigten Marktpreis abgeben.
- **RESERVIEREN:** ein eigenes Stück für das Event binden.
- **FREIGEBEN:** eine Reservierung lösen, ohne das Stück zu verkaufen.

Die Oberfläche entscheidet keine Preise und keine Bestände. Sie sendet nur deine Auswahl; die Runtime prüft den bestätigten Zustand erneut.

## Merksatz

**Arbeiten → Geld sichern → Markt vergleichen → nur freien Bestand handeln → erst danach groß investieren.**

## Spätere Verbesserungsidee

Als nächste Economy-Ausbaustufe bietet sich ein eigener **Handelsverlauf** an: letzte bestätigte Kauf-/Verkaufspreise je Equipment, ohne neue Marktengine. Dadurch könnten Spieler erkennen, ob sie ein Stück gerade mit Gewinn oder Verlust verkaufen würden, während die bestehende Economy-Autorität unverändert bleibt.
