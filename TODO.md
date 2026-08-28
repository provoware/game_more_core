# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Release-Baseline:** `0.8.4-alpha.1` – letzter bewusst freigegebener Produktrelease
- **Status-Sync-Anker:** PR #245 · Merge `f9357d16690675e282bffedd0baa78958079606e`
- **Zuletzt remote validierte Feature-Stufe:** `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY` · PR #238 · Head `20b0ed21b97d16babd2108e76cecc25aaa32a889` · Merge `52934e08dfc5c24e6b9c2933f6c53d8374018079`
- **Start-/Release-Qualität:** PR #244 hat mechanische Venue-Boni ohne eigenen Fachvertrag gesperrt; PR #245 hat das read-only Betriebsprofil auf genau fünf bestätigte Ortswerte aus der bestehenden Property-Upgrade-Projection begrenzt
- **Nächste aktive Entwicklungsstufe:** `0.8.8-UX-VENUE-OPERATING-PROFILE-READONLY`
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

## 0.8.8-UX-JOB-PAYOUT-CONTEXT-CLARITY
- [x] reduzierter Joblohn wird direkt an der vorhandenen Jobkarte verständlich erklärt
- [x] ausschließlich `payout_reduced_by_energy` und `effective_payout_cents` aus der bestehenden Projection verwendet
- [x] bei vollem Lohn bleibt die bisherige Darstellung ohne Warnhinweis
- [x] keine Recovery-Empfehlung, Browserberechnung, Auto-Aktion oder globale Priorisierung eingeführt
- [x] bestehende Runtime-Owned-Guidance-Regression und Laienhilfe aktualisiert
- [x] PR #231 · Head `79adca9dd77cb37f8bc31b861f8cc43e5dda2b66` · Merge `ffef7b170ee162651ccd5da239648445f1f93479`

## 0.8.8-QA-JOB-PAYOUT-CONTEXT-BROWSER-E2E
- [x] echter Chromium-Pfad erzeugt gleichzeitig volle und reduzierte Joblohnfälle aus bestätigter Projection
- [x] Erklärungstext, aktueller Lohn, `aria-label`, Hoher Kontrast und kleines Fenster regressionsgesichert
- [x] keine Produkt-Browserlogik oder zweite Lohnberechnung eingeführt
- [x] PR #232 · Head `e0ad2e99245c985f64b8868972ee0ab458b23257` · Merge `17fa658362b98396e91b0d6a580971a7bc9bc275`

## 0.8.8-QA-JOB-PAYOUT-CONTEXT-DECORATION-WAIT
- [x] Chromium-Acceptance wartet vor der Klassifikation auf vollständig mit `payoutReducedByEnergy` dekorierte Jobkarten
- [x] Lade-Reihenfolge zwischen Basisrenderer und dynamischem Payout-Modul erzeugt dadurch keinen zufälligen Fehlklassifikationslauf mehr
- [x] direkte Presentation-Regression und Laienhilfe nachgezogen; keine Produktlogik geändert
- [x] PR #234 · Head `80baa7ec9307a596dc4a6cd92098cfee6c8d5f2c` · Merge `57a78efecb5aa312fdad595dcae5a8352bef63ec`

## 0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-AUDIT
- [x] bestätigte Kauf-/Verkaufsbuchungen tragen Item-ID, Menge, tatsächlichen Stückpreis, Budgetdelta und Transaktions-ID
- [x] read-only Transaktionshistorie fachlich freigegeben
- [x] realisierter Gewinn/Verlust wegen fehlender Kostenbasis-/Lot-Regel ausdrücklich nicht freigegeben
- [x] `compensates` bleibt Rückbuchungsbezug und keine allgemeine Sell→Buy-Zuordnung
- [x] fokussierte Runtime-Regression, Audit, Laienhilfe und Changelog dokumentieren die Grenze
- [x] PR #236 · Head `df8e343f394f15737d166e61a91ec05dc70b4046` · Merge `08b1bccba3704722143c4669629d021d9cce8598`

## 0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-READONLY
- [x] bestehender Equipment-Bereich zeigt höchstens die letzten acht wirksamen bestätigten Käufe und Verkäufe
- [x] Aktion, Equipment, Menge, tatsächlicher Stückpreis und Ledger-Reihenfolge kommen read-only aus derselben bestehenden Economy-Projection
- [x] explizit kompensierte Original-/Gegenbuchungspaare werden gemeinsam aus der normalen Historie ausgeblendet
- [x] keine FIFO/LIFO-, Kostenbasis-, Gewinn-/Verlust-, Portfolio- oder zweite Marktengine eingeführt
- [x] fokussierte Presentation-Regression und Laienhilfe sichern Ausführungspreise, Limit, Reihenfolge, Compensation-Filter und Browser-Autoritätsgrenze
- [x] PR #238 · Head `20b0ed21b97d16babd2108e76cecc25aaa32a889` · Merge `52934e08dfc5c24e6b9c2933f6c53d8374018079`

## 0.8.8-QA-EQUIPMENT-TRADE-HISTORY-BROWSER-E2E
- [x] echter Chromium-Pfad beweist leere wirksame Historie, realen Kauf und realen Verkauf über bestätigte Runtime-/Projection-Daten
- [x] gespeicherter Ausführungspreis bleibt sichtbar; kompensierte Original-/Gegenbuchungspaare bleiben ausgeblendet
- [x] Hoher Kontrast, 760×680-Fenster, Bounds und `scrollWidth` sind im selben Acceptance-Lauf geprüft
- [x] Browser-Harness sendet keine Economy-Commands und berechnet keine Kostenbasis oder Gewinnlogik
- [x] Release Acceptance, fokussierte Presentation-Regression, Laienhilfe und Changelog sichern den Vertrag
- [x] PR #240 · Head `d919b33ce1c752a99fee933993a4f9d9021d5e67` · Merge `3d256f40da15c2cab42b78a3b64e5dbbea6fbad0`

## 0.8.8-UX-EQUIPMENT-TRADE-HISTORY-DENSITY-AUDIT
- [x] vorhandener Chromium-Harness auf exakt acht wirksame Trades erweitert
- [x] langer rein testseitiger Anzeigename, Große Schrift, Hoher Kontrast und 760×680-Fenster gemeinsam geprüft
- [x] sichtbare Bounds, horizontale Überbreite und Aktions-/Mengen-/Preisstruktur fail-closed abgesichert
- [x] kein reproduzierbarer Darstellungsbefund; deshalb kein CSS-/Layout-Fix und keine Produktlogikänderung
- [x] PR #242 · Head `bc7ebccd34f3ef2b63b7e73c87dc945a2b20a11a` · Merge `5e112a6c6d9655d2f76dde464b24a01a86147815`

## 0.8.8-GAMEPLAY-VENUE-BENEFITS-CONTRACT-AUDIT
- [x] drei Nutzenmodelle gegen bestehende Property-/Upgrade-/Event-/Projection-Autoritäten geprüft
- [x] mechanische Event-, Kosten-, Kapazitäts- und Ertragsboni ohne neuen katalogisierten Fachvertrag auf NO-GO gesetzt
- [x] read-only Betriebsprofil aus bestätigten Besitz-/Ausbauwerten als kleinster sicherer Produkt-Slice freigegeben
- [x] keine Runtime-, Balance-, Save-, Journal-, Browser- oder Gameplay-Produktlogik geändert
- [x] PR #244 · Head `4f45e28c760451d662b2eb576d96e868c106f8b6` · Merge `bcd3fb30b91cfdf638a60163c9c33d6c9ba176a4`

## 0.8.8-UX-VENUE-OPERATING-PROFILE-PRESENTATION-CONTRACT
- [x] Anzeigequelle auf exakt `property_upgrades.entries[*].effective_values` begrenzt
- [x] erlaubte Werte: Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen
- [x] keine zweite Browserberechnung, keine neue Persistenz und keine Ableitung mechanischer Boni
- [x] nicht besessene Locations dürfen kein eigenes Betriebsprofil vortäuschen
- [x] PR #245 · Head `099058d543149176f1870e821fa1cd75a69f3095` · Merge `f9357d16690675e282bffedd0baa78958079606e`

## 0.8.8-STATUS-SYNC-AFTER-SAFE-MERGE
- [x] drei kanonische Statusdateien werden gegen den letzten fachlich relevanten Safe Merge geprüft
- [x] reine Status-Sync-Merges werden übersprungen; kein direkter Bot-Push auf `main`

---

# Aktiv / nächste Iteration – 0.8.8-UX-VENUE-OPERATING-PROFILE-READONLY

## Fortschritt

**Vertrag und Datenquelle remote validiert; sichtbare Implementierung noch 0 %.** `POOL-PROPERTY-003` bleibt bewusst `PULLED`, bis das freigegebene read-only Betriebsprofil tatsächlich in der bestehenden Property-/Location-Ansicht sichtbar ist.

## Ziel

Für besessene Orte die fünf bestätigten Ortswerte **Prestige, Publikumskraft, Risiko, Underground-Faktor und Nutzen** aus der bestehenden Property-Upgrade-Projection verständlich gruppiert anzeigen, ohne neue Fachwerte oder Wirkungen zu erzeugen.

## Abnahme

- [ ] bestehende Property-/Location-Zielstelle und ihren Renderer gezielt lesen; kein zweites Property-Panel und kein Repository-Breitenscan
- [ ] ausschließlich `property_upgrades.entries[*].effective_values` bzw. dieselbe vorhandene Projection als Quelle nutzen
- [ ] genau die fünf bestätigten Ortswerte darstellen; keine zweite Berechnung im Browser
- [ ] nicht besessene Locations zeigen kein eigenes Betriebsprofil
- [ ] keine Event-Verfügbarkeit, Kosten, Kapazität, Ertrag oder andere mechanische Boni aus den Werten ableiten
- [ ] keine neue Persistenz, Journal-/Replay-Daten oder Browserautorität einführen
- [ ] passende Presentation-Regression ergänzen und Laienhilfe um die sichtbare Bedeutung der fünf Werte erweitern
- [ ] relevante Gates auf finalem Head grün, 0 ungelöste Review-Threads, 0 Commits hinter `main`
- [ ] Merge ausschließlich über `/safe-merge`

## Architektur- und Sicherheitsgrenzen

- Property Ownership und Upgrades bleiben in ihren vorhandenen Domain-/Application-Verträgen.
- Das Betriebsprofil ist ausschließlich read-only Presentation.
- Texte und verständliche Bezeichnungen bleiben in der Presentation-/Textschicht.
- Mechanische Venue Benefits benötigen später einen eigenen katalogisierten Domain-/Application-Vertrag.
- Produktversion erst nach eigener Release-Abnahme erhöhen.

Siehe auch: [`FEATURE_POOL.md`](FEATURE_POOL.md) · [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) · [`docs/VENUE_OPERATING_PROFILE_PRESENTATION_CONTRACT.md`](docs/VENUE_OPERATING_PROFILE_PRESENTATION_CONTRACT.md) · [`docs/STATUS_SYNC_LAIENHILFE.md`](docs/STATUS_SYNC_LAIENHILFE.md) · [`AGENTS.md`](AGENTS.md)