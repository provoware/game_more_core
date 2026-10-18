# Venue Benefit Mechanic Audit – Publikumskraft

## Entscheidung

**NO-GO für eine mechanische Wirkung von `audience_pull` auf die aktuelle Event-Abrechnung.**

Der Wert ist als bestätigter, serverseitig berechneter Ortswert vorhanden und auf 0–100 begrenzt. Der versionierte Settlement-Vertrag speichert inzwischen bestätigte Venue-Evidence, besitzt aber weiterhin keinen katalogisierten Venue-Modifikator. Eine direkte Multiplikation oder ein versteckter Bonus würde deshalb eine zweite, unbelegte Wirkungsarchitektur erzeugen.

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

### 1. Read-only Property-Autorität ist jetzt vorhanden

`SETTLEMENT_MANIFEST.json` verlangt nur `event`, `economy` und `character`. `properties` und `property_upgrades` sind optionale read-only State-Blöcke. Zusätzlich setzt der Vertrag `scope_boundaries.property_changes` ausdrücklich auf `false`.

Die neue Evidence-Brücke beweist Event-Ort, bestätigten Besitz und den beim Abschluss geltenden `audience_pull`. Diese Autorität erlaubt eine gespeicherte Erklärung, aber noch keine neue Wirkung.

### 2. Receipt-Evidence ist kein katalogisierter Effekt

Die Settlement-Quelle kennt nur:

- `budget_delta_cents`
- `reputation_delta`
- `crew_stress_delta`
- `stability_delta`
- `heat_delta`

Es existiert kein `venue_audience_pull` und kein Venue-Multiplikator. Das neue Receipt-Feld `venue_evidence` hält ausschließlich einen bestätigten Ortsnachweis fest, keinen angewandten Bonus.

Ein Bonus direkt in bestehende Deltas einzurechnen würde die Ursache im Journal/Replay unsichtbar machen.

### 3. Replay speichert Evidence, nicht einen neuen Effekt

Der bestehende Recovery-Vertrag validiert Settlement gegen bereits angewandte Economy-, Character- und Phase-Records. Die versionierte Venue-Evidence wird nun im selben atomaren Journal-Commit gespeichert und bei Replay/Recovery unverändert übernommen. Event-, Character-, Besitz- und Revisionsbindung sind geprüft. Ein neuer Effekt wäre weiterhin separat zu katalogisieren und abzusichern.

### 4. Keine Balance-Regel vorhanden

Es gibt weiterhin keine freigegebene Formel, keinen aktivierten Cap und keine aktive Skalierung für einen mechanischen `audience_pull`-Effekt. Der unten auditierte Vorschlag ist noch keine Spielregel. Ein ad-hoc Prozentbonus wäre daher neue Balance-Autorität statt Nutzung eines bestehenden Vertrags.

### 5. Scene Jobs sind kein zulässiger Ausweichpfad

Der Scene-Job-Vertrag verbietet clientseitig eingespeiste Payout-/Effektmodifikatoren. `audience_pull` dort als schnellen Ersatz einzubauen würde ebenfalls den bestehenden Autoritätsvertrag umgehen.

## Audit-Freshness-Guard

Der NO-GO-Befund hängt bewusst von der **heutigen** Settlement-Oberfläche ab. Deshalb pinnt die fokussierte Regression jetzt die komplette für diese Entscheidung relevante Autoritätsfläche: erforderliche und optionale State-Blöcke, erlaubte Source Effects, Application-Ziele, Receipt-Invarianten **und die vollständigen Scope-Grenzen**.

Gerade die Scope-Grenzen sind wichtig: Würde dort später etwa `property_changes` freigegeben oder eine neue Venue-bezogene Grenze ergänzt, soll der Audit nicht still weiter als aktuell gelten. Jede Änderung dieser Oberfläche erzwingt deshalb eine erneute fachliche Bewertung.

Mit der Receipt-Brücke wurde die Bewertung bewusst aktualisiert: optionale Property-Eingaben und lesende Client-Anzeige sind erlaubt. Die Source Effects und die Sperre für Property-Änderungen bleiben unverändert. So kann mechanische Venue-Autorität nicht unbemerkt entstehen.

## Voraussetzungen für ein späteres GO

Ein späterer mechanischer Einsatz von `audience_pull` darf erst GO werden, wenn **ein einzelner kanonischer Zielpfad** folgende Punkte gemeinsam definiert:

1. eindeutige Zuordnung Event → eigene Location (Evidence-V1 umgesetzt),
2. autoritative Quelle des beim Abschluss geltenden `audience_pull` (Evidence-V1 umgesetzt),
3. deterministische und begrenzte Formel einschließlich Balancegrenzen,
4. Journal-/Receipt-Evidence für den tatsächlich angewandten Venue-Beitrag (Ortsnachweis vorhanden; angewandter Bonus weiterhin nicht definiert),
5. Replay/Recovery mit demselben Ergebnis,
6. fokussierte Regressionen für Minimum, Maximum, Reload und Idempotenz.

## Architekturgrenze

**Keine generische Venue-Bonusengine, kein Browserbonus, kein stiller Settlement-Multiplikator und kein zweiter Property-State.**

Bis ein Zielvertrag diese Anforderungen erfüllt, bleibt `POOL-PROPERTY-003` mechanisch gesperrt. Das vorhandene read-only Betriebsprofil bleibt davon unberührt.


## Begrenzter Ruf-Vorschlag – Audit vom 2026-10-18

Genau ein nicht-finanzieller Kandidat wurde geprüft. `A` ist die **gespeicherte** Publikumskraft des eigenen Orts beim Settlement, `D` das schon bestätigte Rufdelta aus `pending_settlement` vor einem möglichen Venue-Beitrag:

```text
B = min(2, A // 50, D // 4), falls eigener Ort bestätigt und D > 0
B = 0, sonst
```

Damit wäre der Zusatz auf **höchstens 2 Ruf und höchstens 25 % des positiven Basis-Rufdeltas je Event** begrenzt. Es gibt keinen Geld-, Energie-, Stress-, Heat- oder Stabilitätseffekt. Ein Event ohne positive bestätigte Folgen, ein fremder Ort oder ein kleiner Basisgewinn von 1–3 Ruf erzeugt keinen Zusatz.

| Publikumskraft A | Basis-Ruf D | vorgeschlagener Zusatz B |
|---|---:|---:|
| 49 | 8 | 0 |
| 50 oder 99 | 8 | 1 |
| 100 | 8 | 2 |
| 100 | 4 | 1 |
| 100 | 3, 0 oder negativ | 0 |

### Reproduzierbare Ergebnisse

```bash
PYTHONPATH=src python3 tools/venue_reputation_balance_audit.py
```

Das Tool ist ausschließlich ein read-only Auditwerkzeug und wird von keinem Gameplay-Pfad importiert. Es schreibt keine Spielstände und verändert keine Runtime-Regel.

- **40.602 Fälle**: alle ganzzahligen Publikumskraftwerte 0–100, Rufdeltas −100 bis +100 und beide Besitzfälle.
- **404 Zusatzfälle**: Deltas −10¹², −101, +101 und +10¹² über alle Publikumskraftwerte.
- **2.176 Ausbaukombinationen** aller sieben kaufbaren Orte gegen dieselbe Domain-Wertautorität geprüft; absolute/relative Caps, Monotonie und fehlender Bonus bei Verlust, Nullsaldo oder fremdem Besitz erfüllt.
- `signalwerk`: Publikumskraft 84–100 über alle erlaubten Ausbauten; Bühne Level 2 ergibt 94, Bühne Level 3 allein 99. Ein maximaler Publikumskraftwert ist also nicht allein durch den Bühnenausbau garantiert.
- `plattenstudio` erreicht weiterhin nur 48 Publikumskraft und erhielte mit diesem Vorschlag auch nach Ausbauten keinen Zusatz. Unterschiedliche Ortsarten wären damit bewusst nicht gleichwertig; das ist eine noch zu prüfende Balanceentscheidung.

### Verworfene Alternativen

Ein Gewinnmultiplikator wurde verworfen: Er würde zusätzliche Budget-Autorität und nachvollziehbare Ein- und Auszahlungen erfordern; der Ruf-Kandidat ist enger begrenzbar. Ein Nutzen-Bonus auf Scene Jobs wurde ebenfalls verworfen: Der bestehende Job-Vertrag erlaubt keine fremden Auszahlungsmodifikatoren, und Jobs haben keinen eigenen bestätigten Event-Ortsbezug.

### Entscheidung und Bedingungen

**Numerische Grenzen erfüllt; NO-GO für Aktivierung in der aktuellen Runtime.** Die Prüfung ist abgeschlossen, aktiviert aber bewusst keine neue Wirkung.

Vor einer Implementierung braucht es einen eigenen versionierten Wirkungsvertrag: gespeichertes Basisdelta D, Bonus B und Gesamtdelta müssen getrennt belegbar sein; die bisherigen Receipt-/Replay-Bindungen an `pending_settlement` dürfen nicht still verändert werden. Legacy-Receipts müssen bonusfrei lesbar bleiben. Exactly-once und Crash-Recovery sind für den neuen Beitrag erneut zu beweisen; ein Retry oder Reload darf den Bonus nie erneut erzeugen.

Die Exhaustivprüfung belegt keine langfristige Spielbalance. Wiederholte neue Events und mögliche Anreize zum absichtlichen Auslösen positiver Krisen wurden nicht als Spielschleife simuliert. Vor einem mechanischen GO sind deshalb mehrfache Events, Location-Vergleich und ein zielgerichteter Playtest erforderlich. Der heutige Ortswert aus der Vergleichsanzeige darf niemals den historischen Effekt neu bestimmen.
