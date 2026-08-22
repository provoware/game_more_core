# FEATURE-POOL – BUNKERFREQUENZ

Dieser Pool ist der **Ideen- und Ausbauvorrat** des Projekts. Er ersetzt `TODO.md` nicht.

- `TODO.md` enthält die **aktuell verpflichtende Arbeit**.
- `FEATURE_POOL.md` enthält geplante, sinnvolle oder experimentelle Ausbaupunkte.
- Ein Feature wird erst umgesetzt, wenn es bewusst in eine konkrete Iteration gezogen wurde.
- Pro Iteration werden möglichst wenige zusammenhängende Punkte aktiviert.

## Statuswerte

- `PULLED` – in die nächste/aktive Iteration übernommen
- `READY` – fachlich ausreichend klar
- `DEPENDENCY` – benötigt zuerst einen anderen Baustein
- `IDEA` – vorgemerkt; Vertrag/Abnahme noch offen
- `DONE` – umgesetzt, remote validiert und sicher gemergt

---

## A – Abgeschlossen

| ID | Status | Feature | Ergebnis |
|---|---|---|---|
| `POOL-RANK-001` | `DONE` | Competitive Top-10 Ranking | eindeutige Plätze, Challenger-Verdrängung und Previous-Cycle-Momentum |
| `POOL-PROFILE-001` | `DONE` | A4-Profil personalisieren | Name, Alias, Spitznamen und Motto über bestehenden Profilservice |
| `POOL-STREET-001` | `DONE` | Kleine Straßen-Gimmicks | deterministische/replaybare Encounters ohne Reload-Reroll |
| `POOL-WORLD-001` | `DONE` | Dynamische Bezirkslage | Heat, Prestige, Polizeidruck und Szeneaktivität persistent + Recovery |
| `POOL-RANK-002` | `DONE` | Hall of Tribute | read-only Top 10 im A4-Client; keine erfundenen Gegner |
| `POOL-RANK-003` | `DONE` | Ranking-Bewegung | Aufstieg, Abstieg, gehalten, neu und Top-10-Zone |
| `POOL-PROPERTY-001` | `DONE` | Immobilien kaufen | 7 katalogisierte Orte; Preisautorität City-Map; Economy + Eigentum atomar; 0.8.6-A / PR #82 |
| `POOL-PROPERTY-002` | `DONE` | Immobilien ausbauen | 10 Ausbauarten, Level 1–3, feste Kostenleiter, PropertyUpgradeState, Recovery und Map-Werte; 0.8.6-B / PR #83 |

### Letzte Remote-Abnahmen

- **0.8.5-A:** PR #75 · Merge `b41d8f416679515307f2a580fb66b0569057836a`
- **0.8.5-B:** PR #76 · Merge `5a9eed536d48f30cdd1f4569e9e1b1724e5ced80`
- **0.8.5-C:** PR #77 · Merge `38de9f42c2908d63945db7bf25277b2f940ede6e`
- **0.8.5-D:** PR #79 · Merge `98c8b84715cc308dd1bc9fd92b7c7e56a35cc861`
- **0.8.5-E:** PR #80 · Merge `d383a3f364c6ee8cd954041f1d324e0ace0cb357`
- **0.8.6-A:** PR #82 · Merge `192b3eb4ad9dc4272eafeddc8604f7265bdd30fa`
- **0.8.6-B:** PR #83 · Merge `0b301bc9004f60dbc3ce221a7c6b3e462766b5b7`

PR #78 wurde bewusst nicht übernommen, weil er District-State mit Housing, Mehrstadtlogik, Trust, Minispielen und weiteren Systemen vermischte. Der fokussierte Ersatz wurde anschließend getrennt umgesetzt.

---

## B – Nächste sinnvolle Iterationen

| ID | Status | Feature | Nutzen | Abhängigkeit / Grenze |
|---|---|---|---|---|
| `POOL-MAP-001` | `PULLED` | **Berlin Ops Map PRO** | Districts, Eigentum und Ausbauten als echte visuelle Handlungsebene | 0.8.6-A/B sind stabil; Renderer bleibt read-only und erfindet keine Domainwerte |
| `POOL-RANK-005` | `READY` | Saisonale Hall-of-Tribute-Wertungen | Wochen-/Monatskonkurrenz und Prestige | braucht bestätigten Zeitzyklus; keine Systemzeit als alleinige Autorität |
| `POOL-WORLD-002` | `READY` | Bezirksbezogene Welt-/Zufallsereignisse | Bezirke unterscheiden sich spielerisch stärker | eigener katalogisierter Ereignisvertrag auf DistrictState |
| `POOL-STREET-002` | `READY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung ohne neue Engine | bestehender Street-Encounter-Vertrag |
| `POOL-PROFILE-002` | `READY` | Crewfarben und Emblem-Auswahl | stärkere Identität | nur Darstellungsdaten; Character-ID unverändert |
| `POOL-QA-002` | `READY` | District-No-op-Replay-Semantik präzisieren | exaktere Receipt-Auskunft | kein Datenintegritätsfehler; aktuell sicherer No-op |

---

## C – Größere Folgebausteine

| ID | Status | Feature | Nutzen | Voraussetzung |
|---|---|---|---|---|
| `POOL-PROPERTY-003` | `IDEA` | Venue Benefits / Betriebsprofil | Ausbauten beeinflussen spätere Eventvorbereitung sichtbar | erst getrennten Bonus-/Availability-Vertrag definieren; keine Regeln im Renderer |
| `POOL-PROPERTY-004` | `IDEA` | Verkauf / Miete / laufender Betrieb | tiefere Langzeitökonomie | eigener Bilanz-/Defizit-/Ownership-Transfer-Vertrag erforderlich |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | gemeinsames bestätigtes Ranking und Austausch | eigener Server-/Transportvertrag |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | mehrere Spieler konkurrieren | `POOL-NET-001` |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | kleine Geschichten unterwegs | eigener Ketten-/Replayvertrag |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | zusätzliche Repository-Härtung | geeigneter Admin-Schreibweg |

---

## Pool-Regeln

1. **Keine stille Umsetzung:** Ein Punkt wird vor Codeänderungen auf `PULLED` gesetzt oder in `TODO.md` konkretisiert.
2. **Keine Doppelarchitektur:** Erst vorhandene Domain-/Application-/Projection-Zielstellen prüfen.
3. **Kleine Scopes:** Große Ideen in getrennte überprüfbare Verträge zerlegen.
4. **Gameplay braucht Evidenz:** Persistente Folgen nur über katalogisierte Events und zuständige Services.
5. **Zufall bleibt reproduzierbar:** stabile Seeds/Instanz-IDs; Systemzeit nie alleinige Zufallsautorität.
6. **Presentation bleibt read-only:** Renderer darf State darstellen, aber keine Fachwerte erfinden oder schreiben.
7. **Nach Abschluss:** remote validierte und sicher gemergte Punkte auf `DONE` setzen.

## Nächste Entnahme

**0.8.6-C – `POOL-MAP-001 Berlin Ops Map PRO`** ist jetzt der stärkste nächste Schritt. Zum ersten Mal existieren gleichzeitig persistente Bezirkswerte, bestätigtes Eigentum, dreistufige Ausbauten und eine zentrale Score-/Tier-Projection. Der Renderer kann deshalb echte Spielwelt zeigen, ohne neue Fachlogik zu erfinden.
