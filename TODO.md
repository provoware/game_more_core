# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.7-A – Saisonale Hall of Tribute`
- **0.8.6-C Berlin Ops Map PRO:** PR #85 · Merge `10c7d6b5e04838b07ae6899b8b76580cd87de607`
- **0.8.7-A Saisonale Hall of Tribute:** PR #87 · Head `b887f912675ed2cf5efa8eb85631ab7858721836` · Runtime `32593679072` · Presentation `32593679117` · Repository Health `32593679063` · Release Acceptance `32593679077` · Release Package `32593679102` · 0 Review-Threads · `SAFE MERGE PASS` · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`
- **Aktive Iteration:** `0.8.7-B – Control Deck & Player Choices`
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
- [x] Runtime Core `32593679072` ✅
- [x] Presentation Core `32593679117` ✅
- [x] Repository Health `32593679063` ✅
- [x] Release Acceptance `32593679077` ✅
- [x] Release Package `32593679102` ✅
- [x] 0 Review-Threads
- [x] `/safe-merge` PASS · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`

---

# AKTIV / IN ABNAHME

## 0.8.7-B – Control Deck & Player Choices 🎛️

### Ziel

Die vorhandenen Systeme sollen **schneller verständlich, optisch stärker und spielerisch entscheidungsreicher** werden. Neue Wahlmöglichkeiten dürfen vorhandene Fachlogik nur ansteuern – nicht im Browser neu erfinden.

### B1 – Control Deck 2.0 / Optik

- [x] Sticky HUD für Phase, Budget, Energie, Stress, Ruf und Eigentum
- [x] Schnellnavigation zu Straße, Map, Property, Hall, Event, Equipment und Save
- [x] stärkere Industrial-Control-Room-Hierarchie
- [x] responsive Desktop-/Tablet-/Mobilansicht
- [x] Spielerwahl- und Krisenbereiche visuell hervorheben
- [x] bestehende Berlin Ops Map PRO unverändert als read-only Renderer behalten

### B2 – Lokale Anzeigeoptionen

- [x] Kompaktmodus
- [x] Hoher Kontrast
- [x] Große Schrift
- [x] Einstellungen ausschließlich lokal im Browser speichern
- [x] UI-Einstellungen besitzen keinerlei Gameplay-/Save-Autorität
- [x] Reduced Motion weiterhin respektieren

### B3 – Street Approaches / echte Spielerwahl

- [x] vier Ansätze: `balanced`, `recovery`, `network`, `scout`
- [x] Standardansatz erhält exakt die bisherige Street-Verteilung
- [x] Ansatz verändert ausschließlich katalogisierte Auswahlgewichte
- [x] Encounter bleibt einzige Effekt-Autorität
- [x] Browser sendet nur `approach_id`
- [x] Gewichts-/Effekt-Injection fail-closed
- [x] Retry kann den bereits bestätigten Ansatz nicht austauschen
- [x] alte `0.8.5-c1`-Street-Records replayen weiterhin als `balanced`
- [x] Systemzeit bleibt aus der Auswahl ausgeschlossen

### B4 – Krisenentscheidungen verständlicher

- [x] Antwortoptionen als eigenständige Entscheidungskarten
- [x] Zielphase vor dem Klick sichtbar
- [x] katalogisierte Auswirkungen auf Budget, Ruf, Stress, Stabilität und Heat anzeigen
- [x] Browser berechnet keine Krisenfolgen selbst
- [x] Command sendet weiterhin nur die vorhandene `response_id`

### B5 – Robustheit / Abnahme

- [x] Runtime-Regressionen für Street-Ansätze und Legacy-Replay
- [x] Command-Injection-Regressionen
- [x] Presentation-Verträge für HUD, Anzeigeoptionen und Outcome-Vorschau
- [ ] Runtime Core
- [ ] Presentation Core
- [ ] Repository Health
- [ ] Release Acceptance
- [ ] Release Package
- [ ] 0 Review-Threads
- [ ] `/safe-merge`

### Explizit NICHT in 0.8.7-B

- keine neue Street-Engine
- keine neuen Encounter-Effekte im Browser
- keine Änderung an Property-/Economy-Autorität
- keine Netzwerkgegner
- keine bezirksbezogenen Welt-Ereignisse
- kein Produktversionsbump

---

# Danach – priorisierter Ausbau

1. **0.8.7-C – Bezirksbezogene Welt-Ereignisse:** reproduzierbare Ereignisinstanzen auf dem persistenten DistrictState.
2. **0.8.7-D – Street Content Packs:** mehr Abwechslung über denselben validierten Ansatz-/Encounter-Vertrag.
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
