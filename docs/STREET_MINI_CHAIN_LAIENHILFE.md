# Street-Mini-Ketten – einfach erklärt

## Worum geht es?

Auf der Straße können einzelne Begegnungen passieren: jemand grüßt dich, du bekommst einen Tipp, findest eine Abkürzung oder gerätst in Regen. Einige seltene Begegnungen dürfen später noch einmal **erzählerisch nachhallen**.

Die erste spielbare Mini-Kette ist:

**Kabeltipp am Bauzaun → später hörst du denselben Tipp aus einem anderen Mund → „Der Tipp macht die Runde.“**

So wirkt Berlin etwas erinnerungsfähiger, ohne dir heimlich Geld, Ruf, Energie oder andere Vorteile zu schenken.

## Wie funktioniert die erste Geschichte?

1. Ein bestätigter Street-Walk ergibt **Kabeltipp am Bauzaun**.
2. Der Tipp wird als normale, bestätigte Street-Begegnung gespeichert.
3. Erst bei einem **späteren bestätigten Street-Walk desselben Charakters** darf der Nachhall entstehen.
4. Die Folge heißt **Der Tipp macht die Runde**.
5. Ursache und Folge werden fest miteinander verknüpft. Ein Neuladen erzeugt keine zweite Kopie.
6. Die vorhandene Timeline kann die bestätigte Folge nun read-only anzeigen und – nur bei eindeutig passendem Parent – **„Folge von: Kabeltipp am Bauzaun“** ableiten.

Der spätere Street-Walk bleibt dabei eine ganz normale Straßenrunde. Die Folgegeschichte verändert dessen Auswahl, Balance oder Effekte nicht.

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

Die neue Folge besitzt bewusst **keine Gameplay-Effekte**. Sie ist Erinnerung und Atmosphäre, keine versteckte Belohnung.

## Was ist jetzt sichtbar?

Ein bestätigtes `street.followup_resolved` kann in derselben bestehenden Story-Timeline wie normale Street-Ereignisse erscheinen. Ist der bestätigte Parent vorhanden, älter und demselben Charakter zugeordnet, liefert die Projection zusätzlich die belegte Ursache. Fehlt einer dieser Nachweise, bleibt die Folge höchstens als bestätigtes Einzelereignis sichtbar – ohne erfundene Kausalität.

## Sinnvolle nächste Erweiterung

Als nächster Story-Ausbau eignet sich eine **zweite, anders gefärbte Street-Mini-Kette**. Sie sollte wieder einen vorhandenen Parent nutzen, balance-neutral bleiben und denselben Vertrag verwenden. So wächst die Stadtgeschichte in kleinen, prüfbaren Schritten statt durch ein neues Storysystem.
