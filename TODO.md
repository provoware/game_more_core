# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-ECON-RECOVERY-VARIANTS – zweite Regenerationsentscheidung` · PR #127 · Merge `c9732c28cc723984d59b02018fbed02c3c681913`
- **RECOVERY-VARIANTS Remote-Abnahme:** Runtime `32677148542` · Presentation `32677148505` · Repository Health `32677148521` · Release Acceptance `32677148511` · Release Package `32677148527` · 0 Review-Threads · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-STREET-BALANCE-AUDIT – deterministischer Katalogcheck`
- **STREET-BALANCE-AUDIT-Status:** test-only; 16 Begegnungen × vier Ansätze werden auf Profilabstand, Einzelevent-Dominanz, Polaritätsmix und alle 100 Auswahl-Buckets geprüft
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
- [x] PR #121 · Merge `040be951665a34dd8d81694ab695128e0b846bd5`

## 0.8.8-UX-EXPORT-PROOF – Exportvorschau/Prüfsumme
- [x] Vorschau, Kopieren und Download verwenden dieselbe TXT-/CSV-Serialisierung
- [x] PR #122 · Merge `0909f3c38642f97d4474cd200af11c960e1ada66`

## 0.8.8-ECON-RECOVERY-ACTIONS – bestätigte Regeneration
- [x] `Koffein & kalte Luft`: +20 Energie, +12 Stress
- [x] keine Rechnerzeit, XP, Traits, zweite Ressource oder Browser-Deltas
- [x] bestehendes `character.resources_changed` bleibt Replay-/Recovery-Wahrheit
- [x] PR #123 · Head `31a3c2966549f54260c3d90b148e2d4cec4b6cad` · Runtime `32673385832` · Presentation `32673385764` · Repository Health `32673385757` · Release Acceptance `32673385796` · Release Package `32673385792` · 0 Review-Threads · `/safe-merge` PASS · Merge `7ed085b111a03173f0359bd76129d8d3b5f71900`

## 0.8.8-UX-TIMELINE-FILTER – lokale Timeline-Filter
- [x] Filter `ALLE / STRASSE / KRISE / BEZIRK`
- [x] ausschließlich lokaler Modul-State; keine Sortierung, Persistenz oder Journal-Autorität
- [x] PR #124 · Head `59bcc0909bc508f085b2a40a187074461799a908` · Runtime `32674157706` · Presentation `32674157688` · Repository Health `32674157773` · Release Acceptance `32674157695` · Release Package `32674157723` · 0 Review-Threads · `/safe-merge` PASS · Merge `465dc5040c5a1283fee5e7af52590455feaa9a01`

## 0.8.8-ECON-RECOVERY-FEEDBACK – Regenerationsfeedback
- [x] bestätigte Vorher→Nachher-Werte für Energie und Stress direkt sichtbar
- [x] nächste Verfügbarkeit ausschließlich aus der danach bestätigten Runtime-Projection
- [x] keine neue Mechanik, Delta-/Schwellenberechnung oder Persistenz
- [x] PR #125 · Head `129f1de8b76e569fab4bde51cb722c5aec64b637` · Runtime `32675067361` · Presentation `32675067353` · Repository Health `32675067359` · Release Acceptance `32675067362` · Release Package `32675067352` · 0 Review-Threads · `/safe-merge` PASS · Merge `c8e8cba3dab103c90937f26e90a02a13139dd0f5`

## 0.8.8-STREET-PACK – Straßenereignis-Erweiterung
- [x] Katalog 10 → 16 Begegnungen über denselben Encounter-Vertrag
- [x] globale Verteilung bleibt exakt 25 neutral / 60 positiv / 15 negativ
- [x] `StreetEncounterService` und deterministische Auswahlarchitektur unverändert
- [x] PR #126 · Head `bd2b921089ef6b10dd849e0d9fc7a89bf3efb342` · Runtime `32676087259` · Presentation `32676087194` · Repository Health `32676087191` · Release Acceptance `32676087204` · Release Package `32676087179` · 0 Review-Threads · `/safe-merge` PASS · Merge `00c14d57bf642e688a65c0a9e99d39b52857eb0b`

## 0.8.8-ECON-RECOVERY-VARIANTS – zweite Regenerationsentscheidung
- [x] Balancevertrag vor Runtime-Patch dokumentiert
- [x] `Mate, Zucker & Vollgas`: +30 Energie / +20 Stress, bewusst ineffizienter als +20/+12
- [x] gleicher `RECOVERY_ACTIONS`-Katalog, `RecoveryActionService` und `character.resources_changed`-Replay-Pfad
- [x] keine Echtzeitregeneration, kein Cooldown, keine zweite Engine
- [x] PR #127 · Head `c042e4b9de2d385384ce4d65b6586f519c0a515a` · Runtime `32677148542` · Presentation `32677148505` · Repository Health `32677148521` · Release Acceptance `32677148511` · Release Package `32677148527` · 0 Review-Threads · `/safe-merge` PASS · Merge `c9732c28cc723984d59b02018fbed02c3c681913`

---

# Aktiv – 0.8.8-STREET-BALANCE-AUDIT

## Fortschritt

**70 %** – mathematischer Audit und Laienhilfe implementiert; technischer Head 5/5 remote grün. Ausstehend sind nur finale Status-Abnahme, Merge-Hygiene und Safe Merge.

## Ziel

Den bestehenden 16er Street-Katalog automatisch darauf prüfen, dass die vier Ansätze mathematisch unterscheidbar bleiben, kein Einzelevent dominiert und die deterministische Gewichtsauswahl an allen Grenzen exakt dem Manifest entspricht.

## Abnahme

Ein test-only Audit beweist ohne Telemetrie und ohne Gameplayänderung Profilabstände, maximale Einzelgewichte, Polaritätsprofile sowie die exakte Abbildung aller 100 Buckets je Ansatz.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Test-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `manifests/STREET_ENCOUNTER_MANIFEST.json`

**Arbeitsdateien**
- `tests/runtime/test_street_pack_contract.py` – bestehender Katalogvertrag
- `tests/runtime/test_street_encounter_service.py` – bestehende Determinismus-/Replay-Regressionsgrenze
- `src/bunkerfrequenz/application/street_encounter_service.py` – nur `_stable_bucket` / `_select` als direkte Auswahlquelle; keine Änderung
- `tests/runtime/test_street_balance_audit.py` – neuer Audit
- `docs/LAIENHILFE_STREET_BALANCE_AUDIT.md` – Laienerklärung
- `tests/runtime/test_feature_status_consistency.py` – Statusregression

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### STREET-BALANCE-AUDIT – mathematische Invarianten

- [x] exakt 16 Begegnungen und vier Ansätze `balanced / recovery / network / scout`
- [x] paarweise Total-Variation-Distanz geprüft: 0,17 bis 0,40; Mindestabstand >= 0,15
- [x] maximale Einzelwahrscheinlichkeit pro Ansatz <= 20 %
- [x] Polaritätsprofile exakt geprüft: balanced 25/60/15, recovery 30/55/15, network 15/70/15, scout 15/60/25
- [x] jeder Ansatz bleibt überwiegend positiv; Positivanteil >= 55 %, Negativanteil <= 25 %
- [x] alle 100 möglichen Gewichtsbuckets pro Ansatz vollständig enumeriert
- [x] beobachtete Buckethäufigkeit entspricht für jedes Event exakt dem deklarierten Gewicht
- [x] erste/letzte Bucketposition jedes Gewichtintervalls gegen Off-by-one geprüft
- [x] feste SHA-256-Bucket-Fixtures für `server_sequence=None`, `0`, `1` und Unicode-Eingabe
- [x] `STREET_ENCOUNTER_MANIFEST.json` unverändert
- [x] `StreetEncounterService` unverändert
- [x] keine Telemetrie, kein Tracking, kein Save-/Journal-Write und keine neue Gameplaymechanik
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32677783993` · Presentation `32677784003` · Repository Health `32677784021` · Release Acceptance `32677783987` · Release Package `32677783990`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in STREET-BALANCE-AUDIT

- keine Änderung an Begegnungen, Gewichten oder Effekten
- keine Telemetrie oder Live-Spielerdaten
- keine automatische Live-Balance
- keine neue Zufallsquelle
- keine Systemzeit-Autorität
- keine neue Runtime-/Presentation-Mechanik
- kein Produktversionsbump

### Risiken

- Ein später bewusst geändertes Gewichtsprofil muss die Audit-Invarianten absichtlich mitändern; sonst blockiert der Test korrekt den Merge.
- Die festen Bucket-Fixtures machen eine Änderung der deterministischen Hash-Auswahl sichtbar und verhindern damit versehentliche Replay-Drift.

### Danach

- [ ] **0.8.8-ECON-RECOVERY-BALANCE-AUDIT:** deterministische Energie×Stress-Matrix für beide Recovery-Wege; globale Dominanz, Clamping und Mehrfachfolgen beweisen
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-STREET-EFFECT-AUDIT:** optional später Erwartungswerte der kleinen Energie-/Stress-/Rufeffekte pro Ansatz prüfen, weiterhin test-only

---

## Architektur- und Sicherheitsgrenzen

- Street-Auswahl bleibt vollständig deterministisch aus dem bestehenden bestätigten Vertrag.
- Der Audit liest ausschließlich Manifest und reine Auswahlfunktionen; er schreibt keinen Spielzustand.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
