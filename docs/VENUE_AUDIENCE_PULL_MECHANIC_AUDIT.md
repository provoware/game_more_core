# Venue Benefit Mechanic Audit – Publikumskraft

## Entscheidung

**NO-GO für eine mechanische Wirkung von `audience_pull` auf die aktuelle Event-Abrechnung.**

Der Wert ist als bestätigter, serverseitig berechneter Ortswert vorhanden und auf 0–100 begrenzt. Der bestehende Settlement-Vertrag besitzt aber weder Property-/Upgrade-State als Eingabe noch einen katalogisierten Venue-Modifikator. Eine direkte Multiplikation oder ein versteckter Bonus würde deshalb eine zweite, unbelegte Wirkungsarchitektur erzeugen.

## Geprüfter Einzelkandidat

Diese Iteration prüft ausschließlich:

`property_upgrades.effective_values.audience_pull` → bestehende Event-Abrechnung (`settlement`)

Andere Ortswerte und andere Zielsysteme werden hier bewusst nicht mitentschieden.

## Bestätigte Ausgangslage

- `audience_pull` gehört zu den fünf katalogisierten Upgrade-Werten.
- Die Projection begrenzt Ortswerte auf `[0, 100]`.
- Upgrades dürfen den Wert serverseitig verändern; der Client besitzt keine Kosten- oder Level-Autorität.
- Die bestehende Upgrade-Projection erklärt ausdrücklich, dass Gameplay-Event-Regeln dadurch noch nicht verändert werden.

## Warum die Event-Abrechnung heute NO-GO ist

### 1. Keine Domain-Autorität für Property-State

`SETTLEMENT_MANIFEST.json` verlangt nur `event`, `economy` und `character`. `property` oder `property_upgrades` sind keine erforderlichen State-Blöcke. Zusätzlich setzt der Vertrag `scope_boundaries.property_changes` ausdrücklich auf `false`.

Damit kann Settlement aktuell nicht autoritativ beweisen, welcher eigene Ort zum abzurechnenden Event gehört und welcher bestätigte `audience_pull`-Wert dafür gelten soll.

### 2. Kein katalogisierter Effekt oder Receipt

Die Settlement-Quelle kennt nur:

- `budget_delta_cents`
- `reputation_delta`
- `crew_stress_delta`
- `stability_delta`
- `heat_delta`

Es existiert kein `venue_audience_pull`, kein Venue-Multiplikator und kein Receipt-Feld, das einen angewandten Ortsbeitrag nachvollziehbar festhält.

Ein Bonus direkt in bestehende Deltas einzurechnen würde die Ursache im Journal/Replay unsichtbar machen.

### 3. Replay wäre fachlich mehrdeutig

Der bestehende Recovery-Vertrag validiert Settlement gegen bereits angewandte Economy-, Character- und Phase-Records. Ohne explizite Venue-Quelle oder gespeicherten Beitrag wäre später nicht eindeutig rekonstruierbar, welcher Ortswert den Effekt erzeugt hat.

### 4. Keine Balance-Regel vorhanden

Es gibt weder Formel noch Cap noch Skalierung für einen mechanischen `audience_pull`-Effekt. Ein ad-hoc Prozentbonus wäre daher neue Balance-Autorität statt Nutzung eines bestehenden Vertrags.

### 5. Scene Jobs sind kein zulässiger Ausweichpfad

Der Scene-Job-Vertrag verbietet clientseitig eingespeiste Payout-/Effektmodifikatoren. `audience_pull` dort als schnellen Ersatz einzubauen würde ebenfalls den bestehenden Autoritätsvertrag umgehen.

## Audit-Freshness-Guard

Der NO-GO-Befund hängt bewusst von der **heutigen** Settlement-Oberfläche ab. Deshalb pinnt die fokussierte Regression jetzt die komplette für diese Entscheidung relevante Autoritätsfläche: erforderliche und optionale State-Blöcke, erlaubte Source Effects, Application-Ziele, Receipt-Invarianten **und die vollständigen Scope-Grenzen**.

Gerade die Scope-Grenzen sind wichtig: Würde dort später etwa `property_changes` freigegeben oder eine neue Venue-bezogene Grenze ergänzt, soll der Audit nicht still weiter als aktuell gelten. Jede Änderung dieser Oberfläche erzwingt deshalb eine erneute fachliche Bewertung.

So kann neue Property-/Venue-Autorität nicht unbemerkt entstehen, während diese Dokumentation fälschlich weiter einen alten Zustand behauptet.

## Voraussetzungen für ein späteres GO

Ein späterer mechanischer Einsatz von `audience_pull` darf erst GO werden, wenn **ein einzelner kanonischer Zielpfad** folgende Punkte gemeinsam definiert:

1. eindeutige Zuordnung Event → eigene Location,
2. autoritative Quelle des zum Zeitpunkt der Wirkung geltenden `audience_pull`,
3. deterministische und begrenzte Formel einschließlich Balancegrenzen,
4. Journal-/Receipt-Evidence für den tatsächlich angewandten Venue-Beitrag,
5. Replay/Recovery mit demselben Ergebnis,
6. fokussierte Regressionen für Minimum, Maximum, Reload und Idempotenz.

## Architekturgrenze

**Keine generische Venue-Bonusengine, kein Browserbonus, kein stiller Settlement-Multiplikator und kein zweiter Property-State.**

Bis ein Zielvertrag diese Anforderungen erfüllt, bleibt `POOL-PROPERTY-003` mechanisch gesperrt. Das vorhandene read-only Betriebsprofil bleibt davon unberührt.
