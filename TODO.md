# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-C2 – Assistant Control State` · PR #108 · Merge `5c597479afafe64f63aa4ce015cea5365b2320bf`
- **0.8.8-C2 Remote-Abnahme:** Runtime `32656644301` · Presentation `32656644312` · Repository Health `32656644321` · Release Acceptance `32656644302` · Release Package `32656644313` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-C3 – Confirmed-Round Execution`
- **C3-Status:** bestätigte Runde wird intern genau einmal verarbeitet; vorhandener `SceneJobService` bleibt einzige Jobausführung und Retry darf weder doppelt zahlen noch Ressourcen doppelt verbuchen
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

## 0.8.8-C2 – Assistant Control State

- [x] `AssistantControlState` mit genau `active_job_id + revision`
- [x] Aus, Jobwahl, Wechsel und Stop über denselben Persistence-Kernel
- [x] ausschließlich vorhandene Scene-Job-IDs; keine zweite Aufgabenliste
- [x] `assistant.control_changed` katalogisiert und über Game-Recovery rekonstruierbar
- [x] Retry derselben Command-ID idempotent; Bedeutungswechsel fail-closed
- [x] identische Auswahl ist schreibfrei und verändert Character/Finance nicht
- [x] PR #108 · finaler Head `a8d6b9ffe2c8369ff1a41320a87faad069610779` · 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `5c597479afafe64f63aa4ce015cea5365b2320bf`

---

# Aktiv – 0.8.8-C3 Confirmed-Round Execution

## Ziel

Eine intern bestätigte Spielrunde darf den zu diesem Zeitpunkt gewählten Scene Job exakt einmal über den vorhandenen `SceneJobService` ausführen. Derselbe Rundentrigger bleibt bei Retry, Reload oder einem späteren Jobwechsel ohne zweite Auszahlung und ohne doppelte Energie-/Stressfolge.

### C3 – kleinster Runtime-Slice

- [x] interner `ConfirmedRoundTrigger` mit stabiler Runden-ID und Character-Bindung; keine Browser-Command-Erweiterung
- [x] `AssistantRoundExecutionService` orchestriert nur; fachliche Jobfolgen bleiben vollständig in `SceneJobService`
- [x] deterministische Child-Command-ID pro Character + bestätigter Runde nutzt vorhandene Scene-Job-Idempotenz
- [x] `assistant.round_processed` markiert jede Runde genau einmal, auch wenn der Assistent aus ist
- [x] Runde im Zustand Aus kann nach späterer Jobwahl nicht rückwirkend Arbeit auslösen
- [x] Crash-Fortsetzung erkennt bereits durable Jobausführung und beendet den ursprünglichen Rundenauftrag ohne Doppelzahlung
- [x] Jobwechsel nach bereits verarbeiteter Runde ändert die alte Runde nicht
- [x] Systemzeit ist weder Trigger noch Autorität; Browser erhält keine Rundenautorität
- [x] gezielte Runtime-Regressionen für Retry, Aus-Zustand, Jobwechsel und Crash-Zwischenzustand
- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch weiterhin 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in C3

- keine JOBS-UI-Steuerung für den Assistenten
- keine neue Job-/Lohn-/Ressourcenlogik
- keine Rechnerzeit- oder Browserautorität
- keine Hintergrundschleife außerhalb bestätigter Runden
- kein Freundschafts-/Beziehungsfortschritt
- keine Bank, Zinsen, Anlagen oder Dividenden
- kein Produktversionsbump

### Danach in C

- [ ] **C4:** Assistent im bestehenden JOBS-Bereich auswählen, wechseln, stoppen und verständlich anzeigen; kein zweites Dashboard
- [ ] **C5:** bestätigte Assistentenaktionen als kleinen Freundschafts-/Story-Nachhall projizieren; keine zweite Progressionsengine
- [ ] gezielte Presentation-, Recovery- und Accessibility-Regressionen

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
- Ein verarbeiteter Rundentrigger bleibt fachlich unveränderlich; Retry darf keine spätere Auswahl rückwirkend anwenden.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
