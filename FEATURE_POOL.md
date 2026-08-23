# FEATURE-POOL – BUNKERFREQUENZ

Dieser Pool ist der Ideen- und Ausbauvorrat des Projekts. `TODO.md` bleibt die verbindliche aktive Arbeit.

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
| `POOL-STREET-001` | `DONE` | Kleine Straßen-Gimmicks | deterministisch/replaybar, kein Reload-Reroll |
| `POOL-WORLD-001` | `DONE` | Dynamische Bezirkslage | persistente District-Metriken + Recovery |
| `POOL-RANK-002` | `DONE` | Hall of Tribute | read-only Top 10 ohne erfundene Gegner |
| `POOL-RANK-003` | `DONE` | Ranking-Bewegung | Aufstieg/Abstieg/gehalten/neu |
| `POOL-PROPERTY-001` | `DONE` | Immobilien kaufen | Economy + Eigentum atomar; 0.8.6-A |
| `POOL-PROPERTY-002` | `DONE` | Immobilien ausbauen | Level 1–3 + Recovery + Map-Werte; 0.8.6-B |
| `POOL-MAP-001` | `DONE` | Berlin Ops Map PRO | 8 Districts/12 Locations, read-only; 0.8.6-C |
| `POOL-RANK-005` | `DONE` | Saisonale Hall of Tribute | Wochen-/Monatszyklen, bestätigte Titel, keine Fake-Champions; 0.8.7-A / PR #87 |
| `POOL-UX-001` | `DONE` | Control Deck 2.0 | HUD, Schnellnavigation, lokale Anzeigeoptionen; 0.8.7-B / PR #88 |
| `POOL-STREET-004` | `DONE` | Street Approaches | vier Spieleransätze, nur Auswahlgewichte; 0.8.7-B / PR #88 |
| `POOL-CRISIS-002` | `DONE` | Krisen-Folgenvorschau | katalogisierte Folgen vor der Wahl sichtbar; 0.8.7-B / PR #88 |

### Letzte Remote-Abnahmen

- **0.8.6-C:** PR #85 · Merge `10c7d6b5e04838b07ae6899b8b76580cd87de607`
- **0.8.7-A:** PR #87 · Merge `841258a37915e05d7f87eed7841c8e4b8d79bf46`
- **0.8.7-B:** PR #88 · Merge `4d1a35bfbc086d07599b6ec7b3816e830bcea995`
- **0.8.7-C1:** PR #90 · Merge `337f8ad8f9719ec3389c372da9688bbbec593c16`

---

## B – Aktiv / nächste sinnvolle Iterationen

| ID | Status | Feature | Nutzen | Grenze |
|---|---|---|---|---|
| `POOL-WORLD-002` | `PULLED` | **Bezirksbezogene Welt-/Zufallsereignisse** | C1 Vertrag/Katalog, C2 deterministische Runtime, danach Application-Integration | vorhandener DistrictState bleibt einzige Metrik-Autorität |
| `POOL-STREET-002` | `READY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung ohne neue Engine | bestehender Street-Encounter-/Approach-Vertrag |
| `POOL-PROFILE-002` | `READY` | Crewfarben und Emblem-Auswahl | stärkere Identität | nur Darstellungsdaten; Character-ID unverändert |
| `POOL-QA-002` | `READY` | District-No-op-Replay-Semantik präzisieren | exaktere Receipt-Auskunft | kein Datenintegritätsfehler |
| `POOL-UX-002` | `IDEA` | Ereignis-Timeline im Control Deck | bestätigte Welt-, Street- und Crisis-Ereignisse schneller nachvollziehen | reine Projection/Presentation; Journal bleibt Autorität |
| `POOL-WORLD-003` | `IDEA` | District-Ereignisketten mit Erinnerung | spätere Ereignisse können bestätigte frühere District-Ereignisse erzählerisch aufgreifen | erst nach validierter 0.8.7-C Runtime; keine versteckten Browserzustände |
| `POOL-WORLD-004` | `IDEA` | District-Event-Cadence/Cooldown | verhindert Ereignis-Spam und macht seltene Ereignisse gewichtiger | erst nach kanonischer Application-Integration; Taktung aus bestätigter Spielzeit, nie aus Systemzeit allein |

---

## C – Größere Folgebausteine

| ID | Status | Feature | Nutzen | Voraussetzung |
|---|---|---|---|---|
| `POOL-PROPERTY-003` | `IDEA` | Venue Benefits / Betriebsprofil | Ausbauten beeinflussen Eventvorbereitung | separater Bonus-/Availability-Vertrag |
| `POOL-PROPERTY-004` | `IDEA` | Verkauf / Miete / laufender Betrieb | tiefere Langzeitökonomie | Bilanz-/Ownership-Transfer-Vertrag |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | gemeinsames Ranking und Austausch | eigener Server-/Transportvertrag |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | mehrere Spieler konkurrieren | `POOL-NET-001` |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | kleine Geschichten unterwegs | eigener Ketten-/Replayvertrag |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | zusätzliche Repository-Härtung | geeigneter Admin-Schreibweg |

---

## Pool-Regeln

1. Keine stille Umsetzung: aktive Punkte werden auf `PULLED` gesetzt oder im TODO konkretisiert.
2. Keine Doppelarchitektur: vorhandene Services/Projections zuerst wiederverwenden.
3. Gameplay-Folgen nur über katalogisierte Events und zuständige Services.
4. Presentation darf erklären, filtern und lokal darstellen, aber keine Fachwerte erfinden.
5. Zufall/Zeit bleibt reproduzierbar; Systemzeit nie alleinige Autorität.
6. Nach remote validiertem Safe Merge wird `PULLED` auf `DONE` gesetzt.

## Nächste Entnahme

`POOL-WORLD-002` bleibt bis zum vollständigen 0.8.7-C-Slice aktiv. Nach C2 ist der kleinste nächste Schritt die autorisierte Application-Integration; erst danach sollte die read-only Ereignis-Timeline folgen. `POOL-WORLD-004` hält die spätere Cadence/Cooldown-Idee fest, damit Ereignisse nicht bei jeder Gelegenheit inflationär auftreten.
