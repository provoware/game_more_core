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

## A – Aktuell gezogen

| ID | Status | Feature | Nutzen | Ziel / Abnahme |
|---|---|---|---|---|
| `POOL-RANK-001` | `PULLED` | Competitive Top-10 Ranking | echte Platzkämpfe ohne Gleichstände | Top 10 verdrängt sich bei gleichen Werten über Momentum; Platz 11+ nur Faktor 0,1 |
| `POOL-PROFILE-001` | `PULLED` | A4-Profil personalisieren | Spieler kann Figur sichtbar zu seiner Figur machen | Name, Alias, Spitznamen und Motto im lokalen Client editierbar; ausschließlich über bestehenden Profilservice |
| `POOL-STREET-001` | `PULLED` | Kleine Straßen-Gimmicks | Stadt fühlt sich lebendiger an | deterministische/replaybare Straßenerlebnisse; überwiegend positiv, gelegentlich Pech; keine Systemzeit als RNG-Seed |

---

## B – Bereit für kommende Iterationen

| ID | Status | Feature | Nutzen | Abhängigkeit / Hinweis |
|---|---|---|---|---|
| `POOL-WORLD-001` | `READY` | Dynamische Bezirkslage | Events verändern Berlin dauerhaft | Heat, Prestige, Polizeidruck, Szeneaktivität nur aus bestätigten Ergebnissen |
| `POOL-PROPERTY-001` | `READY` | Immobilien kaufen | langfristige Ziele und Besitz | Kauf ausschließlich über EconomyService |
| `POOL-PROPERTY-002` | `DEPENDENCY` | Immobilien ausbauen | strategischer Ausbau | benötigt `POOL-PROPERTY-001`; Schallschutz, Strom, Fluchtwege, Bühne, Bar, Lager, Security |
| `POOL-RANK-002` | `READY` | Hall of Tribute + saisonales Ranking | langfristige Konkurrenz und Prestige | bestätigte Statistiken; Titel wie Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Nachtminister |
| `POOL-MAP-001` | `DEPENDENCY` | Berlin Ops Map PRO | sichtbare lebendige Spielwelt | sinnvoll nach stabilem District-/Property-State |
| `POOL-STREET-002` | `DEPENDENCY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung ohne neue Engine | nutzt denselben Street-Encounter-Vertrag; nur neue katalogisierte Inhalte |
| `POOL-RANK-003` | `READY` | Ranking-Bewegungsanzeige | Auf-/Abstieg sofort verständlich | Pfeile, Vorplatz, Veränderung; Reduced Motion ohne Informationsverlust |
| `POOL-PROFILE-002` | `READY` | Crew-/Profilfarben und Emblem-Auswahl | stärkere Personalisierung | nur Darstellungsdaten; IDs bleiben unverändert |

---

## C – Später / größere Systeme

| ID | Status | Feature | Nutzen | Voraussetzung |
|---|---|---|---|---|
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | gemeinsames bestätigtes Ranking und Austausch | eigener Server-/Transportvertrag, keine UI-Objekte als Autorität |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | mehrere Spieler konkurrieren über bestätigte Daten | `POOL-NET-001` |
| `POOL-WORLD-002` | `IDEA` | Bezirksbezogene Zufallsereignisse | Stadtteile fühlen sich unterschiedlich an | erst nach persistentem District-State |
| `POOL-STREET-003` | `IDEA` | seltene Mini-Kettenereignisse | kleine Geschichten entstehen unterwegs | Street-Encounter-Basis muss zuerst stabil sein |
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

## Nächste Entnahme nach 0.8.5-A/B/C

Nach Ranking, Personalisierung und Street-Gimmicks ist `POOL-WORLD-001 – Dynamische Bezirkslage` der fachlich stärkste Kandidat, weil dann Event-, Ranking- und Straßenebene auf eine dauerhaft reagierende Stadt treffen können.
