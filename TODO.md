# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe vor aktuellem UX-Slice:** `0.8.8-STREET-SCOUT-BALANCE` · PR #156 · Merge `3f7ee5f24dd27b3cd885b7fa51970ec98e92379c`
- **Start-/Release-Qualität:** `main` enthält die sicher gemergte Härtung bis PR #155 sowie den validierten Scout-Balance-Slice PR #156
- **Recovery-Balance-Audit:** PR #129 · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1` · vollständige Energie×Stress-Matrix sicher gemergt
- **Aktive Entwicklungsstufe:** `0.8.8-UX-RECEIPT-CLARITY – District-Receipt-Klartext aus vorhandenen Runtime-Signalen`
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

## 0.8.8-STREET-EFFECT-AUDIT
- [x] Erwartungswerte aller vier Street-Ansätze direkt aus dem Manifest berechnet
- [x] Balancebefund dokumentiert: `balanced` dominierte `scout` auf Energie, Stress und Ruf
- [x] keine Gameplaywerte im Audit verändert
- [x] PR #136 · `/safe-merge` PASS · Merge `56afe056b05c56033d205fd2fea3e60fc8f7722d`

## 0.8.8-STREET-SCOUT-BALANCE
- [x] nur zwei bestehende Scout-Gewichte innerhalb derselben negativen Polarität verschoben
- [x] Scout-Erwartungswert auf `+1,01 Energie / −0,09 Stress / +0,33 Ruf` gebracht; keine vollständige Dominanz durch Balanced mehr
- [x] Polaritätsmix, maximal 20 Punkte je Encounter, Manifestversion, Runtime und Replay-Vertrag unverändert
- [x] PR #156 · Head `d828d97a2ab6bec89e70724480a486d22f82dac7` · `/safe-merge` PASS · Merge `3f7ee5f24dd27b3cd885b7fa51970ec98e92379c`

---

# Aktiv – 0.8.8-UX-RECEIPT-CLARITY

## Fortschritt

**65 %** – der reine Presentation-Kern ist implementiert. Ein erster Presentation-Lauf hat den vorhandenen MutationObserver-Inventarvertrag korrekt ausgelöst; der neue Observer wurde daraufhin explizit als selbstlöschender, nur auf fehlende flüchtige Meldung reagierender Observer regressionsgesichert. Finale Statussynchronisation und Remote-Abnahme laufen.

## Ziel

Die bereits vorhandenen District-Receipt-Zustände im Control Deck verständlich anzeigen, ohne ein neues Receipt-Feld, eine zweite Timeline oder neuen Gameplay-/Persistenzzustand einzuführen.

## Abnahme

Nach einer bestätigten Abrechnung zeigt der bestehende Settlement-Bereich genau einen der drei Zustände:

- `NEU BESTÄTIGT` – District-Event besitzt bestätigte Event-Identität und der Command ist kein idempotenter Replay.
- `BEREITS BESTÄTIGT` – dieselbe bestätigte Event-Identität kommt mit vorhandenem `idempotent_replay=true` zurück.
- `NICHT AUSGELÖST` – die vorhandenen `district_world_event`-Metadaten besitzen absichtlich keine Event-/Instanz-ID; die UI erfindet keinen Journal-Eintrag.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md`
- aktive Stellen aus `TODO.md`, `FEATURE_POOL.md`, `PROJEKTSTATUS.json`

**Arbeitsdateien**
- `tests/runtime/test_district_replay_receipt_semantics.py`
- `src/bunkerfrequenz/application/game_client_session.py` ausschließlich zum Lesen der bereits vorhandenen Command-Signale
- `web/a4/app.js`, `web/a4/index.html`, `web/a4/client_resilience.js`
- `web/a4/receipt_clarity.js`
- `tests/presentation/test_a4_receipt_clarity.py`
- `tests/presentation/test_a4_mutation_observer_guard.py` nach konkretem roten Presentation-Befund

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich beim konkreten roten Gate

### UX-RECEIPT-CLARITY – Vertrag

- [x] ausschließlich vorhandene `/api/command`-Signale werden gelesen
- [x] keine neue Domain-/Receipt-Klasse
- [x] kein neuer API-Command und kein POST aus dem Modul
- [x] kein Save-/Journal-/Timeline-Write
- [x] keine Systemzeit oder Zufallslogik für die Receipt-Bedeutung
- [x] flüchtige, zugängliche Statusmeldung mit `role=status` und `aria-live=polite`
- [x] Observer reagiert nur auf Entfernung der eigenen flüchtigen Meldung und schreibt danach selbstlöschend genau einmal nach
- [ ] finaler Head: Runtime Core, Presentation Core, Repository Health vollständig grün
- [ ] Release Acceptance und Release Package vollständig grün
- [ ] 0 ungelöste Review-Threads und 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in UX-RECEIPT-CLARITY

- keine neue Receipt-Persistenz
- keine eigene Timeline für No-op/Retry
- keine Veränderung von District-Event-Cadence oder Seed
- keine Gameplay- oder Balanceänderung
- keine künstliche Eventinstanz für `NICHT AUSGELÖST`

### Danach

- [ ] **0.8.8-STREET-BOUNDARY-AUDIT / POOL-QA-010:** Street-Effekte an Energie-/Stress-Grenzen gegen tatsächliches Clamping prüfen, test-only
- [ ] **0.8.8-C6 / POOL-COMPANION-003:** Round-Authority Integration Harness erst bei echtem kanonischem Rundenproduzenten
- [ ] **0.8.8-UX-RECEIPT-REASON-COPY:** nur falls später ein bestätigter No-event-Grund bereits im A4-Command-Vertrag exponiert wird; keine neue Autorität dafür erfinden

---

## Architektur- und Sicherheitsgrenzen

- Receipt-Semantik bleibt Runtime-Autorität; der Browser benennt nur vorhandene Signale.
- Der neue Zustand ist flüchtige Presentation und überlebt einen Reload bewusst nicht als eigenes UI-Receipt.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
