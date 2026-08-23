# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-A – Crew Identity Logo/Fahne` · PR #104 · Merge `7e0ed1e36dcc89436c0430d49e547fe2106f756b`
- **0.8.8-A Remote-Abnahme:** Runtime `32648468121` · Presentation `32648468165` · Repository Health `32648468119` · Release Acceptance `32648468142` · Release Package `32648468140` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-B – Scene Jobs & persönliches Bargeld`
- **B2-Status:** Runtime/Recovery + sichtbare A4-Integration implementiert; Remote-Abnahme und Safe Merge stehen noch aus
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.7-C – District World Events & Timeline

- [x] C1: stabiler District-Event-Katalog mit deterministischer Auswahl
- [x] C2: Runtime, Journal-/Recovery-Nutzung, Fail-fast-Katalogprüfung
- [x] C3: ausschließlich `settlement.complete` als autorisierter Application-Trigger
- [x] C4A: read-only Timeline-Projection aus bestätigten Journalrecords
- [x] C4B: Timeline im Control Deck sichtbar, Browser sortiert oder schreibt nichts
- [x] C5: 24h-Cadence aus bestätigter Spielweltzeit; Retry/Reload bleibt idempotent

## 0.8.8-A – Crew Identity Logo/Fahne

- [x] Logo/Fahne als kleines synchronisierbares Identitätsrezept statt Bildblob
- [x] bestehender `profile.update` / `character.profile_updated`-Pfad bleibt einzige Schreibgrenze
- [x] Legacy-Saves erhalten stabilen neutralen Default ohne Journal-Umschreibung
- [x] A4-Editor mit Preview; Character-ID und Gameplaywerte bleiben unverändert
- [x] Runtime-, Presentation- und Recovery-Regressionen
- [x] PR #104 5/5 Remote-Gates, 0 Review-Threads und `/safe-merge` PASS

---

# Aktiv – 0.8.8-B Scene Jobs & persönliches Bargeld

## Ziel

Der Spieler kann unabhängig von der Eventphase normale szenetypische Jobs ausführen, um persönliches Bargeld anzusparen. Auszahlung und Ressourcenfolgen werden ausschließlich von der Runtime bestimmt.

### B1 – Runtime & Wallet

- [x] `SCENE_JOB_MANIFEST.json` mit fünf szenetypischen Jobs und stabilen IDs
- [x] persönliche Finance-Basis mit `cash_cents`, späterem Bank-/Investment-Platz und einem gemeinsamen Finance-Ledger
- [x] `SceneJobService` verbucht Lohn sowie Energie-/Stressfolge atomar
- [x] `finance.job_completed` im vorhandenen Journal-/Recovery-Pfad integriert
- [x] Job-Retry mit derselben Command-ID zahlt nicht doppelt
- [x] unbekannte Jobs, falscher Character-Kontext und Client-Effektinjektion werden vor Write abgewiesen

### B2 – sichtbarer A4-Slice

- [x] A4-Launcher lädt denselben Scene-Job-Vertrag und konfiguriert den vorhandenen `GameClientSession`
- [x] read-only Scene-Job-/Wallet-Projection aus bestätigtem State + validiertem Service-Katalog
- [x] kompakter `JOBS`-Bereich im Control Deck mit Jobbeschreibung, Dauer, Lohn, Energie und Stress
- [x] persönliches Bargeld kompakt im OPS-HUD und im Jobkontext sichtbar
- [x] Browser sendet bei `job.run` ausschließlich `job_id` + technische Command-ID; keine Auszahlung oder Effekte
- [x] Legacy-Saves ohne Finance-State zeigen 0 € Bargeld, ohne beim Lesen zu schreiben
- [x] gezielte Runtime-/Presentation-Regressionen ergänzt
- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch weiterhin 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in B

- kein Assistenten-Autoloop
- keine Bankeinzahlung/-auszahlung
- keine Zinsen, Anlagen oder Dividenden
- keine Systemzeit als Job- oder Finance-Autorität
- kein Produktversionsbump

---

# Priorisierter Ausbau nach 0.8.8-B

1. **0.8.8-C – Secret Best Friend Assistant:** genau eine vorhandene Aufgabe aktivieren; pro bestätigter Runde exakt einmal ausführen; Stop/Wechsel jederzeit; vorhandene Job-/Task-Services wiederverwenden.
2. **0.8.8-D – Bank & Investments:** Bargeld einzahlen/abheben, bestätigte Zinsperioden, Zinseszins, Anlagen/Dividenden und nachvollziehbare Auszüge auf demselben Finance-Ledger.
3. **0.8.8-E – Control Deck Focus:** Informationen verdichten, doppelte Ansichten entfernen, Arbeitsbereiche lokal maximieren/zurücksetzen und nächste erlaubte Aktion kontrastreich hervorheben; Reduced Motion respektieren.
4. **0.8.8-F – Berlin Ops Map 2:** bezirksartige Darstellung, Zoom/Pan, bessere Objekt-Hierarchie und Detailansicht; Karte bleibt read-only.
5. **POOL-STORY-001 – Ereignis-Nachhall:** bestätigte wichtige District-Ereignisse später in der Crew-Biografie aufgreifen.
6. **POOL-UX-003 – Timeline-Fokusfilter:** lokal Straße/Krise/Bezirk filtern, ohne Reihenfolge oder Save-State zu verändern.

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR: pro fachlichem Modul eigener kleiner Slice.
- Keine zweite Economy-, Finance-, Map-, Timeline-, Profile- oder Sync-Engine.
- Persönliches Bargeld ist nicht das Eventbudget; beide bleiben fachlich getrennt.
- Browser sendet nur erlaubte IDs; Geld, Jobfolgen, Zinsen, Dividenden und Assistentenfolgen werden serverseitig bestimmt.
- Wiederholte Assistentenaktionen und Finanzzyklen brauchen bestätigte Spielrunde/Spielweltzeit; niemals Systemzeit allein.
- Blink-/Puls-Hinweise sind reine lokale Presentation und müssen bei Reduced Motion statisch werden.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
