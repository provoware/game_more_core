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

- **0.8.7-C4A:** PR #98 · Merge `4909fb9f7169baaa5b802e497cdba3e2c6da0dae`
- **0.8.7-C4B:** PR #101 · Merge `3d71f00c5717ae797e6b8f1ca4c65c036bf71c81`
- **0.8.7-C5:** PR #102 · Merge `bd79da8d1e124ec60248a05bf332c6ef338ca7b6`
- **0.8.8-A:** PR #104 · Merge `7e0ed1e36dcc89436c0430d49e547fe2106f756b` · Crew-Logo/Fahne ohne Bildblob
- **0.8.8-B:** PR #105 · Merge `83aa6d050909e949a42f3c1bb3ab5c267b386693` · Scene Jobs + persönliches Bargeld

---

## B – Aktiv / nächste sinnvolle Iterationen

| ID | Status | Feature | Nutzen | Grenze |
|---|---|---|---|---|
| `POOL-COMPANION-001` | `PULLED` | **Secret Best Friend Assistant** | eine vorhandene Aufgabe automatisch Runde für Runde betreiben | genau eine aktive Aufgabe; bestätigte Runde als Autorität; Stop/Wechsel jederzeit; Scene-Job-/Task-Service wiederverwenden |
| `POOL-FINANCE-001` | `READY` | **Bankkonto & Sparen** | Bargeld sichern, Ein-/Auszahlung, Zins und Zinseszins | Finance-State/Ledger aus Scene Jobs wiederverwenden; bestätigte Spielzeit statt Systemzeit |
| `POOL-FINANCE-002` | `DEPENDENCY` | **Anlagen & Dividenden** | langfristige Geldanlage mit Ertrag | benötigt `POOL-FINANCE-001`; keine echten Marktdaten notwendig; katalogisierte Spielkurse |
| `POOL-FINANCE-003` | `DEPENDENCY` | **Kontoauszüge** | Geldbewegungen nachvollziehbar prüfen | liest bestätigtes Finance-Ledger, keine zweite Buchhaltung |
| `POOL-UX-004` | `READY` | **Control Deck Focus & Verdichtung** | weniger Wiederholungen, mehr Arbeitsfläche | Bereiche lokal maximieren/zurücksetzen; redundante Anzeigen entfernen; kein Save-State |
| `POOL-UX-005` | `READY` | **Nächste-Aktion-Signal** | erlaubte nächste Schritte schneller erkennen | kontrastreicher Puls nur Presentation; Reduced Motion = statische Hervorhebung |
| `POOL-MAP-002` | `READY` | **Berlin Ops Map 2** | bessere Bezirkslesbarkeit, Zoom/Pan und Objektübersicht | bestehende Map-Projection bleibt einzige Datenquelle; read-only |
| `POOL-STORY-001` | `READY` | District-Event-Nachhall in Biografie | Weltfolgen werden Teil der Crew-Geschichte | nur bestätigte Journal-/Projection-Daten |
| `POOL-UX-003` | `READY` | Lokaler Timeline-Fokusfilter | Straße/Krise/Bezirk gezielt einblenden | lokal/read-only; keine Sortierung, kein Save-/Journal-State |
| `POOL-ECON-004` | `READY` | **Job-Erschöpfung / Anti-Grind** | verhindert bedeutungsloses Endlosfarmen bei extrem niedriger Energie | Grundregel „phasenunabhängig arbeitbar“ erhalten; Balance getrennt vom Assistenten verändern |
| `POOL-STREET-002` | `READY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung | vorhandener Encounter-/Approach-Vertrag |
| `POOL-QA-002` | `READY` | District-No-op-Replay-Semantik präzisieren | exaktere Receipt-Auskunft | kein Datenintegritätsfehler |

---

## C – Spätere/abhängige Bausteine

| ID | Status | Feature | Voraussetzung |
|---|---|---|---|
| `POOL-WORLD-003` | `IDEA` | District-Ereignisketten mit Erinnerung | Story-/Journalvertrag |
| `POOL-PROPERTY-003` | `IDEA` | Venue Benefits / Betriebsprofil | Bonus-/Availability-Vertrag |
| `POOL-PROPERTY-004` | `IDEA` | Verkauf / Miete / laufender Betrieb | Bilanz-/Ownership-Transfer-Vertrag |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | eigener Server-/Transportvertrag |
| `POOL-NET-002` | `DEPENDENCY` | Crew-Identity-Synchronisation | `POOL-NET-001` + kanonische Crew-Identity-Daten aus `POOL-PROFILE-002` |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | `POOL-NET-001` |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | Ketten-/Replayvertrag |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | geeigneter Admin-Schreibweg |
| `POOL-QA-004` | `IDEA` | Main-Evidenz-Freshness-Gate | Main-Integrity-Provenienz wiederverwenden |
| `POOL-QA-005` | `IDEA` | District-Event-Katalog-Preflight | zentrale Service-Validierung wiederverwenden |
| `POOL-QA-006` | `READY` | Status-Sync nach Safe Merge automatisieren | bestätigten Safe-Merge-Commit read-only erkennen und Statusdrift melden; keine zweite Release-Autorität |
| `POOL-QA-007` | `IDEA` | District-Event-Eligibility-Diagnose | zentrale Requirements-Prüfung |
| `POOL-QA-008` | `IDEA` | Timeline-Projections-Freshness-Check | read-only Contract-Prüfung |
| `POOL-QA-009` | `IDEA` | Timeline-Metadaten-Diagnose | Sanitizing der C4A-Projection |

---

## Pool-Regeln

1. Keine stille Umsetzung: aktive Punkte werden auf `PULLED` gesetzt oder im TODO konkretisiert.
2. Keine Doppelarchitektur: vorhandene Services, Ledger, States und Projections zuerst wiederverwenden.
3. Gameplay-Folgen nur über katalogisierte Regeln und zuständige Services.
4. Presentation darf erklären, filtern, zoomen, maximieren und hervorheben, aber keine Fachwerte erfinden.
5. Zufall, Zinsen, Cadence und wiederholte Assistentenaktionen verwenden bestätigte Spielautorität; Systemzeit nie allein.
6. Synchronisierbare Identität besteht aus kleinen validierten Daten, nicht aus unkontrollierten Binär-/Base64-Blobs.
7. Nach remote validiertem Safe Merge wird `PULLED` auf `DONE` gesetzt.

## Nächste Entnahme

`POOL-COMPANION-001` ist nach dem sicheren Merge von 0.8.8-B freigegeben und aktiv. Der Assistent muss dieselben kanonischen Job-/Task-Services verwenden statt eine zweite Automationslogik zu erzeugen. Danach folgt `POOL-FINANCE-001`; Bank und Anlagen bauen auf demselben persönlichen Finance-Ledger auf.
