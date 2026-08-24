# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-STREET-PACK – Straßenereignis-Erweiterung` · PR #126 · Merge `00c14d57bf642e688a65c0a9e99d39b52857eb0b`
- **STREET-PACK Remote-Abnahme:** Runtime `32676087259` · Presentation `32676087194` · Repository Health `32676087191` · Release Acceptance `32676087204` · Release Package `32676087179` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-ECON-RECOVERY-VARIANTS – zweite Regenerationsentscheidung`
- **RECOVERY-VARIANTS-Status:** Balancevertrag zuerst; `Mate, Zucker & Vollgas` liefert +30 Energie gegen +20 Stress und ist bewusst weniger effizient als +20/+12
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

## 0.8.8-ECON-RECOVERY-FEEDBACK – Regenerationsfeedback
- [x] bestätigte Vorher→Nachher-Werte für Energie und Stress direkt sichtbar
- [x] nächste Verfügbarkeit ausschließlich aus der danach bestätigten Runtime-Projection
- [x] keine neue Mechanik, Delta-/Schwellenberechnung oder Persistenz
- [x] PR #125 · Head `129f1de8b76e569fab4bde51cb722c5aec64b637` · Runtime `32675067361` · Presentation `32675067353` · Repository Health `32675067359` · Release Acceptance `32675067362` · Release Package `32675067352` · 0 Review-Threads · `/safe-merge` PASS · Merge `c8e8cba3dab103c90937f26e90a02a13139dd0f5`

## 0.8.8-STREET-PACK – Straßenereignis-Erweiterung
- [x] Katalog 10 → 16 Begegnungen über denselben Encounter-Vertrag
- [x] globale Verteilung bleibt exakt 25 neutral / 60 positiv / 15 negativ
- [x] `StreetEncounterService` und deterministische Auswahlarchitektur unverändert
- [x] PR #126 · Head `bd2b921089ef6b10dd849e0d9fc7a89bf3efb342` · Runtime `32676087259` · Presentation `32676087194` · Repository Health `32676087191` · Release Acceptance `32676087204` · Release Package `32676087179` · 0 Review-Threads · `/safe-merge` PASS · Merge `00c14d57bf642e688a65c0a9e99d39b52857eb0b`

---

# Aktiv – 0.8.8-ECON-RECOVERY-VARIANTS

## Ziel

Eine zweite bestätigte Regenerationsentscheidung soll eine echte situative Alternative sein: größerer Sofortschub gegen überproportional höheren Stresspreis. Keine Echtzeitregeneration, kein Cooldown und keine zweite Recovery-Engine.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Runtime-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- README wegen aktiver/folgender Iterationskonsistenz

**Arbeitsdateien**
- `docs/RECOVERY_VARIANTS_BALANCE_CONTRACT.md` – mathematischer Vertrag vor Runtime-Patch
- `src/bunkerfrequenz/application/recovery_action_service.py`
- `tests/runtime/test_recovery_action_service.py`
- `src/bunkerfrequenz/presentation/scene_jobs_projection.py` nur zur Generikprüfung, keine Änderung erforderlich
- `web/a4/recovery_actions_ui.js` nur zur Autoritätsprüfung, keine Änderung erforderlich
- `tests/presentation/test_a4_recovery_actions.py` direkte Presentation-Grenze

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### RECOVERY-VARIANTS – Balancevertrag + kleinster Runtime-Slice

- [x] Balancevertrag vor Runtime-Patch separat dokumentiert
- [x] Referenz `Koffein & kalte Luft`: +20 Energie / +12 Stress = 1,67 Energie pro Stress
- [x] neue Variante `Mate, Zucker & Vollgas`: +30 Energie / +20 Stress = 1,50 Energie pro Stress
- [x] 50 % mehr Sofortenergie kostet 66,7 % mehr Stress; neue Variante ist bewusst weniger effizient
- [x] Headroom vollständig: nur bei Energie <= 70 und Stress <= 80; kein Clamp schwächt Kosten
- [x] gleiche `RECOVERY_ACTIONS`-Quelle und derselbe `RecoveryActionService`
- [x] gleicher `character.resources_changed`-Journal-/Replay-Pfad
- [x] Retry derselben Command-ID bleibt schreibfrei; andere Recovery-ID auf derselben Command-ID scheitert
- [x] Projection, Session und Browser bleiben unverändert, weil sie den Recovery-Katalog bereits generisch verarbeiten
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32676850542` · Presentation `32676850575` · Repository Health `32676850715` · Release Acceptance `32676850860` · Release Package `32676850512`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in RECOVERY-VARIANTS

- keine Echtzeit- oder Rechnerzeitregeneration
- kein Cooldown oder globale Recovery-Sperre
- keine zweite Recovery-/Character-Ressourcenengine
- keine XP, Traits oder Zufallsfolgen
- keine Browserlieferung von Energie-/Stresswerten oder Schwellen
- kein neuer Journaltyp
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-STREET-BALANCE-AUDIT:** deterministisch prüfen, dass alle vier Street-Ansätze erkennbar unterschiedlich bleiben und kein einzelnes Ereignis versehentlich dominiert; keine Telemetrie oder Gameplayänderung
- [ ] **0.8.8-ECON-RECOVERY-BALANCE-AUDIT:** Szenariomatrix für beide Recovery-Optionen gegen Dominanz-/Spam-Risiken erweitern, ohne neue Mechanik
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Recovery-Werte, Availability und Anwendung bleiben vollständig Runtime-Autorität.
- Der Browser wählt nur eine katalogisierte `recovery_id` und berechnet keine Fachwerte.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
