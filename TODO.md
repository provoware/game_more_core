# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-C3 – Confirmed-Round Execution` · PR #109 · Merge `85e95995d5e84c53131e24a8ad3dec36717891c6`
- **0.8.8-C3 Remote-Abnahme:** Runtime `32658555902` · Presentation `32658555885` · Repository Health `32658555929` · Release Acceptance `32658555886` · Release Package `32658555891` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-C4 – JOBS-UI-Integration`
- **C4-Status:** Start, Wechsel, Stop und bestätigter Assistentenstatus sind direkt in den vorhandenen JOBS-Bereich integriert; Browser liefert nur `job_id`/`null` und erhält keine Runden-, Lohn- oder Effekt-Autorität
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

## 0.8.8-C3 – Confirmed-Round Execution

- [x] interner `ConfirmedRoundTrigger` mit stabiler Runden-ID und Character-Bindung
- [x] `AssistantRoundExecutionService` delegiert Jobfolgen vollständig an `SceneJobService`
- [x] `assistant.round_processed` verbraucht jede bestätigte Runde genau einmal
- [x] Retry, Jobwechsel und Crash-Zwischenzustand bleiben gegen Doppelzahlung und doppelte Ressourcenfolgen geschützt
- [x] Runde im Zustand Aus kann später nicht rückwirkend Arbeit auslösen
- [x] Systemzeit und Browser besitzen keine Rundenautorität
- [x] PR #109 · finaler Head `4d9a571141815cd0a589672308a25e91421dfb70` · 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `85e95995d5e84c53131e24a8ad3dec36717891c6`

---

# Aktiv – 0.8.8-C4 JOBS-UI-Integration

## Ziel

Der geheime beste Freund wird direkt im vorhandenen JOBS-Bereich bedient: einen bestehenden Scene Job auswählen, auf einen anderen wechseln, stoppen und den bestätigten aktuellen Zustand sehen. Es entsteht kein zweites Dashboard und keine neue Gameplay-Autorität.

### C4 – kleinster UI-/Adapter-Slice

- [x] bestätigter `AssistantControlState` wird in der bestehenden Scene-Jobs-Projektion read-only angezeigt
- [x] unbekannte persistierte Assistant-Job-ID bricht die Projektion fail-closed ab
- [x] dünner A4-Adapter delegiert `assistant.control` ausschließlich an `AssistantControlService`
- [x] Browser darf bei Assistentensteuerung nur `job_id` oder `null` plus technische Command-ID senden
- [x] Auszahlung, Energie, Stress und Rundentrigger werden als Zusatzfelder abgewiesen bzw. nicht angeboten
- [x] Start/Wechsel/Stop sitzen direkt bei den vorhandenen Jobkarten; kein `assistant-panel`
- [x] Status zeigt Aus/Aktiv, gewählten Katalogtitel und bestätigte Steuerrevision
- [x] UI erklärt ausdrücklich: automatische Arbeit erst bei intern bestätigter Spielrunde, nicht durch Browser oder Rechnerzeit
- [x] bestehende direkte `job.run`-Funktion bleibt unverändert
- [x] gezielte Runtime- und Presentation-Regressionen ergänzt
- [x] erster technischer CI-Befund behoben: veraltete Testannahme der Character-Command-Menge um `assistant.control` erweitert
- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch weiterhin 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in C4

- keine Änderung an C3-Rundenausführung
- keine Browser- oder Systemzeit-Rundenautorität
- kein zweites Assistenten-Dashboard
- kein Freundschafts-/Beziehungsfortschritt
- keine neue Job-, Finance- oder Balance-Engine
- kein Produktversionsbump

### Danach in C

- [ ] **C5 – Freundschafts-Nachhall:** nur bestätigte `assistant.round_processed`-/Jobdaten für kleine Storyreaktionen lesen; keine zweite Progressionsengine
- [ ] **C6 – Round-Authority Integration Harness:** späteren kanonischen Rundenproduzenten end-to-end gegen C3 prüfen: Runde → Assistent → Scene Job → Journal → Recovery → Retry

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
