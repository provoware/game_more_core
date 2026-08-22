# Release-Abnahme 0.8.4 – lokales A4-Alpha

## Ziel

Diese Stufe prüft, ob der bereits validierte schreibende A4-Client **aus einem frischen Repository-Checkout tatsächlich startbar, verständlich fehlertolerant und nach Neustart/Recovery reproduzierbar** ist.

Sie verändert keine Gameplay-, Economy-, Incident- oder Settlement-Regel und legt noch keine neue Produktversion fest.

## Freigaberegel

`VERSION.json` und ein Release-Artefakt dürfen erst in der **nachfolgenden** Stufe geändert bzw. erzeugt werden, wenn diese Abnahme vollständig grün gemergt ist.

## Abnahmeumfang

### A. Frischer Start / Klickstart

Der Git-Checkout muss die ausführbare Datei

```text
START_BUNKERFREQUENZ.sh
```

mit ausführbarem Dateimodus enthalten.

Der automatisierte Acceptance-Test startet genau diese Datei als separaten Prozess mit:

```bash
./START_BUNKERFREQUENZ.sh --port 0 --no-browser --save-dir <temporärer-leerer-ordner>
```

Er akzeptiert den Start erst, wenn die tatsächlich ausgegebene localhost-Adresse über `/api/health` den Zustand `ready` liefert.

### B. Lokale Servergrenze

- Bind-Adresse bleibt ausschließlich `127.0.0.1`.
- `--port 0` muss einen freien Port liefern.
- statische Dateien dürfen nur aus `web/a4/` kommen.
- ein Pfadversuch auf Repository-Dateien wie `../README.md` muss scheitern.
- fremde Browser-Origins dürfen keine Schreibrequests auslösen.

### C. Echter HTTP-Spielpfad

Über die reale HTTP-API wird ausgeführt:

```text
First Run
→ Planung
→ Beschaffung
→ PA kaufen
→ PA reservieren
→ Transport
→ Aufbau
→ Soundcheck
→ Live
→ Stromkrise
→ Krisenreaktion
→ Eventende
→ Abbau
→ Settlement
→ completed
→ Snapshot
```

Die Testlogik erzeugt dabei keine zweite Fachregel. Sie sendet dieselben Commands wie der A4-Client.

### D. Neustart und Recovery

Nach `completed` wird der Server geschlossen und derselbe Save neu geladen. Der bestätigte Zustand muss identisch sein.

Danach wird gezielt nur `state/current.json` entfernt, während gültiger Snapshot und Journal erhalten bleiben. Beim nächsten Start muss die kanonische Recovery laufen und exakt denselben bestätigten Zustand wiederherstellen. Ein weiterer Start muss anschließend wieder ohne Recovery gesund öffnen.

### E. Verständliche Fehlerpfade

Folgende Fälle müssen kontrolliert statt mit ungefiltertem Python-Traceback enden:

1. erforderliche Projektdatei fehlt → `START FEHLGESCHLAGEN – fehlt: ...`
2. Standard-/gewählter Port ist belegt → Hinweis auf `--port 0`
3. Save-Ziel ist nicht beschreibbar bzw. kein verwendbarer Ordner → `START FEHLGESCHLAGEN – Spielstandordner ist nicht beschreibbar: ...`
4. nicht sicher recoverbarer Save → vorhandene Recovery-Fehlermeldung; keine Neuerzeugung des Spielverlaufs

## Automatischer Prüfbefehl

Vom Repository-Root:

```bash
PYTHONPATH=src python3 -m unittest tests.runtime.test_a4_release_acceptance -v
```

Der Test ist zusätzlich Bestandteil von `Runtime Core`, weil dieser alle Tests unter `tests/runtime/` aus einem frischen GitHub-Actions-Checkout startet.

## Required Remote Gates

Für den finalen Acceptance-PR-Head müssen wie immer gelten:

- `runtime-core` = grün
- `presentation-core` = grün
- `repository-health` = grün
- ungelöste Review-Threads = 0
- Branch enthält aktuellen `main`
- Merge ausschließlich über `/safe-merge`

## Bewusste Nicht-Ziele

- keine Produktversionsänderung
- noch kein ZIP-/Release-Artefakt
- kein Installer
- kein Kartenrenderer-Ausbau
- keine Bezirks-/Immobilienlogik
- kein Netzwerk-/Telegram-Sync

## Nächster Schritt nach PASS

Erst nach sicher gemergter Release-Abnahme wird die erste spielbare lokale Alpha-Version festgelegt. Danach werden Release Notes, reproduzierbares Paket, SHA-256 und ein erneuter Paket-Smoke in einem eigenen Release-PR erzeugt.
