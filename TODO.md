# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-B – Scene Jobs & persönliches Bargeld` · PR #105 · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`
- **0.8.8-B Remote-Abnahme:** Runtime `32649707398` · Presentation `32649707389` · Repository Health `32649707385` · Release Acceptance `32649707396` · Release Package `32649707391` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-C – Secret Best Friend Assistant`
- **C-Status:** Runtime/Recovery + A4-Integration implementiert; Remote-Abnahme und Safe Merge stehen noch aus
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
- [x] PR #104 5/5 Remote-Gates, 0 Review-Threads und `/safe-merge` PASS

## 0.8.8-B – Scene Jobs & persönliches Bargeld

- [x] fünf szenetypische Jobs mit serverseitiger Dauer, Auszahlung, Energie und Stress
- [x] persönlicher `PlayerFinanceState` + gemeinsames Finance-Ledger
- [x] `SceneJobService` verbucht Lohn und Ressourcen atomar und replaybar
- [x] A4-JOB-Bereich + Bargeldanzeige; Browser sendet nur `job_id`
- [x] Legacy-Saves ohne Finance-State bleiben lesbar und starten bei 0 € ohne Read-Write
- [x] PR #105 / Head `6a653e40e19c80aed4df827910f7c91110a8a679` · 5/5 Gates · 0 Review-Threads · SAFE MERGE PASS · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`

---

# Aktiv – 0.8.8-C Secret Best Friend Assistant

## Ziel

Jeder Spieler erhält einen erzählerisch integrierten **geheimen besten Freund**, dem genau ein vorhandener Scene Job zugewiesen werden kann. Er erledigt diese Aufgabe nach jeder bestätigten Straßenrunde genau einmal, bis der Spieler sie wechselt oder stoppt.

### Vertrag & Runtime

- [x] `ASSISTANT_MANIFEST.json` mit stabiler Story-Rolle und `confirmed_street_walk` als einziger Rundenauslöser
- [x] `AssistantState` mit einer aktiven Aufgabe, letzter bestätigter Runde, Ausführungszähler und Revision
- [x] Assistent verwendet ausschließlich vorhandene `SceneJobService`-Jobs; keine zweite Job-/Task-Engine
- [x] Spieler kann Aufgabe setzen, wechseln und deaktivieren
- [x] aktive Aufgabe wird nach bestätigter `street.walk`-Runde genau einmal ausgeführt
- [x] Retry derselben Straßenrunde kann Joblohn nicht doppelt buchen
- [x] keine Systemzeit und kein Hintergrundtimer als Gameplay-Autorität
- [x] Browser kann weder Assistenten-Auszahlung noch Energie-/Stressfolge noch Rundennummer liefern
- [x] Assistant-State ist im gemeinsamen Journal-/Recovery-Pfad replaybar

### A4 / UX

- [x] read-only Assistant-Projection mit Story, aktiver Aufgabe, erledigten Runden und Triggerhinweis
- [x] kein zweiter Aufgabenbildschirm: Assistent wird direkt im vorhandenen JOBS-Bereich dargestellt
- [x] jede Jobkarte kann mit `FREUND ÜBERNIMMT` zugewiesen werden
- [x] aktiver Job ist eindeutig markiert; `AUFGABE STOPPEN` deaktiviert den Assistenten
- [x] vorhandener `/api/state`-Refresh wird mitgenutzt; kein weiterer Polling-Loop
- [x] Runtime-/GameClient-/Presentation-Regressionen ergänzt

### Noch vor Merge

- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch weiterhin 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in C

- keine Bankeinzahlung/-auszahlung
- keine Zinsen, Anlagen oder Dividenden
- keine frei konfigurierbaren Makros oder beliebigen Command-Ketten
- keine Offline-/Systemzeit-Automatik
- kein Produktversionsbump

---

# Priorisierter Ausbau nach 0.8.8-C

1. **0.8.8-D – Bank & Investments:** Bargeld einzahlen/abheben, bestätigte Zinsperioden, Zinseszins, Anlagen/Dividenden und nachvollziehbare Auszüge auf demselben Finance-Ledger.
2. **0.8.8-E – Control Deck Focus:** Informationen verdichten, doppelte Ansichten entfernen, Arbeitsbereiche lokal maximieren/zurücksetzen und nächste erlaubte Aktion kontrastreich hervorheben; Reduced Motion respektieren.
3. **0.8.8-F – Berlin Ops Map 2:** bezirksartige Darstellung, Zoom/Pan, bessere Objekt-Hierarchie und Detailansicht; Karte bleibt read-only.
4. **POOL-STORY-001 – Ereignis-Nachhall:** bestätigte wichtige District-Ereignisse später in der Crew-Biografie aufgreifen.
5. **POOL-UX-003 – Timeline-Fokusfilter:** lokal Straße/Krise/Bezirk filtern, ohne Reihenfolge oder Save-State zu verändern.

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR: pro fachlichem Modul eigener kleiner Slice.
- Keine zweite Economy-, Finance-, Job-, Map-, Timeline-, Profile- oder Sync-Engine.
- Persönliches Bargeld ist nicht das Eventbudget; beide bleiben fachlich getrennt.
- Browser sendet nur erlaubte IDs; Geld, Jobfolgen, Zinsen, Dividenden und Assistentenfolgen werden serverseitig bestimmt.
- Wiederholte Assistentenaktionen und Finanzzyklen brauchen bestätigte Spielrunde/Spielweltzeit; niemals Systemzeit allein.
- Blink-/Puls-Hinweise sind reine lokale Presentation und müssen bei Reduced Motion statisch werden.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
