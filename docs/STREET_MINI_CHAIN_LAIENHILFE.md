# Street-Mini-Ketten – einfach erklärt

## Worum geht es?

Bisher kann auf der Straße eine einzelne Begegnung passieren: jemand grüßt dich, du bekommst einen Tipp, findest eine Abkürzung oder gerätst in Regen. Der geplante Ausbau soll manche **seltenen** Begegnungen später noch einmal erzählerisch aufgreifen können.

Ein Beispiel, das noch **nicht** ins Spiel eingebaut ist:

**Kabeltipp am Bauzaun → später hörst du denselben Tipp aus einem anderen Mund → „Der Tipp macht die Runde.“**

So soll sich Berlin erinnern, ohne dir heimlich Geld, Ruf oder andere Vorteile zu schenken.

## Was ist heute schon sicher?

Eine bestätigte Straßenbegegnung wird im Spielstand eindeutig gespeichert. Ein Neuladen oder Wiederholen würfelt dieselbe Begegnung nicht noch einmal neu aus.

Das ist eine gute Grundlage für spätere kleine Geschichten.

## Warum wird die Folgegeschichte nicht sofort eingebaut?

Bei der Prüfung wurde eine wichtige Grenze gefunden: Der Street-Record besitzt eine sichere Charakter-Zuordnung über seinen bestätigten `entity_id`-Wert. Ein zusätzliches technisches Feld namens `character_id` kann derzeit aber davon abweichen.

Für die heutigen Straßenbegegnungen ist das kein Problem. Für eine neue Ursache→Folge-Kette muss jedoch vorher eindeutig feststehen, **zu welchem Charakter eine Erinnerung gehört**.

Darum gilt:

**Erst Vertrag absichern → dann Story bauen.**

## Was kommt als Nächstes?

Der nächste technische Schritt soll einen kleinen Street-Kettenvertrag festlegen. Er muss sicherstellen, dass:

- Ursache und Folge zum selben bestätigten Charakter gehören,
- dieselbe Folge nicht doppelt gespeichert wird,
- ein Reload keine neue Story auswürfelt,
- höchstens eine Folge pro bestätigtem Straßenlauf entsteht,
- die Oberfläche nur bereits bestätigte Geschichten anzeigt.

## Was bleibt unverändert?

- deine bisherigen 16 Street-Begegnungen,
- die vier Ansätze **Ausgeglichen, Runterkommen, Kontakte und Scout**,
- deren Balance und Effekte,
- dein Spielstand,
- die vorhandene Ereignis-Timeline.

Der aktuelle Audit fügt **keine neue spielbare Street-Story** hinzu. Er sorgt nur dafür, dass der spätere Ausbau nicht auf einer unsauberen Abkürzung basiert.
