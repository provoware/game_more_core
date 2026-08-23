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
| `POOL-PROFILE-002` | `DONE` | Crew-Logo/Fahne | syncbereites Identitätsrezept, Legacy-Default, Control-Deck-Editor; 0.8.8-A / PR #104 |
| `POOL-ECON-003` | `DONE` | Scene Jobs & persönliches Bargeld | fünf katalogisierte Jobs, persönlicher Finance-State, A4-JOB-Bereich; 0.8.8-B / PR #105 |

### Letzte Remote-Abnahmen

- **0.8.8-C3:** PR #109 · Merge `85e95995d5e84c53131e24a8ad3dec36717891c6` · bestätigte Runde exakt einmal an Scene Job gebunden
- **0.8.8-C4:** PR #110 · Merge `f8295564a4bddabddb4493c778e549d1cb083374` · Assistent direkt im bestehenden JOBS-Bereich steuerbar
- **0.8.8-C5A:** PR #111 · Merge `dc22935d92cf9fea0d72aaac449921a6093a431f` · bestätigte Assistentenarbeit als read-only Nachhall-Projektion
- **0.8.8-C5B:** PR #112 · Merge `eaa615e48eecd84ba3ffb69551f8fb324fb42c12` · sichtbarer deterministischer Freundschafts-Nachhall
- **0.8.8-D:** PR #113 · Merge `c1a27a977ff76a397d95ae097395317c4d46950b` · atomare Wallet↔Bank-Transfers
- **0.8.8-D2:** PR #114 · Merge `bbebc9c3cafeac7f71eebeea1b89d4861b304e76` · bestätigte Sparzinsen/Zinseszins exakt einmal pro Finance-Tick
- **0.8.8-E:** PR #115 · Merge `6ac72d794ad3565bc40eb23dd501626382aa679a` · lokaler Panel-Fokus + Runtime-abgeleitetes Nächste-Aktion-Signal
- **0.8.8-FIN-STATEMENTS:** PR #116 · Merge `81dda0d21170a5d876cd5a7ebf05a8409ec735c8` · read-only Geldhistorie aus bestätigtem Finance-Ledger
- **0.8.8-F:** PR #117 · Merge `8119bf71a6f169d5cac367d5123d2bc1e6a73193` · begrenzter lokaler Zoom/Pan + Auswahlfokus auf bestehender Map-Projection
- **0.8.8-STORY-DISTRICT-BIO:** PR #118 · Merge `2330669692391e3747a3c807ec9b2a1cb7b7cb6d` · bestätigte District-Timeline als read-only Berlin-Erinnerungen im Profil

---

## B – Aktiv / nächste sinnvolle Iterationen

| ID | Status | Feature | Nutzen | Grenze |
|---|---|---|---|---|
| `POOL-COMPANION-001` | `DONE` | **Secret Best Friend Assistant – Steuerung & Ausführung** | vorhandene Aufgabe automatisch Runde für Runde betreiben | C1–C4 remote validiert; bestehende Scene Jobs, keine neue Rundenautorität |
| `POOL-COMPANION-002` | `DONE` | **Freundschafts-Nachhall** | bestätigte Assistentenarbeit bekommt kleine Storyreaktion | C5A/C5B remote validiert; deterministische Texte, keine Progressionsengine |
| `POOL-FINANCE-001` | `DONE` | **Bankkonto & Sparen** | Wallet↔Bank plus bestätigte Sparzinsen auf demselben Finance-State | D/D2 remote validiert; keine Rechnerzeit-/Browserautorität |
| `POOL-FINANCE-002` | `DEPENDENCY` | **Anlagen & Dividenden** | langfristige Geldanlage mit Ertrag | benötigt späteren eigenen Anlagenvertrag; keine echten Marktdaten notwendig |
| `POOL-FINANCE-003` | `DONE` | **Kontoauszüge** | Geldbewegungen nachvollziehbar prüfen | FIN-STATEMENTS remote validiert; liest bestätigtes Ledger read-only |
| `POOL-FINANCE-004` | `PULLED` | **Kontoauszug CSV/TXT-Export** | bestätigten Kontoauszug lokal weiterverwenden/archivieren | ausschließlich validierte FIN-STATEMENTS-Projection; kein Import, keine neue Buchhaltung |
| `POOL-UX-004` | `DONE` | **Control Deck Focus & Verdichtung** | weniger Wiederholungen, mehr Arbeitsfläche | 0.8.8-E remote validiert; Fokus bleibt lokaler Presentation-State |
| `POOL-UX-005` | `DONE` | **Nächste-Aktion-Signal** | erlaubte nächste Schritte schneller erkennen | 0.8.8-E remote validiert; nur bereits freigegebene Runtime-Aktion |
| `POOL-MAP-002` | `DONE` | **Berlin Ops Map 2** | bessere Kartenlesbarkeit durch Zoom/Pan und Auswahlfokus | 0.8.8-F remote validiert; bestehende 0–100-Projection bleibt einzige Datenquelle |
| `POOL-STORY-001` | `DONE` | **District-Event-Nachhall im Profil** | bestätigte Weltfolgen werden als Berlin-Erinnerungen sichtbar | STORY-DISTRICT-BIO remote validiert; nur bestätigte Timeline, keine Progressions-/Journalengine |
| `POOL-UX-003` | `READY` | Lokaler Timeline-Fokusfilter | Straße/Krise/Bezirk gezielt einblenden | lokal/read-only; keine Sortierung, kein Save-/Journal-State |
| `POOL-ECON-004` | `READY` | **Job-Erschöpfung / Anti-Grind** | verhindert bedeutungsloses Endlosfarmen bei extrem niedriger Energie | Grundregel „phasenunabhängig arbeitbar“ erhalten; Balance getrennt verändern |
| `POOL-STREET-002` | `READY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung | vorhandener Encounter-/Approach-Vertrag |
| `POOL-QA-002` | `READY` | District-No-op-Replay-Semantik präzisieren | exaktere Receipt-Auskunft | kein Datenintegritätsfehler |

---

## C – Spätere/abhängige Bausteine

| ID | Status | Feature | Voraussetzung |
|---|---|---|---|
| `POOL-COMPANION-003` | `DEPENDENCY` | **Round-Authority Integration Harness** | echter kanonischer Rundenproduzent; dann End-to-End Runde → Assistent → Scene Job → Journal → Recovery → Retry |
| `POOL-WORLD-003` | `IDEA` | District-Ereignisketten mit Erinnerung | Story-/Journalvertrag |
| `POOL-PROPERTY-003` | `IDEA` | Venue Benefits / Betriebsprofil | Bonus-/Availability-Vertrag |
| `POOL-PROPERTY-004` | `IDEA` | Verkauf / Miete / laufender Betrieb | Bilanz-/Ownership-Transfer-Vertrag |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | eigener Server-/Transportvertrag |
| `POOL-NET-002` | `DEPENDENCY` | Crew-Identity-Synchronisation | `POOL-NET-001` + kanonische Crew-Identity-Daten |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | `POOL-NET-001` |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | Ketten-/Replayvertrag |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | geeigneter Admin-Schreibweg |
| `POOL-QA-004` | `IDEA` | Main-Evidenz-Freshness-Gate | Main-Integrity-Provenienz wiederverwenden |
| `POOL-QA-006` | `READY` | Status-Sync nach Safe Merge automatisieren | bestätigten Safe-Merge-Commit read-only erkennen und Statusdrift melden |
| `POOL-MAP-003` | `IDEA` | Map-Viewport-Miniübersicht | validierte Map 2; aktuellen Ausschnitt rein lokal markieren |
| `POOL-UX-006` | `IDEA` | Exportvorschau / Kopieren | nach FIN-EXPORT dieselbe Projection lokal vor Download prüfen oder in Zwischenablage kopieren; kein Finanz-Write |

---

## Pool-Regeln

1. Keine stille Umsetzung: aktive Punkte werden auf `PULLED` gesetzt oder im TODO konkretisiert.
2. Keine Doppelarchitektur: vorhandene Services, Ledger, States und Projections zuerst wiederverwenden.
3. Gameplay-Folgen nur über katalogisierte Regeln und zuständige Services.
4. Presentation darf erklären, filtern, zoomen, maximieren, exportieren und hervorheben, aber keine Fachwerte erfinden.
5. Zufall, Zinsen, Cadence und wiederholte Assistentenaktionen verwenden bestätigte Spielautorität; Systemzeit nie allein.
6. Nach remote validiertem Safe Merge wird `PULLED` auf `DONE` gesetzt.

## Nächste Entnahme

`POOL-FINANCE-004` ist für 0.8.8-FIN-EXPORT aktiv. TXT und CSV serialisieren ausschließlich die bereits validierte FIN-STATEMENTS-Projection; lokaler Filterzustand, Rechnerzeit und Browser-Fachlogik verändern den Export nicht. Danach ist `POOL-ECON-004` der stärkste spielmechanische Slice. `POOL-COMPANION-003` bleibt abhängig, bis ein echter kanonischer Rundenproduzent vorhanden ist.