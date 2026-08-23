# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-UX-TIMELINE-FILTER – lokale Timeline-Filter` · PR #124 · Merge `465dc5040c5a1283fee5e7af52590455feaa9a01`
- **TIMELINE-FILTER Remote-Abnahme:** Runtime `32674157706` · Presentation `32674157688` · Repository Health `32674157773` · Release Acceptance `32674157695` · Release Package `32674157723` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-ECON-RECOVERY-FEEDBACK – verständliches Regenerationsfeedback`
- **RECOVERY-FEEDBACK-Status:** nach bestätigter Regeneration werden Vorher→Nachher-Werte aus bestätigten Projection-Snapshots gezeigt; nächste Verfügbarkeit kommt ausschließlich aus der danach gerenderten Runtime-Projection
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

---

# Aktiv – 0.8.8-ECON-RECOVERY-FEEDBACK

## Ziel

Nach bestätigter Regeneration sollen die tatsächlichen Vorher-/Nachher-Werte und die nächste Runtime-Verfügbarkeit unmittelbar verständlich sichtbar sein, ohne neue Mechanik oder Browser-Regelberechnung.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Presentation-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- README wegen aktiver/folgender Iterationskonsistenz

**Arbeitsdateien**
- `web/a4/recovery_actions_ui.js`
- `tests/presentation/test_a4_recovery_actions.py`
- `tests/runtime/test_feature_status_consistency.py`
- `docs/LAIENHILFE_REGENERATION_FEEDBACK.md`

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### RECOVERY-FEEDBACK – kleinster erklärender UX-Slice

- [x] Vorherwerte direkt aus bestätigter `state.projection.character` vor dem Command übernehmen
- [x] Nachherwerte erst nach Rückkehr des vorhandenen bestätigten `sendCommand(...)`-Pfads aus der neuen Projection übernehmen
- [x] keine Delta-, Schwellen- oder Verfügbarkeitsberechnung im Browser
- [x] nächsten `can_run`-/Blocker-Status ausschließlich aus `state.projection.scene_jobs.recovery_actions` erklären
- [x] bei unverändertem State kein falsches Erfolgssignal erzeugen
- [x] technische Implementierung nur in bestehendem Recovery-UI-Modul; Runtime-Service und Session bleiben unverändert
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32674791670` · Presentation `32674791661` · Repository Health `32674791642` · Release Acceptance `32674791660` · Release Package `32674791644`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in RECOVERY-FEEDBACK

- keine neue Recovery-Aktion oder Balanceänderung
- keine neue Runtime-/Service-/Session-Logik
- keine Browserberechnung von Deltas oder Schwellen
- keine neue Persistenz oder Journalart
- keine Systemzeit
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-STREET-PACK:** zusätzliche Straßenereignisse über den vorhandenen Encounter-Vertrag ergänzen; keine neue Encounter-Engine
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-ECON-RECOVERY-VARIANTS:** erst nach Balancingbeobachtung weitere Regenerationsoptionen erwägen

---

## Architektur- und Sicherheitsgrenzen

- Recovery-Mechanik und Availability bleiben vollständig Runtime-Autorität.
- Feedback darf bestätigte Werte erklären, aber keine neue Ressourcenauswirkung ableiten oder autorisieren.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)