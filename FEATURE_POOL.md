# FEATURE-POOL – BUNKERFREQUENZ

Dieser Pool ist der Ausbauvorrat. `TODO.md` bleibt die verbindliche aktive Arbeit.

- **Status-Sync-Anker:** PR #231 · Merge `ffef7b170ee162651ccd5da239648445f1f93479`

## Statuswerte

- `PULLED` – aktiv/in nächste Iteration übernommen
- `READY` – fachlich ausreichend klar
- `DEPENDENCY` – benötigt zuerst einen anderen Baustein
- `IDEA` – vorgemerkt
- `DONE` – umgesetzt, remote validiert und sicher gemergt

---

## A – Abgeschlossen

| ID | Status | Feature | Ergebnis |
|---|---|---|---|
| `POOL-RANK-001` | `DONE` | Competitive Top-10 Ranking | eindeutige Plätze + Challenger-Verdrängung |
| `POOL-PROFILE-001` | `DONE` | A4-Profil personalisieren | Name, Alias, Spitznamen, Motto |
| `POOL-STREET-001` | `DONE` | Kleine Straßen-Gimmicks | deterministisch/replaybar |
| `POOL-WORLD-001` | `DONE` | Dynamische Bezirkslage | persistente District-Metriken + Recovery |
| `POOL-RANK-002` | `DONE` | Hall of Tribute | read-only Top 10 ohne erfundene Gegner |
| `POOL-RANK-003` | `DONE` | Ranking-Bewegung | Aufstieg/Abstieg/gehalten/neu |
| `POOL-PROPERTY-001` | `DONE` | Immobilien kaufen | Economy + Eigentum atomar |
| `POOL-PROPERTY-002` | `DONE` | Immobilien ausbauen | Level 1–3 + Recovery + Map-Werte |
| `POOL-MAP-001` | `DONE` | Berlin Ops Map PRO | 8 Districts/12 Locations, read-only |
| `POOL-RANK-005` | `DONE` | Saisonale Hall of Tribute | bestätigte Wochen-/Monatszyklen |
| `POOL-UX-001` | `DONE` | Control Deck 2.0 | HUD, Schnellnavigation, lokale Anzeigeoptionen |
| `POOL-STREET-004` | `DONE` | Street Approaches | vier Ansätze, katalogisierte Gewichte |
| `POOL-CRISIS-002` | `DONE` | Krisen-Folgenvorschau | katalogisierte Folgen vor der Wahl |
| `POOL-QA-003` | `DONE` | District-Event-Katalogdiagnose | Event-ID + Feldpfad im Fail-fast |
| `POOL-WORLD-002` | `DONE` | District World Events | Vertrag, Runtime, Settlement-Integration |
| `POOL-UX-002` | `DONE` | Ereignis-Timeline im Control Deck | C4A Projection + C4B sichtbare read-only Timeline |
| `POOL-WORLD-004` | `DONE` | District-Event-Cadence/Cooldown | 24h bestätigte Spielweltzeit, kein Systemzeit-Fallback |
| `POOL-PROFILE-002` | `DONE` | Crew-Logo/Fahne | syncbereites Identitätsrezept; 0.8.8-A |
| `POOL-ECON-003` | `DONE` | Scene Jobs & persönliches Bargeld | fünf katalogisierte Jobs + Finance-State |
| `POOL-ECON-009` | `DONE` | Jobs, Handel & Economy Guidance | Stundenlohn/Erschöpfungslohn, kanonische Marktpreise, Kaufen/Verkaufen/Reservieren/Freigeben und 5-Schritte-Geldführung; PR #218 |

### Letzte Remote-Abnahmen

- **0.8.8-UX-JOB-PAYOUT-CONTEXT-CLARITY:** PR #231 · Merge `ffef7b170ee162651ccd5da239648445f1f93479` · reduzierter Joblohn wird direkt an der bestehenden Jobkarte aus `payout_reduced_by_energy` erklärt; voller Lohn bleibt unverändert; keine Recovery-Empfehlung, Browserberechnung, globale Priorisierung oder Auto-Aktion
- **0.8.8-UX-RUNTIME-OWNED-STRATEGIC-GUIDANCE-AUDIT:** PR #229 · Merge `d8b5833b91861e1e80ee74d6f0fbab32cd2c0c27` · reduzierter Joblohn und Event-Blocker als getrennte bestätigte Runtime-/Projection-Fakten geprüft; kein globaler `strategic_guidance`-Aggregator, keine Browser-Priorisierung und keine Auto-Aktion eingeführt
- **0.8.8-UX-VISUAL-HIERARCHY-3:** PR #226 · Merge `aa4fb893efd01e7060ee82b8e326e597975e495a` · Event-Steuerung nutzt die volle Arbeitsbreite und trennt bestätigte Eckdaten, nächste Runtime-Aktion und Blocker klar; High Contrast, Reduced Motion und kleine Fenster bleiben erhalten; keine Gameplay- oder Browser-Fachautorität
- **0.8.8-UX-NEXT-BEST-ACTION-GUIDANCE:** PR #224 · Merge `9777fb10d1339ba69d672e7520946b08af915a8b` · Erststart, freigegebene Runtime-Event-Aktion und bestätigte Blocker werden in der bestehenden Schnellleiste verständlich geführt; keine Energie-, Geld- oder Marktpreisheuristik im Browser
- **0.8.8-STORY-STREET-TONE-DIVERSITY-AUDIT:** PR #222 · Merge `008326acc726e9be513c97682293c4a26e932c3a` · zwei vorhandene Street-Nachhalle gegen vier reale Parents geprüft; Story 003 bewusst nicht freigegeben; `street.construction_detour` bleibt nur Reservekandidat; keine Runtime-, Balance- oder Persistenzänderung
- **0.8.8-ECON-JOBS-TRADE-GUIDANCE-VISUAL:** PR #218 · Merge `eb97181f80678110ca12063165d446273cfcff5e` · Jobs zeigen Stundenlohn und aktuellen Erschöpfungslohn; Equipment-Handel nutzt den bestehenden Runtime-Vertrag vollständig; aktueller Marktpreis und frei verkaufbarer Bestand kommen read-only aus der kanonischen Projection; responsive KPI-/Marktvisuals und Geldkreislauf-Führung ergänzt
- **0.8.8-UX-TOOL-HELP-CLARITY:** PR #217 · Merge `12b001a731c0da5a1d98913676da9e48b0afd064` · zentrale Control-Deck-Hilfen in kurze Spielersprache übersetzt; `Bestätigt`, `Nur Anzeige` und `Sofort gespeichert` direkt erklärt

---

## B – Aktiv / nächste sinnvolle Iterationen

| ID | Status | Feature | Nutzen | Grenze |
|---|---|---|---|---|
| `POOL-COMPANION-001` | `DONE` | Secret Best Friend Assistant | vorhandene Aufgabe automatisch Runde für Runde betreiben | bestehende Scene Jobs, keine neue Rundenautorität |
| `POOL-COMPANION-002` | `DONE` | Freundschafts-Nachhall | bestätigte Assistentenarbeit bekommt kleine Storyreaktion | keine Progressionsengine |
| `POOL-FINANCE-001` | `DONE` | Bankkonto & Sparen | Wallet↔Bank + bestätigte Sparzinsen | keine Rechnerzeit-/Browserautorität |
| `POOL-FINANCE-002` | `DEPENDENCY` | Anlagen & Dividenden | langfristige Geldanlage | benötigt eigenen Anlagenvertrag |
| `POOL-FINANCE-003` | `DONE` | Kontoauszüge | Geldbewegungen nachvollziehbar prüfen | liest bestätigtes Ledger read-only |
| `POOL-FINANCE-004` | `DONE` | Kontoauszug CSV/TXT-Export | lokalen Kontoauszug weiterverwenden | kein Import/keine neue Buchhaltung |
| `POOL-UX-004` | `DONE` | Control Deck Focus & Verdichtung | mehr Arbeitsfläche | lokaler Presentation-State |
| `POOL-UX-005` | `DONE` | Nächste-Aktion-Signal | freigegebene Schritte schneller erkennen | nur vorhandene Runtime-Aktion |
| `POOL-MAP-002` | `DONE` | Berlin Ops Map 2 | bessere Kartenlesbarkeit | bestehende Projection bleibt Quelle |
| `POOL-STORY-001` | `DONE` | District-Event-Nachhall im Profil | bestätigte Weltfolgen sichtbar | keine Progressionsengine |
| `POOL-UX-003` | `DONE` | Lokaler Timeline-Fokusfilter | Straße/Krise/Bezirk gezielt einblenden | PR #124 sicher gemergt; keine Sortier-/Journalautorität |
| `POOL-ECON-004` | `DONE` | Job-Erschöpfung / Anti-Grind | verhindert Endlosfarmen ohne Energie | gleicher SceneJobService |
| `POOL-ECON-005` | `DONE` | Scene-Job-Lohnvorschau | tatsächlichen Erschöpfungslohn vor Jobstart sehen | PR #121 sicher gemergt; Browser rendert nur |
| `POOL-UX-006` | `DONE` | Exportvorschau / Prüfsumme | TXT/CSV vor Download prüfen und kopieren | PR #122 sicher gemergt; gleiche Serialisierung, kein Finanz-Write |
| `POOL-ECON-006` | `DONE` | Bestätigte Regenerationsaktionen | Energie aktiv zurückgewinnen | PR #123 sicher gemergt; +20 Energie gegen +12 Stress |
| `POOL-ECON-007` | `DONE` | Regenerationsfeedback | Vorher→Nachher nach bestätigter Regeneration verständlich zeigen | PR #125 sicher gemergt; nur bestätigte Projection-Snapshots |
| `POOL-STREET-002` | `DONE` | Straßenereignis-Erweiterungspakete | mehr Abwechslung | PR #126 sicher gemergt; 16 Begegnungen, gleiche Engine |
| `POOL-ECON-008` | `DONE` | Weitere Regenerationsentscheidungen | unterschiedliche Erholungsstrategien | PR #127 sicher gemergt; Balancevertrag zuerst, keine Echtzeitregeneration |
| `POOL-QA-007` | `DONE` | Street-Balance-Audit | Ansatzprofile und Katalogdominanz deterministisch prüfen | PR #128 sicher gemergt; keine Telemetrie, keine Gameplayänderung |
| `POOL-QA-008` | `DONE` | Recovery-Balance-Audit | beide Recovery-Wege über Energie×Stress-Matrix gegen Dominanz und Gratisfolgen prüfen | PR #129 sicher gemergt; test-only |
| `POOL-QA-002` | `DONE` | District-No-op-Replay-Semantik präzisieren | exaktere Receipt-Auskunft und Regression | PR #133 sicher gemergt; keine zweite Receipt-Architektur |
| `POOL-QA-009` | `DONE` | Street-Effekt-Erwartungswert-Audit | Energie-/Stress-/Rufwirkung der vier Ansätze mathematisch vergleichen | PR #136 sicher gemergt; Balancebefund führte zum Scout-Fix |
| `POOL-UX-007` | `DONE` | Receipt-Klartext im Control Deck | neu / Replay / nicht ausgelöst verständlich anzeigen | PR #157 sicher gemergt; nur vorhandene Runtime-Signale |
| `POOL-STREET-005` | `DONE` | Scout-Balance nach Effekt-Audit | Scout als Discovery-Tradeoff statt dominierte Scheinwahl | PR #156 sicher gemergt; bestehende Engine/Invarianten erhalten |
| `POOL-QA-010` | `DONE` | Street-Effekt-Grenzzustandsaudit | Clamping und Replay an realen Grenzwerten beweisen | PRs #158–#163 plus Bucket-Nachweis #168; test-only |
| `POOL-QA-006` | `DONE` | Status-Sync nach Safe Merge automatisieren | Drift der drei kanonischen Statusdateien automatisch erkennen | read-only Git-Anker; kein direkter Bot-Push auf `main` |
| `POOL-UX-008` | `DONE` | Avatar Visual Consistency Audit | Profil, HUD, Karte und Ranking visuell vereinheitlichen | PR #175 sicher gemergt; nur konkrete Presentation-Inkonsistenzen |
| `POOL-QA-011` | `DONE` | Avatar Context Browser E2E | bestätigte Identität durch Profil → HUD → Map → Ranking beweisen | PR #177 sicher gemergt; bestehender Chromium-Acceptance-Pfad |
| `POOL-QA-013` | `DONE` | Avatar Context Firefox Interaction | denselben bestätigten Identitätsablauf im vorhandenen nativen Firefox-Pfad absichern | PR #179 sicher gemergt; kein zweites Browserframework |
| `POOL-QA-014` | `DONE` | Runtime-Owned Map E2E Fixture | künstlichen `.owned`-DOM-Marker durch echten bestätigten Eigentumszustand im isolierten Testspielstand ablösen | PR #181 sicher gemergt; kanonischer Property-/Projection-Pfad, keine Browser-Besitzautorität |
| `POOL-QA-015` | `DONE` | Runtime-Owned Evidence Receipt | bestätigten Map-Eigentumskontext kompakt in vorhandener Release-Evidence nachweisen | PR #183 sicher gemergt; bestehende Fixture-/Property-/Ledger-Daten, keine zweite Evidence-Architektur |
| `POOL-UX-009` | `DONE` | Crew Identity Micro Polish Audit | kompakte Ranking-Kurzmarke auf gemeinsamen Lesbarkeitsboden bringen | PR #185 sicher gemergt; genau ein reproduzierter Größenbefund, keine Neugestaltung |
| `POOL-QA-016` | `DONE` | Avatar Context Computed Size E2E | tatsächliche Browser-Kaskade der kompakten Crew-Kurzmarken absichern | PR #188 sicher gemergt; Chromium/Firefox fail-closed unter `0.34rem`, keine zweite Browserarchitektur |
| `POOL-QA-017` | `DONE` | Avatar Context Text Clip E2E | reale Kurzmarken-Abschneidung in Chromium/Firefox erkennen | PR #192 sicher gemergt; gerenderte Box-Maße fail-closed, kein CSS-Fix nötig |
| `POOL-STORY-002` | `DONE` | Street Story Tone Diversity Audit | PR #222: Story 003 bewusst zurückgestellt; `construction_detour` bleibt Reserve ohne erfundene Persistenz |

---

## C – Spätere/abhängige Bausteine

| ID | Status | Feature | Voraussetzung |
|---|---|---|---|
| `POOL-COMPANION-003` | `DEPENDENCY` | Round-Authority Integration Harness | echter kanonischer Rundenproduzent |
| `POOL-WORLD-003` | `DONE` | District-Ereignisketten mit Erinnerung | Contract V1, zwei produktive Micro-Stories, read-only Kausalitätsprojection und Runtime→Browser-E2E bis PR #206 vollständig validiert |
| `POOL-PROPERTY-003` | `IDEA` | Venue Benefits / Betriebsprofil | Bonus-/Availability-Vertrag |
| `POOL-PROPERTY-004` | `IDEA` | Verkauf / Miete / laufender Betrieb | Bilanz-/Ownership-Transfer-Vertrag |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | eigener Server-/Transportvertrag |
| `POOL-NET-002` | `DEPENDENCY` | Crew-Identity-Synchronisation | `POOL-NET-001` |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | `POOL-NET-001` |
| `POOL-STREET-003` | `DONE` | seltene Mini-Kettenereignisse | eigener Contract, zwei produktive Street-Stories, read-only Kausalitätsprojection und Runtime→Browser-E2E bis PR #215 vollständig validiert |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | geeigneter Admin-Schreibweg |
| `POOL-QA-004` | `IDEA` | Main-Evidenz-Freshness-Gate | Main-Integrity-Provenienz wiederverwenden |
| `POOL-MAP-003` | `DONE` | Map-Viewport-Miniübersicht | PR #190 Audit: `1:1`-Reset reicht als Rückweg; keine Miniübersicht auf Verdacht |
| `POOL-QA-012` | `IDEA` | Status-Sync-PR-Autoprep | read-only Driftcheck muss sich zuerst im Alltag bewähren; niemals Direktwrite nach `main` |
| `POOL-UX-010` | `DONE` | Globale Spiel-Führung / Next Best Action 2 | PR #224: Erststart, Runtime-Event-Aktion und bestätigte Blocker klar geführt; keine Browserstrategie |
| `POOL-UX-011` | `DONE` | Control-Deck Visual Hierarchy 3 | PR #226: Event-Steuerung über volle Arbeitsbreite; Status, nächste Runtime-Aktion und Blocker klar getrennt; High Contrast/Reduced Motion erhalten |
| `POOL-UX-012` | `DONE` | Runtime-owned strategische Führung | PR #229: Job-Lohnreduktion und Event-Blocker als getrennte sichere Fakten bestätigt; kein globaler Aggregator ohne Runtime-Priorität |
| `POOL-UX-013` | `DONE` | Job-Lohn-Kontexthinweis | PR #231: reduzierten bestätigten Lohn direkt an der vorhandenen Jobkarte laienklar erklärt; keine Recovery-Empfehlung, Browserberechnung oder globale Priorisierung |
| `POOL-ECON-010` | `PULLED` | Equipment-Handelsverlauf | zuerst vorhandene Kauf-/Verkaufs-Ledgerdaten auf belastbare read-only Gewinn-/Verlust-Hilfe auditieren; keine zweite Marktengine |

---

## Pool-Regeln

1. Keine stille Umsetzung: aktive Punkte werden auf `PULLED` gesetzt oder im TODO konkretisiert.
2. Keine Doppelarchitektur: vorhandene Services, Ledger, States und Projections zuerst wiederverwenden.
3. Gameplay-Folgen nur über katalogisierte Regeln und zuständige Services.
4. Presentation darf erklären, filtern, zoomen, maximieren, exportieren und hervorheben, aber keine Fachwerte erfinden.
5. Zufall, Zinsen, Cadence und wiederholte Assistentenaktionen verwenden bestätigte Spielautorität; Systemzeit nie allein.
6. Nach remote validiertem Safe Merge wird `PULLED` auf `DONE` gesetzt, wenn der Pool-Punkt vollständig abgeschlossen ist; Contract-Audits dürfen denselben Owner bewusst `PULLED` lassen, wenn der produktive Vertrag noch fehlt.
7. Status-Sync verwendet ausschließlich den letzten fachlich relevanten Safe-Merge-Anker; reine Statuskorrektur-Merges werden zur Vermeidung von Selbstdrift übersprungen.

## Nächste Entnahme

`POOL-UX-013` ist nach PR #231 abgeschlossen: Der bestätigte reduzierte Joblohn wird lokal an der vorhandenen Jobkarte erklärt, ohne Browserstrategie oder zweite Lohnlogik. Als nächster Owner ist `POOL-ECON-010` gezogen, zunächst nur als `0.8.8-ECON-EQUIPMENT-TRADE-HISTORY-AUDIT`: Vor jeder Darstellung wird geprüft, ob das vorhandene Ledger historische Kauf-/Verkaufspreise und Identitäten ausreichend belegt. Ohne belastbare Evidenz darf keine Gewinn-/Verlust-Hilfe erfunden werden.