# Street-Mini-Ketten – einfach erklärt

## Worum geht es?

Auf der Straße können einzelne Begegnungen passieren: jemand grüßt dich, du bekommst einen Tipp, findest eine Abkürzung oder gerätst in Regen. Einige seltene Begegnungen dürfen nun später noch einmal **erzählerisch nachhallen**.

Die erste spielbare Mini-Kette ist:

**Kabeltipp am Bauzaun → später hörst du denselben Tipp aus einem anderen Mund → „Der Tipp macht die Runde.“**

So wirkt Berlin etwas erinnerungsfähiger, ohne dir heimlich Geld, Ruf, Energie oder andere Vorteile zu schenken.

## Wie funktioniert die erste Geschichte?

1. Ein bestätigter Street-Walk ergibt **Kabeltipp am Bauzaun**.
2. Der Tipp wird als normale, bestätigte Street-Begegnung gespeichert.
3. Erst bei einem **späteren bestätigten Street-Walk desselben Charakters** darf der Nachhall entstehen.
4. Die Folge heißt **Der Tipp macht die Runde**.
5. Ursache und Folge werden fest miteinander verknüpft. Ein Neuladen erzeugt keine zweite Kopie.

Der spätere Street-Walk bleibt dabei eine ganz normale Straßenrunde. Die Folgegeschichte verändert dessen Auswahl, Balance oder Effekte nicht.

## Was schützt vor Doppelungen und falschen Zuordnungen?

Der bestätigte Charakter des ursprünglichen Street-Records ist die einzige maßgebliche Zuordnung. Falls ein zusätzlich gespeicherter Charakterwert dazu widerspricht, wird die Folge **nicht** erzeugt. Das System bricht an dieser Stelle sicher ab (fail-closed), statt die Geschichte dem falschen Charakter zuzuschreiben.

Außerdem gilt:

- dieselbe Ursache erzeugt dieselbe eindeutige Folge-ID,
- ein Retry oder Reload schreibt keine zweite Folge,
- pro bestätigtem späteren Street-Walk entsteht höchstens eine Folge,
- Ursache und Folge werden im selben sicheren Speichervorgang des späteren Walks bestätigt,
- der Browser darf keine Folge selbst erfinden oder schreiben.

## Was bleibt unverändert?

- die bisherigen 16 Street-Begegnungen,
- die vier Ansätze **Ausgeglichen, Runterkommen, Kontakte und Scout**,
- deren Gewichte und Balance,
- bestehende Street-Effekte auf Energie, Stress und Ruf,
- die vorhandene Persistenz- und Journal-Architektur.

Die neue Folge besitzt bewusst **keine Gameplay-Effekte**. Sie ist Erinnerung und Atmosphäre, keine versteckte Belohnung.

## Noch nicht enthalten

Die Folge ist zunächst ein bestätigtes Journal-Ereignis. Eine eigene Darstellung dieses Street-Nachhalls in Timeline oder Control Deck wird in diesem kleinen Schritt nicht ergänzt. Dafür soll zuerst der Runtime-Pfad stabil bleiben und anschließend dieselbe vorhandene read-only Projection genutzt werden, statt eine zweite Anzeige- oder Storyarchitektur zu bauen.

## Sinnvolle nächste Erweiterung

Als nächster Story-Ausbau eignet sich nach einer read-only Sichtbarkeitsprüfung eine **zweite, anders gefärbte Street-Mini-Kette**. Sie sollte wieder einen vorhandenen Parent nutzen, balance-neutral bleiben und denselben Vertrag verwenden. So wächst die Stadtgeschichte in kleinen, prüfbaren Schritten statt durch ein neues Storysystem.
