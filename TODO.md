# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-STREET-BALANCE-AUDIT – deterministischer Katalogcheck` · PR #128 · Merge `bef5e2ad78923c4ce36c116c66f2755abe442d3d`
- **STREET-BALANCE-AUDIT Remote-Abnahme:** Runtime `32677951158` · Presentation `32677951294` · Repository Health `32677951209` · Release Acceptance `32677951288` · Release Package `32677951160` · 0 Review-Threads · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-ECON-RECOVERY-BALANCE-AUDIT – deterministische Energie×Stress-Matrix`
- **RECOVERY-BALANCE-AUDIT-Status:** test-only; beide Recovery-Wege werden über alle 10.201 Energie×Stress-Zustände sowie alle erreichbaren Mehrfachfolgen gegen Dominanz, Clamping und Gratisstrategien geprüft
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

## 0.8.8-ECON-RECOVERY-ACTIONS / FEEDBACK / VARIANTS
- [x] `Koffein & kalte Luft`: +20 Energie / +12 Stress
- [x] `Mate, Zucker & Vollgas`: +30 Energie / +20 Stress, bewusst ineffizienter für mehr Sofortreserve
- [x] gleicher `RecoveryActionService` und `character.resources_changed`-Replay-Pfad; keine Echtzeitregeneration oder zweite Engine
- [x] PRs #123, #125 und #127 sicher gemergt

## 0.8.8-UX-TIMELINE-FILTER
- [x] Filter `ALLE / STRASSE / KRISE / BEZIRK` ausschließlich lokal, ohne Journal- oder Sortierautorität
- [x] PR #124 · Merge `465dc5040c5a1283fee5e7af52590455feaa9a01`

## 0.8.8-STREET-PACK
- [x] Katalog 10 → 16 Begegnungen über denselben Encounter-Vertrag
- [x] globale Verteilung bleibt exakt 25 neutral / 60 positiv / 15 negativ
- [x] PR #126 · Merge `00c14d57bf642e688a65c0a9e99d39b52857eb0b`

## 0.8.8-STREET-BALANCE-AUDIT
- [x] vier Ansatzprofile: paarweise Total-Variation-Distanz 0,17 bis 0,40
- [x] maximale Einzelwahrscheinlichkeit 20 %, Polaritätsprofile und alle 100 Auswahl-Buckets deterministisch geprüft
- [x] `STREET_ENCOUNTER_MANIFEST.json` und `StreetEncounterService` unverändert; keine Telemetrie oder Gameplayänderung
- [x] PR #128 · Head `9f823e72f2e11a6891a96272d8faaf1ba53ee08b` · Runtime `32677951158` · Presentation `32677951294` · Repository Health `32677951209` · Release Acceptance `32677951288` · Release Package `32677951160` · 0 Review-Threads · `/safe-merge` PASS · Merge `bef5e2ad78923c4ce36c116c66f2755abe442d3d`

---

# Aktiv – 0.8.8-ECON-RECOVERY-BALANCE-AUDIT

## Fortschritt

**70 %** – deterministischer Matrix-/Folgen-Audit und Laienhilfe implementiert; technischer Head 5/5 remote grün. Ausstehend sind finale Status-Abnahme, Merge-Hygiene und Safe Merge.

## Ziel

Die beiden bestehenden Recovery-Optionen mathematisch über den kompletten zulässigen Zustandsraum absichern, ohne Gameplaywerte oder Recovery-Architektur zu verändern.

## Abnahme

Ein test-only Audit beweist für alle Energie×Stress-Zustände und alle erreichbaren Recovery-Folgen, dass Availability exakt dem Headroom-Vertrag entspricht, Kosten nie geclamped werden, keine Option die andere global Pareto-dominiert und keine Folge eine unerwartete Gratisstrategie erzeugt.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Test-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `docs/RECOVERY_VARIANTS_BALANCE_CONTRACT.md`

**Arbeitsdateien**
- `src/bunkerfrequenz/application/recovery_action_service.py` – `RECOVERY_ACTIONS` und kanonische Availability; keine Änderung
- `tests/runtime/test_recovery_action_service.py` – bestehende direkte Recovery-Regressionen; keine Änderung
- `tests/runtime/test_recovery_balance_audit.py` – neuer Matrix-/Folgen-Audit
- `docs/LAIENHILFE_RECOVERY_BALANCE_AUDIT.md` – Laienerklärung
- `tests/runtime/test_feature_status_consistency.py` – Statusregression

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### RECOVERY-BALANCE-AUDIT – mathematische Invarianten

- [x] beide katalogisierten Recovery-Aktionen werden aus derselben `RECOVERY_ACTIONS`-Quelle gelesen
- [x] für jede Aktion alle 10.201 Kombinationen Energie 0–100 × Stress 0–100 geprüft
- [x] Availability entspricht exakt `max_energy_before` und `max_stress_before`
- [x] bei jeder erlaubten Aktion werden Energiegewinn und Stresspreis vollständig angewendet
- [x] kein erlaubter Zustand überschreitet Energie 100 oder Stress 100; kein Clamping erforderlich
- [x] in allen gemeinsam verfügbaren Zuständen liefert `Vollgas` mehr Energie, kostet aber zugleich mehr Stress; keine Pareto-Dominanz
- [x] die kleine Recovery besitzt zusätzliche erlaubte Randzustände wegen des geringeren Stress-/Energiebedarfs
- [x] alle erreichbaren Mehrfachfolgen werden deterministisch traversiert
- [x] jeder positive kumulierte Energiegewinn besitzt positiven kumulierten Stresspreis
- [x] keine Mehrfachfolge übertrifft die Energie-pro-Stress-Effizienz der effizientesten Einzelaktion
- [x] `RECOVERY_ACTIONS` und `RecoveryActionService` unverändert
- [x] keine Telemetrie, keine Live-Spielerdaten, keine neue Mechanik und kein Save-/Journal-Write
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32678195704` · Presentation `32678195684` · Repository Health `32678195705` · Release Acceptance `32678195690` · Release Package `32678195721`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in RECOVERY-BALANCE-AUDIT

- keine Änderung an Recovery-Werten oder Schwellen
- kein Cooldown oder Zeitmechanismus
- keine Telemetrie oder Live-Balance
- keine neue Ressourcenengine
- keine UI- oder Presentation-Änderung
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-QA-REPLAY-PRECISION:** District-No-op-/Retry-Receipts semantisch präzisieren, ohne Gameplayänderung
- [ ] **0.8.8-STREET-EFFECT-AUDIT:** Erwartungswerte der kleinen Energie-/Stress-/Rufeffekte pro Street-Ansatz prüfen, weiterhin test-only
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Recovery-Werte, Availability und Anwendung bleiben vollständig Runtime-Autorität.
- Der Audit liest nur den bestehenden Katalog und die kanonische Availability-Funktion; er schreibt keinen Spielzustand.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
