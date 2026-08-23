# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.7-C4A – read-only Ereignis-Timeline Projection/Textschicht` · PR #98 · Merge `4909fb9f7169baaa5b802e497cdba3e2c6da0dae`
- **0.8.7-C1 District-Event-Vertrag/Katalog:** PR #90 · `SAFE MERGE PASS` · Merge `337f8ad8f9719ec3389c372da9688bbbec593c16`
- **0.8.7-C2 District-Event Runtime:** PR #91 · `SAFE MERGE PASS` · Merge `5e32d6de2a5859b1cadca62543dd10949717e4fc`; anschließend Katalog-Fail-fast über PR #92 gehärtet
- **0.8.7-C3 Application-Integration:** PR #95 · `SAFE MERGE PASS` · Merge `fb62c5226997462cc2a9adc67529a7691e16ae2b`
- **0.8.7-C4A Timeline-Projection:** PR #98 · `SAFE MERGE PASS` · Merge `4909fb9f7169baaa5b802e497cdba3e2c6da0dae`
- **District-Event-Robustheit:** `no_eligible_event` wird als expliziter schreibfreier No-op behandelt; kein künstliches Ersatz-Ereignis
- **Aktive Entwicklungsstufe:** `0.8.7-C4B – sichtbares Control Deck`; C4A ist Daten-/Textquelle, C4B bleibt reine Presentation
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; ein neuer Produktrelease benötigt weiterhin eine eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.1–0.8.6 – Kernspiel, Living World, Property & Map

- [x] Character Forge, Event-State, Economy, Crisis und Settlement
- [x] schreibender lokaler A4-Client mit Save/Snapshot/Recovery
- [x] Competitive Ranking, Profilpersonalisierung und replaybare Street Encounters
- [x] persistente Living Districts
- [x] Property Purchase + Property Upgrades
- [x] Berlin Ops Map PRO mit 8 Districts, 12 Locations, Eigentum/Ausbau und read-only Filtern

## 0.8.7-A – Saisonale Hall of Tribute ✅

- [x] Wochen- und Monatszyklen mit explizitem Saisonvertrag
- [x] bestehende Competitive-Ranking-Engine wiederverwendet
- [x] `game_world_time` aus abgeschlossenem bestätigtem Event als stabiler lokaler Anker
- [x] Systemzeit niemals alleinige Saisonautorität
- [x] endgültige Titel nur bei geschlossenem bestätigtem Zyklus + echter bestätigter Konkurrenz
- [x] lokale Einzelspieler-Hall vergibt keine Fake-Championtitel
- [x] Wochen-/Monatssicht im A4-Client
- [x] `/safe-merge` PASS · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`

## 0.8.7-B – Control Deck & Player Choices ✅

- [x] Sticky HUD und Schnellnavigation
- [x] Kompaktmodus, hoher Kontrast und große Schrift ausschließlich lokal
- [x] vier Street Approaches mit katalogisierten Auswahlgewichten
- [x] Encounter bleibt einzige Effekt-Autorität
- [x] Krisenentscheidungen zeigen katalogisierte Folgen vor dem Klick
- [x] Browser sendet weiterhin nur erlaubte IDs
- [x] `/safe-merge` PASS · Merge `4d1a35bfbc086d07599b6ec7b3816e830bcea995`

## 0.8.7-C1 – District-Event-Vertrag/Katalog ✅

- [x] vorhandenen DistrictState-Vertrag als einzige Metrik-/Bounds-Basis referenzieren
- [x] vier Ereignisse mit stabilen IDs, Gewichten, Voraussetzungen und kleinen Effekten definieren
- [x] Auswahlvertrag deterministisch/replaybar halten; Systemzeit nie als Seed
- [x] Browser-Aktivierung und Browser-Effektwerte ausdrücklich verbieten
- [x] deutsche Story-Texte separat von Spiellogik katalogisieren
- [x] gezielte Vertragsregressionen ergänzen
- [x] `/safe-merge` PASS · Merge `337f8ad8f9719ec3389c372da9688bbbec593c16`

## 0.8.7-C2 – District-Event Runtime ✅

- [x] Auswahlservice aus bestätigtem `world_seed + district_id + trigger_id` implementieren
- [x] Voraussetzungen vor der gewichteten Auswahl gegen aktuellen DistrictState prüfen
- [x] bestätigte Folgen über den vorhandenen `DistrictService` und `world.district_effect_applied` journalisieren
- [x] derselbe District-/Trigger-Kontext darf auch bei verändertem Retry-Seed nicht erneut würfeln oder doppelt anwenden
- [x] vorhandenen District-Recovery-Pfad für den resultierenden Journalrecord regressiv absichern
- [x] ungültigen District-Kontext vor jedem Write ablehnen
- [x] Runtime-Katalog beim Initialisieren vollständig auf IDs, Gewichte, Voraussetzungen, Metriken und Effektgrenzen prüfen
- [x] ungültige Katalogeinträge nennen Event-ID und Feldpfad statt nur die Vertragsart (QA-003 / PR #94)
- [x] kein zulässiges Ereignis ist ein expliziter `no_eligible_event`-No-op ohne Journal-Write oder District-Mutation
- [x] C2-Status/Evidenz nach PR #92 kanonisch in `PROJEKTSTATUS.json`, TODO und Feature-Pool synchronisieren

## 0.8.7-C3 – Application-Integration ✅

- [x] genau einen autorisierten Trigger festlegen: `settlement.complete`
- [x] District-Event erst nach bestätigtem Settlement und bestätigter District-Zuordnung auslösen
- [x] stabilen Trigger aus der bestätigten Settlement-Quelle ableiten; Browser liefert weder Trigger-ID noch Effekte
- [x] bestehenden `DistrictWorldEventService` und `DistrictService` wiederverwenden
- [x] A4-Runtime mit vorhandenem `DISTRICT_EVENT_MANIFEST.json` konfigurieren
- [x] Regression abgesichert: Street-Walk löst weiterhin kein District-Welt-Ereignis aus
- [x] Regression abgesichert: Settlement-Retry würfelt nicht neu und schreibt nicht doppelt
- [x] Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package grün
- [x] 0 offene Review-Threads, aktuelles `main`, `/safe-merge` PASS · Merge `fb62c5226997462cc2a9adc67529a7691e16ae2b`

---

# Aktiv – 0.8.7-C4 Ereignis-Timeline

## C4A – bestätigte Projection-/Textschicht ✅

- [x] bestätigte District-, Street- und Crisis-Ereignisse ausschließlich aus Journalrecords lesen
- [x] Reihenfolge ausschließlich aus kanonischer Journal-`sequence` ableiten
- [x] Street- und District-Texte aus vorhandenen Textkatalogen auflösen; Incident-Schlüssel erhalten einen eigenen UI-Textkatalog
- [x] leere Historie bleibt leer; fehlende/ungültige Records oder Texte erzeugen keinen erfundenen Ersatzinhalt
- [x] Projection liefert maximal die letzten 12 bestätigten Einträge und bleibt vollständig vom Eingabejournal entkoppelt
- [x] Regressionen für Reihenfolge, Textauflösung, leere Historie, ungültige Records, Limit und Detached Data ergänzen
- [x] `/safe-merge` PASS · PR #98 · Merge `4909fb9f7169baaa5b802e497cdba3e2c6da0dae`

## C4B – sichtbares Control Deck

- [ ] C4A-Projection über die bestehende A4-Runtime an den Client reichen
- [ ] Control Deck zeigt eine kompakte, tastatur- und screenreaderfreundliche Timeline
- [ ] Darstellung bleibt read-only und enthält keinen Command-/Write-Pfad
- [ ] bestehende C4A-Reihenfolge und Texte unverändert verwenden; Browser sortiert oder erfindet nichts neu

### Explizit NICHT in C4

- keine neuen Gameplay-Effekte
- keine zweite Journal-/Timeline-Persistenz
- keine Client-Autorität
- kein Cooldown/Cadence-System
- kein Produktversionsbump ohne eigene Release-Abnahme

---

# Danach – priorisierter Ausbau

1. **0.8.7-C5 – Cadence/Cooldown:** District-Events über bestätigte Spielzeit dosieren, niemals über Systemzeit allein.
2. **0.8.7-D – Street Content Packs:** mehr Abwechslung über denselben validierten Ansatz-/Encounter-Vertrag.
3. **QA – Timeline-Diagnose:** optional read-only anzeigen, warum ein bestätigter Journalrecord wegen fehlendem/ungültigem Text nicht projiziert wurde; keine Fallback-Story erfinden.

---

## Arbeitsregeln

- Pro Iteration kleinster sinnvoller Scope.
- Keine zweite Implementierung vorhandener Services/States.
- UI/Renderer schreibt Domain-State niemals direkt.
- Economy nur über kanonische Economy-Services/Events.
- Journal bleibt append-only.
- Systemzeit ist niemals alleinige Zufalls-, Saison- oder Replayautorität.
- Normaler Merge ausschließlich nach aktuellem `main`, grünen Required Checks, 0 offenen Review-Threads und `/safe-merge`.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
