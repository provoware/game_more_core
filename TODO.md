# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-ECON-RECOVERY-ACTIONS – bestätigte Regeneration` · PR #123 · Merge `7ed085b111a03173f0359bd76129d8d3b5f71900`
- **RECOVERY-ACTIONS Remote-Abnahme:** Runtime `32673385832` · Presentation `32673385764` · Repository Health `32673385757` · Release Acceptance `32673385796` · Release Package `32673385792` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-UX-TIMELINE-FILTER – lokale Timeline-Filter`
- **TIMELINE-FILTER-Status:** ALLE / STRASSE / KRISE / BEZIRK filtern ausschließlich die vorhandene bestätigte Runtime-Timeline; keine Neusortierung, kein Journal-State, keine Speicherung
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

---

# Aktiv – 0.8.8-UX-TIMELINE-FILTER

## Ziel

Die bestehende bestätigte Timeline soll lokal nach `ALLE / STRASSE / KRISE / BEZIRK` filterbar sein, ohne ihre Reihenfolge, Quelle oder Persistenz zu verändern.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Presentation-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- README nur wegen aktiver/folgender Iterationskonsistenz

**Arbeitsdateien**
- `web/a4/event_timeline.js`
- `tests/presentation/test_a4_event_timeline_control_deck.py`
- `tests/runtime/test_feature_status_consistency.py`
- `docs/LAIENHILFE_TIMELINE_FILTER.md`

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### TIMELINE-FILTER – kleinster read-only UX-Slice

- [x] Filter `ALLE / STRASSE / KRISE / BEZIRK`
- [x] Filterstate ausschließlich im Modul-RAM; kein Local-/Session-Storage
- [x] Filterung ausschließlich mit `.filter(...)` auf der vorhandenen Runtime-Reihenfolge
- [x] kein `.sort(...)`, `.reverse(...)`, POST, Command oder Save-/Journal-Write
- [x] `aria-pressed`, Gruppennamen und verständlicher Status für Tastatur/Screenreader
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32673876348` · Presentation `32673876321` · Repository Health `32673876323` · Release Acceptance `32673876297` · Release Package `32673876299`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in TIMELINE-FILTER

- keine neue Timeline-Projection oder Storyquelle
- keine neue Sortierlogik
- keine Filterpersistenz
- kein Journal-State
- keine Änderung an Runtime-/Gameplay-Autorität
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-ECON-RECOVERY-FEEDBACK:** bestätigte Vorher→Nachher-Werte der Regeneration verständlich anzeigen; keine neue Mechanik
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-STREET-PACK:** bestehende Straßenereignisse später über den vorhandenen Encounter-Vertrag erweitern

---

## Architektur- und Sicherheitsgrenzen

- Timeline-Quelle bleibt ausschließlich die vorhandene bestätigte Runtime-Projection.
- Filter dürfen Einträge nur ausblenden, nie umsortieren, neu erzeugen oder zurückschreiben.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
