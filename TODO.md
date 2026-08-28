# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Status-Sync-Anker:** PR #229 · Merge `d8b5833b91861e1e80ee74d6f0fbab32cd2c0c27`
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-UX-RUNTIME-OWNED-STRATEGIC-GUIDANCE-AUDIT` · PR #229 · Head `40ec4d980d77dc1b801ece77fe65e4018a1eda37` · Merge `d8b5833b91861e1e80ee74d6f0fbab32cd2c0c27`
- **Start-/Release-Qualität:** strategische Hinweise bleiben an bestätigte Runtime-/Projection-Fakten gebunden; kein globaler Recommendation-Aggregator und keine Browserpriorisierung eingeführt
- **Nächste aktive Entwicklungsstufe:** `0.8.8-UX-JOB-PAYOUT-CONTEXT-CLARITY`
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

## 0.8.8-STREET-BOUNDARY-DISTRIBUTION-REPORT
- [x] alle 100 Runtime-Buckets je Ansatz stimmen exakt mit den deklarierten Gewichten überein; Nullgewichte besitzen 0 Buckets
- [x] read-only Report, keine zweite Auswahlengine
- [x] PR #168 · Merge `d00ac7675a5a6a125cd0713789d51386ccd10205`

## 0.8.8-UX-MOTION / AVATAR-PRESENCE / CONFIRMED-EVENT-FX
- [x] Motion-Depth, Avatar-Präsenz, Browser-Kontext und bestätigte Event-FX über PRs #164–#192 sicher validiert
- [x] Chromium + Firefox prüfen Profil → HUD → runtime-bestätigten Map-Kontext → eigenen Ranking-Eintrag inklusive High Contrast, kleinem Fenster und Clipping

## 0.8.8-UX-MAP-VIEWPORT-MINIUEBERSICHT-AUDIT
- [x] realer Randort bleibt bei begrenztem Fokus reproduzierbar off-center; `1:1` stellt Gesamtansicht wieder her
- [x] keine zweite Mini-Map auf Verdacht; PR #190 sicher gemergt

## 0.8.8-STORY-DISTRICT-EVENT-CHAIN-CONTRACT-AUDIT
- [x] `world.district_effect_applied` als append-only Parent-Evidenz bestätigt
- [x] Biography bleibt read-only und ist keine Kettenautorität
- [x] PR #194 sicher gemergt

## 0.8.8-STORY-DISTRICT-CHAIN-CONTRACT-V1
- [x] Child-Eventtyp `world.district_followup_resolved`, Parent-/District-Bindung und Exactly-once-Vertrag katalogisiert
- [x] bestehender PersistenceKernel wiederverwendet; PR #196 sicher gemergt

## 0.8.8-STORY-DISTRICT-CHAIN-MICRO-STORY-001
- [x] `district.power_flicker` → späterer `power_flicker_afterglow` im selben Bezirk
- [x] keine Balancewirkung, Exactly-once; PR #198 sicher gemergt

## 0.8.8-STORY-DISTRICT-CHAIN-READONLY-PROJECTION
- [x] bestätigte Follow-ups erscheinen in der bestehenden Timeline mit belegtem `Folge von: …`
- [x] fehlende oder bezirksfremde Parents erzeugen keine erfundene Kausalität; PR #200 sicher gemergt

## 0.8.8-STORY-DISTRICT-MICRO-STORY-002-AUDIT
- [x] drei verbleibende District-Parents verglichen; `temporary_space_opens` mit 30/30 ausgewählt
- [x] PR #202 sicher gemergt

## 0.8.8-STORY-DISTRICT-MICRO-STORY-002
- [x] `district.temporary_space_opens` → späterer `temporary_space_afterimage` auf demselben Contract V1
- [x] „Die Tür ist zu – die Adresse lebt weiter.“ liegt im deutschen Textkatalog, Runtime bleibt textfrei
- [x] Story 001 und 002 bleiben same-district, Exactly-once und balance-neutral
- [x] mehrere katalogisierte Storys verwenden denselben Resolver; pro District-Zyklus höchstens ein offener Follow-up
- [x] vorhandene read-only Projection zeigt Story 002 als `Folge von: Eine Tür steht plötzlich offen`
- [x] PR #204 · Head `edc10eb491f706b9c56ab4c0d7722e91cbdcc50a` · Merge `a03cf981b352064415e4cbf1fc3a8f88f34beed6`

## 0.8.8-QA-DISTRICT-CHAIN-RUNTIME-BROWSER-E2E
- [x] Story 001 und Story 002 über echte Runtime-/Persistence-Pfade in einem isolierten Save erzeugt
- [x] Parent-ID, Child-ID, `causation_id`, `correlation_id`, `district_id`, Reihenfolge, Retry und Cross-District fail-closed geprüft
- [x] derselbe persistierte Save über normalen A4-Server neu geöffnet
- [x] `/api/state` und echtes Chromium-DOM zeigen `Folge von: Das Netz flackert` und `Folge von: Eine Tür steht plötzlich offen`
- [x] keine Gameplay-, Balance-, Journal-, Projection-, Browser- oder CSS-Produktlogik geändert
- [x] PR #206 · Head `14a1c2914c6b366bda1ca71198340f00f58cef3a` · Merge `75aea005dcbf95abf80159b0ed96b0149bec0973`

## 0.8.8-STORY-STREET-MINI-CHAIN
- [x] Contract-Audit und eigener `street.followup_resolved`-Vertrag ohne District-Resolver-Kopie
- [x] Story 001 `street.cable_tip → cable_tip_echo` und Story 002 `street.lost_glove → lost_glove_fence_echo` auf demselben Contract umgesetzt
- [x] beide Folgen read-only in der bestehenden Timeline mit belegtem `Folge von: …` sichtbar
- [x] beide Stories Runtime→Persistenz→Reload→API→Chromium-E2E und Exactly-once regressionsgesichert
- [x] PRs #208–#215 sicher gemergt; zuletzt PR #215 · Head `ab15032ecf1b67aa2724ce6c461c613674a63c26` · Merge `1acceec43514caf7e2e945535896bce9472a19de`

## 0.8.8-UX-TOOL-HELP-CLARITY
- [x] zentrale Control-Deck-Hilfetexte in handlungsorientierte Spielersprache übersetzt
- [x] Kurzhilfe für `Bestätigt`, `Nur Anzeige` und `Sofort gespeichert`; technische ID verständlich erklärt
- [x] PR #217 · Merge `12b001a731c0da5a1d98913676da9e48b0afd064`

## 0.8.8-ECON-JOBS-TRADE-GUIDANCE-VISUAL
- [x] Jobkarten zeigen Stundenlohn, aktuellen Erschöpfungslohn, Energie- und Stresskosten
- [x] bestehender Equipment-Vertrag ist im Control Deck mit Kaufen, Verkaufen, Reservieren und Freigeben vollständig bedienbar
- [x] aktueller Marktpreis und frei verkaufbarer Bestand kommen read-only aus der kanonischen Runtime-Projection
- [x] 5-Schritte-Geldkreislauf führt Job → Bargeld → Bank → Equipment-Handel → Investition
- [x] responsive KPI-/Marktkarten und Reduced-Motion-Fallback heben Jobs und Handel visuell an
- [x] PR #218 · Head `39a3a4343657231872de08b7fed5376b9ff99c6e` · Merge `eb97181f80678110ca12063165d446273cfcff5e`

## 0.8.8-STORY-STREET-TONE-DIVERSITY-AUDIT
- [x] Story 001 als sozial-technisch und Story 002 als materiell-persönlich klassifiziert
- [x] vier reale Street-Parents gegen Tonvielfalt, Kausalität, Seltenheit, Balance-Neutralität und No-Persistence geprüft
- [x] Story 003 bewusst nicht freigegeben; `street.construction_detour` bleibt nur Reservekandidat
- [x] Auditannahmen sind gegen den echten Street-Katalog regressionsgesichert
- [x] PR #222 · Head `719c86f8a68db5355625bfebaffa36c2a368c87f` · Merge `008326acc726e9be513c97682293c4a26e932c3a`

## 0.8.8-UX-NEXT-BEST-ACTION-GUIDANCE
- [x] Erststart hebt `NEUES SPIEL ANLEGEN` als sicheren nächsten Schritt hervor
- [x] freigegebene Event-Aktion bleibt Runtime-owned und einzige automatisch hervorgehobene Event-Aktion
- [x] bestätigte Blocker werden kompakt als `EVENT BLOCKIERT: …` erklärt
- [x] Energie-, Bargeld- und Marktpreisheuristiken im Browser bewusst verworfen
- [x] Audit, Laienhilfe und MutationObserver-Regressionsvertrag aktualisiert
- [x] PR #224 · Head `4a6134ae7d56c8ef3ca2da65997d2201e541f051` · Merge `9777fb10d1339ba69d672e7520946b08af915a8b`

## 0.8.8-UX-VISUAL-HIERARCHY-3
- [x] genau einen belegten Hierarchiebruch in der Event-Steuerung behoben
- [x] Event-Panel nutzt volle Arbeitsbreite; bestätigte Eckdaten, nächste Runtime-Aktion und Blocker sind klar gestaffelt
- [x] bestehende IDs, Commands, Panels und Runtime-Autorität unverändert gelassen
- [x] High Contrast, Reduced Motion und kleine Fenster regressionsgesichert
- [x] PR #226 · Head `829169c87d3e1ebfeca0d7758fecc8c7606a5b74` · Merge `aa4fb893efd01e7060ee82b8e326e597975e495a`

## 0.8.8-UX-RUNTIME-OWNED-STRATEGIC-GUIDANCE-AUDIT
- [x] Job-Lohnreduktion als kanonisch berechneten Projection-Fakt bestätigt
- [x] Event-Blocker als Ergebnis von `EventExecutionService.available_actions()` bestätigt
- [x] gemeinsamen globalen `strategic_guidance`-Aggregator bewusst verworfen, solange keine Runtime-Priorität existiert
- [x] keine Browser-Heuristik, keine Auto-Aktion und keine Produktionslogik ergänzt
- [x] Audit, Laienhilfe, Changelog und Autoritätsregression aktualisiert
- [x] PR #229 · Head `40ec4d980d77dc1b801ece77fe65e4018a1eda37` · Merge `d8b5833b91861e1e80ee74d6f0fbab32cd2c0c27`

## 0.8.8-STATUS-SYNC-AFTER-SAFE-MERGE
- [x] drei kanonische Statusdateien werden gegen den letzten fachlich relevanten Safe Merge geprüft
- [x] reine Status-Sync-Merges werden übersprungen; kein direkter Bot-Push auf `main`

---

# Aktiv / nächste Iteration – 0.8.8-UX-JOB-PAYOUT-CONTEXT-CLARITY

## Fortschritt

**Bereit für einen kleinen Presentation-Slice.** Die Runtime-/Projection-Autorität ist bereits geklärt: `payout_reduced_by_energy` und `effective_payout_cents` sind bestätigte read-only Daten. Jetzt wird nur deren Bedeutung direkt an der bestehenden Jobkarte laienklarer erklärt.

## Ziel

Bei reduziertem Joblohn einen kurzen, eindeutigen Kontext wie **„Aktueller Lohn reduziert – deine Energie reicht nicht für die volle Auszahlung“** an der bestehenden Jobkarte anzeigen, ohne daraus automatisch „Erholen“ oder eine andere Strategie zu empfehlen.

## Abnahme

- [ ] ausschließlich `payout_reduced_by_energy` bzw. den bereits projizierten effektiven Lohn als Quelle verwenden
- [ ] reduzierte Auszahlung direkt und verständlich an der vorhandenen Jobkarte erklären
- [ ] bei vollem Lohn keinen falschen Warnhinweis anzeigen
- [ ] keine Energiegrenze, Auszahlung oder Recovery-Empfehlung im Browser neu berechnen
- [ ] keine globale Next-Best-Action-Priorisierung und keinen neuen Recommendation-Aggregator einführen
- [ ] vorhandene Jobkartenstruktur und Command-Payload unverändert lassen
- [ ] fokussierte Presentation-Regression für reduzierten und vollen Lohn ergänzen
- [ ] Laienhilfe nur dort erweitern, wo der neue Hinweis tatsächlich sichtbar wird
- [ ] relevante Gates auf finalem Head grün, 0 ungelöste Review-Threads, 0 Commits hinter `main`
- [ ] Merge ausschließlich über `/safe-merge`

## Architektur- und Sicherheitsgrenzen

- `SceneJobService` und `scene_jobs_projection` bleiben einzige Lohn-/Energieautorität.
- Browser rendert den bereits gelieferten Zustand und berechnet keine Fachgrenze neu.
- Kein automatisches Recovery, kein Auto-Job und keine versteckte Optimierungsfunktion.
- Multi-Hinweis-Priorisierung bleibt zurückgestellt, bis mehrere gleichzeitig gültige Hinweise einen belegten Konflikt erzeugen.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`docs/A4_CONTROL_DECK_HILFE.md`](docs/A4_CONTROL_DECK_HILFE.md) · [`docs/RUNTIME_OWNED_STRATEGIC_GUIDANCE_AUDIT.md`](docs/RUNTIME_OWNED_STRATEGIC_GUIDANCE_AUDIT.md) · [`AGENTS.md`](AGENTS.md)