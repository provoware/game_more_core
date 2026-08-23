# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.7-B – Control Deck & Player Choices`
- **0.8.7-A Saisonale Hall of Tribute:** PR #87 · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`
- **0.8.7-B Control Deck & Player Choices:** PR #88 · Head `6482daa2ac4d7e0c370ef6bca4a1d8a079438b6c` · Runtime `32600255789` · Presentation `32600255795` · Repository Health `32600255756` · Release Acceptance `32600255773` · Release Package `32600255763` · 0 Review-Threads · `SAFE MERGE PASS` · Merge `4d1a35bfbc086d07599b6ec7b3816e830bcea995`
- **Aktive Iteration:** `0.8.7-C – Bezirksbezogene Welt-Ereignisse`; erster Slice = Vertrag/Katalog, noch ohne schreibende Runtime
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
- [x] Runtime Core `32600255789` ✅
- [x] Presentation Core `32600255795` ✅
- [x] Repository Health `32600255756` ✅
- [x] Release Acceptance `32600255773` ✅
- [x] Release Package `32600255763` ✅
- [x] 0 Review-Threads
- [x] `/safe-merge` PASS · Merge `4d1a35bfbc086d07599b6ec7b3816e830bcea995`

---

# AKTIVER AUSBAU

## 0.8.7-C – Bezirksbezogene Welt-Ereignisse

### Ziel

Reproduzierbare, katalogisierte Welt-Ereignisse sollen den vorhandenen persistenten DistrictState sichtbar beeinflussen, ohne eine zweite Event- oder Zufallsengine einzuführen.

### Slice C1 – Vertrag/Katalog

- [x] vorhandenen DistrictState-Vertrag als einzige Metrik-/Bounds-Basis referenzieren
- [x] Ereigniskatalog mit stabilen IDs, Gewichten, Voraussetzungen und kleinen Effekten definieren
- [x] Auswahlvertrag deterministisch/replaybar halten; Systemzeit nie als Seed
- [x] genau eine aktive District-Event-Instanz pro Kontext als Vertragsgrenze festlegen
- [x] Browser-Aktivierung und Browser-Effektwerte ausdrücklich verbieten
- [x] deutsche Story-Texte separat von Spiellogik katalogisieren
- [x] gezielte Vertragsregressionen für IDs, Gewichte, Bounds, Voraussetzungen und Textschlüssel ergänzen

### Slice C2 – Runtime/Recovery als nächster Schritt

- [ ] Auswahlservice auf bestätigtem `world_seed + district_id + trigger_id` implementieren
- [ ] bestätigte Folgen ausschließlich über zuständigen District-Service + Journal anwenden
- [ ] Idempotenz/Reload/Recovery für eine konkrete Event-Instanz absichern
- [ ] A4 zunächst nur lesend informieren; keine District-Fachlogik in JavaScript
- [ ] gezielte Runtime-/Recovery-/Projection-Regressionen ergänzen

### Explizit NICHT in 0.8.7-C

- keine zweite Crisis-/Street-Engine
- keine Netzwerkgegner
- keine frei erfundenen Browser-Effekte
- kein Property-Resale/Rent-System
- kein Produktversionsbump ohne eigene Release-Abnahme

---

# Danach – priorisierter Ausbau

1. **0.8.7-D – Street Content Packs:** mehr Abwechslung über denselben validierten Ansatz-/Encounter-Vertrag.
2. **0.8.7-E – Crewfarben & Emblem:** reine Identitäts-/Darstellungsdaten ohne Character-ID-Änderung.
3. **0.9 – Network Foundation:** eigener Server-/Transport-/Konfliktvertrag vor Netzwerk-Ranking oder Telegram-Sync.

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
