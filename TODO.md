# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-ECON-JOB-PREVIEW – Scene-Job-Lohnvorschau` · PR #121 · Merge `040be951665a34dd8d81694ab695128e0b846bd5`
- **JOB-PREVIEW Remote-Abnahme:** Runtime `32671395304` · Presentation `32671395288` · Repository Health `32671395282` · Release Acceptance `32671395294` · Release Package `32671395295` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-UX-EXPORT-PROOF – Exportvorschau/Prüfsumme`
- **EXPORT-PROOF-Status:** TXT/CSV werden vor dem Download lokal aus exakt derselben Serialisierung angezeigt; Kopieren und kleine deterministische Prüfsumme verwenden denselben Inhalt
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

---

# Aktiv – 0.8.8-UX-EXPORT-PROOF

## Ziel

TXT/CSV vor dem Download lokal sichtbar und vergleichbar machen, ohne Export- oder Finanzlogik zu duplizieren.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md`
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- README nur falls Repository Health die aktive Iteration dort verlangt

**Arbeitsdateien**
- `web/a4/finance_statement_export.js`
- `tests/presentation/test_a4_finance_export.py`
- `docs/LAIENHILFE_FIN_EXPORT.md`

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei konkretem roten Gate

### EXPORT-PROOF – kleinster read-only UX-Slice

- [x] eine gemeinsame `serializeStatement(...)`-Stelle für TXT/CSV
- [x] Vorschau verwendet exakt denselben serialisierten String wie der Download
- [x] Kopieren verwendet exakt den aktuell geprüften String
- [x] kleine deterministische 32-Bit-FNV-1a-Prüfsumme über exakt denselben String
- [x] Prüfsumme ausdrücklich nicht als kryptografischer Nachweis dargestellt
- [x] keine Ledger-/Summen-Neuberechnung, kein Finance-Command, kein Save-/Journal-Write
- [x] Laienhilfe um Prüfen → Kopieren → Download und Prüfsummen-Grenze erweitert
- [ ] finalen Remote-Prüfstand 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in EXPORT-PROOF

- keine SHA-256-/Signatur-Infrastruktur
- kein Exportmanifest
- kein Import
- keine Finance-Neuberechnung
- keine Änderung an Runtime, Ledger oder Projection
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-ECON-RECOVERY-ACTIONS:** echte bestätigte Regenerationsaktionen prüfen, ohne Systemzeit-Autorität
- [ ] **0.8.8-UX-TIMELINE-FILTER:** Timeline lokal nach Straße/Krise/Bezirk filtern
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Keine zweite Finance-, Export- oder Kontoauszugsengine.
- Exportquelle bleibt ausschließlich die bestehende `finance_statement`-Projection.
- Vorschau, Kopieren, Prüfsumme und Download bleiben lokale Presentation.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
