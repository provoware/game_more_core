# Street Encounters 0.8.5-C – kleine Zufälle unterwegs

## Für Spieler

Im lokalen A4-Client gibt es nach dem ersten Spielstart den Bereich **KLEINE STRASSENRUNDE**.

Ein Klick auf **STRASSENRUNDE** löst genau eine bestätigte Runde aus. Dabei kann:

- etwas Kleines Gutes passieren,
- einfach nichts Besonderes passieren,
- oder gelegentlich Pech auftreten.

Die Ereignisse sind bewusst klein. Sie sollen Berlin lebendiger machen und keine große Mission ersetzen.

## Verteilung

Der Startkatalog besitzt exakt 100 Gewichtspunkte:

| Art | Gewicht | Anteil |
|---|---:|---:|
| ruhige Runde | 25 | 25 % |
| positiv | 60 | 60 % |
| negativ | 15 | 15 % |

Wenn tatsächlich etwas passiert, sind damit:

- **80 % der Begegnungen positiv**,
- **20 % negativ**.

Das Pech bleibt also spürbar, dominiert die Straßenrunde aber nicht.

## Startkatalog

Positive Beispiele:

- Wasser aufs Haus
- bekanntes Gesicht aus der Szene
- hilfreiche Abkürzung
- Grüße von einer anderen Crew
- Kaffee aufs Haus
- kleiner nützlicher Fund

Pech-Beispiele:

- Pfütze bis zum Knöchel
- Fahrradspritzer
- spontaner Regenschauer

Außerdem gibt es die ruhige Runde ohne Effekt.

## Kleine bestätigte Effekte

0.8.5-C verwendet nur bereits vorhandene Character-Werte:

- Energie
- Stress
- Ruf

Es wird **kein** neues Bargeld-, Inventar- oder Itemsystem für Gimmicks erfunden.

Energie und Stress bleiben im gültigen Bereich `0..100`; Ruf fällt nicht unter `0`.

## Wichtig: Neuladen würfelt nicht neu

Die Auswahl wird nicht im Browser und nicht aus der Uhrzeit erzeugt.

```text
serverseitiger World-Seed
+ eindeutige Walk-ID
+ optional bestätigte Server-Sequenz
        ↓
SHA-256
        ↓
gewichtete katalogisierte Auswahl
```

Dieselbe Walk-ID mit denselben bestätigten Eingaben liefert dasselbe Ergebnis.

Sobald die Runde journalisiert wurde, ist sie bestätigt. Ein Retry erkennt das vorhandene `street.encounter_resolved` und liefert denselben Encounter als idempotenten Replay zurück, ohne einen zweiten Effekt anzuwenden.

## Persistenz

Die Reihenfolge einer Runde lautet:

```text
street.encounter_resolved
        ↓
optional character.resources_changed
        ↓
optional character.reputation_changed
        ↓
bestätigter Character-State
```

Das erste Event speichert:

- Walk-ID
- Encounter-ID
- positiv / neutral / negativ
- Textschlüssel
- tatsächlich angewendete Effekte
- Vertragsversion

Dadurch bleibt nachvollziehbar, warum sich Energie, Stress oder Ruf verändert haben.

## Recovery

Der neue Encounter-Record selbst erfindet beim Replay keine Characterwerte. Die Character-Folgen werden weiterhin über die bereits bestehenden `character.resources_changed`- und `character.reputation_changed`-Replaypfade rekonstruiert.

Damit entsteht keine zweite Recovery-Logik.

## Browser-Grenze

Der Browser sendet ausschließlich:

```json
{
  "type": "street.walk",
  "command_id": "..."
}
```

Der Browser entscheidet **nicht**:

- welches Ereignis erscheint,
- ob Glück oder Pech eintritt,
- wie groß ein Effekt ist,
- ob ein Retry neu würfeln darf.

Diese Regeln liegen im `StreetEncounterService` und im `STREET_ENCOUNTER_MANIFEST.json`.

## Inhalte erweitern

Weitere kleine Straßenereignisse können später als Content-Pakete ergänzt werden, solange sie denselben Vertrag einhalten. Größere Kettenereignisse, Bezirksabhängigkeit oder Inventargewinne bleiben eigene spätere Feature-Pool-Punkte und werden nicht still in diesen kleinen Loop hineingemischt.
