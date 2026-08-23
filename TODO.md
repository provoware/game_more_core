# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-FIN-STATEMENTS – Kontoauszüge` · PR #116 · Merge `81dda0d21170a5d876cd5a7ebf05a8409ec735c8`
- **0.8.8-FIN-STATEMENTS Remote-Abnahme:** Runtime `32665075313` · Presentation `32665075287` · Repository Health `32665075289` · Release Acceptance `32665075282` · Release Package `32665075278` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-F – Berlin Ops Map 2`
- **F-Status:** lokale, begrenzte Zoom-/Pan-Steuerung und Auswahlfokus auf derselben bestätigten read-only Map-Projection; keine neue Map- oder Geodaten-Engine
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
- [x] neueste Buchung zuerst, Summen nur aus bestätigten Ledgerzeilen, keine erfundenen Zeitstempel
- [x] lokale Filter im bestehenden Bankbereich; keine zweite Finance-Engine und kein Write-Command
- [x] JSON-stabile Projection über HTTP, Restart und Recovery
- [x] PR #116 · Head `614e4363e95f6fedb5aac51e5aac72a67848ffbb` · Runtime `32665075313` · Presentation `32665075287` · Repository Health `32665075289` · Release Acceptance `32665075282` · Release Package `32665075278` · 0 Review-Threads · `/safe-merge` PASS · Merge `81dda0d21170a5d876cd5a7ebf05a8409ec735c8`

---

# Aktiv – 0.8.8-F Berlin Ops Map 2

## Ziel

Die bestehende Berlin Ops Map wird besser navigierbar, ohne ihre read-only Autoritätsgrenze zu verändern: begrenzter lokaler Zoom/Pan und Fokus auf die bereits ausgewählte Projection-Position.

### Planned-Read-Liste gemäß AGENTS.md

- `AGENTS.md`
- `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `manifests/BERLIN_OPS_MAP_PRO_MANIFEST.json`
- `src/bunkerfrequenz/presentation/berlin_ops_map_pro.py`
- `web/a4/map_pro.js`
- `web/a4/index.html` nur Map-Struktur
- `web/a4/styles.css` nur Map-Regeln
- `tests/presentation/test_a4_map_pro_contract.py`
- `tests/runtime/test_feature_status_consistency.py`
- neue `docs/LAIENHILFE_BERLIN_OPS_MAP.md`

Weitere Dateien nur nach konkretem Gate-/Vertragsbefund.

### F – kleinster Map-2-Slice

- [x] bestehende 0–100-Projection bleibt einzige Kartenquelle
- [x] Zoom lokal auf `1.0×–2.2×` begrenzt
- [x] Pan lokal begrenzt, damit die Kartenfläche nicht beliebig verloren geht
- [x] normale Buttons für Zoom, Reset und vier Pan-Richtungen; derselbe Pfad für Maus und Tastatur
- [x] `AUSWAHL FOKUS` richtet die Ansicht auf den bereits ausgewählten Bezirk oder Ort aus
- [x] Fokus verwendet ausschließlich vorhandene `district.map_box`-/`location.position`-Koordinaten
- [x] keine Pointer-/Wheel-Sonderautorität, kein persistierter Karten-Zustand
- [x] keine API, kein Geocoding, kein externer Kartendienst, keine Domain-/Property-Schreiblogik
- [x] Manifest beschreibt Zoom/Pan ausdrücklich als `local_bounded`
- [x] gezielte Presentation-Regressionen ergänzt
- [x] Laienhilfe für Zoom/Pan/Fokus ergänzt
- [ ] finalen Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in F

- kein echtes Geocoding oder Straßennetz
- keine neue Map-Projection oder zweite Kartenengine
- kein Drag-/Wheel-Zwang; Bedienbarkeit bleibt über Standardbuttons vollständig
- kein Save-/Journal-State für Zoom/Pan
- keine Property-, District-, Finance-, Assistant- oder Gameplayänderung
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-STORY-DISTRICT-BIO:** bestätigte District-World-Events als kleine Biografie-Nachhalltexte aus bestehenden Journal-/Projection-Daten
- [ ] **0.8.8-ECON-ANTI-GRIND:** extrem niedrige Energie bei Scene Jobs spielerisch lesbarer begrenzen, ohne phasenunabhängige Jobs abzuschaffen
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR und keine zweite Economy-/Finance-/Map-/Assistant-Engine.
- Map-2-Steuerung ist ausschließlich lokaler Presentation-State.
- UI-Filter, Fokus und Map-Zoom gehören nicht ins Journal.
- Kartenwerte und Koordinaten kommen ausschließlich aus der bestätigten Projection.
- Keine Navigation, Geocoding- oder externe Kartendienst-Abhängigkeit.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)