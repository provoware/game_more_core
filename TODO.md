# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-C1 – Assistant Authority Contract` · PR #107 · Merge `a16436582928d02202f38366c63d7cf790d5deb6`
- **0.8.8-C1 Remote-Abnahme:** Runtime `32653528714` · Presentation `32653528815` · Repository Health `32653528779` · Release Acceptance `32653528627` · Release Package `32653528682` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-C2 – Assistant Control State`
- **C2-Status:** persistenter Steuerzustand für Aus/Jobwahl, Start/Stop/Wechsel und Recovery implementiert; Remote-Abnahme dieses PRs steht noch aus
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.8-A – Crew Identity Logo/Fahne

- [x] Logo/Fahne als kleines synchronisierbares Identitätsrezept statt Bildblob
- [x] bestehender `profile.update` / `character.profile_updated`-Pfad bleibt einzige Schreibgrenze
- [x] Legacy-Saves erhalten stabilen neutralen Default ohne Journal-Umschreibung
- [x] A4-Editor mit Preview; Character-ID und Gameplaywerte bleiben unverändert
- [x] PR #104 5/5 Remote-Gates, 0 Review-Threads und `/safe-merge` PASS

## 0.8.8-B – Scene Jobs & persönliches Bargeld

- [x] fünf katalogisierte Scene Jobs mit stabilen IDs
- [x] persönlicher `PlayerFinanceState` mit Bargeld + gemeinsamem Finance-Ledger
- [x] Joblohn sowie Energie-/Stressfolge atomar über `SceneJobService`
- [x] `finance.job_completed` in Journal und Recovery integriert
- [x] Retry derselben Command-ID zahlt nicht doppelt
- [x] A4 zeigt JOBS-Bereich, Jobfolgen und persönliches Bargeld
- [x] Browser sendet bei `job.run` ausschließlich `job_id` + technische Command-ID
- [x] PR #105 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693`

## 0.8.8-C1 – Assistenten-Autoritätsvertrag

- [x] Assistenten-Regeln direkt im bestehenden Scene-Job-Vertrag; kein zweiter Aufgabenkatalog
- [x] `task_source=scene_jobs` und `max_active_tasks=1` fail-closed validiert
- [x] bestätigte Spielrunde zwingend; Systemzeit ausdrücklich keine Autorität
- [x] Browser darf weder Rundenautorität noch Lohn/Effekte liefern
- [x] Stop und Aufgabenwechsel für die spätere Steuerung verpflichtend
- [x] PR #107 · finaler Head `3cf918ac98d5a76d2b4ff13b3f6e46b2a458d06f` · 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `a16436582928d02202f38366c63d7cf790d5deb6`

---

# Aktiv – 0.8.8-C2 Assistant Control State

## Ziel

Der Spieler kann für den geheimen besten Freund genau einen vorhandenen Scene Job auswählen, wechseln oder stoppen; diese reine Steuerentscheidung bleibt über Save/Recovery erhalten, führt aber noch keine Arbeit aus.

### C2 – kleinster Runtime-Slice

- [x] `AssistantControlState` mit `active_job_id` und monotoner Revision
- [x] genau ein aktiver Job oder `null` für Aus; keine Liste paralleler Aufgaben
- [x] ausschließlich IDs aus dem bestehenden `SCENE_JOB_MANIFEST.json`
- [x] Start, Wechsel und Stop über denselben Persistence-Kernel
- [x] `assistant.control_changed` im kanonischen Journal katalogisiert
- [x] Retry derselben Command-ID idempotent; Bedeutungswechsel derselben Command-ID fail-closed
- [x] gleiche Auswahl erneut ist schreibfreier No-op
- [x] Game-Recovery rekonstruiert den Assistenten-Steuerzustand
- [x] Character und Finance bleiben durch reine Steuerung unverändert
- [x] gezielte Runtime-Regressionen und Laienhilfe ergänzt
- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch weiterhin 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in C2

- keine automatische Jobausführung
- keine Auszahlung oder Energie-/Stressfolge
- kein bestätigter Runden-Trigger
- keine Hintergrundausführung per Rechneruhr
- kein zweites Aufgaben-/Rundensystem
- keine Bank, Zinsen, Anlagen oder Dividenden
- kein Produktversionsbump

### Danach in C

- [ ] **C3:** bestätigten Runden-Trigger an genau eine Assistenten-Ausführung binden
- [ ] derselbe bestätigte Runden-Trigger kann weder erneut auszahlen noch erneut Ressourcen verbuchen
- [ ] **C4:** kompakte erzählerische Integration im bestehenden JOBS-Kontext statt zweitem Assistenten-Dashboard
- [ ] gezielte Recovery- und Presentation-Regressionen

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
- Ein gespeicherter Assistenten-Steuerzustand ist noch keine Ausführungsberechtigung.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
