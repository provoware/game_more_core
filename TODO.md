# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe vor aktuellem Gameplay-Slice:** `0.8.8-STREET-EFFECT-AUDIT` · PR #136 · Merge `56afe056b05c56033d205fd2fea3e60fc8f7722d`
- **Start-/Release-Qualität:** `main` enthält zusätzlich die sicher gemergte Härtung bis PR #155 · Merge `8e9606a888f350305e1cd8ee8a8b94ef7ab2990e`
- **Recovery-Balance-Audit:** PR #129 · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1` · vollständige Energie×Stress-Matrix sicher gemergt
- **Aktive Entwicklungsstufe:** `0.8.8-STREET-SCOUT-BALANCE – eigener Scout-Tradeoff ohne Doppelarchitektur`
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

---

# Aktiv – 0.8.8-STREET-SCOUT-BALANCE

## Fortschritt

**70 %** – der erste Remote-Lauf deckte zwei bestehende Balance-Invarianten auf; der Patch wurde daraufhin enger gemacht. Manifest, direkte Effektregression, bestehender Balance-Audit, Statusregression und Laienhilfe sind jetzt auf denselben Vertrag ausgerichtet. Finale Remote-Gates, Merge-Hygiene und Safe Merge stehen noch aus.

## Ziel

`scout` eine kleine eigene mathematische Stärke geben und die vollständige Dominanz durch `balanced` beseitigen, ohne neue Encounter-, Zufalls-, Effekt- oder Persistenzlogik einzuführen und ohne den bestehenden Makro-Balancevertrag aufzuweichen.

## Abnahme

Scout behält den stärksten Discovery-Fokus bei 40/100, den bestehenden Polaritätsmix `15 neutral / 60 positiv / 25 negativ` und maximal 20 Punkte pro Einzelbegegnung. Der Erwartungswert wird `+1,01 Energie / −0,09 Stress / +0,33 Ruf`; damit ist Scout knapp energieeffizienter als Balanced, aber klar schwächer bei Stressabbau und Ruf.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md`
- aktive Stellen aus `TODO.md`, `FEATURE_POOL.md`, `PROJEKTSTATUS.json`

**Arbeitsdateien**
- `manifests/STREET_ENCOUNTER_MANIFEST.json`
- `tests/runtime/test_street_effect_audit.py`
- `tests/runtime/test_street_balance_audit.py` – nach konkretem roten Runtime-Befund
- `tests/runtime/test_feature_status_consistency.py` – nach konkretem roten Runtime-Befund
- `docs/LAIENHILFE_STREET_SCOUT_BALANCE.md`
- `CHANGELOG.md` nur für die fachliche Änderungsnotiz

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich beim konkreten roten Gate

### STREET-SCOUT-BALANCE – Vertrag

- [x] ausschließlich zwei Scout-Gewichte innerhalb der negativen Polarität verschoben; Summe bleibt 100
- [x] `street.construction_detour` für Scout 5 → 0
- [x] `street.lost_glove` für Scout 5 → 10
- [x] Discovery-Gewicht `shortcut + useful_find + cable_tip` bleibt unverändert 40 und höher als bei allen anderen Ansätzen
- [x] Scout-Polaritätsmix bleibt 15 / 60 / 25
- [x] maximales Einzelgewicht bleibt 20
- [x] Manifestversion bleibt `0.8.8-street-pack`; bestehende Replay-/Pack-Verträge werden nicht künstlich versioniert
- [x] Scout-Erwartungswert: +1,01 Energie / −0,09 Stress / +0,33 Ruf
- [x] `balanced` dominiert `scout` nicht mehr; gleichzeitig dominiert Scout keinen anderen Ansatz vollständig
- [x] Recovery bleibt Energie-Spezialist; Network bleibt Stress-/Ruf-Spezialist
- [x] keine Encounter-Effekte, Runtime-Services, Saves, Journalarten oder UI verändert
- [ ] Remote-Gates auf exakt dem finalen Head vollständig grün
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in STREET-SCOUT-BALANCE

- keine neue Encounter-Art
- keine Telemetrie
- keine zweite Zufalls- oder Effektengine
- keine Produktversionsänderung
- keine UI-Sonderregel für Scout
- keine Aufweichung der vorhandenen Street-Balance-Invarianten

### Danach

- [ ] **0.8.8-UX-RECEIPT-CLARITY:** bestätigte Receipt-Zustände in klarer UI-Sprache anzeigen, nur aus Runtime-Signalen
- [ ] **0.8.8-STREET-BOUNDARY-AUDIT:** Street-Effekte an Character-Grenzzuständen gegen tatsächliches Clamping prüfen, test-only
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Street-Auswahl, Effekte und Zufall bleiben vollständig Runtime-/Manifest-Autorität.
- Der Balance-Patch ändert nur katalogisierte Auswahlgewichte und führt keine zweite Engine ein.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
