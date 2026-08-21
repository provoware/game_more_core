# Ranking / Network Foundation 0.6.5

## Ziel

0.6.5 bereitet die gemeinsame Ranking-/Network-Anzeige für beliebig viele Spieler vor. Die Schicht bleibt reine Presentation und besitzt noch keinen Telegram-Transport, keine Presence-Abfrage und keinen eigenen Online-State.

## Quellen

Character-Metriken stammen ausschließlich aus bestätigten Character-Projections:

- Level
- Ruf
- Resonanzrang
- Skills

Gemeinsame Netzwerkmetriken werden nur aus explizit bestätigten Network-Datensätzen übernommen:

- Events
- Clubs

Die Autorität dafür stammt aus `SYNC_MANIFEST.json` und lautet derzeit `server_confirmed_transaction`.

## Keine erfundenen Daten

Fehlt ein bestätigter Network-Datensatz, gilt:

- Sync verfügbar: nein
- Sync-Status: `unknown`
- sichtbarer Status: `NICHT BESTÄTIGT`
- Events/Clubs: nicht verfügbar (`null`), nicht `0`
- Rankingplatz für die fehlende Metrik: `null`
- Online-/Presence-Status: wird überhaupt nicht abgeleitet

`offline` bedeutet nur einen bestätigten Sync-Zustand und ist kein Beweis für aktuelle Anwesenheit oder Abwesenheit.

## Rankingmodi

- `level`
- `reputation`
- `resonance`
- `skill` mit expliziter `skill_id`
- `events`
- `clubs`

Sortierung: verfügbare Werte zuerst, Wert absteigend, danach stabile `character_id`.

## Gleichstände

Competition Ranking:

```text
100 → Rang 1
100 → Rang 1
 90 → Rang 3
```

Ein fehlender Wert erhält keinen Rang.

## Top 10 / Alle

Die Quellliste besitzt keine künstliche Spielerobergrenze. Standardmäßig zeigt die Projection die ersten 10 Einträge. `show_all=true` liefert die vollständige sortierte Liste.

## Identität und Integrität

Abgewiesen werden:

- doppelte `player_id`
- doppelte `character_id`
- doppelte bestätigte Network-Datensätze
- Network-Datensätze für unbekannte Spieler
- Character-Mismatch zwischen Participant und Network Record
- falsche Server-Autorität
- unbekannte Network-Metriken
- nicht katalogisierte Sync-Statuswerte

## Textvertrag

Sichtbare Begriffe werden ausschließlich über `content/de/ui/character_forge.json` referenziert. Neu relevant sind unter anderem:

- Rankingmetriken Level/Ruf/Resonanz/Events/Clubs
- `ALLE ANZEIGEN`
- `NICHT BESTÄTIGT`
- `ui.sync.unknown`

Skill-Rankings verwenden die vorhandenen `skill.<id>.label`-Schlüssel.

## Telegram-Grenze

Telegram bleibt Transport-/Identity-Bridge und ist ausdrücklich **nicht** Primärspeicher. 0.6.5 verarbeitet nur bereits bestätigte Datenobjekte; Abruf, Upload, Konfliktlösung und Serverbetrieb folgen in der späteren Sync-Phase.

## Abnahme

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote auf demselben Implementierungs-Head:

- Runtime Core
- Presentation Core
