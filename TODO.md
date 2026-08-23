# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-FIN-EXPORT – Kontoauszug TXT/CSV` · PR #119 · Merge `11c023f927ad9a74673587fefd1709fe2322553f`
- **FIN-EXPORT Remote-Abnahme:** Runtime `32669021501` · Presentation `32669021500` · Repository Health `32669021494` · Release Acceptance `32669021495` · Release Package `32669021502` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-ECON-ANTI-GRIND – Scene-Job-Erschöpfung`
- **ANTI-GRIND-Status:** Scene Jobs bleiben jederzeit verfügbar; voller Lohn nur bei gedecktem Energieverbrauch, Teilenergie proportional, 0 Energie = 0 Cent; manueller Job und Assistent verwenden denselben `SceneJobService`
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
- [x] PR #113 · Merge `c1a27a977ff76a397d95ae097395317c4d46950b`
- [x] PR #114 · Merge `bbebc9c3cafeac7f71eebeea1b89d4861b304e76`

## 0.8.8-E – Control Deck Focus
- [x] lokale Bereichsfokussierung + Runtime-abgeleitetes Nächste-Aktion-Signal
- [x] kein Save-/Journal-State, Reduced Motion respektiert
- [x] PR #115 · Merge `6ac72d794ad3565bc40eb23dd501626382aa679a`

## 0.8.8-FIN-STATEMENTS – Kontoauszüge
- [x] Joblohn, Einzahlung, Auszahlung und Sparzins read-only aus `PlayerFinanceState.ledger`
- [x] JSON-stabile Projection über HTTP, Restart und Recovery
- [x] PR #116 · Merge `81dda0d21170a5d876cd5a7ebf05a8409ec735c8`

## 0.8.8-F – Berlin Ops Map 2
- [x] bestehende 0–100-Projection bleibt einzige Kartenquelle
- [x] Zoom `1.0×–2.2×`, begrenztes Pan, 1:1-Reset und Auswahlfokus
- [x] Standardbuttons für Tastatur/Maus; kein Wheel-/Drag-Zwang, kein Save-/Journal-State
- [x] keine API, kein Geocoding und keine neue Map-Engine
- [x] PR #117 · Merge `8119bf71a6f169d5cac367d5123d2bc1e6a73193`

## 0.8.8-STORY-DISTRICT-BIO – Bezirks-Nachhall
- [x] bestätigte District-Einträge der vorhandenen Ereignis-Timeline als maximal fünf Berlin-Erinnerungen im Profil sichtbar
- [x] kein neuer persistenter Story-/Biografie-State, kein neuer Journaltyp, keine XP/Ruf/Beziehungs-/Bonusfolge
- [x] PR #118 · Merge `2330669692391e3747a3c807ec9b2a1cb7b7cb6d`

## 0.8.8-FIN-EXPORT – Kontoauszug TXT/CSV
- [x] Quelle ausschließlich `state.projection.scene_jobs.finance_statement`
- [x] TXT/CSV lokal; vollständiger unterstützter Kontoauszug unabhängig vom lokalen Filter
- [x] keine Ledger-Neuberechnung, kein Import, kein `/api/command`, keine erfundene Zeitangabe
- [x] PR #119 · Head `73257a4dd3ff06a546d8332af4c411fdc614967e` · Runtime `32669021501` · Presentation `32669021500` · Repository Health `32669021494` · Release Acceptance `32669021495` · Release Package `32669021502` · 0 Review-Threads · `/safe-merge` PASS · Merge `11c023f927ad9a74673587fefd1709fe2322553f`

---

# Aktiv – 0.8.8-ECON-ANTI-GRIND

## Ziel

Scene Jobs bleiben phasenunabhängig und jederzeit verfügbar, erzeugen bei extrem niedriger bestätigter Energie aber nur noch den tatsächlich energetisch gedeckten Anteil des katalogisierten Joblohns.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` nur Prozess-/Dateiklassenvertrag
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `manifests/SCENE_JOB_MANIFEST.json`

**Arbeitsdateien**
- `src/bunkerfrequenz/application/scene_job_service.py`
- `src/bunkerfrequenz/application/assistant_round_service.py` nur Delegationsnachweis, keine Änderung geplant
- `src/bunkerfrequenz/domain/finance.py` nur Nullbuchungs-Vertragsprüfung
- `tests/runtime/test_scene_job_service.py`
- `tests/runtime/test_assistant_round_service.py`
- `tests/runtime/test_feature_status_consistency.py`
- `docs/LAIENHILFE_SCENE_JOB_ERSCHOEPFUNG.md`

**Evidenz/Logs**
- nur Run-ID/Status im Normalfall
- vollständiger CI-Log ausschließlich bei rotem Gate und nur für den konkreten Fehlerjob

### ANTI-GRIND – Balancevertrag und kleinster Runtime-Slice

- [x] `exhaustion_policy` im bestehenden Scene-Job-Manifest definiert und fail-closed validiert
- [x] Jobs bleiben mit vorhandenem Character jederzeit verfügbar
- [x] voller katalogisierter Lohn, wenn Vor-Job-Energie den katalogisierten Energieverbrauch deckt
- [x] Teilenergie: `basislohn * verfügbare_energie // energieverbrauch`
- [x] 0 Energie: Job bleibt ausführbar, erzeugt aber 0 Cent Joblohn
- [x] bestehendes Finance-Ledger und `finance.job_completed` bleiben einzige Joblohn-Buchung
- [x] kein Rechnerzeit-Cooldown und keine zweite Erschöpfungsressource
- [x] Client darf keinen Lohnfaktor oder Zielbetrag liefern
- [x] Assistent delegiert unverändert an denselben `SceneJobService`; gezielte Regression beweist dieselbe Niedrigenergie-Regel
- [x] Retry/Recovery-Vertrag bleibt unverändert
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32670308989` · Presentation `32670309016` · Repository Health `32670308982` · Release Acceptance `32670308991` · Release Package `32670308980`
- [ ] finalen Status-/Dokumentations-Head erneut 5/5 prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in ANTI-GRIND

- keine Sperre der Scene Jobs bei 0 Energie
- keine neue Erschöpfungsleiste, Müdigkeitswährung oder Cooldown-Uhr
- keine neue Assistant-Jobengine
- keine Änderung an Bank, Zinsen, Investments oder Eventbudget
- kein Browser-Lohnrechner als Autorität
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-UX-EXPORT-PROOF:** Exportvorschau/Kopieren oder kleine Prüfsumme ausschließlich aus derselben FIN-STATEMENTS-Projection; read-only
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-ECON-RECOVERY-ACTIONS:** später echte bestätigte Regenerationsaktionen prüfen, ohne Systemzeit-Autorität einzuführen

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR und keine zweite Economy-, Finance-, Assistant- oder Erschöpfungsengine.
- Der `SceneJobService` bleibt die einzige Jobauszahlungsstelle für manuellen Job und Assistent.
- Character-Energie direkt vor dem Job ist die einzige Erschöpfungsautorität dieses Slices.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
