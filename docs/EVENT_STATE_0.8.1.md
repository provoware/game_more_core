# Event State Foundation 0.8.1

## Zweck

0.8.1 führt den ersten kanonischen Eventzustand ein. Er verbindet den bereits validierten Character-/Persistence-Kern mit der kommenden Event-/Wirtschaftsschicht, ohne Markt-, Inventar- oder Abrechnungslogik aus 0.8.2/0.8.3 vorwegzunehmen.

## Kanonischer State-Block

Der Save-Zustand erhält optional den Block `event`.

```text
state
├─ character   bestehender Character-Forge-Zustand
└─ event       EventState 0.8.1
```

`EventState` enthält:

| Feld | Bedeutung |
|---|---|
| `event_id` | unveränderliche technische ID |
| `display_name` | sichtbarer Eventname |
| `location` | Ort, Region und verifizierter Zugangsstatus |
| `budget_cents` | Event-Budgetrahmen in Cent |
| `acts` | geplante/bestätigte/cancelled Acts |
| `crew` | Character-Zuordnung mit Rolle und Status |
| `equipment` | Event-Anforderungen/Readiness, noch kein Inventarbesitz |
| `time_window` | Start/Ende mit UTC-Offset + Zeitzone |
| `safety_status` | `unreviewed`, `cleared`, `restricted`, `blocked` |
| `phase` | Eventphase |
| `revision` | monotone Revision für Stale-Write-Schutz |

## Phasenmaschine

```text
draft
  ↓
planning
  ↓
procurement
  ↓
transport
  ↓
setup
  ↓
soundcheck
  ↓
live ↔ crisis
  ↓       ↓
teardown ←
  ↓
settlement
  ↓
completed
```

`cancelled` ist aus den dafür freigegebenen Vor-/Krisenphasen erreichbar und terminal.

Rücksprung `procurement → planning` ist erlaubt, weil Beschaffung Planungsänderungen erzwingen kann. Andere Rücksprünge sind bewusst blockiert.

## Sicherheitsgate

Ab `transport` beginnt eine physische Eventphase. Dafür müssen gleichzeitig gelten:

1. `location` ist gesetzt.
2. `location.access_status` ist nicht `unverified`.
3. `time_window` ist gesetzt und zeitlich gültig.
4. `safety_status == cleared`.

Damit kann der Eventkern keine reale Aufbau-/Live-Phase auf einem ungeklärten Ort freigeben. Ein Ort darf `fictionalized`, `authorized` oder `public` sein; aus einem Namen allein wird keine Zugangsberechtigung abgeleitet.

## Journalvertrag

0.8.1 verwendet drei zustandsbildende Eventtypen:

- `event.created`
- `event.planning_updated`
- `event.phase_changed`

Die bereits vorhandenen Typen `event.started`, `event.incident_resolved` und `event.completed` bleiben kompatibel reserviert und werden erst mit dem vollständigen Event-Loop semantisch belegt.

Jeder Event-Command verwendet:

```text
event_id        = <command_id>:event
transaction_id  = tx:<command_id>
```

Eine wiederholte identische Command-ID ist idempotent. Dieselbe Command-ID mit anderem Inhalt wird abgewiesen.

## Planungsupdates

Direkt editierbar sind nur:

- `display_name`
- `location`
- `budget_cents`
- `acts`
- `crew`
- `equipment`
- `time_window`
- `safety_status`

Direkte Planungsänderungen sind nur in `draft`, `planning` und `procurement` erlaubt. Nach Beginn von `transport` müssen spätere Änderungen über explizite Event-/Krisenregeln modelliert werden; diese folgen in 0.8.3.

## Koexistenz mit Character Forge

0.8.1 behebt eine notwendige Zustandsgrenze: Character- und Profil-Commits ersetzen nicht mehr den gesamten abgeleiteten Save-Inhalt, sondern nur ihren eigenen `character`-Block. Dadurch bleibt `event` erhalten.

Analog ersetzt `EventStateService` ausschließlich `event`.

`GameRecoveryService` kombiniert Character- und Event-Replay:

```text
Journalrecord
   ↓
replay_character_event(...)
   ↓
replay_event_state_event(...)
   ↓
vollständiger abgeleiteter Save-Zustand
```

Damit sind Snapshot/Journal-Recovery und zukünftige gemischte Character-/Eventtransaktionen vorbereitet.

## Bewusst nicht Teil von 0.8.1

### 0.8.2

- dynamische Marktpreise
- Kaufen/Verkaufen/Verbrauchen
- Inventarbesitz
- Economy-Ledger
- Budgetabbuchungen aus bestätigten Käufen

### 0.8.3

- vollständige Eventaktionen je Phase
- Transport-/Aufbau-/Soundcheck-/Live-/Krisenregeln
- Abbau und Abrechnung
- Ruf- und Character-Folgen
- Eventfeedback/Presentation des kompletten Loops

## Abnahmeinvarianten

0.8.1 gilt nur dann als bestanden, wenn:

1. EventState strikt validiert und serialisierbar ist.
2. IDs in Acts/Crew/Equipment innerhalb ihrer Liste eindeutig sind.
3. Zeitfenster offset-aware und vorwärtsgerichtet sind.
4. illegale Phasenwechsel blockiert werden.
5. physische Phasen das Sicherheitsgate erzwingen.
6. Event-Commands idempotent und stale-revision-sicher sind.
7. Eventänderungen journalisiert und replaybar sind.
8. Recovery einen durable, aber noch nicht in State angewendeten Event-Commit rekonstruieren kann.
9. Character- und Event-State-Blöcke gegenseitig erhalten bleiben.
10. Runtime Core, Presentation Core und Repository Health remote grün sind.
