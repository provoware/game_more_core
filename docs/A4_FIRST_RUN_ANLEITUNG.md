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

Im Terminal muss anschließend stehen:

```text
STATUS: BEREIT
```

Beenden: `Strg+C`.

## 2. Neues Spiel anlegen

Beim ersten Start erscheint **FIRST RUN**:

1. Crew-/Charaktername eintragen.
2. Eventname eintragen.
3. **NEUES SPIEL ANLEGEN** drücken.

Ein vorhandener Spielstand wird nicht still überschrieben.

## 3. Das neue Control Deck verstehen

Oben findest du den aktuellen Spielstatus. Das HUD zeigt kompakt:

- Eventphase
- Budget
- Energie
- Stress
- Ruf
- Anzahl eigener Orte

Darunter liegt die Schnellnavigation:

```text
STRASSE · MAP · PROPERTY · HALL · EVENT · EQUIPMENT · SAVE
```

Damit springst du direkt zum gewünschten Bereich, ohne den kompletten Bildschirm durchsuchen zu müssen.

## 4. Ansicht anpassen

Oben rechts gibt es **ANSICHT**. Dort stehen drei reine Anzeigeoptionen zur Verfügung:

### Kompakt
Weniger Abstände und kleinere Flächen. Sinnvoll, wenn du viel gleichzeitig sehen möchtest.

### Hoher Kontrast
Stärkere Linien und deutlichere Flächen. Sinnvoll bei schlechter Erkennbarkeit.

### Große Schrift
Vergrößert die Grunddarstellung.

Wichtig: Diese Optionen verändern **nur die Oberfläche dieses Browsers**. Sie verändern keinen Spielstand, keine Chancen, kein Budget und keine Regeln.

## 5. Straßenrunde – jetzt mit echter Auswahl

Vor einer Straßenrunde wählst du einen Ansatz:

| Ansatz | Bedeutung |
|---|---|
| **Ausgeglichen** | bekannte Standardverteilung |
| **Runterkommen** | eher Ruhe, Wasser, Kaffee und Erholung |
| **Kontakte** | eher bekannte Gesichter und Crew-Kontakte |
| **Scout** | eher Wege und nützliche Funde, mit etwas mehr möglichem Ärger |

Danach **RUNDE STARTEN** drücken.

### Was die Auswahl wirklich macht

Sie verändert nur die **Wahrscheinlichkeit**, welche bereits katalogisierte Begegnung gezogen wird. Sie garantiert kein bestimmtes Ergebnis.

Der Browser darf nicht selbst sagen: „Gib mir +10 Ruf“. Er sendet lediglich beispielsweise:

```text
approach_id = network
```

Der Spielkern wählt deterministisch eine erlaubte Begegnung und übernimmt deren bestätigte Effekte.

### Wichtig für Reload/Retry

Eine bereits bestätigte Straßenrunde kann nicht durch Reload neu gewürfelt werden. Derselbe Walk behält auch seinen bestätigten Ansatz.

## 6. Berlin Ops Map PRO

Die Map zeigt die vorhandene Spielwelt:

- 8 Districts
- 12 Orte
- District-Werte
- Score/Tier
- Eigentum
- Ausbauten
- Hall of Tribute

Du kannst filtern und Orte/Bezirke fokussieren. Die Karte selbst schreibt **keine** Gameplaywerte.

Kaufen und Ausbauen erfolgt weiterhin im Property-Bereich.

## 7. Immobilien und Ausbau

Bei kaufbaren Orten gibt es **ÜBERNEHMEN**. Preis und Eigentümer bestimmt der Spielkern.

Eigene Orte können über katalogisierte Ausbauarten bis Level 3 verbessert werden. Der Browser darf weder Preis noch Ziellevel erfinden.

## 8. Hall of Tribute und Saison

Die Hall zeigt Ruf, Level und Resonanz sowie Woche/Monat.

Wichtig:

- Ein lokaler Rang 1 bedeutet nicht automatisch einen Championtitel.
- Endgültige Titel benötigen einen bestätigten abgeschlossenen Zyklus.
- Für echte Konkurrenz-Titel müssen bestätigte Konkurrenten vorhanden sein.
- Die Systemuhr allein bestimmt niemals eine Saison.

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

Das ist normalerweise kein Fehler. Unter den Buttons steht der Blocker, z. B.:

```text
Blockiert: Equipment ist noch nicht bereit
```

Dann zuerst die fehlende Voraussetzung erfüllen.

## 11. Krise entscheiden – Folgen vorher sehen

Während `LIVE` kann eine katalogisierte Krise geöffnet werden. Bei einer aktiven Krise erscheinen Antwortkarten.

Jede Karte zeigt vor der Wahl die **bereits katalogisierten** Auswirkungen, zum Beispiel:

```text
Budget −50,00 € · Ruf +2 · Crew-Stress +1 · Stabilität +2
```

Das ist eine Vorschau des vorhandenen Crisis-Vertrags. Der Browser berechnet die Folgen nicht neu. Beim Klick sendet er nur die `response_id` an die Crisis Engine.

## 12. Speichern

Jede bestätigte Aktion wird sofort journalisiert.

Mit **CHECKPOINT SPEICHERN** legst du zusätzlich einen Snapshot an.

## 13. Neustart und Recovery

1. Client mit `Strg+C` beenden.
2. Mit demselben Spielstandordner neu starten.
3. Bestätigte Werte und Eventphase müssen wieder erscheinen.

Wenn aktueller State und Journal nicht zusammenpassen, versucht der Client die vorhandene Recovery. Er erfindet dabei keinen neuen Spielverlauf, sondern verwendet bestätigte Snapshots und Journalrecords.

Wenn sichere Recovery nicht möglich ist, stoppt der Start mit einer verständlichen Fehlermeldung. Journal-, State- oder Snapshot-Dateien dann nicht von Hand löschen.

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

Bei:

```text
START FEHLGESCHLAGEN – fehlt: ...
```

keine einzelnen Dateien verschiedener Versionen zusammenkopieren. Einen vollständigen Checkout bzw. ein vollständiges Release-Paket benutzen.

## 15. Wo liegt der Spielstand?

Standard:

```text
~/.local/share/bunkerfrequenz/a4-alpha
```

Die lokalen **Ansichtseinstellungen** liegen getrennt im Browser und sind kein Bestandteil des Spielstands.

## 16. Woran erkenne ich den geprüften Entwicklungsstand?

Für Spieler ist die Produkt-Release-Baseline weiterhin `0.8.4-alpha.1`. Neue Features können bereits darüber hinaus geprüft und sicher gemergt sein, ohne dass die Produktversion sofort hochgezählt wird.

Der aktuell bestätigte Feature-Stand steht in `PROJEKTSTATUS.json` unter `last_validated_feature_iteration`. Für 0.8.7-B muss dort stehen:

```text
0.8.7-B
```

Zusätzlich nennt `TODO.md` denselben Stand samt PR, grünen CI-Gates und Safe-Merge-Nachweis. Wenn diese Angaben widersprüchlich sind, gilt `PROJEKTSTATUS.json` als kanonischer Status und der Widerspruch ist ein Dokumentationsfehler – nicht automatisch ein Spielfehler.

## 17. Was noch nicht enthalten ist

Noch nicht Teil dieses Slices sind unter anderem:

- bezirksbezogene Welt-Ereignisse als eigenes System,
- Property-Miete/Verkauf/laufende Rendite,
- echtes Netzwerk-/Telegram-Sync,
- echte Remote-Gegner ohne bestätigte Netzwerkquelle,
- neuer Produktrelease oberhalb `0.8.4-alpha.1`.

**0.8.7-B – Control Deck & Player Choices** ist remote validiert und über `/safe-merge` übernommen. Als nächster Entwicklungsbaustein ist **0.8.7-C – Bezirksbezogene Welt-Ereignisse** vorbereitet.
