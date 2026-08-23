# A4 Control Deck – Erste spielbare Runde für absolute Anfänger

Diese Anleitung gilt für den **lokalen schreibenden BUNKERFREQUENZ-Client**. Fachbegriffe werden möglichst vermieden; alle Gameplay-Änderungen laufen weiterhin durch den vorhandenen Spielkern.

## 1. Spiel starten

Im Projektordner:

```bash
./START_BUNKERFREQUENZ.sh
```

Wenn der Port belegt ist:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

Für einen getrennten Test-Spielstand:

```bash
./START_BUNKERFREQUENZ.sh --port 0 --save-dir /tmp/bunkerfrequenz-test
```

Im Terminal muss anschließend `STATUS: BEREIT` stehen. Beenden: `Strg+C`.

## 2. Neues Spiel anlegen

Beim ersten Start erscheint **FIRST RUN**:

1. Crew-/Charaktername eintragen.
2. Eventname eintragen.
3. **NEUES SPIEL ANLEGEN** drücken.

Ein vorhandener Spielstand wird nicht still überschrieben.

## 3. Das Control Deck verstehen

Das HUD zeigt Eventphase, Budget, Energie, Stress, Ruf und Anzahl eigener Orte. Darunter liegt die Schnellnavigation:

```text
STRASSE · MAP · PROPERTY · HALL · EVENT · EQUIPMENT · SAVE
```

## 4. Ansicht anpassen

Unter **ANSICHT** stehen Kompaktmodus, hoher Kontrast und große Schrift bereit. Diese Optionen verändern ausschließlich die Darstellung im Browser. Spielstand, Chancen, Budget und Regeln bleiben unverändert.

## 5. Straßenrunde – mit echter Auswahl

Vor einer Straßenrunde wählst du einen Ansatz:

| Ansatz | Bedeutung |
|---|---|
| **Ausgeglichen** | bekannte Standardverteilung |
| **Runterkommen** | eher Ruhe, Wasser, Kaffee und Erholung |
| **Kontakte** | eher bekannte Gesichter und Crew-Kontakte |
| **Scout** | eher Wege und nützliche Funde, mit etwas mehr möglichem Ärger |

Der Ansatz verändert nur die Wahrscheinlichkeit katalogisierter Begegnungen. Der Browser sendet nur die gewählte ID; bestätigte Effekte kommen aus dem Spielkern. Eine bestätigte Straßenrunde wird beim Reload nicht neu gewürfelt.

## 6. Berlin Ops Map PRO

Die Map zeigt 8 Districts, 12 Orte, District-Werte, Score/Tier, Eigentum, Ausbauten und Hall of Tribute. Die Karte selbst schreibt keine Gameplaywerte. Kaufen und Ausbauen erfolgt weiterhin im Property-Bereich.

## 7. Immobilien und Ausbau

Bei kaufbaren Orten gibt es **ÜBERNEHMEN**. Preis und Eigentümer bestimmt der Spielkern. Eigene Orte können über katalogisierte Ausbauarten bis Level 3 verbessert werden. Der Browser darf weder Preis noch Ziellevel erfinden.

## 8. Hall of Tribute und Saison

Die Hall zeigt Ruf, Level und Resonanz sowie Woche/Monat. Ein lokaler Rang 1 bedeutet nicht automatisch einen Championtitel. Endgültige Titel brauchen einen bestätigten abgeschlossenen Zyklus und echte bestätigte Konkurrenz. Die Systemuhr allein bestimmt niemals eine Saison.

## 9. Event spielen

Der kleinste vollständige Weg ist:

```text
PLANUNG BEGINNEN
→ BESCHAFFUNG BEGINNEN
→ benötigtes Equipment kaufen/reservieren
→ TRANSPORT STARTEN
→ AUFBAU BEGINNEN
→ SOUNDCHECK BESTÄTIGEN
→ EVENT STARTEN
→ optional Krise
→ EVENT BEENDEN
→ ABBAU BEENDEN
→ SETTLEMENT ABSCHLIESSEN
```

Danach muss die Eventphase `COMPLETED` sein.

## 10. Warum manche Event-Buttons ausgegraut sind

Das ist normalerweise kein Fehler. Unter den Buttons steht der Blocker, beispielsweise `Blockiert: Equipment ist noch nicht bereit`. Dann zuerst die fehlende Voraussetzung erfüllen.

## 11. Krise entscheiden – Folgen vorher sehen

Während `LIVE` kann eine katalogisierte Krise geöffnet werden. Antwortkarten zeigen vor der Wahl die bereits katalogisierten Auswirkungen. Der Browser berechnet die Folgen nicht neu, sondern sendet nur die `response_id` an die Crisis Engine.

## 12. Speichern

Jede bestätigte Aktion wird sofort journalisiert. Mit **CHECKPOINT SPEICHERN** legst du zusätzlich einen Snapshot an.

## 13. Neustart und Recovery

1. Client mit `Strg+C` beenden.
2. Mit demselben Spielstandordner neu starten.
3. Bestätigte Werte und Eventphase müssen wieder erscheinen.

Wenn State und Journal nicht zusammenpassen, verwendet die Recovery bestätigte Snapshots und Journalrecords. Ist eine sichere Wiederherstellung nicht möglich, stoppt der Start mit einer verständlichen Fehlermeldung. Journal-, State- oder Snapshot-Dateien dann nicht von Hand löschen.

## 14. Häufige Startfehler

### Port belegt

```text
START FEHLGESCHLAGEN – Port 8044 ist belegt; nutze --port 0 für automatische freie Portwahl
```

Lösung:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

### Spielstandordner nicht beschreibbar

```bash
./START_BUNKERFREQUENZ.sh --save-dir "$HOME/BUNKERFREQUENZ-SAVE"
```

### Programmdatei fehlt

Bei `START FEHLGESCHLAGEN – fehlt: ...` keine einzelnen Dateien verschiedener Versionen zusammenkopieren. Einen vollständigen Checkout bzw. ein vollständiges Release-Paket benutzen.

## 15. Wo liegt der Spielstand?

Standard:

```text
~/.local/share/bunkerfrequenz/a4-alpha
```

Lokale Ansichtseinstellungen liegen getrennt im Browser und sind kein Bestandteil des Spielstands.

## 16. Produktversion und Entwicklungsstand

Die Produkt-Release-Baseline bleibt `0.8.4-alpha.1`. Neue Features können bereits darüber hinaus geprüft und sicher gemergt sein. `PROJEKTSTATUS.json` trennt deshalb Produktrelease, aktive Iteration und letzten validierten Feature-Stand.

## 17. District-Welt-Ereignisse: C1 und C2 einfach erklärt

C1 hat zuerst festgelegt, **was** ein District-Ereignis sein darf: stabile IDs, Gewichte, Voraussetzungen, kleine District-Effekte und getrennte deutsche Story-Texte. Der Startkatalog enthält:

- **Das Netz flackert**
- **Die Nachricht macht die Runde**
- **Mehr Blau in den Nebenstraßen**
- **Eine Tür steht plötzlich offen**

C2 ergänzt jetzt den kleinen Runtime-Kern dahinter. Vereinfacht passiert intern:

```text
bestätigter Welt-Seed + Bezirk + Trigger
        ↓
Voraussetzungen prüfen
        ↓
reproduzierbar ein erlaubtes Ereignis auswählen
        ↓
vorhandenen DistrictService benutzen
        ↓
District-Werte journalisieren
        ↓
Reload/Recovery kann denselben Stand wiederherstellen
```

Wichtig: Derselbe Bezirk + Trigger wird nicht durch Reload oder einen zweiten Versuch neu ausgewürfelt. Selbst wenn ein Retry versehentlich mit einem anderen Seed ankommt, bleibt die bereits bestätigte Event-Instanz maßgeblich und wird nicht doppelt angewendet.

Ebenso wichtig: **Der A4-Browser löst diese neue Runtime in C2 noch nicht selbst aus.** Es gibt deshalb noch keinen neuen District-Event-Button und noch keine sichtbare Ereigniskarte. C2 schafft zuerst die sichere, testbare Server-/Application-Grenze. Die nächste Stufe bindet einen autorisierten Trigger in den bestehenden Spielablauf ein; der Browser darf dabei weiterhin keine District-Effekte mitsenden.

## 18. Was noch nicht enthalten ist

Noch nicht Teil des sichtbaren District-Event-Gameplays sind:

- automatische Auslösung aus einem kanonischen Game-Client-/Application-Flow,
- sichtbare District-Event-Karten oder Ereignis-Timeline im Control Deck,
- Event-Cadence/Cooldown auf bestätigter Spielzeit,
- District-Ereignisketten mit Erinnerung,
- Property-Miete/Verkauf/laufende Rendite,
- echtes Netzwerk-/Telegram-Sync,
- echte Remote-Gegner ohne bestätigte Netzwerkquelle,
- neuer Produktrelease oberhalb `0.8.4-alpha.1`.

Der nächste saubere Schritt ist **C3 – Application-Integration**: einen einzigen autorisierten District-Event-Trigger in den vorhandenen Spielablauf einhängen, ohne neue Browser-Fachlogik.
