# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Status-Sync-Anker:** PR #202 · Merge `4265002c0ccbbfd9ceaa91ae79fe4f3e9cdfbfdc`
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-STORY-DISTRICT-MICRO-STORY-002-AUDIT` · PR #202 · Head `287e1c980ebb70b3f9c804d4e5cd6e50cc6d7177` · Merge `4265002c0ccbbfd9ceaa91ae79fe4f3e9cdfbfdc`
- **Start-/Release-Qualität:** `main` enthält die sicher gemergte Feature-/QA-/UX-/Story-Linie bis PR #202; Micro-Story 002 wurde vor Implementierung fachlich auditiert und `district.temporary_space_opens` als stärkster Parent für `temporary_space_afterimage` ausgewählt
- **Nächste aktive Entwicklungsstufe:** `0.8.8-STORY-DISTRICT-MICRO-STORY-002`
- **Status-Drift-Schutz:** `tools/status_sync.py` + `.github/workflows/status-sync.yml` prüfen die drei kanonischen Statusdateien gegen den letzten fachlich relevanten Safe Merge
- **Repository-Arbeitsmodus:** Focused-Read bleibt verpflichtend; grüne Logs kompakt, rote Gates zuerst nur im konkreten Fehlerausschnitt
- **Release-Blocker:** keiner für `0.8.4-alpha.1`; neuer Produktrelease benötigt eigene Release-Abnahme

---

# Abgeschlossen ✅

## 0.8.8-A bis C5B – Identität, Scene Jobs und bester Freund
- [x] Crew-Identität, fünf Scene Jobs, persönliches Bargeld, Assistant Authority/Control/Confirmed-Round/JOBS-UI und bestätigter Freundschafts-Nachhall
- [x] PRs #104, #105, #107–#112 sicher gemergt

## 0.8.8-D / D2 – Bank & Sparen
- [x] atomare Wallet↔Bank-Transfers auf bestehendem `PlayerFinanceState` und Ledger
- [x] 1 % Sparzins pro bestätigtem Finance-Tick, Zinseszins, Retry-/Recovery-Schutz
- [x] PR #113 / #114 sicher gemergt

## 0.8.8-E bis FIN-EXPORT – Control Deck, Kontoauszug, Map, Story und Export
- [x] Control Deck Focus, FIN-STATEMENTS, Berlin Ops Map 2, Bezirks-Nachhall und TXT/CSV-Kontoauszug
- [x] PRs #115–#119 sicher gemergt

## 0.8.8-ECON-ANTI-GRIND / JOB-PREVIEW
- [x] Scene Jobs bleiben verfügbar; Lohn skaliert bei Teilenergie proportional, 0 Energie = 0 Cent
- [x] gleiche kanonische Berechnung für Auszahlung und read-only Vorschau
- [x] PR #120 / #121 sicher gemergt

## 0.8.8-UX-EXPORT-PROOF
- [x] Vorschau, Kopieren und Download verwenden dieselbe TXT-/CSV-Serialisierung
- [x] PR #122 · Merge `0909f3c38642f97d4474cd200af11c960e1ada66`

## 0.8.8-ECON-RECOVERY-ACTIONS / FEEDBACK / VARIANTS
- [x] `Koffein & kalte Luft`: +20 Energie / +12 Stress
- [x] `Mate, Zucker & Vollgas`: +30 Energie / +20 Stress
- [x] gleicher `RecoveryActionService` und `character.resources_changed`-Replay-Pfad; keine Echtzeitregeneration oder zweite Engine
- [x] PRs #123, #125 und #127 sicher gemergt

## 0.8.8-UX-TIMELINE-FILTER
- [x] Filter `ALLE / STRASSE / KRISE / BEZIRK` ausschließlich lokal, ohne Journal- oder Sortierautorität
- [x] PR #124 · Merge `465dc5040c5a1283fee5e7af52590455feaa9a01`

## 0.8.8-STREET-PACK / STREET-BALANCE-AUDIT
- [x] Katalog 10 → 16 Begegnungen über denselben Encounter-Vertrag
- [x] vier Ansatzprofile, Polaritätsmix und alle 100 Auswahl-Buckets deterministisch geprüft
- [x] PR #126 / #128 sicher gemergt

## 0.8.8-ECON-RECOVERY-BALANCE-AUDIT
- [x] beide Recovery-Aktionen über alle 10.201 Energie×Stress-Zustände geprüft
- [x] alle erreichbaren Mehrfachfolgen gegen Clamping, Gratisstrategien und unerwartete Effizienzsteigerung geprüft
- [x] keine Gameplaywerte, Recovery-Services oder Journalverträge verändert
- [x] PR #129 · Merge `3f51e57e58b2cbd6244f36333fea6cce970043c1`

## 0.8.8-MAP-USABILITY / Control-Deck-Freeze-Hotfix
- [x] Kartenmarker, District-Hierarchie, Legende und optionale Beschriftungen rein lokal verbessert; PR #130 sicher gemergt
- [x] selbsttriggernde `MutationObserver`-Schleife im Focus-Modul beseitigt und direkt regressionsgesichert; PR #132 sicher gemergt

## 0.8.8-QA-REPLAY-PRECISION
- [x] neu angewendet, idempotenter Replay und bewusst nicht ausgelöst sind anhand der vorhandenen Receipt-Signale eindeutig regressionsgesichert
- [x] kein Gameplay-, District-, Seed-, Cadence-, Save- oder Journalvertrag verändert
- [x] PR #133 · Merge `f3c7c6657b52171d024e1157ffd879ee252df2b9`

## START-QUALITY v2
- [x] realer lokaler Server, `/api/health`, `/api/state` und Headless-Browser als Release Acceptance
- [x] ein Klickstartpfad über `START_BUNKERFREQUENZ.sh` und `BUNKERFREQUENZ.desktop`
- [x] PR #135 · Merge `0f0c04b50e89b25bbf6e54df338f3e27ed63cd0b`

## 0.8.8-STREET-EFFECT-AUDIT / STREET-SCOUT-BALANCE
- [x] Erwartungswerte aller vier Street-Ansätze direkt aus dem Manifest berechnet
- [x] Scout nach dem Audit als eigener Discovery-Tradeoff ausbalanciert; keine vollständige Dominanz durch Balanced mehr
- [x] PR #136 · Merge `56afe056b05c56033d205fd2fea3e60fc8f7722d`
- [x] PR #156 · Merge `3f7ee5f24dd27b3cd885b7fa51970ec98e92379c`

## 0.8.8-UX-RECEIPT-CLARITY
- [x] Klartextzustände `NEU BESTÄTIGT`, `BEREITS BESTÄTIGT`, `NICHT AUSGELÖST` aus vorhandenen Runtime-Signalen
- [x] keine neue Receipt-, Journal-, Save- oder Gameplayarchitektur
- [x] PR #157 · Merge `138f329e4f662908329ada40d720989dd479bbc5`

## 0.8.8-STREET-BOUNDARY- / REPLAY-MATRIX
- [x] Energie 0/100, Stress 0/100 und Ruf-Floor 0 gegen den bestehenden Clamping-Vertrag geprüft
- [x] identische Replays an allen kanonischen Grenzen bleiben State-/Journal-idempotent
- [x] reale Encounter-Effekte sowie alle vier Ansätze gegen den echten Katalog regressionsgesichert
- [x] PRs #158–#163 sicher gemergt
- [x] Merge-Linie: `27711d0f0e1f5ed04c45033ffbc0c92dda89d231` → `518a4484f92ca361d47ca449d7dbcbc478ab12bc` → `387cb0af02ea8091e1291b91b51f756ea222faf3` → `d0d26b8c79a7282c955f91af870074b0ba03deaa` → `154ea922b1629d59bdb0c38f752bc24ea46cf18d` → `4fc5d7f9aab19ba3e15918d10106560f20183f19`

## 0.8.8-STREET-BOUNDARY-DISTRIBUTION-REPORT
- [x] alle 100 Runtime-Buckets je Ansatz stimmen exakt mit den deklarierten Gewichten überein; Nullgewichte besitzen 0 Buckets
- [x] read-only Report, keine zweite Auswahlengine
- [x] PR #168 · Merge `d00ac7675a5a6a125cd0713789d51386ccd10205`

## 0.8.8-UX-MOTION / AVATAR-PRESENCE / CONFIRMED-EVENT-FX
- [x] Motion-Depth für Control Deck mit autoritativem Reduced-Motion-Fallback; PR #164 · Merge `64579974e53f32e071bdbaca495a1c1b2028a067`
- [x] Avatar-Geometrie und Profilpräsenz gehärtet; PR #165 · Merge `23f5769fc20897c45ab38631a16dc64f1060040d`, PR #166 · Merge `567207051f739a804367fcee8b0f0baefb849223`
- [x] bestätigte Crew-Identität im Live-HUD; PR #167 · Merge `055c71c425db8b9cb9f28c5d8ce46de194c65633`
- [x] bestätigte Street-/Recovery-/Krisenergebnisse erhalten kurze lokale Presentation-FX; PR #169 · Merge `6259237050454526366cdf83c4ed4b19e6818b3b`
- [x] HUD-Refresh nach bestätigtem Profil-Save robust; PR #170 · Merge `89cb7484b8cf257bbc668729c567c8cb78776d9d`
- [x] Avatar-Sticky-Offset bei mittleren Fensterbreiten korrigiert; PR #171 · Merge `6d42e3b6ba180a4f97a9ab89a03265e01adc0980`
- [x] bestätigte Crew-Marke an eigenen Map-Orten; PR #172 · Merge `d2a1452b4ee6094584d0c63a94a85773c2821890`
- [x] bestätigte Crew-Marke ausschließlich am eigenen Hall-/Ranking-Eintrag; PR #173 · Merge `a96fa7c34cd17ff169712963e019380748e158a1`
- [x] High-Contrast-Außenkante, Symbol- und Kurzmarken-Trennung über Profil, HUD/Map-Klon und Ranking vereinheitlicht; PR #175 · Merge `d9e53a6e820cc79a3081b42c6a95f02c914bad15`
- [x] echter Chromium-Pfad Profil → bestätigtes HUD → Map-Klon → eigener Ranking-Eintrag inklusive kleinem Fenster und Hohem Kontrast; PR #177 · Merge `bb8d083061fb83453547d0ba4238c6eaeea8afc7`
- [x] derselbe Identitäts-Harness im vorhandenen nativen Firefox-/Geckodriver-Pfad inklusive kleinem Fenster und Hohem Kontrast; PR #179 · Merge `8988e2883b842d29acc12e7e40140cfc4b46e304`
- [x] isolierter Acceptance-Spielstand kauft deterministisch über `property.purchase`; Map-Avatar wird an runtime-bestätigtem Eigentum geprüft, kein künstlicher `.owned`-DOM-Marker; PR #181 · Merge `48f16864c319123e8ae4bcd04ba446aaa6ff153d`
- [x] vorhandene Chromium-/Firefox-Evidence bindet `location_id`, bestätigten `property.purchase`, Event-IDs und passende `property_purchase`-Ledger-Buchung an denselben Runtime-Owned-Kontext; PR #183 · Merge `9803d68a2d7ce71aa38db8c909fd68257bef1d9c`
- [x] kompakte Ranking-Kurzmarke auf denselben `0.34rem`-Lesbarkeitsboden wie das kleine HUD angehoben; keine andere Crew-Geometrie verändert; PR #185 · Merge `22d2774a8a0f55c645d5eb97141099b8f0ae7433`
- [x] Chromium und Firefox prüfen die tatsächlich berechnete `font-size` für HUD-, Map- und Ranking-Kurzmarken gegen denselben `0.34rem`-Boden; PR #188 · Merge `2d4a608e765a47990030ec839407a1d80346f883`
- [x] Chromium und Firefox prüfen reale Kurzmarken-Abschneidung in HUD, Map und Ranking über gerenderte Box-Maße; kein CSS-Fix nötig; PR #192 · Merge `f5132827d8d80522f952eb220db63047a091c77d`

## 0.8.8-UX-MAP-VIEWPORT-MINIUEBERSICHT-AUDIT
- [x] realer Randort `generator_ost` bleibt bei `AUSWAHL FOKUS` wegen der begrenzten Pan-Spanne reproduzierbar deutlich außerhalb der Kartenmitte
- [x] vorhandener zugänglicher `1:1`-Reset stellt Zoom und Pan vollständig auf die Gesamtansicht zurück
- [x] keine zweite Mini-Map, Projection, Fetch- oder Persistenzarchitektur auf Verdacht erzeugt
- [x] PR #190 · Head `012dd1f3455465e189c17df48c60d894e2700a03` · Merge `3f4ac78912d8d7a3c79bda2d2e3d6aa6d5aea9db`

## 0.8.8-STORY-DISTRICT-EVENT-CHAIN-CONTRACT-AUDIT
- [x] `world.district_effect_applied` als append-only Parent-Evidenz mit Event-, District- und Source-Referenz bestätigt
- [x] District-World-Event-Quelle bleibt replaybar; Biography konsumiert nur persistierte Biography-Records und ist keine Kettenautorität
- [x] fehlender katalogisierter Child-Eventtyp als klare Implementierungsgrenze regressionsgesichert; bewusst keine Micro-Story gebaut
- [x] PR #194 · Head `cc7cecace77eaa29f90b80549f6649e8f88c08a6` · Merge `60328eb48ac7dfdd1b1aef4166bdafeb0d30a28e`

## 0.8.8-STORY-DISTRICT-CHAIN-CONTRACT-V1
- [x] genau ein Child-Eventtyp `world.district_followup_resolved` katalogisiert
- [x] `parent_event_id`, `district_id` und `followup_id` verpflichtend; `causation_id` bindet den Parent, `correlation_id` die Kette
- [x] identischer Retry bleibt Exactly-once; gleicher Child-Key mit verändertem Parent-Payload wird als Konflikt abgewiesen
- [x] bestehender `PersistenceKernel` wiederverwendet; keine zweite Event-/Replay-/Save-Architektur
- [x] PR #196 · Head `004d3fd60c9794f27d38e74eb298862c5fe10e35` · Merge `ca5af40fb6bee1e90b1325bea8f6026fef8bc577`

## 0.8.8-STORY-DISTRICT-CHAIN-MICRO-STORY-001
- [x] genau eine verzögerte Folgegeschichte `power_flicker_afterglow` auf dem bestehenden Child-Eventvertrag umgesetzt
- [x] Folge entsteht erst in einem späteren bestätigten District-Zyklus desselben Bezirks; kein Cross-District-Nachhall
- [x] Parent-ID, `causation_id`, `correlation_id` und deterministische Child-ID bleiben Exactly-once gebunden
- [x] keine neuen Balanceeffekte, keine zweite Eventengine, Texte außerhalb der Runtime
- [x] PR #198 · Head `231ecc47ee43e1bf81907cc6e66ab58951888daf` · Merge `030d40e4b22c38a11fd98a2d028b398779955507`

## 0.8.8-STORY-DISTRICT-CHAIN-READONLY-PROJECTION
- [x] bestätigte `world.district_followup_resolved`-Records werden in der bestehenden Event-Timeline projiziert
- [x] `Folge von: …` erscheint nur bei bestätigtem Parent, identischem Bezirk und gültiger Journal-Reihenfolge
- [x] fehlende, bezirksfremde oder inkonsistente Parent-Referenzen erzeugen keine erfundene Kausalität
- [x] Browser bleibt strikt read-only; keine zweite Story-, Timeline-, Save- oder Projection-Architektur
- [x] PR #200 · Head `10b00a872f9a986404800323401883590d0ba6dd` · Merge `5f403defcf3773c3c44fefa3b282b0015ad9d68e`

## 0.8.8-STORY-DISTRICT-MICRO-STORY-002-AUDIT
- [x] `word_of_mouth_wave`, `patrol_sweep` und `temporary_space_opens` dramaturgisch und technisch auf demselben Contract V1 verglichen
- [x] `temporary_space_opens` mit 30/30 als stärkster Kandidat ausgewählt; `patrol_sweep` bleibt Reserve für einen späteren dunkleren Storybogen
- [x] Folgeidee `temporary_space_afterimage` / „Die Tür ist zu – die Adresse lebt weiter.“ ohne Runtime- oder Manifeständerung festgelegt
- [x] Regression beweist, dass bis zum Audit weiterhin nur Micro-Story 001 implementiert ist
- [x] PR #202 · Head `287e1c980ebb70b3f9c804d4e5cd6e50cc6d7177` · Merge `4265002c0ccbbfd9ceaa91ae79fe4f3e9cdfbfdc`

## 0.8.8-STATUS-SYNC-AFTER-SAFE-MERGE
- [x] Statusdrift seit PR #156 systematisch auf den bestätigten Stand zurückgeführt
- [x] `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` verwenden denselben maschinenprüfbaren Safe-Merge-Anker
- [x] read-only Checker erkennt den letzten fachlich relevanten Safe Merge aus der Git-First-Parent-Historie
- [x] reine Status-Sync-Merges werden übersprungen, damit kein Selbstdrift entsteht
- [x] eigener `Status Sync`-Workflow prüft Drift auf PRs und nach Pushes auf `main`
- [x] kein direkter Bot-Push auf `main`; Korrekturen bleiben normale prüfbare PRs

---

# Aktiv / nächste Iteration – 0.8.8-STORY-DISTRICT-MICRO-STORY-002

## Fortschritt

**0 %** – der Audit ist sicher gemergt. Der zweite District-Nachhall wird jetzt ausschließlich auf dem bestehenden Contract V1 umgesetzt.

## Ziel

`district.temporary_space_opens` soll in einem späteren bestätigten District-Zyklus desselben Bezirks genau einen `temporary_space_afterimage`-Child erzeugen: **„Die Tür ist zu – die Adresse lebt weiter.“**

## Abnahme

- [ ] `micro_story_002` im bestehenden District-Manifest katalogisieren; kein neuer Eventtyp
- [ ] Parent bleibt ausschließlich ein bestätigtes `district.temporary_space_opens` / `world.district_effect_applied`
- [ ] Child entsteht frühestens in einem späteren bestätigten District-Zyklus desselben Bezirks
- [ ] Child verwendet `world.district_followup_resolved`, `causation_id = parent_event_id` und `correlation_id = district-chain:{parent_event_id}`
- [ ] deterministische Child-ID; identischer Retry bleibt Exactly-once
- [ ] keine District-Deltas, kein Geld, kein Property-Besitz und keine neue Ressource
- [ ] deutsche Texte im vorhandenen UI-Textkatalog; Runtime bleibt textfrei
- [ ] bestehende read-only Timeline-Projection zeigt beim bestätigten Child automatisch `Folge von: Eine Tür steht plötzlich offen`
- [ ] direkte Runtime-/Projection-Regressionen für Story 001 und Story 002 grün
- [ ] relevante Runtime-/Presentation-/Repository-/Release-Gates auf finalem Head grün
- [ ] 0 ungelöste Review-Threads, 0 Commits hinter `main`
- [ ] Merge ausschließlich über `/safe-merge`

### Danach

- [ ] **DISTRICT-CHAIN-RUNTIME-BROWSER-E2E:** beide echten Parent→Child-Ketten in isoliertem Spielstand über Persistenz, Projection und Browser durchtesten
- [ ] **DISTRICT-STORY-TONE-BALANCE:** erst ab mindestens drei Micro-Stories prüfen, ob positive, bedrohliche, melancholische und soziale Nachhalltypen ausreichend unterschiedlich verteilt sind
- [ ] **STATUS-SYNC-DRIFT-AGE:** bei späterer Drift zusätzlich rein diagnostisch die Anzahl fachlicher Safe Merges Rückstand anzeigen; kein automatischer Write

---

## Architektur- und Sicherheitsgrenzen

- Git-Historie liefert nur den bestätigten Merge-Anker; die drei vorhandenen Statusdateien bleiben die kanonischen Projektinformationen.
- District-Ketten verwenden ausschließlich den katalogisierten Child-Eventvertrag; Timeline, Biography und Browser bleiben read-only.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`docs/STATUS_SYNC_LAIENHILFE.md`](docs/STATUS_SYNC_LAIENHILFE.md) · [`docs/DISTRICT_MICRO_STORY_002_AUDIT.md`](docs/DISTRICT_MICRO_STORY_002_AUDIT.md) · [`docs/EVENT_TIMELINE_LAIENHILFE.md`](docs/EVENT_TIMELINE_LAIENHILFE.md) · [`AGENTS.md`](AGENTS.md)