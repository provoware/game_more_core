# Ranking / Network Foundation 0.6.5 – historischer Vertrag

> **Hinweis:** Dieses Dokument beschreibt die ursprüngliche 0.6.5-Foundation. Der aktuelle Rankingvertrag ab 0.8.5-A steht in [`RANKING_COMPETITION_0.8.5-A.md`](RANKING_COMPETITION_0.8.5-A.md). Insbesondere die frühere Competition-Ranking-Regel mit gemeinsamen Rangnummern wurde durch eindeutige Plätze und den Verdrängungszyklus ersetzt.

## Ziel von 0.6.5

0.6.5 bereitete die gemeinsame Ranking-/Network-Anzeige für beliebig viele Spieler vor. Die Schicht blieb reine Presentation und besaß noch keinen Telegram-Transport, keine Presence-Abfrage und keinen eigenen Online-State.

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

Diese Metriken bleiben auch im 0.8.5-A-Vertrag erhalten.

## Historische Gleichstandsregel

0.6.5 verwendete Competition Ranking:

```text
100 → Rang 1
100 → Rang 1
 90 → Rang 3
```

Diese Regel ist **nicht mehr aktuell**. Ab 0.8.5-A sind Rangnummern eindeutig; ein aufsteigender Teilnehmer kann bei gleichem aktuellen Wert einen stehengebliebenen Teilnehmer verdrängen.

## Top 10 / Alle

Die Quellliste besitzt keine künstliche Spielerobergrenze. Standardmäßig zeigt die Projection die ersten 10 Einträge. `show_all=true` liefert die vollständige sortierte Liste. Diese Anzeigegrenze bleibt bestehen; 0.8.5-A ergänzt zusätzlich den stärkeren Konkurrenzdruck innerhalb der Top 10.

## Identität und Integrität

Weiterhin abgewiesen werden:

- doppelte `player_id`
- doppelte `character_id`
- doppelte bestätigte Network-Datensätze
- Network-Datensätze für unbekannte Spieler
- Character-Mismatch zwischen Participant und Network Record
- falsche Server-Autorität
- unbekannte Network-Metriken
- nicht katalogisierte Sync-Statuswerte

## Telegram-Grenze

Telegram bleibt Transport-/Identity-Bridge und ist ausdrücklich **nicht** Primärspeicher. Der Ranking-Code verarbeitet nur bereits bestätigte Datenobjekte; Abruf, Upload, Konfliktlösung und Serverbetrieb folgen in einer späteren Sync-Phase.
