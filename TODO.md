# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-D – Atomic Wallet ↔ Bank Transfers` · PR #113 · Merge `c1a27a977ff76a397d95ae097395317c4d46950b`
- **0.8.8-D Remote-Abnahme:** Runtime `32662002026` · Presentation `32662002022` · Repository Health `32662002030` · Release Acceptance `32662002025` · Release Package `32662002046` · `SAFE MERGE PASS`
- **Aktive Entwicklungsstufe:** `0.8.8-D2 – Confirmed Savings Interest`
- **D2-Status:** Sparzinsen und Zinseszins werden ausschließlich aus einem bereits kanonisch bestätigten Finance-Periodentrigger berechnet; Systemzeit und Browser können keine Periode oder Zinsmenge autorisieren
- **Entwicklungsprozess:** `AGENTS.md` verlangt jetzt eine Planned-Read-Liste und gezieltes Einlesen nur der geplanten Änderungsdateien, direkten Verträge und konkret benötigten Regressionen
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

## 0.8.8-C4 – JOBS-UI-Integration

- [x] bestätigter `AssistantControlState` wird in der bestehenden Scene-Jobs-Projektion read-only angezeigt
- [x] unbekannte persistierte Assistant-Job-ID bricht die Projektion fail-closed ab
- [x] dünner A4-Adapter delegiert `assistant.control` ausschließlich an `AssistantControlService`
- [x] Browser sendet nur `job_id` oder `null` plus technische Command-ID
- [x] Start/Wechsel/Stop sitzen direkt bei den vorhandenen Jobkarten; kein zweites Dashboard
- [x] Status zeigt Aus/Aktiv, gewählten Katalogtitel und bestätigte Steuerrevision
- [x] direkte `job.run`-Funktion bleibt unverändert
- [x] PR #110 · finaler Head `06895cefb4fd715a7935578566452c7382fd7a1a` · 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `f8295564a4bddabddb4493c778e549d1cb083374`

## 0.8.8-C5A – Confirmed Afterglow Projection

- [x] externer deutscher Nachhall-Katalog für alle fünf vorhandenen Scene Jobs
- [x] neue read-only `assistant_afterglow_projection` ohne Journal- oder Save-Write
- [x] Storyeintrag nur bei Paar `assistant.round_processed` + exakt passendem `finance.job_completed`
- [x] manuelle Jobs, Assistent-Aus-Runden und unvollständige Paare erzeugen keinen Nachhall
- [x] unbekannte Job-ID im bestätigten Marker bricht fail-closed ab
- [x] Ausgabe auf die letzten drei bestätigten Einträge begrenzt, geordnet und vom Quelljournal entkoppelt
- [x] PR #111 · finaler Head `5f875cd066fd9608a482ec26092f64ec0b992437` · 5/5 Gates · `/safe-merge` PASS · Merge `dc22935d92cf9fea0d72aaac449921a6093a431f`

## 0.8.8-C5B – Visible Friendship Afterglow

- [x] Nachhall unter `scene_jobs.assistant_afterglow` an den bestehenden A4-State gehängt
- [x] Journalrecords im A4-Projektionslauf einmal gelesen und für Timeline sowie Nachhall wiederverwendet
- [x] Nachhall direkt im bestehenden `jobs-assistant-control`; kein zweites Dashboard
- [x] drei externe Textvarianten pro vorhandenem Scene Job
- [x] Variantenauswahl deterministisch aus bestätigter `character_id + round_id + job_id`; kein Refresh-/Retry-Reroll
- [x] UI rendert ausschließlich projizierte Überschrift, Text und katalogisierten Jobtitel
- [x] kein Browser-Story-Write, keine XP, kein neuer persistenter Freundschaftszustand
- [x] PR #112 · finaler Head `da76621ecea0cd8e1afecd967fe7201a7c1d4c6c` · 5/5 Gates · 0 Review-Threads · `/safe-merge` PASS · Merge `eaa615e48eecd84ba3ffb69551f8fb324fb42c12`

## 0.8.8-D – Atomic Wallet ↔ Bank Transfers

- [x] `PersonalFinanceService` für `deposit` und `withdraw` auf dem bestehenden Persistence-Kernel
- [x] `finance.bank_transfer_posted` katalogisiert und recoverbar
- [x] Wallet, Bank, Finance-Ledger und Revision atomar in genau einem Commit
- [x] Retry schreibfrei; Bedeutungswechsel derselben Command-ID fail-closed
- [x] Browser sendet nur Richtung + positiven Centbetrag, keine Zielstände
- [x] Einzahlen/Abheben im vorhandenen JOBS-/Geldbereich; kein zweites Finance-Dashboard
- [x] PR #113 · finaler Head `e41f2b40beb6508c21175a768ea3fb18050c79b1` · Runtime `32662002026` · Presentation `32662002022` · Repository Health `32662002030` · Release Acceptance `32662002025` · Release Package `32662002046` · 0 Review-Threads · `/safe-merge` PASS · Merge `c1a27a977ff76a397d95ae097395317c4d46950b`

---

# Aktiv – 0.8.8-D2 Confirmed Savings Interest

## Ziel

Das vorhandene Bankguthaben erhält Zins und Zinseszins nur dann, wenn die Runtime bereits eine kanonisch bestätigte Finance-Periode übergibt. D2 erzeugt selbst keine Zeitautorität.

### Planned-Read-Liste gemäß AGENTS.md

- `AGENTS.md`
- `src/bunkerfrequenz/application/personal_finance_service.py`
- `src/bunkerfrequenz/domain/finance.py`
- `src/bunkerfrequenz/application/game_recovery.py`
- `manifests/JOURNAL_MANIFEST.json`
- `manifests/PERSONAL_FINANCE_MANIFEST.json`
- `manifests/ZEIT_MANIFEST.json` nur zur Prüfung der bestehenden Zeitgrenze
- `tests/runtime/test_personal_finance_service.py`
- `tests/runtime/test_confirmed_savings_interest.py`
- `tests/runtime/test_feature_status_consistency.py`
- `TODO.md`, `PROJEKTSTATUS.json`, `FEATURE_POOL.md` und die kleine Finanz-Laienhilfe

Weitere Dateien nur bei einem konkreten Import-, Vertrags- oder Gate-Befund.

### D2 – kleinster bestätigter Sparzins-Slice

- [x] `PERSONAL_FINANCE_MANIFEST.json` katalogisiert 100 Basispunkte = 1 % pro bestätigter Finance-Periode
- [x] Zins wird auf dem aktuell bestätigten Bankguthaben berechnet; Folgeperioden verzinsen damit bereits gebuchte Zinsen
- [x] `ConfirmedFinancePeriod` enthält nur stabile Perioden-ID, fortlaufenden `finance_tick` und Character-Bindung
- [x] `finance.savings_interest_posted` aktualisiert Bank, Ledger, `confirmed_finance_tick` und Revision atomar
- [x] dieselbe bestätigte Periode ist bei Retry schreibfrei, auch wenn die technische Command-ID wechselt
- [x] Perioden dürfen nicht übersprungen oder rückwirkend neu interpretiert werden
- [x] auch eine 0-Cent-Zinsperiode wird dauerhaft verbraucht, damit späteres Guthaben keine alte Periode rückwirkend verzinst
- [x] Game-Recovery rekonstruiert Zins und Zinseszins über denselben `PlayerFinanceState`
- [x] Browser kann weder Finance-Periode noch Zinsbetrag bestätigen; Systemzeit allein bleibt wirkungslos
- [x] keine neue UI und kein neuer Finance-State
- [ ] finalen PR-Head durch Runtime Core, Presentation Core, Repository Health, Release Acceptance und Release Package prüfen
- [ ] 0 ungelöste Review-Threads bestätigen
- [ ] Branch weiterhin 0 Commits hinter `main`
- [ ] ausschließlich über `/safe-merge` mergen und SAFE MERGE PASS abwarten

### Bewusst nicht in D2

- kein eigener Zeit-/Periodenproduzent
- keine Rechnerzeit-Zinsen
- keine Browseraktion zum „Zinsen auslösen“
- keine Anlagen oder Dividenden
- keine zweite Finance-/Ledger-Engine
- keine Änderung am Eventbudget
- kein Produktversionsbump

### Danach

- [ ] **0.8.8-E – Control Deck Focus:** redundante Anzeigen reduzieren, Bereiche lokal maximieren/zurücksetzen und nächste erlaubte Aktionen klarer hervorheben
- [ ] **0.8.8-C6 – Round-Authority Integration Harness:** weiterhin erst bei echtem kanonischem Rundenproduzenten end-to-end prüfen
- [ ] **0.8.8-FIN-STATEMENTS – Kontoauszüge:** bestätigtes Finance-Ledger read-only verständlich als persönliche Geldhistorie darstellen

---

# Danach priorisiert

1. **0.8.8-E – Control Deck Focus:** Informationen verdichten, doppelte Ansichten entfernen, Arbeitsbereiche lokal maximieren/zurücksetzen und nächste erlaubte Aktion kontrastreich hervorheben.
2. **0.8.8-FIN-STATEMENTS – Kontoauszüge:** Wallet-, Bank-, Job- und Zinsbuchungen aus demselben bestätigten Ledger verständlich sichtbar machen.
3. **0.8.8-F – Berlin Ops Map 2:** bezirksartige Darstellung, Zoom/Pan, bessere Objekt-Hierarchie und Detailansicht; Karte bleibt read-only.

---

## Architektur- und Sicherheitsgrenzen

- Keine Mega-PR: pro fachlichem Modul eigener kleiner Slice.
- Keine zweite Economy-, Finance-, Map-, Timeline-, Profile-, Assistant-Task- oder Sync-Engine.
- Persönliches Bargeld und Bankguthaben gehören zum selben `PlayerFinanceState`; das Eventbudget bleibt fachlich getrennt.
- Browser darf bei Banktransfers nur Richtung und positiven Betrag liefern; Zielstände, Zinsperioden, Zinsen und Dividenden werden nicht vom Browser autorisiert.
- Zinsen benötigen einen bereits bestätigten Finance-Tick; Rechnerzeit allein erzeugt niemals Geld.
- Wiederholte Assistentenaktionen brauchen bestätigte Spielrunde; Systemzeit allein bleibt ohne Autorität.
- Story-Projections lesen nur bestätigte Journal-/Katalogdaten und schreiben keinen Progressionszustand.
- Map-Zoom, Focus-Maximierung und Timeline-Filter sind lokale UI-Zustände und gehören nicht ins Journal.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`AGENTS.md`](AGENTS.md)
