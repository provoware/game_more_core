# FEATURE-POOL – BUNKERFREQUENZ

Dieser Pool ist der **Ideen- und Ausbauvorrat** des Projekts. Er ersetzt `TODO.md` nicht.

- `TODO.md` enthält die **aktuell verpflichtende Arbeit**.
- `FEATURE_POOL.md` enthält **geplante, sinnvolle oder experimentelle Ausbaupunkte**.
- Ein Feature wird erst umgesetzt, wenn es bewusst aus diesem Pool in eine konkrete Iteration gezogen wurde.
- Pro Iteration sollen möglichst nur wenige zusammenhängende Poolpunkte gleichzeitig aktiviert werden.

## Statuswerte

- `PULLED` – in eine aktive Iteration übernommen
- `READY` – fachlich sinnvoll und ausreichend klar für eine kommende Iteration
- `DEPENDENCY` – sinnvoll, aber benötigt zuerst einen anderen Baustein
- `IDEA` – vorgemerkt; Vertrag/Abnahme noch nicht ausreichend konkret
- `DONE` – umgesetzt und validiert

---

## A – Abgeschlossen

| ID | Status | Feature | Ergebnis |
|---|---|---|---|
| `POOL-RANK-001` | `DONE` | Competitive Top-10 Ranking | eindeutige Plätze; Challenger-Verdrängung bei Wertgleichstand; Top-10-Faktor 1,0, ab Vorplatz 11 Faktor 0,1 |
| `POOL-PROFILE-001` | `DONE` | A4-Profil personalisieren | Name, Alias, Spitznamen und Motto über bestehenden Profilservice editierbar |
| `POOL-STREET-001` | `DONE` | Kleine Straßen-Gimmicks | deterministische/replaybare Straßenerlebnisse; 60 % positiv, 25 % ruhig, 15 % negativ; kein Reload-Reroll |
| `POOL-WORLD-001` | `DONE` | Dynamische Bezirkslage | Heat, Prestige, Polizeidruck und Szeneaktivität persistent; Settlement-/Street-Quellen, Replay und Recovery |
| `POOL-RANK-002` | `DONE` | Hall of Tribute + sichtbares Top-10 Ranking | read-only Hall im A4-Client; Ruf/Level/Resonanz; Auf-/Abstieg; keine erfundenen Gegner |
| `POOL-RANK-003` | `DONE` | Ranking-Bewegungsanzeige | `↑` Aufstieg, `↓` Abstieg, `→` gehalten, `★` neu sowie Top-10-Zone werden aus der kanonischen Ranking-Projection dargestellt |

### Remote-Abnahme 0.8.5

- **0.8.5-A:** PR #75 · Merge `b41d8f416679515307f2a580fb66b0569057836a`
- **0.8.5-B:** PR #76 · Merge `5a9eed536d48f30cdd1f4569e9e1b1724e5ced80`
- **0.8.5-C:** PR #77 · Merge `38de9f42c2908d63945db7bf25277b2f940ede6e`
- **0.8.5-D:** PR #79 · Merge `98c8b84715cc308dd1bc9fd92b7c7e56a35cc861`
- **0.8.5-E:** PR #80 · Merge `d383a3f364c6ee8cd954041f1d324e0ace0cb357`

PR #78 wurde bewusst **nicht** übernommen: Der Entwurf vermischte District-State mit Housing, Mehrstadtlogik, Trust, Minispielen und weiteren Systemen. 0.8.5-D wurde stattdessen als kleiner fokussierter Ersatz umgesetzt.

---

## B – Bereit für kommende Iterationen

| ID | Status | Feature | Nutzen | Abhängigkeit / Hinweis |
|---|---|---|---|---|
| `POOL-PROPERTY-001` | `READY` | Immobilien kaufen | langfristige Ziele und Besitz | Kauf ausschließlich über EconomyService; City-Map besitzt bereits 7 kaufbare Orte |
| `POOL-PROPERTY-002` | `DEPENDENCY` | Immobilien ausbauen | strategischer Ausbau | benötigt `POOL-PROPERTY-001`; Schallschutz, Strom, Fluchtwege, Bühne, Bar, Lager, Security |
| `POOL-RANK-005` | `READY` | Saisonale Hall-of-Tribute-Wertungen | Wochen-/Monatskonkurrenz und Prestige | separater bestätigter Zeitzyklus; Titel wie Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Nachtminister |
| `POOL-STREET-002` | `READY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung ohne neue Engine | nutzt denselben validierten Street-Encounter-Vertrag; nur neue katalogisierte Inhalte |
| `POOL-WORLD-002` | `READY` | Bezirksbezogene Zufallsereignisse | Stadtteile fühlen sich unterschiedlich an | persistenter District-State ist jetzt vorhanden; Ereignisregeln separat katalogisieren |
| `POOL-PROFILE-002` | `READY` | Crew-/Profilfarben und Emblem-Auswahl | stärkere Personalisierung | nur Darstellungsdaten; technische IDs bleiben unverändert |
| `POOL-QA-002` | `READY` | District-No-op-Replay-Semantik präzisieren | Receipt/Replay-Auskunft wird auch bei unbekannten Orten semantisch exakt | kein Datenfehler; aktuell bereits sicherer No-op ohne Doppelwrite |

---

## C – Später / größere Systeme

| ID | Status | Feature | Nutzen | Voraussetzung |
|---|---|---|---|---|
| `POOL-MAP-001` | `DEPENDENCY` | Berlin Ops Map PRO | sichtbare lebendige Spielwelt | District-State vorhanden; sinnvoll nach stabilem Property-State |
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | gemeinsames bestätigtes Ranking und Austausch | eigener Server-/Transportvertrag, keine UI-Objekte als Autorität |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | mehrere Spieler konkurrieren über bestätigte Daten | `POOL-NET-001`; Hall-UI ist bereits vorbereitet |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | kleine Geschichten entstehen unterwegs | Street-Encounter-Basis ist stabil; eigener Kettenvertrag fehlt noch |
| `POOL-QA-001` | `READY` | Native GitHub Branch Protection / Ruleset | zusätzliche Repository-Härtung | geeigneter Admin-Schreibweg |

---

## Pool-Regeln

1. **Keine stille Umsetzung:** Ein Poolpunkt wird vor Codeänderungen auf `PULLED` gesetzt bzw. in `TODO.md` als aktive Iteration konkretisiert.
2. **Keine Doppelarchitektur:** Vor Umsetzung wird geprüft, ob bereits eine zuständige Runtime-/Presentation-Zielstelle existiert.
3. **Kleine Scopes:** Große Ideen werden in getrennte, überprüfbare Teilverträge zerlegt.
4. **Gameplay braucht Evidenz:** Persistente Folgen entstehen nur über katalogisierte Events und zuständige Services.
5. **Zufall bleibt reproduzierbar:** Zufallsmechaniken verwenden stabile Seeds/Instanz-IDs; Systemzeit ist niemals alleinige Zufallsautorität.
6. **Pool ist kein Versprechen:** `IDEA` und `DEPENDENCY` bedeuten ausdrücklich nicht, dass ein Feature bereits implementiert ist.
7. **Nach Abschluss:** Erfolgreich gemergte Poolpunkte werden auf `DONE` gesetzt; Folgeideen dürfen neu eingetragen werden.

## Nächste sinnvolle Entnahme

Nach 0.8.5-A bis E ist `POOL-PROPERTY-001 – Immobilien kaufen` der stärkste nächste Baustein: EconomyService, kaufbare City-Map-Orte und persistenter District-State existieren bereits. Ein sauberer Property-Kaufvertrag schafft langfristigen Besitz, ohne bereits Ausbau-, Renderer- oder Netzwerklogik vorwegzunehmen.
