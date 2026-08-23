# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-D2 – Confirmed Savings Interest` · PR #114 · Merge `bbebc9c3cafeac7f71eebeea1b89d4861b304e76`
- **0.8.8-D2 Remote-Abnahme:** Runtime `32663103520` · Presentation `32663103517` · Repository Health `32663103523` · Release Acceptance `32663103519` · Release Package `32663103518` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-E – Control Deck Focus`
- **E-Status:** Fokus/Zurücksetzen und Nächste-Aktion-Signal sind reine lokale Presentation; keine neue Gameplay-, Save- oder Journal-Autorität
- **Entwicklungsprozess:** Focused-Read bleibt verpflichtend; Codex-Code-Review ist vollständig aus Entwicklung, Gate-Evidenz und Mergeprozess entfernt
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.8-A – Crew Identity Logo/Fahne
- [x] syncfähiges Identitätsrezept, Legacy-Default, A4-Editor
- [x] PR #104 · Merge `7e0ed1e36dcc89436c0430d49e547fe2106f756b`

## 0.8.8-B – Scene Jobs & persönliches Bargeld
- [x] fünf katalogisierte Jobs, persönlicher Finance-State, Retry/Recovery
- [x] PR #105 · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`

## 0.8.8-C1 – Assistant Authority
- [x] bestehender Scene-Job-Katalog, eine Aufgabe, bestätigte Runde, keine Systemzeit-/Browserautorität
- [x] PR #107 · Merge `a16436582928d02202f38366c63d7cf790d5deb6`

## 0.8.8-C2 – Assistant Control State
- [x] Aus/Jobwahl/Wechsel/Stop persistent und recoverbar
- [x] PR #108 · Merge `5c597479afafe64f63aa4ce015cea5365b2320bf`

## 0.8.8-C3 – Confirmed-Round Execution
- [x] bestätigte Runde exakt einmal; Retry/Crash/Jobwechsel abgesichert
- [x] PR #109 · Merge `85e95995d5e84c53131e24a8ad3dec36717891c6`

## 0.8.8-C4 – JOBS-UI-Integration
- [x] Assistent Start/Wechsel/Stop/Status direkt im vorhandenen JOBS-Bereich
- [x] PR #110 · Merge `f8295564a4bddabddb4493c778e549d1cb083374`

## 0.8.8-C5A/C5B – Freundschafts-Nachhall
- [x] nur bestätigte Runde + passende Jobbuchung; deterministisch sichtbar; keine Progressionsengine
- [x] PR #111 · Merge `dc22935d92cf9fea0d72aaac449921a6093a431f`
- [x] PR #112 · Merge `eaa615e48eecd84ba3ffb69551f8fb324fb42c12`

## 0.8.8-D – Atomic Wallet ↔ Bank Transfers
- [x] atomare Ein-/Auszahlung auf bestehendem `PlayerFinanceState` und Finance-Ledger
- [x] Retry/Recovery fail-closed, Browser liefert keine Zielstände
- [x] PR #113 · Merge `c1a27a977ff76a397d95ae097395317c4d46950b`

## 0.8.8-D2 – Confirmed Savings Interest
- [x] 1 % pro bestätigter Finance-Periode auf aktuellen Bankstand
- [x] Zinseszins ohne zweite Finance-Engine
- [x] lückenloser `confirmed_finance_tick`, Retry exakt einmal
- [x] Nullzinsperioden werden verbraucht; keine rückwirkende Verzinsung
- [x] kein Systemzeit-/Browser-Trigger
- [x] PR #114 · Head `897b5717776012376ef20e33093b413700744e07` · Runtime `32663103520` · Presentation `32663103517` · Repository Health `32663103523` · Release Acceptance `32663103519` · Release Package `32663103518` · 0 Review-Threads · `/safe-merge` PASS · Merge `bbebc9c3cafeac7f71eebeea1b89d4861b304e76`

---

# Aktiv – 0.8.8-E Control Deck Focus

## Ziel

Das bestehende Control Deck wird übersichtlicher, ohne einen neuen Spielzustand einzuführen: einzelne Bereiche lokal fokussieren/zurücksetzen und die bereits von der Runtime erlaubte nächste Event-Aktion deutlich hervorheben.

### Planned-Read-Liste gemäß AGENTS.md

- `AGENTS.md`
- `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md`
- `web/a4/index.html` nur Struktur
- `web/a4/app.js` nur Event-Aktionsrendering
- `web/a4/styles.css` nur Panel-/Layoutbasis
- `web/a4/ui_prefs.js`
- `web/a4/control_deck_focus.js`
- `tests/presentation/test_a4_control_deck_focus.py`
- `tests/runtime/test_feature_status_consistency.py`

Weitere Dateien nur nach konkretem Gate-/Vertragsbefund.

### E – kleinster Presentation-Slice

- [x] Codex-Code-Review aus Entwicklungs-/Review-/Gate-/Mergeprozess entfernt
- [x] isoliertes `control_deck_focus.js` ohne API-, Save- oder Journalzugriff
- [x] jeder sichtbare bestehende Panel-Header erhält lokalen `FOKUS`
- [x] fokussierter Bereich nutzt die volle Arbeitsfläche; `GESAMTANSICHT` stellt sofort zurück
- [x] Fokuszustand wird weder in `localStorage` noch `sessionStorage` gespeichert
- [x] Nächste-Aktion-Signal nimmt ausschließlich `#event-actions button:not(:disabled)` als Quelle
- [x] keine eigene Action-/Gate-Regel im Browser
- [x] Reduced Motion erhält statische Hervorhebung ohne notwendige Animation
- [x] kein zweites Dashboard und keine Runtime-/Domainänderung
- [x] gezielte Presentation-Regressionen
- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch 0 Commits hinter `main` bestätigen
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in E

- keine Gameplay-, Economy-, Finance- oder Assistant-Änderung
- keine neuen Commands/API-Endpunkte
- kein persistenter UI-Fokuszustand
- keine frei erfundene „nächste Aktion“
- keine Kontoauszüge
- kein C6 ohne kanonischen Rundenproduzenten
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-FIN-STATEMENTS – Kontoauszüge:** bestätigtes persönliches Finance-Ledger read-only als verständliche Job-, Einzahlungs-, Auszahlungs- und Zinsbewegungen darstellen
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-F – Berlin Ops Map 2:** Zoom/Pan und bessere Objekt-Hierarchie auf bestehender read-only Projection

---

# Danach priorisiert

1. **0.8.8-FIN-STATEMENTS – Kontoauszüge:** persönliche Geldhistorie aus dem bereits bestätigten Finance-Ledger; keine zweite Buchhaltung.
2. **0.8.8-F – Berlin Ops Map 2:** bessere Bezirkslesbarkeit, Zoom/Pan und Objekt-Hierarchie; Map bleibt read-only.
3. **0.8.8-C6 – Round-Authority Integration Harness:** sehr hohe Robustheitswirkung, aber weiterhin `DEPENDENCY` bis ein kanonischer Rundenproduzent existiert.

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR: pro fachlichem Modul eigener kleiner Slice.
- Keine zweite Economy-, Finance-, Map-, Timeline-, Profile-, Assistant-Task- oder Sync-Engine.
- UI-Fokus, Map-Zoom und lokale Filter sind Presentation-State und gehören nicht ins Journal.
- Nächste-Aktion-Hervorhebung darf ausschließlich bereits bestätigte/erlaubte Runtime-Daten spiegeln.
- Zinsen benötigen bestätigten Finance-Tick; Rechnerzeit allein erzeugt niemals Geld.
- Wiederholte Assistentenaktionen brauchen bestätigte Spielrunde; Systemzeit allein bleibt ohne Autorität.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
