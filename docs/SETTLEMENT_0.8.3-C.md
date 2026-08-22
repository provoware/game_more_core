# 0.8.3-C – Settlement & Consequences

## Zweck

0.8.3-C schließt den fachlichen Event-Loop. Ein Event darf erst von `settlement` nach `completed` wechseln, wenn alle bereits bestätigten Incident-Folgen genau einmal verarbeitet und gemeinsam dauerhaft geschrieben wurden.

Der Settlement-Service erfindet keine neuen Krisenfolgen. Seine einzige Quelle ist `IncidentState.pending_settlement`.

## Verbindlicher Ablauf

```text
Event.phase = settlement
+ EconomyState vorhanden
+ CharacterState vorhanden
+ IncidentState.active = null
+ pending_settlement bestätigt
        ↓
SettlementService.complete(...)
        ↓
1. Economy-Ledger: budget_delta_cents
2. Character-Ressourcen: crew_stress_delta
3. Character-Ruf: reputation_delta
4. Biografie: bestätigter Eventabschluss
5. Eventphase: settlement → completed
6. event.completed + SettlementState
        ↓
Incident pending_settlement = 0
SettlementState.status = completed
Event.phase = completed
```

Alle sechs Journalrecords gehören zu **einem** Persistence-Commit. Ein Crash darf deshalb keinen fachlich halben Abschluss erzeugen.

## Geld

`budget_delta_cents` wird nicht direkt am Event vorbei geschrieben. 0.8.3-C erweitert das vorhandene Economy-Ledger um genau eine neue, nicht kompensierbare Buchungsart:

```text
kind = settlement
item_id = __event_settlement__
quantity = 1
unit_price_cents = 0
```

Der Betrag steht ausschließlich in `budget_delta_cents`. Eine Settlement-Buchung verändert den Markt-Tick nicht, weil sie kein Kauf-/Verkaufsvorgang ist.

Ein Endbudget unter `0` ist in 0.8.3-C1 nicht erlaubt. Eine spätere Schulden-/Finanzierungsregel darf nicht durch stilles Klemmen oder negative Eventbudgets vorweggenommen werden.

## Character-Folgen

### Stress

`crew_stress_delta` wird über `character.resources_changed` angewandt und wie alle Character-Ressourcen auf `0..100` begrenzt.

### Ruf

`reputation_delta` wird über den neuen Journaltyp `character.reputation_changed` angewandt. Der Replay-Vertrag prüft `old + delta = new` und den bestätigten Ausgangswert.

Der Settlement-Character muss dem Event als Crewmitglied zugeordnet sein. So kann ein Eventabschluss nicht versehentlich den falschen Character verändern.

## Stabilität und Heat

`stability_delta` und `heat_delta` werden **bestätigt und aus `pending_settlement` verbraucht**, aber 0.8.3-C macht daraus bewusst noch keinen persistenten Bezirkszustand.

Sie bleiben im unveränderlichen `SettlementState.effects` als abgeschlossenes Event-Ergebnis. Die spätere dynamische Bezirkslage kann diese bestätigten Ergebnisse verarbeiten, ohne den Eventabschluss neu zu berechnen.

Damit bleibt die Scope-Grenze von 0.8.3-B2 erhalten:

- keine persistente Bezirks-Simulation,
- kein Polizeidruck-Update,
- keine Scene-Activity-Buchung,
- kein Map-Schreibweg.

## Incident-Verbrauch

Nach erfolgreichem Settlement:

- `IncidentState.history` bleibt byte-/inhaltsgleich,
- `active` bleibt `null`,
- alle fünf Werte in `pending_settlement` werden auf `0` gesetzt,
- die Incident-Revision steigt exakt um `1`.

`SettlementState.incident_ids` hält fest, welche Incident-Historie dem Abschluss zugrunde lag.

## Eventabschluss

Der allgemeine `EventStateService.transition_phase(...)` darf `completed` nicht mehr direkt erzeugen. Dieser Zielzustand ist für `SettlementService` reserviert.

Der Settlement-Commit enthält zunächst die Budgetänderung, danach den kanonischen Phasenrecord

```text
event.phase_changed
reason = event_settlement:complete
```

und abschließend `event.completed`.

## Recovery

Beim Replay gilt dieselbe Reihenfolge wie beim Commit:

1. Economy-Replay stellt Ledger + neues Budget her.
2. Character-Replay stellt Stress und Ruf her.
3. Event-Phasenreplay stellt `completed` her.
4. `event.completed` prüft diese Zwischenresultate gegen den Settlement-Receipt.
5. Erst dann werden `pending_settlement` geleert und `SettlementState` eingesetzt.

Bei widersprüchlichen Revisionen, Event-IDs, Character-IDs, Budgetwerten, Stress-/Rufwerten oder Incident-Folgen bricht Recovery fail-closed ab.

## Idempotenz

Die Event-ID `<command_id>:completed` ist der kanonische Abschlussmarker.

- gleiche Command-ID + gleicher Abschlussrequest → idempotenter Replay,
- gleiche Command-ID + anderer Request → Fehler,
- falsche `entity_id` → Fehler, auch beim Replay,
- zweites fachliches Settlement desselben Saves → Fehler.

## Biografie

Ein bestätigter Eventabschluss erzeugt genau einen `character.biography_entry_added`-Record der Kategorie `event`. Sichtbare Texte verwenden die bereits katalogisierten Biography-Keys; der Journalrecord enthält zusätzlich Event-ID, Incident-Anzahl und die bestätigten Settlement-Deltas als Platzhalterdaten.

## Nicht Bestandteil von 0.8.3-C

- kein Kartenrenderer,
- keine persistente Bezirksdynamik,
- kein Immobilienkauf/-ausbau,
- keine saisonalen Rankings,
- kein Telegram-/Network-Sync,
- kein schreibender A4-Client.

Diese Systeme bauen anschließend auf einem vollständig abgeschlossenen und recovery-fähigen Event-Loop auf.
