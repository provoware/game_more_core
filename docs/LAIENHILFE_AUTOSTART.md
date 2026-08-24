# BUNKERFREQUENZ – vollautomatischer Start

## Kurz gesagt

Starte BUNKERFREQUENZ weiterhin über **`START_BUNKERFREQUENZ.sh`** oder per Doppelklick auf **`BUNKERFREQUENZ.desktop`**. Es gibt keinen zweiten Spielstart.

Der Starter arbeitet die nötigen Prüfungen automatisch in dieser Reihenfolge ab:

1. **Vorprüfung** – wichtige Programmdateien und eine passende Python-Version werden geprüft.
2. **Abhängigkeiten** – der Spielstandordner wird geprüft beziehungsweise sicher angelegt; ein belegter Wunschport wird automatisch durch einen freien Port ersetzt.
3. **Serverstart** – der vorhandene lokale BUNKERFREQUENZ-Server wird gestartet.
4. **API-Prüfung** – `/api/health` und `/api/state` müssen korrekt antworten.
5. **Browserprüfung** – wenn Chrome/Chromium vorhanden ist, wird die echte JavaScript-Oberfläche automatisch bis zum Zustand `● BEREIT` geprüft.
6. **Browserstart** – ein vorhandener Browser wird geöffnet; falls das nicht möglich ist, bleibt die lokale Adresse sichtbar.
7. **Nachvalidierung** – nach der Browserübergabe werden Server und API erneut geprüft.
8. **BEREIT** – erst danach meldet der Starter 100 %.

## Ampelfarben

- **🟢 Grün** – dieser Schritt ist vollständig bestanden.
- **🟡 Gelb** – das Spiel kann weiterlaufen, aber ein Komfortpunkt benötigt eventuell eine manuelle Handlung, zum Beispiel das Öffnen der angezeigten Adresse im Browser.
- **🔴 Rot** – der sichere Start wurde gestoppt. Es wird nichts einfach übersprungen.
- **🔵 Blau** – Information oder eine gerade laufende automatische Prüfung.

Die Prozentanzeige zeigt den Startfortschritt von **0 % bis 100 %**.

## Was der Starter automatisch beheben darf

Ohne Nachfrage werden nur lokale, risikoarme Dinge korrigiert:

- fehlenden Standard-Spielstandordner anlegen,
- einen belegten Port erkennen und auf einen freien lokalen Port wechseln,
- mitgelieferte Startdateien nach Möglichkeit ausführbar machen,
- einen fehlgeschlagenen Serverstart genau einmal kontrolliert mit freier Portwahl wiederholen,
- eine noch nicht sofort antwortende API kurz erneut prüfen,
- einen geeigneten vorhandenen Browserstarter auswählen.

## Was der Starter absichtlich nicht heimlich macht

Der Starter führt **kein `sudo`** aus, installiert keine Systempakete und verändert keine systemweiten Browser- oder Desktop-Einstellungen. Fehlt zum Beispiel eine passende Python-Version, wird die konkrete Lösung angezeigt, aber nicht mit Administratorrechten im Hintergrund ausgeführt.

## START_STATUS.txt

Während des Starts entsteht **`START_STATUS.txt`**. Darin stehen die bereits durchlaufenen Phasen, ihre Ampelzustände und alle automatisch vorgenommenen Auflösungen. Zusätzlich gibt es jetzt eine kompakte **Auto-Auflösungsbilanz**. So ist auf einen Blick erkennbar, ob der Starter nichts ändern musste oder bereits eine oder mehrere Bedingungen automatisch gelöst hat.

Falls der Programmordner selbst nicht beschreibbar ist, verwendet der Starter automatisch einen beschreibbaren temporären Statusordner und zeigt dessen Pfad an.

## START_DIAGNOSE.txt

Nur bei einem echten Fehler entsteht **`START_DIAGNOSE.txt`**. Der Bericht ist bewusst wie eine kleine Reparaturkarte aufgebaut und nennt:

- eine stabile **Fehlerklasse**,
- die verständliche Bedeutung dieser Fehlerklasse,
- die Startphase, in der der Fehler erkannt wurde,
- den konkreten technischen Grund,
- einen Abschnitt **`JETZT BEHEBEN`** mit nummerierten Handlungsschritten,
- eine kompakte **Auto-Auflösungsbilanz**,
- bei bereits vorgenommenen Korrekturen ein **transparentes Auflösungsprotokoll**,
- Projektordner, Python-Version und Pfad zur Statusdatei.

Aktuell unterscheidet die Diagnose unter anderem diese Klassen:

- `release_integrity` – Release unvollständig oder Dateien aus verschiedenen Ständen vermischt,
- `python_runtime` – Python-Version nicht geeignet,
- `filesystem_permissions` – Spielstandordner oder Dateirechte blockieren,
- `port_configuration` – ungültige Portkonfiguration,
- `server_start` – lokaler Server wird nicht bereit,
- `api_health` – lokale API antwortet nicht sicher,
- `browser_validation` – automatische UI-Prüfung schlägt fehl,
- `post_validation` – Start verliert nach der Übergabe seine Bereitschaft.

Der Diagnosehelfer **entscheidet nichts neu**. Er erklärt nur einen Fehler, den der bestehende Orchestrator bereits erkannt hat. Er führt selbst keine Reparatur, Installation, Gameplay-Änderung oder zusätzliche Recovery aus.

Ein gelber Browserhinweis allein ist kein Spielabbruch.

## Manueller Browsermodus

Mit

```bash
./START_BUNKERFREQUENZ.sh --no-browser
```

wird kein sichtbarer Browser automatisch geöffnet. Der Server und die API werden trotzdem vollständig geprüft; die lokale Adresse wird angezeigt.

## Reiner Prüfmodus

Für Diagnose und automatische Tests gibt es:

```bash
./START_BUNKERFREQUENZ.sh --port 0 --no-browser --exit-after-ready
```

Der Starter führt Vorprüfung, Serverstart, API-/Browserprüfung und Nachvalidierung durch und beendet den lokalen Server anschließend wieder sauber.

## Stoppen

Beim normalen Spielstart bleibt das Terminalfenster geöffnet, weil dort der lokale Server läuft. Zum Beenden **Strg+C** drücken. Das beendet den durch den Starter verwalteten Serverprozess kontrolliert.

## Sicherheitsgrenze

Der Autostart entscheidet nicht über Gameplay, Geld, Energie, Stress, Story, Journal oder Spielstände. Er orchestriert ausschließlich den bereits vorhandenen lokalen Start- und Prüfpfad.