# Hilfe im Control Deck – kurz erklärt

## Worum geht es?

Das Control Deck soll dir beim Spielen sagen, **was du gerade siehst, was du als Nächstes tun kannst und was deine Entscheidung verändert**. Du musst keine internen Programmnamen verstehen.

## Drei wichtige Hinweise

- **Bestätigt:** Das Spiel hat das Ergebnis bereits angenommen. Es ist keine bloße Vorschau.
- **Nur Anzeige:** Du kannst hier Informationen ansehen oder filtern. Dadurch ändern sich keine Spielwerte.
- **Sofort gespeichert:** Eine bestätigte Aktion landet direkt im Spielverlauf. Ein zusätzlicher Checkpoint ist nur ein weiterer Wiederherstellungspunkt.

## „Nächster Schritt“ oben in der Leiste

Die kleine Anzeige oben hilft dir nur mit bereits sicheren Informationen:

- Beim ersten Start zeigt sie **„Neues Spiel anlegen“**.
- Gibt die Runtime eine Event-Aktion frei, zeigt und markiert sie genau diese Aktion.
- Ist das Event blockiert, zeigt sie den bereits vom Spiel bestätigten Blockiergrund in Klartext.
- Gibt es gerade keine freigegebene normale Event-Aktion, erfindet die Oberfläche keine Empfehlung.

Wichtig: Die Anzeige berechnet **keine eigene Strategie** aus Energie, Geld, Marktpreisen oder anderen Werten. Sie entscheidet auch nichts automatisch für dich.

## Die wichtigsten Bereiche

**Straße:** Wähle einen Stil für deine Runde. Er verschiebt Chancen, verspricht aber kein bestimmtes Ereignis.

**Bezirkslage:** Zeigt dir Heat, Prestige, Polizeidruck und Szeneaktivität. Die Anzeige selbst verändert nichts.

**Was bisher passiert ist:** Deine bestätigten Erlebnisse stehen hier in zeitlicher Reihenfolge. „Folge von“ erscheint nur, wenn das Spiel den Zusammenhang wirklich bestätigt hat.

**Berlin Ops Map:** Überblick über Bezirke, Orte und dein Eigentum. Kaufen und Ausbauen machst du im Bereich „Orte & Ausbau“.

**Orte & Ausbau:** Hier kaufst du Orte und verbesserst vorhandene Ausbauplätze bis Stufe 3. Preis und mögliche Stufe werden vom Spiel vorgegeben.

**Hall of Tribute:** Zeigt bestätigte Ranglistenwerte. Ohne echte bestätigte Konkurrenz erfindet das Spiel keine Gegner.

**Event-Steuerung:** Zeigt dir die nächste erlaubte Aktion für dein vorbereitetes Event. Ist etwas blockiert, steht der Grund direkt darunter und jetzt zusätzlich kompakt oben in der Leiste.

**Krise:** Bekannte Folgen stehen vor der Entscheidung sichtbar da. Erst dein Klick löst die gewählte Antwort aus.

**Spielstand:** Bestätigte Aktionen werden sofort gespeichert. „Checkpoint speichern“ legt zusätzlich einen Wiederherstellungspunkt an.

**Client-Protokoll:** Nur für Fehlersuche und Transparenz. Zum normalen Spielen musst du diesen Bereich nicht verstehen.

## Technische ID

Die technische ID ist die eindeutige interne Kennung deines Charakters. Sie ist vor allem für Fehlerberichte nützlich. Für normales Spielen musst du sie weder merken noch eingeben.

## Merksatz

**Erst lesen, dann wählen: Das Spiel zeigt dir bekannte Folgen vor der Entscheidung und bestätigt das echte Ergebnis danach.**

## Spätere Verbesserungsidee

Eine echte Empfehlung wie „erst erholen“ oder „jetzt handeln“ sollte erst dann ergänzt werden, wenn die Runtime dafür einen eigenen bestätigten Empfehlungshinweis liefert. Solange dieser Vertrag fehlt, bleibt die Oberfläche absichtlich bei sicheren Status- und Blockerinformationen und erfindet keine Strategie im Browser.
