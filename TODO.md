# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe vor aktuellem QA-Slice:** `0.8.8-MAP-USABILITY` · PR #130 · Merge `47eb5b5288221fb0c6cd2ebfa3473b2b5ba85a07`
- **Recovery-Balance-Audit:** PR #129 · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1` · vollständige Energie×Stress-Matrix sicher gemergt
- **Browser-Freeze-Hotfix:** PR #132 · Merge `f78e4bd6b212dbd7e9477b9d681c2dbf6e0af060` · selbsttriggernde `MutationObserver`-Schleife im Control Deck behoben
- **Aktive Entwicklungsstufe:** `0.8.8-QA-REPLAY-PRECISION – District-Event-Receipt-Semantik`
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

## 0.8.8-ECON-ANTI-GRIND / JOB-PREVIEW
- [x] Scene Jobs bleiben verfügbar; Lohn skaliert bei Teilenergie proportional, 0 Energie = 0 Cent
- [x] gleiche kanonische Berechnung für Auszahlung und read-only Vorschau
- [x] PR #120 / #121 sicher gemergt

## 0.8.8-UX-EXPORT-PROOF
- [x] Vorschau, Kopieren und Download verwenden dieselbe TXT-/CSV-Serialisierung
- [x] PR #122 · Merge `0909f3c38642f97d4474cd200af11c960e1ada66`

## 0.8.8-ECON-RECOVERY-ACTIONS / FEEDBACK / VARIANTS
- [x] `Koffein & kalte Luft`: +20 Energie / +12 Stress
- [x] `Mate, Zucker & Vollgas`: +30 Energie / +20 Stress
- [x] gleicher `RecoveryActionService` und `character.resources_changed`-Replay-Pfad; keine Echtzeitregeneration oder zweite Engine
- [x] PRs #123, #125 und #127 sicher gemergt

## 0.8.8-UX-TIMELINE-FILTER
- [x] Filter `ALLE / STRASSE / KRISE / BEZIRK` ausschließlich lokal, ohne Journal- oder Sortierautorität
- [x] PR #124 · Merge `465dc5040c5a1283fee5e7af52590455feaa9a01`

## 0.8.8-STREET-PACK / STREET-BALANCE-AUDIT
- [x] Katalog 10 → 16 Begegnungen über denselben Encounter-Vertrag
- [x] vier Ansatzprofile, Polaritätsmix und alle 100 Auswahl-Buckets deterministisch geprüft
- [x] PR #126 / #128 sicher gemergt

## 0.8.8-ECON-RECOVERY-BALANCE-AUDIT
- [x] beide Recovery-Aktionen über alle 10.201 Energie×Stress-Zustände geprüft
- [x] alle erreichbaren Mehrfachfolgen gegen Clamping, Gratisstrategien und unerwartete Effizienzsteigerung geprüft
- [x] keine Gameplaywerte, Recovery-Services oder Journalverträge verändert
- [x] PR #129 · Head `d449a7f3827f0a94a4506028c74e5ae640d0bd30` · Runtime `32678508499` · Presentation `32678508432` · Repository Health `32678508482` · Release Acceptance `32678508462` · Release Package `32678508457` · `/safe-merge` PASS · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1`

## 0.8.8-MAP-USABILITY / Control-Deck-Freeze-Hotfix
- [x] Kartenmarker, District-Hierarchie, Legende und optionale Beschriftungen rein lokal verbessert; PR #130 sicher gemergt
- [x] selbsttriggernde `MutationObserver`-Schleife im Focus-Modul beseitigt und direkt regressionsgesichert; PR #132 sicher gemergt

---

# Aktiv – 0.8.8-QA-REPLAY-PRECISION

## Fortschritt

**60 %** – vorhandene Receipt-Signale analysiert; direkte Runtime-Regression und Laienhilfe implementiert. Remote-Gates, Merge-Hygiene und Safe Merge stehen noch aus.

## Ziel

District-Event-Ergebnisreceipts so regressionssicher festlegen, dass **neu angewendet**, **idempotent wiederverwendet** und **bewusst nicht ausgelöst** nicht miteinander verwechselt werden können.

## Abnahme

Ein gezielter Runtime-Test beweist die drei vorhandenen Zustände anhand von `triggered`, `no_event_reason`, `applied`, `idempotent_replay`, `committed_event_ids` und Receipt-Metadaten; ein Replay darf weder neu würfeln noch schreiben, ein No-op darf weder Eventinstanz noch Journalwrite erfinden.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Test-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `FEATURE_POOL.md`, `PROJEKTSTATUS.json`

**Arbeitsdateien**
- `src/bunkerfrequenz/application/district_world_event_service.py` – bestehender Ergebnis-/No-event-Vertrag, nur lesen
- `src/bunkerfrequenz/application/district_service.py` – vorhandene `DistrictCommitResult`-Replaysemantik, nur relevanter `_apply`-Ausschnitt
- `tests/runtime/test_district_world_event_service.py` – bestehende direkte Regressionen, nur lesen
- `tests/runtime/test_district_replay_receipt_semantics.py` – neue explizite Semantikregression
- `docs/LAIENHILFE_DISTRICT_REPLAY_RECEIPTS.md` – neue Laienerklärung

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### QA-REPLAY-PRECISION – Invarianten

- [x] neu bestätigtes Event: `triggered=true`, `applied=true`, `idempotent_replay=false`, genau ein neuer Journal-Write
- [x] Replay desselben Triggers: gleiche Eventinstanz, `idempotent_replay=true`, keine neuen `committed_event_ids`, kein neuer Journal-Write
- [x] anderer Seed beim Retry darf kein Reroll erzeugen
- [x] bewusst blockiertes Event: `triggered=false`, `applied=false`, `idempotent_replay=false`, kein Event-ID-/Instanz-Fake und kein Journal-Write
- [x] `no_event_reason` entspricht der Receipt-Metadatenursache
- [x] kein Gameplay-, District-, Seed-, Cadence-, Save- oder Journalvertrag verändert
- [ ] Remote-Gates auf exakt dem finalen Head vollständig grün
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in QA-REPLAY-PRECISION

- keine neue Receipt-Klasse oder zweite Result-Architektur
- keine Änderung an District-Werten oder Eventgewichten
- keine UI-Anzeige der Receipts
- kein neuer Eventtyp
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-STREET-EFFECT-AUDIT:** Erwartungswerte der Energie-/Stress-/Rufeffekte pro Street-Ansatz mathematisch vergleichen, test-only
- [ ] **0.8.8-UX-RECEIPT-CLARITY:** die drei bereits bestätigten Receipt-Zustände optional in klarer UI-Sprache anzeigen, ohne Browserautorität
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- District-Event-Auswahl, Effekte und Cadence bleiben vollständig Runtime-Autorität.
- Der neue Audit schreibt selbst keinen Spielzustand und führt keine neue Receipt-Engine ein.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
