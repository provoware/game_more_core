# 0.8.3-B – Crisis Engine + Berlin Ops Map Foundation

## Ziel

0.8.3-B macht aus dem linearen Eventablauf erstmals eine echte Entscheidungsschicht und legt parallel die stabile Datenbasis für eine stilisierte Berlin-Handlungskarte an.

## B1 – Crisis / Incident Engine (implementiert)

### Ablauf

```text
Event.phase = live
      ↓
IncidentService.open(...)
      ↓ atomarer Commit
Event.phase = crisis
IncidentState.active = Incident
      ↓
Response auswählen
      ↓
IncidentService.resolve(...)
      ↓ atomarer Commit
IncidentState.history += Ergebnis
pending_settlement += bestätigte Folgen
Event.phase = live | teardown | cancelled
```

### Warum Folgen zunächst `pending_settlement` sind

0.8.2 hat festgelegt, dass Event-Budget nur durch bestätigte Economy-Transaktionen verändert wird. Die Crisis Engine darf diesen Vertrag nicht umgehen. Deshalb werden bestätigte Krisenfolgen zunächst im Incident-State gesammelt und erst in 0.8.3-C über die zuständigen Economy-/Character-/Reputation-Wege gebucht.

### Incident-State

- `event_id` – bindet den Block an genau ein Event.
- `active` – höchstens ein aktuell offener Incident.
- `history` – abgeschlossene Incidents mit gewählter Reaktion und bestätigten Effekten.
- `pending_settlement` – kumulierte Budget-, Ruf-, Stress-, Stabilitäts- und Heat-Folgen.
- `revision` – monotone Incident-Revision.

### Incident-Katalog

Die erste Stufe enthält sechs Typen:

1. Stromausfall / Power Drop
2. Security-Probleme
3. Equipment-Ausfall
4. verspäteter Act
5. Crowd Overload
6. Lärmdruck

Jeder Typ besitzt genau drei konkrete Reaktionswege. Die Schwere liegt zwischen 1 und 5; Effekte werden deterministisch relativ zur katalogisierten Basisschwere skaliert.

### Sicherheits-/Integritätsregeln

- B1-Incidents entstehen nur aus `live`.
- Nur ein Incident kann gleichzeitig aktiv sein.
- `JournalContext.entity_id` muss zum bestätigten Event passen.
- Öffnen und Event-Phasenwechsel liegen in derselben Persistenztransaktion.
- Auflösen und Folge-Phasenwechsel liegen ebenfalls in derselben Persistenztransaktion.
- gleiche `command_id` + gleicher Request ist idempotent.
- gleiche `command_id` + anderer Request schlägt fail-closed fehl.
- Recovery replayt Event- und Incident-State gemeinsam.

## B2 – Berlin Ops Map (Foundation)

### Zweck

Die Karte ist eine **stilisierte Spielkarte**, keine Navigation. Sie verwendet normierte Koordinaten von 0 bis 100 und kann später unabhängig von Bildschirmgröße, Renderer oder Framework skaliert werden.

### Stilrichtung

**Retro-Autokarte × moderner Control Room**

- entsättigte kartografische Grundfläche
- transparente Bezirkszonen
- kontrastreiche Neonmarker
- Score-/Tier-Hervorhebung
- Halo, Pulse und Ranking-Badges für Premium-Orte
- statische Ersatzdarstellung bei Reduced Motion

### Startumfang

- 8 Bezirke
- 12 Spielorte
- 7 kaufbare Objekte
- 10 katalogisierte Ausbauarten
- eine eindeutige **Hall of Tribute**

### Ortswerte

Jeder Ort besitzt Werte von 0 bis 100:

- `prestige`
- `audience_pull`
- `risk`
- `underground_factor`
- `utility`

Der Projection-Score wird ausschließlich aus diesen bestätigten Manifestwerten berechnet. Daraus entstehen die vier visuellen Tiers:

- `legendary`
- `prime`
- `strong`
- `standard`

### Bezirkswerte – bereits vorbereitet, noch nicht persistent

- `heat`
- `prestige`
- `police_pressure`
- `scene_activity`

0.8.3-B2 kann diese Werte read-only projizieren und für Tests überschreiben. Persistente Veränderungen durch Events, Immobilien oder Krisen folgen erst in einem eigenen Slice.

### Immobilien-Ausbaupfade

Der Datenvertrag kennt bereits Slots für:

- Schallschutz
- Stromversorgung
- Fluchtwege
- Deko
- Bühne
- Bar
- Lager
- Sicherheitsraum
- Studio
- Büro

Kauf, Besitz und Ausbau selbst werden noch nicht geschrieben. Dadurch wird die spätere Economy-Erweiterung vorbereitet, ohne 0.8.2 zu duplizieren.

## Hall of Tribute

Die Hall of Tribute ist genau einmal im Manifest vorhanden und `ranking_enabled`.

Für die spätere Präsentation sind unter anderem folgende satirische Titel vorbereitet:

- Lärmadel
- Bunkerbaron
- Kabelkönig
- Pegelpapst
- Stromheiland
- Bassbeauftragter
- Betonlegende
- Nachtminister

## Abnahme / Testmatrix

| Bereich | Test |
|---|---|
| Incident-Lifecycle | `live → crisis → live/teardown` |
| Severity | deterministische Skalierung |
| Response-Gate | falsche Response fail-closed |
| Parallelkrise | zweiter aktiver Incident blockiert |
| Idempotenz | Open + Resolve wiederholbar ohne Doppelwirkung |
| Recovery | Crash nach durable Journal wird vollständig replayt |
| Karte | exakt eine Hall of Tribute |
| Karte | Location-Scores/Tiers deterministisch |
| Districts | Heat/Prestige/Polizeidruck/Szeneaktivität 0–100 |
| Immobilien | Kaufpreis + gültige Ausbau-Slots |
| Ownership-Projektion | unbekannte Property-ID fail-closed |

## Bewusst nicht Bestandteil von 0.8.3-B

- direkte Buchung der Krisenfolgen auf Economy/Character/Reputation
- persistente Bezirksdynamik
- Immobilienkauf oder Ausbau
- echte Karten-/Straßennavigation
- High-End-Renderer oder animierter Client
- saisonale Ranking-Auswertung

## Nächster logischer Schritt

**0.8.3-C – Settlement & Consequences:** `pending_settlement` über die vorhandenen Economy-/Character-Verträge atomar buchen, `event.completed` erzeugen und den vollständigen Ablauf `Event → Krise → Abrechnung → Save → Recovery` testen.

Danach kann die Berlin Ops Map schreibend angebunden werden, ohne eine zweite Spiellogik zu erzeugen.
