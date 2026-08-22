# A4 – Erste spielbare Runde für absolute Anfänger

Diese Anleitung gilt für den **lokalen schreibenden A4-Alpha-Client**. Sie verändert nicht den bisherigen schreibgeschützten Blueprint.

## 1. A4 starten

### Am einfachsten: Klick-/Direktstart

Im Projektordner gibt es jetzt:

```text
START_BUNKERFREQUENZ.sh
```

Unter Ubuntu/Kubuntu kannst du diese ausführbare Datei direkt starten. Falls der Dateimanager fragt, wähle **Ausführen**.

### Alternativ im Terminal

Öffne ein Terminal im Projektordner und gib ein:

```bash
./START_BUNKERFREQUENZ.sh
```

oder direkt:

```bash
python3 tools/start_a4_game_client.py
```

Danach öffnet sich normalerweise der Browser. Im Terminal muss `STATUS: BEREIT` stehen.

Falls der Standard-Port belegt ist:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

`--port 0` bedeutet: Das Programm sucht automatisch einen freien lokalen Port.

Für einen komplett getrennten Test-Spielstand:

```bash
./START_BUNKERFREQUENZ.sh --port 0 --save-dir /tmp/bunkerfrequenz-a4-test
```

Wenn du den Browser bewusst selbst öffnen möchtest:

```bash
./START_BUNKERFREQUENZ.sh --port 0 --no-browser
```

Kopiere danach die hinter `ADRESSE:` angezeigte lokale Adresse in Firefox oder Chrome.

Beenden: im Terminal `Strg+C` drücken.

## 2. Neues Spiel anlegen

Beim ersten Start siehst du **FIRST RUN**.

1. Crew-/Charaktername eintragen.
2. Eventname eintragen.
3. **NEUES SPIEL ANLEGEN** drücken.

Der Client legt nur einen kleinen Starter an. Danach werden alle Änderungen vom vorhandenen Spielkern geprüft und gespeichert.

## 3. Was bedeuten ausgegraute Event-Buttons?

Ein ausgegrauter Button ist kein Fehler. Direkt darunter steht, was noch fehlt. Diese Blockade stammt aus derselben Runtime-Regel, die beim echten Ausführen geprüft wird.

Beispiel:

```text
TRANSPORT STARTEN – ausgegraut
Blockiert: Equipment ist noch nicht bereit
```

Dann zuerst im Bereich **Equipment & Economy** die benötigte PA kaufen und reservieren.

## 4. Erste komplette Runde

Der kleinste Testweg ist:

```text
PLANUNG BEGINNEN
→ BESCHAFFUNG BEGINNEN
→ PA KAUFEN
→ PA RESERVIEREN
→ TRANSPORT STARTEN
→ AUFBAU BEGINNEN
→ SOUNDCHECK BESTÄTIGEN
→ EVENT STARTEN
→ optional eine Krise auslösen und lösen
→ EVENT BEENDEN
→ ABBAU BEENDEN
→ SETTLEMENT ABSCHLIESSEN
```

Danach muss die Eventphase `COMPLETED` anzeigen.

## 5. Krise ausprobieren

Während `LIVE` erscheint der Krisenbereich. Für den Alpha-Test kannst du dort eine katalogisierte Krise öffnen und anschließend eine angebotene Reaktion wählen.

Wichtig: Der Browser berechnet die Folgen nicht. Er sendet nur deine Auswahl an die vorhandene Crisis Engine und zeigt danach den bestätigten Zustand.

## 6. Speichern

Jede bestätigte Aktion wird sofort im Journal gesichert. Du musst also nicht bis zum manuellen Speichern warten.

Mit **CHECKPOINT SPEICHERN** legst du zusätzlich einen Snapshot an. Dieser Snapshot hilft bei Recovery.

## 7. Neustart prüfen

1. A4 mit `Strg+C` beenden.
2. Mit demselben Befehl erneut starten.
3. Der vorhandene Spielstand muss direkt erscheinen.
4. Die bestätigte Eventphase, Budget-/Equipmentdaten und Settlement-Ergebnisse müssen erhalten sein.

## 8. Recovery

Wenn Journal und aktueller State nicht zusammenpassen, versucht A4 beim Start die vorhandene Recovery-Funktion. Dabei wird kein neuer Spielverlauf erfunden: Wiederhergestellt wird ausschließlich aus gültigem Snapshot und Journal.

Auch der Fall **„aktueller State fehlt, gültiger Snapshot und Journal sind aber vorhanden“** ist regressionsgetestet. Der Start darf diesen Zustand nicht fälschlich als gesund behandeln, sondern muss den bestätigten State wiederherstellen.

Wenn sichere Recovery nicht möglich ist, bricht der Start mit einer verständlichen Fehlermeldung ab. Lösche dann **keine** Journal-, State- oder Snapshot-Dateien von Hand.

## 9. Verständliche Startfehler

### Port ist schon belegt

Beispiel:

```text
START FEHLGESCHLAGEN – Port 8044 ist belegt; nutze --port 0 für automatische freie Portwahl
```

Lösung:

```bash
./START_BUNKERFREQUENZ.sh --port 0
```

### Spielstandordner kann nicht beschrieben werden

Beispiel:

```text
START FEHLGESCHLAGEN – Spielstandordner ist nicht beschreibbar: ...
```

Wähle einen Ordner, in dem dein Benutzer schreiben darf, zum Beispiel:

```bash
./START_BUNKERFREQUENZ.sh --save-dir "$HOME/BUNKERFREQUENZ-SAVE"
```

### Eine erforderliche Programmdatei fehlt

Der Start nennt die fehlende Datei hinter:

```text
START FEHLGESCHLAGEN – fehlt: ...
```

In diesem Fall nicht einzelne Dateien aus verschiedenen Versionen zusammenkopieren. Nutze einen vollständigen Checkout bzw. später das vollständige Release-Paket.

## 10. Wo liegt der Spielstand?

Standardmäßig unter:

```text
~/.local/share/bunkerfrequenz/a4-alpha
```

Mit `--save-dir` kannst du für Tests einen anderen Ordner verwenden.

## 11. Was dieser Alpha-Client noch nicht ist

Noch nicht enthalten sind unter anderem:

- final versioniertes Release-Paket/Installer,
- Berlin-Kartenrenderer als Hauptspielansicht,
- Immobilienkauf/-ausbau,
- persistente Bezirksdynamik,
- Netzwerk-/Telegram-Sync.

Der **Klick-/Direktstart selbst ist jetzt vorhanden und wird in der Release-Abnahme aus einem frischen Checkout als echter Prozess getestet**. Erst wenn diese Release-Abnahme vollständig grün ist, werden Produktversion und reproduzierbares Release-Artefakt festgelegt.
