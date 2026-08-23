# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-UX-EXPORT-PROOF – Exportvorschau/Prüfsumme` · PR #122 · Merge `0909f3c38642f97d4474cd200af11c960e1ada66`
- **EXPORT-PROOF Remote-Abnahme:** Runtime `32672139829` · Presentation `32672139815` · Repository Health `32672139802` · Release Acceptance `32672139807` · Release Package `32672139805` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-ECON-RECOVERY-ACTIONS – bestätigte Regeneration`
- **RECOVERY-ACTIONS-Status:** `Koffein & kalte Luft` tauscht bestätigt +20 Energie gegen +12 Stress; nur bei Energie ≤ 80 und Stress ≤ 88, ohne Rechnerzeit, XP, Traits oder zweite Ressourcenengine
- **Repository-Arbeitsmodus:** Basisdateien, Arbeitsdateien und Evidenz/Logs sind getrennt; grüne Logs werden nicht dauerhaft übertragen, rote Gates zuerst nur im konkreten Fehlerausschnitt gelesen
- **Entwicklungsprozess:** Focused-Read bleibt verpflichtend; Codex-Code-Review bleibt vollständig außerhalb von Entwicklung, Gate-Evidenz und Mergeprozess
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.8-A bis C5B – Identität, Scene Jobs und bester Freund
- [x] Crew-Identität, fünf Scene Jobs, persönliches Bargeld, Assistant Authority/Control/Confirmed-Round/JOBS-UI und bestätigter Freundschafts-Nachhall
- [x] PRs #104, #105, #107–#112 sicher gemergt

## 0.8.8-D / D2 – Bank & Sparen
- [x] atomare Wallet↔Bank-Transfers auf bestehendem `PlayerFinanceState` und Ledger
- [x] 1 % Sparzins pro bestätigtem Finance-Tick, Zinseszins, Retry-/Recovery-Schutz
- [x] PR #113 / #114 sicher gemergt

## 0.8.8-E bis FIN-EXPORT – Control Deck, Kontoauszug, Map, Story und Export
- [x] Control Deck Focus, FIN-STATEMENTS, Berlin Ops Map 2, Bezirks-Nachhall und TXT/CSV-Kontoauszug
- [x] PRs #115–#119 sicher gemergt

## 0.8.8-ECON-ANTI-GRIND – Scene-Job-Erschöpfung
- [x] Scene Jobs bleiben verfügbar; Lohn skaliert bei Teilenergie proportional, 0 Energie = 0 Cent
- [x] PR #120 · Merge `49d6947b9f1b3a35d0785a958a7688e3b22a6bc1`

## 0.8.8-ECON-JOB-PREVIEW – Scene-Job-Lohnvorschau
- [x] gleiche kanonische Anti-Grind-Berechnung für echte Auszahlung und read-only Projection
- [x] Browser zeigt bei Teilenergie verständlich `bis zu … / aktuell …`
- [x] kein Browser-Lohnrechner, kein neuer Command, kein Writeback
- [x] PR #121 · Head `226d89bd758a05b5d0972ffebdcacb5cc5c4c359` · Runtime `32671395304` · Presentation `32671395288` · Repository Health `32671395282` · Release Acceptance `32671395294` · Release Package `32671395295` · 0 Review-Threads · `/safe-merge` PASS · Merge `040be951665a34dd8d81694ab695128e0b846bd5`

## 0.8.8-UX-EXPORT-PROOF – Exportvorschau/Prüfsumme
- [x] Vorschau, Kopieren und Download verwenden dieselbe TXT-/CSV-Serialisierung
- [x] lokale FNV-1a-32-Prüfsumme über UTF-8-Bytes; keine kryptografische oder Gameplay-Autorität
- [x] PR #122 · Head `9af0ff007b47c18b9b38bcefe33f8879a3b97573` · Runtime `32672139829` · Presentation `32672139815` · Repository Health `32672139802` · Release Acceptance `32672139807` · Release Package `32672139805` · 0 Review-Threads · `/safe-merge` PASS · Merge `0909f3c38642f97d4474cd200af11c960e1ada66`

---

# Aktiv – 0.8.8-ECON-RECOVERY-ACTIONS

## Ziel

Eine kleine bestätigte Spielerentscheidung soll Energie aktiv zurückgeben, ohne Rechnerzeit, automatisches Warten, kostenlosen Endlos-Reset oder zweite Ressourcenengine.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` nur Prozess-/Autoritätsgrenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- bestehender Character-Ressourcen-/Replay-Vertrag

**Arbeitsdateien**
- `src/bunkerfrequenz/application/recovery_action_service.py`
- `src/bunkerfrequenz/application/assistant_game_client_session.py`
- `src/bunkerfrequenz/presentation/scene_jobs_projection.py`
- `web/a4/recovery_actions_ui.js`
- `web/a4/ui_prefs.js`
- direkte Runtime-/Presentation-Regressionen

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei konkretem roten Gate

### RECOVERY-ACTIONS – kleinster kanonischer Gameplay-Slice

- [x] `Koffein & kalte Luft`: +20 Energie, +12 Stress
- [x] nur erlaubt bei bestätigter Energie ≤ 80 und Stress ≤ 88; Gewinn und Preis können dadurch nicht weggeclampt werden
- [x] keine XP, Trait-Evidence, Zufallswürfe, Rechnerzeit oder automatische Regeneration
- [x] bestehendes `character.resources_changed` bleibt Journal-/Recovery-Wahrheit; kein neuer Eventtyp
- [x] Retry derselben Command-ID ist schreibfrei
- [x] Scene-Jobs-Projection liefert `can_run` und Blocker aus bestätigtem Character-State
- [x] Browser sendet nur `recovery_id`; keine Energie-/Stresswerte oder Schwellen
- [x] Regeneration sitzt im bestehenden JOBS-Bereich, kein zweites Ressourcen-Dashboard
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32673048911` · Presentation `32673048896` · Repository Health `32673048885` · Release Acceptance `32673048901` · Release Package `32673048879`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in RECOVERY-ACTIONS

- keine Systemzeit, Echtzeitregeneration oder Cooldown-Uhr
- keine zweite Energie-/Müdigkeitsressource
- keine Finance-Kosten oder neue Buchhaltung
- keine XP-/Trait-Farm-Aktion
- keine Browser-Autorität über Deltas oder Schwellen
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-UX-TIMELINE-FILTER:** bestätigte Timeline lokal nach Straße/Krise/Bezirk filtern; keine neue Journal-/Sortierautorität
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-ECON-RECOVERY-VARIANTS:** erst später weitere Regenerationsoptionen erwägen, falls Balancingbeobachtung sie rechtfertigt

---

## Architektur- und Sicherheitsgrenzen

- Keine zweite Character-, Ressourcen-, Finance- oder Action-Engine.
- `RecoveryActionService` schreibt ausschließlich die bestehende replaybare `character.resources_changed`-Semantik.
- Availability und Ressourcendeltas kommen aus der Runtime; der Browser wählt nur die stabile `recovery_id`.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
