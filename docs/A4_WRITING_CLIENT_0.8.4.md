# 0.8.4 – Schreibender A4-Game-Client

## Ziel

0.8.4 verbindet den bereits validierten fachlichen Event-Loop mit einem kleinsten lokal bedienbaren A4-Client. Der Browser ist dabei **keine zweite Spielengine**: Er zeigt bestätigte Projektionen an und sendet nur explizite Commands an die Application-Schicht.

## Schreibgrenze

```text
Browser A4
  ↓ JSON-Command
lokaler A4-Server
  ↓
GameClientSession
  ├─ EventStateService
  ├─ EventExecutionService
  ├─ EconomyService
  ├─ IncidentService
  └─ SettlementService
  ↓
PersistenceKernel
  ↓
Journal + State + Snapshot
```

Der Browser darf keine Phase, Budgetwirkung, Incident-Folge oder Settlement-Wirkung selbst berechnen. Event-Aktionsfreigaben und Blocker stammen direkt aus `EventExecutionService.available_actions(...)`.

## Erlaubte Client-Commands

- `event.create`
- `event.update_planning`
- `event.execute`
- `economy.initialize`
- `economy.transact`
- `incident.open`
- `incident.resolve`
- `settlement.complete`

Jeder Command besitzt eine feste Feld-Allowlist. Zusätzliche Felder werden vor jedem Schreibversuch fail-closed abgewiesen.

## First Run

Der erste lokale Start verwendet `web/a4/starter.json` als **Einstiegsszenario**, nicht als neue Balancequelle. Der Starter enthält einen Character, einen vorbereiteten Eventvertrag und einen minimalen PA-Katalog.

Für Character-Erstellung existiert noch kein kanonischer `character.created`-Journaltyp. Deshalb darf A4 den GENESIS-Character nur dann initialisieren, wenn noch kein Journalrecord existiert. Ein vorhandener Save wird niemals durch First Run überschrieben.

Event und Economy werden anschließend ausschließlich über die vorhandenen Application-Services angelegt.

## Recovery-Härtung

Der First-Run-Smoke hat einen bestehenden Persistence-Randfall offengelegt: Ein Snapshot auf Journal-Head durfte bisher einen fehlenden `state/current.json` fälschlich als `healthy` erscheinen lassen. 0.8.4 korrigiert den zentralen Recovery-Vertrag:

- `healthy` erfordert einen echten State-Checkpoint auf Journal-Head,
- ein Snapshot allein ist Recovery-Basis, aber kein Beweis für vorhandenen Current-State,
- fehlt der State, wird er aus Snapshot + Journal wiederhergestellt,
- anschließend wird erneut ein konsistenter State/Meta/Snapshot-Stand geschrieben.

## Lokale HTTP-Grenze

Der A4-Server:

- bindet ausschließlich an `127.0.0.1`,
- liefert statisch nur `web/a4/` aus,
- akzeptiert schreibende Requests nur als JSON,
- begrenzt Request-Bodies auf 64 KiB,
- akzeptiert Browser-Origin nur vom eigenen localhost-Port,
- protokolliert keine Request-Bodies,
- serialisiert lokale Commands über einen Runtime-Lock.

## Start

```bash
python3 tools/start_a4_game_client.py
```

Für einen isolierten Test-Spielstand:

```bash
python3 tools/start_a4_game_client.py --port 0 --save-dir /tmp/bunkerfrequenz-a4-test
```

Der bestehende `tools/start_web_blueprint.py` bleibt unverändert der schreibgeschützte Blueprint-Start.

## Verbindlicher Smoke-Pfad

```text
Neues Spiel
→ Planung
→ Beschaffung
→ PA kaufen
→ PA reservieren
→ Transport
→ Aufbau
→ Soundcheck
→ Live
→ optional Incident öffnen
→ Incident lösen
→ Event beenden
→ Abbau beenden
→ Settlement
→ completed
→ Snapshot
→ Neustart
→ identischer bestätigter Zustand
→ State-Checkpoint entfernen
→ Recovery aus Snapshot + Journal
→ identischer bestätigter Zustand
→ erneuter sauberer Neustart
```

## Nicht Bestandteil

- keine neue Gameplay-/Balance-Regel,
- keine neue Journal-Eventart,
- keine persistente Bezirksdynamik,
- kein Immobilienkauf,
- kein Network-/Telegram-Sync,
- kein Release-/Versionssprung.

Die Produktversion wird erst nach separater Release-Abnahme festgelegt.
