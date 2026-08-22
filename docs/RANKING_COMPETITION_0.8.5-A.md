# Competitive Ranking 0.8.5-A

## Ziel

Das Ranking bleibt aus bestätigten Character-/Network-Daten abgeleitet, erhält aber einen echten Konkurrenzzyklus. Besonders die ersten zehn Plätze sollen sich sichtbar gegenseitig verdrängen können, ohne dass gleiche Messwerte zu gleichen Rangnummern führen.

## Grundregel: kein Gleichstand

Rangnummern sind immer eindeutig:

```text
Platz 1
Platz 2
Platz 3
...
```

Zwei Spieler können denselben aktuellen Messwert besitzen, aber niemals denselben Rang.

## Verdrängungsregel bei gleichem aktuellen Wert

Der aktuelle Messwert bleibt die wichtigste Größe. Erst wenn zwei Spieler denselben aktuellen Wert besitzen, entscheidet die Entwicklung seit dem vorherigen Ranking-Zyklus:

1. höheres druckgewichtetes Momentum,
2. bisheriger Rang,
3. stabile `character_id` als letzter deterministischer Fallback.

Beispiel:

```text
Zyklus 1
A: Wert 10 → Platz 1
B: Wert  9 → Platz 2

Zyklus 2
A: Wert 10 → Veränderung 0
B: Wert 10 → Veränderung +1

Ergebnis
B: Platz 1 ↑
A: Platz 2 ↓
```

B hat A eingeholt und verdrängt ihn. A bleibt nicht aufgrund des alten Platzes künstlich vorne.

## Top-10-Druck

Für Spieler, die im vorherigen Zyklus auf Platz 1–10 standen, wird die Messwertveränderung mit Faktor `1.0` als Momentum berücksichtigt.

Ab dem bisherigen Platz 11 gilt Faktor `0.1`.

Dadurch bleibt die Top 10 die deutlich umkämpftere Zone. Das Feld darunter bewegt sich ebenfalls weiter, aber Momentum wirkt dort nur zu einem Zehntel. Der eigentliche aktuelle Messwert wird dabei niemals künstlich reduziert: Wer klar bessere Werte erreicht, kann weiterhin in die Top 10 aufsteigen.

## Ranking-Zyklus

`build_ranking_network_projection(...)` kann optional den `cycle_snapshot` des vorherigen Laufs als `previous_cycle` erhalten.

Der neue Lauf liefert wiederum einen Snapshot:

```json
{
  "sort_by": "reputation",
  "skill_id": null,
  "entries": [
    {"character_id": "char.a", "rank": 1, "value": 42},
    {"character_id": "char.b", "rank": 2, "value": 42}
  ]
}
```

Der Snapshot ist klein, rendererunabhängig und enthält nur die für den nächsten Rankingvergleich notwendigen bestätigten Werte.

## Bewegungsdaten

Jeder gerankte Eintrag liefert zusätzlich:

- `previous_rank`
- `previous_value`
- `metric_delta`
- `momentum_factor`
- `effective_momentum`
- `movement`: `up`, `down`, `same`, `new` oder `unranked`
- `rank_delta`
- aktuelle Konkurrenzzone `top10` oder `open_field`

Diese Angaben sind Darstellungshilfen. Sie verändern keine Character-, Event- oder Economy-Zustände.

## Erste Runde ohne Historie

Fehlt ein vorheriger Zyklus, wird nicht geraten. Gleiche Werte werden deterministisch nach stabiler `character_id` auf eindeutige Plätze verteilt. Ab dem zweiten Zyklus kann echte Auf-/Abstiegsdynamik berücksichtigt werden.

## Bestehende Grenzen bleiben bestehen

- keine erfundenen Network-Werte,
- keine Online-/Presence-Ableitung,
- Events/Clubs nur aus bestätigten Network-Datensätzen,
- sichtbare Namen sind keine Identifikatoren,
- Ranking ist weiterhin eine Projection und schreibt keinen Domain-State.

## Abnahme

Gezielte Regression:

```bash
PYTHONPATH=src python3 -m unittest tests.presentation.test_ranking_network -v
```

Remote auf demselben finalen PR-Head:

- Runtime Core
- Presentation Core
- Repository Health
