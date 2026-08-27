# Street-Mini-Ketten – einfach erklärt

## Worum geht es?

Auf der Straße können einzelne Begegnungen passieren: jemand grüßt dich, du bekommst einen Tipp, findest eine Abkürzung oder verlierst etwas. Einige seltene Begegnungen dürfen später noch einmal **erzählerisch nachhallen**.

Aktuell gibt es zwei spielbare Mini-Ketten:

1. **Kabeltipp am Bauzaun → „Der Tipp macht die Runde.“**
2. **Ein Handschuh weniger → „Der Handschuh wartet noch.“**

Beide Geschichten machen Berlin erinnerungsfähiger, ohne dir heimlich Geld, Ruf, Energie, Inventar oder andere Vorteile zu schenken.

## Wie funktionieren die Geschichten?

1. Ein bestätigter Street-Walk erzeugt eine passende seltene Begegnung.
2. Diese Begegnung wird als normales, bestätigtes Street-Ereignis gespeichert.
3. Erst bei einem **späteren bestätigten Street-Walk desselben Charakters** darf der Nachhall entstehen.
4. Ursache und Folge werden fest miteinander verknüpft.
5. Ein Retry oder Neuladen erzeugt keine zweite Kopie.
6. Die vorhandene Timeline zeigt die bestätigte Folge read-only und – nur bei eindeutig passendem Parent – **„Folge von: …“**.

Der spätere Street-Walk bleibt dabei eine normale Straßenrunde. Die Folgegeschichte verändert weder Auswahl noch Balance noch Effekte.

## Beispiel 1 – der Kabeltipp

Du erhältst zuerst **Kabeltipp am Bauzaun**. Bei einem späteren Street-Walk kann daraus **Der Tipp macht die Runde** entstehen. Die Timeline zeigt dann zusätzlich **„Folge von: Kabeltipp am Bauzaun“**.

## Beispiel 2 – der verlorene Handschuh

Du bemerkst zuerst **Ein Handschuh weniger**. Bei einem späteren Street-Walk kann daraus **Der Handschuh wartet noch** entstehen: Der Handschuh hängt sichtbar über einem Bauzaun, weil ihn offenbar jemand aufgehoben hat.

Wichtig: Das Spiel verbucht daraus **keinen Gegenstand und keinen Bonus**. Der Moment ist reine Erinnerung und Atmosphäre. Die Timeline zeigt bei belegter Ursache **„Folge von: Ein Handschuh weniger“**.

## Was schützt vor Doppelungen und falschen Zuordnungen?

Der bestätigte Charakter des ursprünglichen Street-Records ist die maßgebliche Zuordnung. Falls Ursache und Folge nicht zum selben bestätigten Charakter gehören, zeigt die Timeline **keine erfundene Ursache** an. Eine falsche `causation_id`, ein fehlender Parent oder eine zeitlich unplausible Reihenfolge erzeugen ebenfalls kein „Folge von“.

Außerdem gilt:

- dieselbe Ursache erzeugt dieselbe eindeutige Folge-ID,
- ein Retry oder Reload schreibt keine zweite Folge,
- pro bestätigtem späteren Street-Walk entsteht höchstens eine Folge,
- Ursache und Folge werden im selben sicheren Speichervorgang des späteren Walks bestätigt,
- die Timeline liest nur bereits bestätigte Journal-Ereignisse,
- der Browser darf keine Folge selbst erfinden oder schreiben.

## Was bleibt unverändert?

- die bisherigen 16 Street-Begegnungen,
- die vier Ansätze **Ausgeglichen, Runterkommen, Kontakte und Scout**,
- deren Gewichte und Balance,
- bestehende Street-Effekte auf Energie, Stress und Ruf,
- die vorhandene Persistenz- und Journal-Architektur,
- die vorhandene Timeline als einzige Presentation-Projection für diese Ereignisse.

Die Folgen besitzen bewusst **keine Gameplay-Effekte**. Sie sind Erinnerung und Atmosphäre, keine versteckte Belohnung.

## Wie wird das technisch wirklich geprüft?

Die Qualitätsprüfung baut die Geschichten nicht künstlich im Browser nach. Sie erzeugt die Parent-Ereignisse und ihre späteren Nachhalle über den normalen A4-Spielpfad, speichert alles im echten Test-Spielstand und wiederholt die auslösenden Street-Walks als Retry. Dabei muss jede Folge genau **einmal** erhalten bleiben.

Danach wird derselbe gespeicherte Spielstand geschlossen und über den normalen lokalen A4-Server neu geöffnet. Erst dann wird geprüft, ob `/api/state` und ein echter Chromium-Browser beide Geschichten samt **„Folge von: …“** korrekt anzeigen. Damit ist die Kette Runtime → Journal/Persistenz → Reload → API → echtes Browser-DOM abgedeckt.

## Sinnvolle nächste Erweiterung

Vor einer dritten Street-Micro-Story sollte zuerst geprüft werden, ob die vorhandenen Nachhalle dramaturgisch zu ähnlich wirken. Sinnvoll wäre als nächster Content-Schritt ein anderer Ton – zum Beispiel sozial, räumlich oder leicht unheimlich – aber weiterhin selten, balance-neutral und auf demselben Vertrag. So wächst die Stadtgeschichte ohne neues Storysystem.
