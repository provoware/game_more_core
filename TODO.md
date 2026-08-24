# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe vor aktuellem QA-Slice:** `0.8.8-QA-REPLAY-PRECISION` · PR #133 · Merge `f3c7c6657b52171d024e1157ffd879ee252df2b9`
- **Start-/Release-Qualität:** PR #135 · Merge `0f0c04b50e89b25bbf6e54df338f3e27ed63cd0b` · realer Browser-Acceptance-Gate, Klickstartpfad und Main-Provenienz sicher gemergt
- **Recovery-Balance-Audit:** PR #129 · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1` · vollständige Energie×Stress-Matrix sicher gemergt
- **Aktive Entwicklungsstufe:** `0.8.8-STREET-EFFECT-AUDIT – Erwartungswerte und Dominanzbeziehungen`
- **Repository-Arbeitsmodus:** Focused-Read bleibt verpflichtend; grüne Logs kompakt, rote Gates zuerst nur im konkreten Fehlerausschnitt
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
- [x] PR #129 · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1`

## 0.8.8-MAP-USABILITY / Control-Deck-Freeze-Hotfix
- [x] Kartenmarker, District-Hierarchie, Legende und optionale Beschriftungen rein lokal verbessert; PR #130 sicher gemergt
- [x] selbsttriggernde `MutationObserver`-Schleife im Focus-Modul beseitigt und direkt regressionsgesichert; PR #132 sicher gemergt

## 0.8.8-QA-REPLAY-PRECISION
- [x] neu angewendet, idempotenter Replay und bewusst nicht ausgelöst sind anhand der vorhandenen Receipt-Signale eindeutig regressionsgesichert
- [x] kein Gameplay-, District-, Seed-, Cadence-, Save- oder Journalvertrag verändert
- [x] PR #133 · Head `a387ec62358fccac69957ceeb2fd076230daad04` · `/safe-merge` PASS · Merge `f3c7c6657b52171d024e1157ffd879ee252df2b9`

## START-QUALITY v2
- [x] realer lokaler Server, `/api/health`, `/api/state` und Headless-Browser als Release Acceptance
- [x] ein Klickstartpfad über `START_BUNKERFREQUENZ.sh` und `BUNKERFREQUENZ.desktop`
- [x] PR #135 · `/safe-merge` PASS · Merge `0f0c04b50e89b25bbf6e54df338f3e27ed63cd0b`

---

# Aktiv – 0.8.8-STREET-EFFECT-AUDIT

## Fortschritt

**60 %** – Erwartungswert-Audit und Laienhilfe implementiert; erster Remote-Lauf hat einen echten Balancebefund sichtbar gemacht und die Regression wurde darauf korrigiert. Finale Remote-Gates, Merge-Hygiene und Safe Merge stehen noch aus.

## Ziel

Die vier vorhandenen Street-Ansätze anhand ihrer katalogisierten Energie-, Stress- und Rufwirkungen deterministisch vergleichen, ohne Telemetrie oder Gameplaywerte zu verändern.

## Abnahme

Ein gezielter Runtime-Test berechnet die gewichteten Effektvektoren direkt aus `STREET_ENCOUNTER_MANIFEST.json`, fixiert die aktuellen Erwartungswerte und macht vollständige Dominanzbeziehungen explizit.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md`
- aktive Stellen aus `TODO.md`, `FEATURE_POOL.md`, `PROJEKTSTATUS.json`

**Arbeitsdateien**
- `manifests/STREET_ENCOUNTER_MANIFEST.json` – nur lesen
- `tests/runtime/test_street_balance_audit.py` – vorhandenen mathematischen Vertrag wiederverwenden
- `tests/runtime/test_street_effect_audit.py` – neuer Effekt-Audit
- `docs/LAIENHILFE_STREET_EFFECT_AUDIT.md` – Laienerklärung

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich beim konkreten roten Gate

### STREET-EFFECT-AUDIT – Befund und Invarianten

- [x] `balanced`: +1,00 Energie / −0,49 Stress / +0,35 Ruf pro gewichteter Auswahl
- [x] `recovery`: +1,23 / −0,49 / +0,23
- [x] `network`: +0,53 / −0,59 / +0,65
- [x] `scout`: +0,91 / −0,14 / +0,33
- [x] `recovery` besitzt den höchsten Energie-Erwartungswert
- [x] `network` besitzt stärkste Stresssenkung und höchsten Ruf-Erwartungswert
- [x] **Balancebefund:** `balanced` dominiert `scout` derzeit auf allen drei unbedingten Erwartungswerten
- [x] keine Gewichte, Effekte, Services, Saves, Journalarten oder UI verändert
- [ ] Remote-Gates auf exakt dem finalen Head vollständig grün
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in STREET-EFFECT-AUDIT

- keine stille Scout-Neubalancierung im QA-Slice
- keine Telemetrie
- keine neue Zufalls- oder Effektengine
- keine Produktversionsänderung
- keine Änderung des Clamping-/Ressourcenvertrags

### Danach

- [ ] **0.8.8-STREET-SCOUT-BALANCE:** gezielt prüfen, ob `scout` eine eigene mathematische Stärke bekommen soll; kleinster bestehender Manifest-Patch, Balancevertrag zuerst
- [ ] **0.8.8-UX-RECEIPT-CLARITY:** bestätigte Receipt-Zustände in klarer UI-Sprache anzeigen, nur aus Runtime-Signalen
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Street-Auswahl, Effekte und Zufall bleiben vollständig Runtime-/Manifest-Autorität.
- Der Audit schreibt selbst keinen Spielzustand und führt keine zweite Balance-Engine ein.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
