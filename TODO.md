# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-STORY-DISTRICT-BIO – Bezirks-Nachhall` · PR #118 · Merge `2330669692391e3747a3c807ec9b2a1cb7b7cb6d`
- **STORY Remote-Abnahme:** Runtime `32667441909` · Presentation `32667441903` · Repository Health `32667441900` · Release Acceptance `32667441908` · Release Package `32667441996` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-FIN-EXPORT – Kontoauszug TXT/CSV`
- **FIN-EXPORT-Status:** vollständige validierte `finance_statement`-Projection lokal als TXT/CSV exportieren; keine Ledger-Neuberechnung, kein Filterverlust, kein Write-Command
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
- [x] PR #117 · Head `91255bbb7bee90050cbd762ce93600802a666940` · Runtime `32666137485` · Presentation `32666137499` · Repository Health `32666137472` · Release Acceptance `32666137497` · Release Package `32666137508` · 0 Review-Threads · `/safe-merge` PASS · Merge `8119bf71a6f169d5cac367d5123d2bc1e6a73193`

## 0.8.8-STORY-DISTRICT-BIO – Bezirks-Nachhall
- [x] bestätigte District-Einträge der vorhandenen Ereignis-Timeline als maximal fünf Berlin-Erinnerungen im Profil sichtbar
- [x] kein neuer persistenter Story-/Biografie-State, kein neuer Journaltyp, keine XP/Ruf/Beziehungs-/Bonusfolge
- [x] keine erfundenen Zeitangaben; ausschließlich read-only Presentation
- [x] PR #118 · Head `9b83fbcc2a3e0c4848c93241861303529aec1b9c` · Runtime `32667441909` · Presentation `32667441903` · Repository Health `32667441900` · Release Acceptance `32667441908` · Release Package `32667441996` · 0 Review-Threads · `/safe-merge` PASS · Merge `2330669692391e3747a3c807ec9b2a1cb7b7cb6d`

---

# Aktiv – 0.8.8-FIN-EXPORT

## Ziel

Den bereits validierten persönlichen Kontoauszug lokal als TXT oder CSV speichern, ohne Ledger, Finanzwerte oder Spielzustand neu zu berechnen oder zu verändern.

### Planned-Read-Liste gemäß AGENTS.md

- `AGENTS.md`
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `src/bunkerfrequenz/presentation/scene_jobs_projection.py`
- `web/a4/assistant_jobs_ui.js` nur bestehender Kontoauszug
- `web/a4/ui_prefs.js`
- neues `web/a4/finance_statement_export.js`
- `tests/presentation/test_a4_finance_statements.py`
- neue `tests/presentation/test_a4_finance_export.py`
- `tests/runtime/test_feature_status_consistency.py`
- `docs/LAIENHILFE_BANK_UND_SPAREN.md`

Weitere Dateien nur nach konkretem Gate-/Vertragsbefund.

### FIN-EXPORT – kleinster Export-Slice

- [x] Quelle ausschließlich `state.projection.scene_jobs.finance_statement`
- [x] TXT- und CSV-Export lokal im Browser
- [x] Export verwendet alle unterstützten Projection-Einträge unabhängig vom lokalen Anzeige-Filter
- [x] vorhandene `totals`, `supported_entries`, `other_entries` und `filters` werden direkt übernommen
- [x] keine Browser-Neuberechnung von Summen oder Ledgerwerten
- [x] kein Zugriff auf `PlayerFinanceState`, `finance.ledger` oder zweite Buchhaltung
- [x] kein `fetch`, kein `/api/command`, kein Save-/Journal-Write
- [x] keine erfundenen Datums-/Uhrzeitangaben im Inhalt oder Dateinamen
- [x] fester verständlicher Dateiname `bunkerfrequenz-kontoauszug.txt/.csv`
- [x] erster Remote-Prüfstand fand ausschließlich eine zu konkrete Test-Assertion; Produktcode unverändert
- [x] korrigierter technischer Head 5/5 grün
- [ ] finalen Dokumentations-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in FIN-EXPORT

- keine neue Finance-/Ledger-Projection
- keine Ledger-Neuberechnung
- keine Auswahl neuer Finanzwerte durch den Browser
- kein Import zurück ins Spiel
- kein Server-Dateiexport und keine externe Abhängigkeit
- keine Änderung an Bank, Zinsen, Scene Jobs oder Assistant
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-ECON-ANTI-GRIND:** niedrige Energie bei Scene Jobs spielerisch sinnvoll behandeln; zuerst Balancevertrag, danach kleinster Runtime-Slice
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-UX-EXPORT-PREVIEW:** optional später Exportvorschau/Kopieren, weiterhin rein lokal und ohne Finanzautorität

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR und keine zweite Story-, Economy-, Finance-, Map- oder Assistant-Engine.
- FIN-EXPORT liest ausschließlich die bereits bestätigte Kontoauszug-Projection.
- Browser darf keine Buchungen, Summen, Salden oder Zeitpunkte bestätigen.
- Exportdateien sind lokale Kopien zur Ansicht und kein Importformat für Gameplay-State.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)