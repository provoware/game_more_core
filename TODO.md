# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Status-Sync-Anker:** PR #181 · Merge `48f16864c319123e8ae4bcd04ba446aaa6ff153d`
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-QA-RUNTIME-OWNED-MAP-E2E-FIXTURE` · PR #181 · Head `a22d626b9af74e3f8370d76ae1d717f4ee7e3f3f` · Merge `48f16864c319123e8ae4bcd04ba446aaa6ff153d`
- **Start-/Release-Qualität:** `main` enthält die sicher gemergte Feature-/QA-/UX-Linie bis PR #181; Chromium und Firefox prüfen die Crew-Identitätskette jetzt mit runtime-bestätigtem Eigentum statt künstlichem `.owned`-DOM-Marker
- **Nächste aktive Entwicklungsstufe:** `0.8.8-QA-RUNTIME-OWNED-EVIDENCE-RECEIPT`
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

## 0.8.8-STATUS-SYNC-AFTER-SAFE-MERGE
- [x] Statusdrift seit PR #156 systematisch auf den bestätigten Stand zurückgeführt
- [x] `TODO.md`, `FEATURE_POOL.md` und `PROJEKTSTATUS.json` verwenden denselben maschinenprüfbaren Safe-Merge-Anker
- [x] read-only Checker erkennt den letzten fachlich relevanten Safe Merge aus der Git-First-Parent-Historie
- [x] reine Status-Sync-Merges werden übersprungen, damit kein Selbstdrift entsteht
- [x] eigener `Status Sync`-Workflow prüft Drift auf PRs und nach Pushes auf `main`
- [x] kein direkter Bot-Push auf `main`; Korrekturen bleiben normale prüfbare PRs

---

# Aktiv / nächste Iteration – 0.8.8-QA-RUNTIME-OWNED-EVIDENCE-RECEIPT

## Fortschritt

**0 %** – der Runtime-Owned-Map-E2E ist vollständig remote validiert; offen ist nur ein kompakter read-only Provenienz-Nachweis für genau diesen bereits bestätigten Testkontext.

## Ziel

Den bestehenden Release-Evidence-Nachweis um die bereits vorhandenen Daten des runtime-bestätigten Property-Kaufs ergänzen, ohne einen zweiten Receipt-, Property- oder Evidence-Pfad zu erzeugen.

## Abnahme

- [ ] ausschließlich vorhandene Fixture-/Property-/Ledger-Daten lesen
- [ ] mindestens `location_id`, bestätigten `property.purchase`-Status und vorhandene Property-/Ledger-Ereignisreferenz kompakt nachweisen
- [ ] keine Gameplay-, Kaufpreis-, Eigentums-, Save-, Journal- oder Map-Logik verändern
- [ ] kein neuer Browser-Command und keine zweite Evidence-Architektur
- [ ] Regression beweist, dass Evidence aus dem bereits bestätigten Runtime-Owned-Kontext stammt
- [ ] Runtime Core, Presentation Core und Repository Health auf finalem Head grün
- [ ] relevante Release-/Status-Sync-Gates grün, 0 ungelöste Review-Threads, 0 Commits hinter `main`
- [ ] Merge ausschließlich über `/safe-merge`

### Danach

- [ ] **CREW-IDENTITY-MICRO-POLISH:** nur konkrete verbleibende E2E-Befunde zu Größen, Abständen oder Clipping beheben; keine Neugestaltung auf Verdacht
- [ ] **0.8.8-C6 / POOL-COMPANION-003:** Round-Authority Integration Harness erst bei echtem kanonischem Rundenproduzenten
- [ ] **STATUS-SYNC-PR-AUTOPREP:** nur falls sich der read-only Driftcheck weiter bewährt; höchstens vorbereiteten PR erzeugen, niemals direkt `main` beschreiben

---

## Architektur- und Sicherheitsgrenzen

- Git-Historie liefert nur den bestätigten Merge-Anker; die drei vorhandenen Statusdateien bleiben die kanonischen Projektinformationen.
- Status-Sync verändert keine Runtime-, Gameplay-, Save-, Journal- oder Presentation-Autorität.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`docs/STATUS_SYNC_LAIENHILFE.md`](docs/STATUS_SYNC_LAIENHILFE.md) · [`AGENTS.md`](AGENTS.md)
