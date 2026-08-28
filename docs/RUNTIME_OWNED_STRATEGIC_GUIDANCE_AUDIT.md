# Runtime-owned Strategic Guidance Audit

## Ziel

Prüfen, ob BUNKERFREQUENZ jetzt schon einen gemeinsamen read-only Vertrag für strategische Hinweise braucht, ohne Energie-, Geld-, Markt- oder Eventregeln im Browser nachzubauen.

## Geprüfte Signale

### 1. Scene Job: reduzierter Lohn durch Energie

Die Scene-Jobs-Projektion besitzt bereits einen sicheren fachlichen Anker:

- `build_scene_jobs_projection(...)` liest den bestätigten Character-State.
- Die Auszahlungsvorschau wird mit `calculate_scene_job_payout_cents(...)` aus dem bestehenden Scene-Job-Service berechnet.
- Die Projection liefert `effective_payout_cents` und das explizite Bool `payout_reduced_by_energy`.
- Der Browser rendert dieses Bool nur. Er entscheidet nicht selbst anhand eines Energie-Grenzwerts, ob der Lohn reduziert ist.

Damit ist die Aussage **„Der aktuelle Joblohn ist wegen Energie reduziert“** bereits runtime-/projection-owned. Daraus folgt aber noch nicht automatisch die Strategie **„Du solltest dich jetzt erholen“**. Eine Recovery-Aktion hat eigene Stresskosten und bleibt eine Spielerentscheidung.

### 2. Event: bestätigter Blocker

Die A4-Projektion bezieht Event-Aktionen direkt aus `EventExecutionService.available_actions(event)` und übernimmt deren `enabled`- und `blockers`-Felder.

Die bestehende Next-Action-Hilfe kopiert nur den bereits gerenderten Blocker-Klartext. Sie wertet dafür weder Budget noch Equipment noch Safety selbst aus.

Damit ist **„Dieses Event ist aus Grund X blockiert“** ein sicherer Runtime-Fakt. Auch daraus entsteht noch keine allgemeine Strategie über Jobs, Recovery, Handel oder Property.

## Vergleich

| Signal | Fachquelle | Browser darf | Browser darf nicht |
|---|---|---|---|
| Joblohn reduziert | Scene-Job-Service → Scene-Jobs-Projection | `payout_reduced_by_energy` und bestätigte Beträge anzeigen | Energiegrenze oder Auszahlung selbst berechnen |
| Event blockiert | EventExecutionService → Event-Projection | bestätigten Blocker erklären | Budget/Equipment/Safety selbst zu einem Blocker ableiten |

## Entscheidung

**Kein neuer gemeinsamer `strategic_guidance`-/Recommendation-Vertrag in dieser Iteration.**

Begründung:

1. Beide geprüften Fälle besitzen bereits eindeutige zuständige Projections.
2. Ein globaler Aggregator würde dieselben Fakten kopieren und müsste anschließend entscheiden, welcher Hinweis wichtiger ist.
3. Diese Priorisierung wäre bereits der Beginn einer zweiten Recommendation-Engine, solange keine fachliche Runtime-Priorität existiert.
4. Der Browser braucht keine neue Logik, um die vorhandenen Fakten korrekt zu erklären.

Der kleinste sichere Ausbau ist deshalb **nicht ein neues Schema**, sondern die bestehende Grenze verbindlich festzuhalten: domänenspezifische Projections dürfen explizite Fakten und Gründe liefern; die globale Führung darf sie erst dann zusammenführen, wenn die Runtime zusätzlich eine eindeutige Priorität oder einen eigenen Empfehlungstyp bestätigt.

## Fail-closed-Regel

- Fehlt ein bestätigter Character-State, gibt es keinen energiebezogenen Job-Hinweis.
- Fehlt ein bestätigter Event-Blocker, darf die globale Führung keinen Blocker erfinden.
- Aus einem reduzierten Joblohn darf nicht automatisch „Recovery starten“ werden.
- Aus Bargeld, Marktpreis, Energie oder Stress darf der Browser keine beste Aktion berechnen.
- Kein Hinweis führt automatisch einen Command aus.

## Regression

`tests/presentation/test_runtime_owned_strategic_guidance_audit.py` schützt:

- die kanonische serverseitige Job-Lohnberechnung;
- das explizite Projection-Bool `payout_reduced_by_energy`;
- den rein darstellenden Browserverbrauch;
- die Event-Blocker-Quelle `EventExecutionService.available_actions(...)`;
- das Fehlen von Energie-/Geld-/Markt-Heuristik in der globalen Next-Action-Hilfe;
- die bewusste Entscheidung gegen einen zweiten globalen Recommendation-Vertrag.

## Nächster fachlicher Trigger

Ein gemeinsamer Hinweisvertrag wird erst neu bewertet, wenn mindestens ein echter Bedarf entsteht, mehrere gleichzeitig gültige Hinweise **fachlich** zu priorisieren. Dann muss die Priorität aus Runtime/Application/Projection kommen und darf nicht aus DOM-Reihenfolge, Farbe, Geldbetrag oder Browserlogik entstehen.
