# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-ECON-RECOVERY-FEEDBACK – verständliches Regenerationsfeedback` · PR #125 · Merge `c8e8cba3dab103c90937f26e90a02a13139dd0f5`
- **RECOVERY-FEEDBACK Remote-Abnahme:** Runtime `32675067361` · Presentation `32675067353` · Repository Health `32675067359` · Release Acceptance `32675067362` · Release Package `32675067352` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-STREET-PACK – Straßenereignis-Erweiterung`
- **STREET-PACK-Status:** sechs zusätzliche Begegnungen teilen ausschließlich vorhandene Gewichtstöpfe auf; Makroverteilung, Auswahlalgorithmus, Ansätze und Replay-Pfad bleiben erhalten
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
- [x] PR #123 · Merge `7ed085b111a03173f0359bd76129d8d3b5f71900`

## 0.8.8-UX-TIMELINE-FILTER – lokale Timeline-Filter
- [x] Filter `ALLE / STRASSE / KRISE / BEZIRK`
- [x] ausschließlich lokaler Modul-State; keine Sortierung, Persistenz oder Journal-Autorität
- [x] PR #124 · Merge `465dc5040c5a1283fee5e7af52590455feaa9a01`

## 0.8.8-ECON-RECOVERY-FEEDBACK – Regenerationsfeedback
- [x] bestätigte Vorher→Nachher-Werte für Energie und Stress direkt sichtbar
- [x] nächste Verfügbarkeit ausschließlich aus der danach bestätigten Runtime-Projection
- [x] keine neue Mechanik, Delta-/Schwellenberechnung oder Persistenz
- [x] PR #125 · Head `129f1de8b76e569fab4bde51cb722c5aec64b637` · Runtime `32675067361` · Presentation `32675067353` · Repository Health `32675067359` · Release Acceptance `32675067362` · Release Package `32675067352` · 0 Review-Threads · `/safe-merge` PASS · Merge `c8e8cba3dab103c90937f26e90a02a13139dd0f5`

---

# Aktiv – 0.8.8-STREET-PACK

## Ziel

Mehr Abwechslung auf der Straße ausschließlich durch zusätzliche katalogisierte Begegnungen. Auswahl, Replay, Ansätze und Effekt-Autorität bleiben vollständig beim bestehenden `StreetEncounterService` und `STREET_ENCOUNTER_MANIFEST`.

### Planned-Read-Liste gemäß AGENTS.md

**Basisdateien**
- `AGENTS.md` – Focused Read, Katalog-/Merge-Grenzen
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- README wegen aktiver/folgender Iterationskonsistenz

**Arbeitsdateien**
- `manifests/STREET_ENCOUNTER_MANIFEST.json`
- `content/de/ui/street_encounters.json`
- `tests/runtime/test_street_pack_contract.py`
- bestehender `StreetEncounterService` nur zur Vertragsprüfung, ohne geplante Änderung
- `docs/LAIENHILFE_STREET_PACK.md`

**Evidenz/Logs**
- nur Run-ID/Status bei grünen Gates
- vollständiger Log ausschließlich bei einem konkreten roten Gate

### STREET-PACK – kataloggetriebener Erweiterungsslice

- [x] Katalog von 10 auf 16 Begegnungen erweitert
- [x] sechs neue Varianten: 1 neutral, 3 positiv, 2 negativ
- [x] globale Verteilung bleibt exakt `25 neutral / 60 positiv / 15 negativ`
- [x] `balanced` bleibt exakt der Basisgewichtskatalog
- [x] alle vier Ansätze enthalten exakt denselben vollständigen Katalog und summieren auf 100
- [x] Auswahl bleibt `sha256_stable_weighted`; Systemzeit bleibt ausgeschlossen
- [x] bisherige Vertragsversion `0.8.7-b1` bleibt als Replay-Version kompatibel
- [x] keine Economy-/Inventory-Effekte und keine neue Eventart
- [x] `StreetEncounterService` bleibt unverändert
- [x] technischer Remote-Prüfstand 5/5 grün: Runtime `32675648994` · Presentation `32675648960` · Repository Health `32675648979` · Release Acceptance `32675648956` · Release Package `32675648962`
- [ ] finalen Status-/Dokumentations-Head 5/5 grün bestätigen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in STREET-PACK

- keine zweite Encounter-Engine
- keine neue Zufallsquelle oder Systemzeit-Autorität
- keine neue Street-Ressource, Economy- oder Inventory-Logik
- keine Mini-Kettenereignisse
- keine Änderung an vorhandenen Approach-IDs
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-ECON-RECOVERY-VARIANTS:** erst nach Balancingprüfung eine zweite deutlich anders gewichtete Regenerationsentscheidung prüfen; keine Echtzeitregeneration
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-STREET-PACK-2:** nur bei nachgewiesenem Bedarf weitere Katalogvielfalt ergänzen; keine zweite Architektur

---

## Architektur- und Sicherheitsgrenzen

- Street-Auswahl bleibt deterministisch und replaybar aus der bestehenden bestätigten Autorität.
- Neue Begegnungen dürfen nur katalogisierte kleine Energie-/Stress-/Rufeffekte besitzen.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
