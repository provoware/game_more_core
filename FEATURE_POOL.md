# FEATURE-POOL – BUNKERFREQUENZ

Dieser Pool ist der Ausbauvorrat. `TODO.md` bleibt die verbindliche aktive Arbeit.

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

### Letzte Remote-Abnahmen

- **0.8.8-STREET-EFFECT-AUDIT:** PR #136 · Merge `56afe056b05c56033d205fd2fea3e60fc8f7722d` · Erwartungswerte fixiert; vollständige Dominanz `balanced > scout` als Gameplay-Befund belegt
- **0.8.8-QA-REPLAY-PRECISION:** PR #133 · Merge `f3c7c6657b52171d024e1157ffd879ee252df2b9` · District-Receipt-Semantik für angewendet / Replay / nicht ausgelöst regressionsgesichert
- **START-QUALITY v2:** PR #135 · Merge `0f0c04b50e89b25bbf6e54df338f3e27ed63cd0b` · realer Browser-Acceptance-Gate, Klickstart und Main-Provenienz

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
| `POOL-QA-009` | `DONE` | Street-Effekt-Erwartungswert-Audit | Energie-/Stress-/Rufwirkung der vier Ansätze mathematisch vergleichen | PR #136 sicher gemergt; Balancebefund `balanced` dominiert `scout` |
| `POOL-UX-007` | `READY` | Receipt-Klartext im Control Deck | neu / Replay / nicht ausgelöst verständlich anzeigen | nur bestätigte Runtime-Signale rendern |
| `POOL-STREET-005` | `PULLED` | Scout-Balance nach Effekt-Audit | Scout als Discovery-Tradeoff statt dominierte Scheinwahl | aktiv; nur bestehende Manifestgewichte, keine neue Engine |

---

## C – Spätere/abhängige Bausteine

| ID | Status | Feature | Voraussetzung |
|---|---|---|---|
| `POOL-COMPANION-003` | `DEPENDENCY` | Round-Authority Integration Harness | echter kanonischer Rundenproduzent |
| `POOL-WORLD-003` | `IDEA` | District-Ereignisketten mit Erinnerung | Story-/Journalvertrag |
| `POOL-PROPERTY-003` | `IDEA` | Venue Benefits / Betriebsprofil | Bonus-/Availability-Vertrag |
| `POOL-PROPERTY-004` | `IDEA` | Verkauf / Miete / laufender Betrieb | Bilanz-/Ownership-Transfer-Vertrag |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | eigener Server-/Transportvertrag |
| `POOL-NET-002` | `DEPENDENCY` | Crew-Identity-Synchronisation | `POOL-NET-001` |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | `POOL-NET-001` |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | Ketten-/Replayvertrag |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | geeigneter Admin-Schreibweg |
| `POOL-QA-004` | `IDEA` | Main-Evidenz-Freshness-Gate | Main-Integrity-Provenienz wiederverwenden |
| `POOL-QA-006` | `READY` | Status-Sync nach Safe Merge automatisieren | bestätigten Safe-Merge-Commit read-only erkennen |
| `POOL-MAP-003` | `IDEA` | Map-Viewport-Miniübersicht | validierte Map 2 |
| `POOL-QA-010` | `IDEA` | Street-Effekt-Grenzzustandsaudit | tatsächlichen Character-Clamping-/Ressourcenvertrag zuerst gezielt prüfen |

---

## Pool-Regeln

1. Keine stille Umsetzung: aktive Punkte werden auf `PULLED` gesetzt oder im TODO konkretisiert.
2. Keine Doppelarchitektur: vorhandene Services, Ledger, States und Projections zuerst wiederverwenden.
3. Gameplay-Folgen nur über katalogisierte Regeln und zuständige Services.
4. Presentation darf erklären, filtern, zoomen, maximieren, exportieren und hervorheben, aber keine Fachwerte erfinden.
5. Zufall, Zinsen, Cadence und wiederholte Assistentenaktionen verwenden bestätigte Spielautorität; Systemzeit nie allein.
6. Nach remote validiertem Safe Merge wird `PULLED` auf `DONE` gesetzt.

## Nächste Entnahme

`POOL-STREET-005` ist für `0.8.8-STREET-SCOUT-BALANCE` aktiv. Der Slice verschiebt ausschließlich vorhandene Scout-Gewichte: Discovery-Begegnungen bleiben sein stärkster Fokus, während die vollständige Erwartungswert-Dominanz durch `balanced` entfällt. Danach ist `POOL-UX-007` der stärkste unabhängige UX-Kandidat; `POOL-QA-010` ist der bestehende kleine test-only Folgeaudit und `POOL-COMPANION-003` bleibt vom echten kanonischen Rundenproduzenten abhängig.
