# Laienhilfe – Street-Balance-Audit

## Was wird hier geprüft?

Die Straßenbegegnungen wurden nicht neu ausgewürfelt und auch nicht verändert. Diese Iteration prüft nur automatisch, ob der bestehende Katalog weiterhin nachvollziehbar ausbalanciert ist.

Es gibt weiterhin 16 Begegnungen und vier Spielweisen:

- **Ausgeglichen** (`balanced`)
- **Erholung** (`recovery`)
- **Netzwerk** (`network`)
- **Erkundung** (`scout`)

## Sind die vier Spielweisen wirklich verschieden?

Ja. Der Audit vergleicht die vollständigen 16 Gewichte miteinander. Als Abstand wird die sogenannte **Total-Variation-Distanz** benutzt. Vereinfacht gesagt: Sie zeigt, wie viel Wahrscheinlichkeit zwischen zwei Profilen umverteilt wurde.

Die gemessenen Abstände sind:

| Vergleich | Abstand |
|---|---:|
| Ausgeglichen ↔ Erholung | 17 % |
| Ausgeglichen ↔ Netzwerk | 27 % |
| Ausgeglichen ↔ Erkundung | 30 % |
| Erholung ↔ Netzwerk | 35 % |
| Erholung ↔ Erkundung | 40 % |
| Netzwerk ↔ Erkundung | 30 % |

Die kleinste Distanz liegt damit bei 17 %. Die vier Ansätze sind also nicht nur anders benannt, sondern mathematisch unterschiedlich gewichtet.

## Kann ein einzelnes Ereignis alles dominieren?

Nein. In keinem der vier Ansätze besitzt eine einzelne Begegnung mehr als **20 %** Auswahlgewicht.

Das heißt nicht, dass alle Begegnungen gleich wahrscheinlich sind. Ein Ansatz darf bestimmte Situationen deutlich bevorzugen. Aber keine einzelne Begegnung nimmt mehr als ein Fünftel des gesamten Gewichts ein.

## Wie unterscheiden sich positive und negative Begegnungen?

| Ansatz | Neutral | Positiv | Negativ |
|---|---:|---:|---:|
| Ausgeglichen | 25 % | 60 % | 15 % |
| Erholung | 30 % | 55 % | 15 % |
| Netzwerk | 15 % | 70 % | 15 % |
| Erkundung | 15 % | 60 % | 25 % |

Damit bleibt jeder Ansatz überwiegend positiv, aber mit erkennbarem Schwerpunkt. Netzwerk ist am stärksten auf positive Kontakte gewichtet. Erkundung trägt das höchste Risiko negativer Begegnungen. Erholung verschiebt mehr Gewicht in neutrale beziehungsweise ruhigere Situationen.

## Was bedeutet „alle 100 Buckets prüfen“?

Die Street-Auswahl arbeitet mit einem deterministischen Wert zwischen 0 und 99. Der Audit spielt nicht 100 echte Straßenrunden. Er prüft mathematisch jede mögliche Auswahlposition des Gewichtsrasters.

Wenn eine Begegnung laut Manifest 5 Gewichtspunkte besitzt, muss sie exakt fünf dieser 100 Positionen erhalten. Der Test zählt deshalb für jeden Ansatz alle 100 Positionen durch und vergleicht das Ergebnis mit dem Manifest.

Dadurch werden typische Grenzfehler wie „ein Wert zu viel“ oder „ein Wert zu wenig“ automatisch erkannt.

## Wird dadurch Gameplay verändert?

Nein.

- keine neuen Begegnungen
- keine veränderten Gewichte
- keine Telemetrie
- kein Tracking des Spielers
- kein neuer Zufall
- keine Systemzeit
- keine Save- oder Journaländerung
- keine neue Runtime-Mechanik

Der Audit ist ausschließlich ein automatischer Qualitätscheck für den bestehenden Street-Katalog.

## Warum ist das hilfreich?

Spätere Erweiterungen können versehentlich ein Gewicht verschieben oder eine Begegnung zu stark machen. Der Audit macht solche Änderungen bereits im Testlauf sichtbar, bevor sie gemergt werden.

## Spätere sinnvolle Erweiterung

Wenn der Street-Katalog später erneut wächst, kann derselbe Audit zusätzlich Erwartungswerte der kleinen Energie-, Stress- und Rufeffekte pro Ansatz vergleichen. Das sollte weiterhin nur ein Prüfwerkzeug bleiben und keine Telemetrie oder automatische Live-Balance erzeugen.
