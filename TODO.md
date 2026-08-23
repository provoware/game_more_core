# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-E – Control Deck Focus` · PR #115 · Merge `6ac72d794ad3565bc40eb23dd501626382aa679a`
- **0.8.8-E Remote-Abnahme:** Runtime `32664026523` · Presentation `32664026458` · Repository Health `32664026461` · Release Acceptance `32664026528` · Release Package `32664026553` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-FIN-STATEMENTS – Kontoauszüge`
- **FIN-STATEMENTS-Status:** bestätigtes persönliches Finance-Ledger wird read-only als Joblohn, Einzahlung, Auszahlung und Sparzins sichtbar; keine zweite Buchhaltung und keine erfundenen Datumswerte
- **Entwicklungsprozess:** Focused-Read bleibt verpflichtend; Codex-Code-Review bleibt vollständig außerhalb von Entwicklung, Gate-Evidenz und Mergeprozess
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.8-A bis C5B – Identität, Scene Jobs und bester Freund
- [x] Crew-Identität, fünf Scene Jobs, persönliches Bargeld, Assistant Authority/Control/Confirmed-Round/JOBS-UI und bestätigter Freundschafts-Nachhall
- [x] PRs #104, #105, #107–#112 sicher gemergt

## 0.8.8-D – Atomic Wallet ↔ Bank Transfers
- [x] atomare Ein-/Auszahlung auf bestehendem `PlayerFinanceState` und Finance-Ledger
- [x] Retry/Recovery fail-closed; Browser liefert nur Richtung + Betrag
- [x] PR #113 · Merge `c1a27a977ff76a397d95ae097395317c4d46950b`

## 0.8.8-D2 – Confirmed Savings Interest
- [x] 1 % pro bestätigter Finance-Periode auf aktuellen Bankstand
- [x] Zinseszins, lückenloser `confirmed_finance_tick`, Retry exakt einmal, Nullzinsperiode verbraucht
- [x] kein Systemzeit-/Browser-Trigger
- [x] PR #114 · Head `897b5717776012376ef20e33093b413700744e07` · Merge `bbebc9c3cafeac7f71eebeea1b89d4861b304e76`

## 0.8.8-E – Control Deck Focus
- [x] Bereiche lokal fokussieren und mit `GESAMTANSICHT` zurückstellen
- [x] Fokus bleibt reiner Presentation-State ohne Save/Journal/Storage
- [x] nächste Event-Aktion wird nur aus bereits freigegebenem Runtime-Button hervorgehoben
- [x] Reduced Motion respektiert; keine neue Browser-Autorität
- [x] Codex-Code-Review verbindlich aus Entwicklungsprozess entfernt
- [x] PR #115 · Head `131d7a8eff787a04ced995b1385ae85e7bdff89f` · Runtime `32664026523` · Presentation `32664026458` · Repository Health `32664026461` · Release Acceptance `32664026528` · Release Package `32664026553` · 0 Review-Threads · `/safe-merge` PASS · Merge `6ac72d794ad3565bc40eb23dd501626382aa679a`

---

# Aktiv – 0.8.8-FIN-STATEMENTS Kontoauszüge

## Ziel

Das bestehende bestätigte `PlayerFinanceState.ledger` wird ohne neue Buchhaltung als verständliche persönliche Geldhistorie direkt beim vorhandenen Bankkonto dargestellt.

### Planned-Read-Liste gemäß AGENTS.md

- `AGENTS.md`
- `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `src/bunkerfrequenz/domain/finance.py`
- `src/bunkerfrequenz/presentation/scene_jobs_projection.py`
- `web/a4/assistant_jobs_ui.js`
- `tests/presentation/test_a4_scene_jobs_control_deck.py`
- neue `tests/presentation/test_a4_finance_statements.py`
- `tests/runtime/test_feature_status_consistency.py`
- `docs/LAIENHILFE_BANK_UND_SPAREN.md`

Konkrete Scope-Erweiterungen: `personal_finance_service.py` und `scene_job_service.py` nur zur Belegung der vier Ledger-Semantiken; `test_a4_release_acceptance.py` nur nach dem konkreten JSON-Stabilitätsbefund. README erst bei einem expliziten Repository-Health-Befund.

### FIN-STATEMENTS – kleinster read-only Slice

- [x] nur bestätigte `PlayerFinanceState.ledger`-Zeilen als Quelle
- [x] unterstützte Arten: `job_income`, `bank_deposit`, `bank_withdrawal`, `savings_interest`
- [x] neueste unterstützte Buchung zuerst; stabile `Buchung #N` statt erfundener Zeitstempel
- [x] Summen ausschließlich aus vorhandenen bestätigten Ledgerzeilen
- [x] Jobtitel nur aus vorhandenem Scene-Job-Katalog; Bank/Zins mit festen Presentation-Bezeichnungen
- [x] andere/future Ledgerarten werden nicht interpretiert, sondern nur transparent gezählt
- [x] Kontoauszug direkt im bestehenden Bankbereich unter JOBS; kein zweites Finance-Dashboard
- [x] Filter `ALLE / JOBLOHN / BANK / ZINSEN` bleiben lokaler Presentation-State
- [x] kein `finance.statement`-Command, keine API, kein Save-/Journal-/Storage-Write
- [x] Projection ist JSON-stabil über HTTP, Restart und Recovery
- [x] gezielte Presentation-Regressionen
- [ ] finalen Dokumentations-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in FIN-STATEMENTS

- keine Investments-/Dividenden-Auswertung
- kein Export
- keine Datumsangaben ohne bestätigte Quelle
- keine Finance-Writes oder zweite Ledger-Engine
- keine Map-/Assistant-/Gameplayänderung
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-F – Berlin Ops Map 2:** Zoom/Pan, bessere Bezirks-/Objekthierarchie und fokussierte Detailansicht auf bestehender read-only Projection
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-FIN-EXPORT – Kontoauszug exportieren:** erst nach validiertem FIN-STATEMENTS optionaler lokaler CSV/TXT-Export aus derselben Projection, ohne neue Buchhaltung

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR und keine zweite Economy-/Finance-/Map-/Assistant-Engine.
- Kontoauszug ist ausschließlich read-only Presentation über das bestätigte persönliche Ledger.
- UI-Filter, Fokus und Map-Zoom gehören nicht ins Journal.
- Keine Buchungszeit erfinden, solange das kanonische Ledger keine bestätigte Zeit trägt.
- Zinsen benötigen bestätigten Finance-Tick; Rechnerzeit allein erzeugt niemals Geld.
- Wiederholte Assistentenaktionen brauchen bestätigte Spielrunde; Systemzeit allein bleibt ohne Autorität.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
