# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-ECON-JOB-PREVIEW – Scene-Job-Lohnvorschau` · PR #121 · Merge `040be951665a34dd8d81694ab695128e0b846bd5`
- **JOB-PREVIEW Remote-Abnahme:** Runtime `32671395304` · Presentation `32671395288` · Repository Health `32671395282` · Release Acceptance `32671395294` · Release Package `32671395295` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-UX-EXPORT-PROOF – Exportvorschau/Prüfsumme`
- **EXPORT-PROOF-Status:** TXT/CSV-Vorschau, Kopieren, Prüfsumme und Download verwenden dieselbe Serialisierung; Prüfsumme wird lokal über die UTF-8-Bytes gebildet
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
- [x] PR #119 · Merge `11c023f927ad9a74673587fefd1709fe2322553f`

## 0.8.8-ECON-ANTI-GRIND – Scene-Job-Erschöpfung
- [x] Scene Jobs bleiben jederzeit verfügbar
- [x] voller Lohn nur bei gedecktem Energieverbrauch; Teilenergie proportional; 0 Energie = 0 Cent
- [x] manueller Job und Assistent verwenden denselben `SceneJobService`
- [x] keine Rechnerzeit, kein Cooldown, keine zweite Erschöpfungsressource
- [x] PR #120 · Head `95882e97fdb8a1a84c14a17e377dc9978c342f1e` · Runtime `32670613358` · Presentation `32670613422` · Repository Health `32670613395` · Release Acceptance `32670613449` · Release Package `32670613455` · 0 Review-Threads · `/safe-merge` PASS · Merge `49d6947b9f1b3a35d0785a958a7688e3b22a6bc1`

## 0.8.8-ECON-JOB-PREVIEW – Scene-Job-Lohnvorschau
- [x] echte Auszahlung und read-only Projection verwenden dieselbe kanonische Anti-Grind-Berechnung
- [x] bei Teilenergie zeigt die UI verständlich `bis zu … / aktuell …`; Browser berechnet keinen Lohn
- [x] PR #121 · Head `226d89bd758a05b5d0972ffebdcacb5cc5c4c359` · Runtime `32671395304` · Presentation `32671395288` · Repository Health `32671395282` · Release Acceptance `32671395294` · Release Package `32671395295` · 0 Review-Threads · `/safe-merge` PASS · Merge `040be951665a34dd8d81694ab695128e0b846bd5`

---

# Aktiv – 0.8.8-UX-EXPORT-PROOF

## Ziel

TXT/CSV vor dem Download lokal sichtbar, kopierbar und vergleichbar machen, ohne Export- oder Finanzlogik zu duplizieren.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` nur unveränderter Prozess-/Dateiklassenvertrag
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- README-Projekt-Puls als bekannter Repository-Health-Statusvertrag

**Arbeitsdateien**
- `web/a4/finance_statement_export.js`
- `tests/presentation/test_a4_finance_export.py`
- `docs/LAIENHILFE_FIN_EXPORT.md`
- `tests/runtime/test_feature_status_consistency.py` nur Statusvertrag

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei konkretem roten Gate

### EXPORT-PROOF – kleinster read-only UX-Slice

- [x] gemeinsame `serializeStatement(...)`-Stelle bleibt einzige TXT/CSV-Serialisierung
- [x] Vorschau verwendet exakt denselben serialisierten Inhalt wie der Download
- [x] Download aktualisiert unmittelbar vorher die Vorschau und verwendet genau diesen Inhalt
- [x] Kopieren verwendet exakt den aktuell geprüften Inhalt
- [x] kleine deterministische 32-Bit-FNV-1a-Prüfsumme über die UTF-8-Bytes des Exportinhalts
- [x] Prüfsumme ist ausdrücklich keine Signatur und keine Gameplay-/Finanzautorität
- [x] keine Ledger-/Summen-Neuberechnung, kein Finance-Command, kein Save-/Journal-Write
- [x] Laienhilfe um Prüfen → Kopieren → Download und Prüfsummen-Grenze erweitert
- [ ] finalen Remote-Prüfstand 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in EXPORT-PROOF

- keine kryptografische Signatur-Infrastruktur
- kein Exportmanifest
- kein Import
- keine Finance-Neuberechnung
- keine Runtime-/Ledger-/Projection-Änderung
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-ECON-RECOVERY-ACTIONS:** echte bestätigte Regenerationsaktionen prüfen, ohne Systemzeit-Autorität einzuführen
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-UX-TIMELINE-FILTER:** Timeline lokal nach Straße/Krise/Bezirk filtern; read-only

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR und keine zweite Finance-, Export- oder Kontoauszugsengine.
- Exportquelle bleibt ausschließlich die bestehende `finance_statement`-Projection.
- Vorschau, Kopieren, Prüfsumme und Download bleiben lokale Presentation.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
