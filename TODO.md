# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-B – Scene Jobs & persönliches Bargeld` · PR #105 · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`
- **0.8.8-B Remote-Abnahme:** Runtime `32649707398` · Presentation `32649707389` · Repository Health `32649707385` · Release Acceptance `32649707396` · Release Package `32649707391` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-C – Secret Best Friend Assistant`
- **C1:** Assistenten-Autoritätsvertrag am bestehenden Scene-Job-Katalog implementiert; Remote-Abnahme dieses PRs steht noch aus
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

## 0.8.8-B – Scene Jobs & persönliches Bargeld

- [x] fünf katalogisierte Scene Jobs mit stabilen IDs
- [x] persönlicher `PlayerFinanceState` mit Bargeld + gemeinsamem Finance-Ledger
- [x] Joblohn sowie Energie-/Stressfolge atomar über `SceneJobService`
- [x] `finance.job_completed` in Journal und Recovery integriert
- [x] Retry derselben Command-ID zahlt nicht doppelt
- [x] A4 zeigt JOBS-Bereich, Jobfolgen und persönliches Bargeld
- [x] Browser sendet bei `job.run` ausschließlich `job_id` + technische Command-ID
- [x] Legacy-Saves ohne Finance-State zeigen lesend 0 € ohne Write
- [x] PR #105 finaler Head `6a653e40e19c80aed4df827910f7c91110a8a679` · 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`

---

# Aktiv – 0.8.8-C Secret Best Friend Assistant

## Ziel

Genau eine vorhandene kanonische Aufgabe aktivieren und pro bestätigter Spielrunde exakt einmal durch den „geheimen besten Freund“ ausführen lassen; Stop und Wechsel bleiben jederzeit möglich.

### C1 – Autoritäts- und Wiederverwendungsvertrag

- [x] Assistenten-Regeln direkt in `SCENE_JOB_MANIFEST.json`; kein zweiter Aufgaben- oder Jobkatalog
- [x] `task_source=scene_jobs` und `max_active_tasks=1` fail-closed validiert
- [x] bestätigte Spielrunde zwingend; Systemzeit ausdrücklich keine Autorität
- [x] Browser darf weder Rundenautorität noch Lohn/Effekte liefern
- [x] Stop und Aufgabenwechsel als Pflicht für die spätere Steuerung vertraglich festgelegt
- [x] gezielte Runtime-Regression gegen unsichere/duplizierte Assistenten-Policy
- [x] Laienhilfe erklärt klar: C1 definiert Regeln, aktiviert aber noch keine Automatik

### C2 – kleinster nächster Runtime-Slice

- [ ] kleinen dauerhaften Assistenten-Steuerzustand für `aus / gewählter job` anlegen
- [ ] Start, Stop und Wechsel replaybar/recoverbar machen
- [ ] ausschließlich vorhandene Scene-Job-IDs akzeptieren
- [ ] noch keine automatische Rundenausführung in denselben Patch mischen

### Danach in C

- [ ] bestätigten Runden-Trigger an genau eine Assistenten-Ausführung binden
- [ ] derselbe bestätigte Runden-Trigger kann weder erneut auszahlen noch erneut Ressourcen verbuchen
- [ ] kompakte erzählerische Integration im bestehenden JOBS-Kontext statt zweitem Assistenten-Dashboard
- [ ] gezielte Recovery- und Presentation-Regressionen

### Bewusst nicht in C1

- keine automatische Jobausführung
- keine neue Journal-Eventart
- keine Bankeinzahlung/-auszahlung
- keine Zinsen, Anlagen oder Dividenden
- keine Hintergrundausführung per Rechneruhr
- kein zweites Aufgaben-/Rundensystem
- kein Produktversionsbump

---

# Danach priorisiert

1. **0.8.8-D – Bank & Investments:** Bargeld einzahlen/abheben, bestätigte Zinsperioden, Zinseszins, Anlagen/Dividenden und nachvollziehbare Auszüge auf demselben Finance-Ledger.
2. **0.8.8-E – Control Deck Focus:** Informationen verdichten, doppelte Ansichten entfernen, Arbeitsbereiche lokal maximieren/zurücksetzen und nächste erlaubte Aktion kontrastreich hervorheben.
3. **0.8.8-F – Berlin Ops Map 2:** bezirksartige Darstellung, Zoom/Pan, bessere Objekt-Hierarchie und Detailansicht; Karte bleibt read-only.

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR: pro fachlichem Modul eigener kleiner Slice.
- Keine zweite Economy-, Finance-, Map-, Timeline-, Profile-, Assistant-Task- oder Sync-Engine.
- Persönliches Bargeld ist nicht das Eventbudget; beide bleiben fachlich getrennt.
- Browser sendet nur erlaubte IDs; Geld, Jobfolgen, Zinsen, Dividenden und Assistentenfolgen werden serverseitig bestimmt.
- Wiederholte Assistentenaktionen und Finanzzyklen brauchen bestätigte Spielrunde/Spielweltzeit; niemals Systemzeit allein.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
