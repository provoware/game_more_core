# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-F – Berlin Ops Map 2` · PR #117 · Merge `8119bf71a6f169d5cac367d5123d2bc1e6a73193`
- **0.8.8-F Remote-Abnahme:** Runtime `32666137485` · Presentation `32666137499` · Repository Health `32666137472` · Release Acceptance `32666137497` · Release Package `32666137508` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-STORY-DISTRICT-BIO – Bezirks-Nachhall`
- **STORY-Status:** bis zu fünf bestätigte District-Einträge der bestehenden Ereignis-Chronik werden read-only als Berlin-Erinnerungen im vorhandenen Profil sichtbar; keine neue Progressions-/Journalengine
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
- [x] PR #117 · Head `91255bbb7bee90050cbd762ce93600802a666940` · Runtime `32666137485` · Presentation `32666137499` · Repository Health `32666137472` · Release Acceptance `32666137497` · Release Package `32666137508` · 0 Review-Threads · `/safe-merge` PASS · Merge `8119bf71a6f169d5cac367d5123d2bc1e6a73193`

---

# Aktiv – 0.8.8-STORY-DISTRICT-BIO

## Ziel

Bestätigte Veränderungen in Berlin werden im bestehenden Profil als kleiner erzählerischer Nachhall sichtbar, ohne eine zweite Biografie-, Story- oder Progressionsengine zu erzeugen.

### Planned-Read-Liste gemäß AGENTS.md

- `AGENTS.md`
- aktive Stellen aus `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `src/bunkerfrequenz/presentation/event_timeline.py`
- `src/bunkerfrequenz/presentation/biography_projection.py` nur zur Architekturabgrenzung
- `web/a4/index.html` nur Profilstruktur
- `web/a4/ui_prefs.js`
- neues `web/a4/district_biography.js`
- neue `tests/presentation/test_a4_district_biography.py`
- `tests/runtime/test_feature_status_consistency.py`
- neue `docs/LAIENHILFE_DISTRICT_BIO.md`

Weitere Dateien nur nach konkretem Gate-/Vertragsbefund.

### STORY – kleinster Nachhall-Slice

- [x] ausschließlich vorhandene bestätigte `event_timeline` als Datenquelle
- [x] nur Einträge mit `kind === "district"` und bestätigter `district_id`
- [x] maximal fünf Berlin-Erinnerungen im bestehenden Profilbereich
- [x] Titel, Text und District-Deltas werden nicht neu berechnet oder umgedeutet
- [x] keine erfundenen Datums-/Uhrzeitangaben
- [x] kein `/api/command`, kein Storage, kein neuer Save-/Journal-State
- [x] keine XP, Ruf-, Beziehungs-, Bonus- oder Unlock-Folge
- [x] kein `character.biography_entry_added` und keine zweite persistente Biografie
- [x] isoliertes Presentation-Modul wird über bestehenden kleinen UI-Lader geladen
- [x] gezielte Presentation-Regression und Laienhilfe ergänzt
- [x] erster technischer Remote-Prüfstand 5/5 grün
- [ ] finalen Dokumentations-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in STORY-DISTRICT-BIO

- keine neuen District-Events oder Gameplayeffekte
- keine neue Journal-/Biografie-Eventart
- kein persistenter Story-State
- keine frei erfundenen Erinnerungen oder Zeitangaben
- keine Finance-, Assistant-, Map- oder Propertyänderung
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-FIN-EXPORT:** validierte FIN-STATEMENTS-Projection optional als TXT/CSV exportieren; keine neue Buchhaltung
- [ ] **0.8.8-ECON-ANTI-GRIND:** niedrige Energie bei Scene Jobs spielerisch lesbarer begrenzen, getrennt von diesem Story-Slice
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR und keine zweite Story-, Economy-, Finance-, Map- oder Assistant-Engine.
- Berlin-Erinnerungen sind ausschließlich lokale read-only Presentation aus bestätigter Timeline.
- Browser darf keine District-Ereignisse, Texte, Deltas oder Zeitpunkte bestätigen.
- Persistente Charakterbiografie bleibt unverändert.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)