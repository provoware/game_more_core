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
| `POOL-WORLD-001` | `PULLED` | Dynamische Bezirkslage | Events verändern Stadtteile dauerhaft | Heat, Prestige, Polizeidruck und Szeneaktivität ausschließlich aus bestätigten Ergebnissen; Replay/Recovery exakt |
| `POOL-WORLD-003` | `PULLED` | Spielerbewegung + Stadt-Sitten | Figuren befinden sich wirklich in Stadt/Bezirk/Ort | persistente Positionen; Städte besitzen datengetriebene Kultur- und Preisfaktoren |
| `POOL-IDENTITY-001` | `PULLED` | Einmalige Einbuchungs-ID + Intro | eindeutige Spieleridentität und persönlicher Spieleinstieg | Einbuchungs-ID innerhalb eines Saves niemals doppelt; Intro setzt bestätigten Anzeigenamen ein |
| `POOL-HOUSING-001` | `PULLED` | Ein Zuhause zu wenig | dauerhafter sozialer Reibungspunkt | bei N registrierten Spielern existieren höchstens N-1 unabhängige Wohnplätze; genau eine Person ist obdachlos oder Gast |
| `POOL-TRUST-001` | `PULLED` | Einseitige Misstrauenssperre | Betrug/Misstrauen hat spürbare soziale Folgen | Täterwirkung auf betroffene Person für katalogisierte Wirkzyklen = 0; Gegenrichtung bleibt wirksam; kein Uhrzeit-Timer |
| `POOL-HONOR-001` | `PULLED` | Ehrenruf, Titel und große Werke | langfristige Identität auch für gute/schlechte Legenden | bestätigte Ereignisse erzeugen katalogisierte Taten und honor/infamy-Titel, niemals freie Clientwerte |
| `POOL-MINIGAME-001` | `PULLED` | Poker, Automat und XOXO | echte kleine Beschäftigungen in der Stadt | serverautoritativ, replaybar, ohne Echtgeld/Cash-out; Poker ohne Wette, Slot als Punktemodus, XOXO gegen deterministische KI |
| `POOL-STOREFRONT-001` | `PULLED` | Schaufenster-Geheimnisse | Erkundung belohnt Aufmerksamkeit | Hinweise stehen zwischen belanglosen Notizen; Presentation verrät nicht maschinell, welcher Text das Geheimnis ist |
| `POOL-CIVIC-001` | `PULLED` | Behördenbegegnung bei riskanten Partys | Entscheidungen unter Druck | passende fiktionale Bunker/Open-Air-Situationen können deterministisch eine Begegnung erzeugen; exakt drei sichere, abstrakte Entscheidungen mit unterschiedlichen Folgen |

---

## B – Bereit für kommende Iterationen

| ID | Status | Feature | Nutzen | Abhängigkeit / Hinweis |
|---|---|---|---|---|
| `POOL-PROPERTY-001` | `READY` | Immobilien kaufen | langfristige Ziele und Besitz | Kauf ausschließlich über EconomyService; folgt nach stabilem Living-City-State |
| `POOL-PROPERTY-002` | `DEPENDENCY` | Immobilien ausbauen | strategischer Ausbau | benötigt `POOL-PROPERTY-001`; Schallschutz, Strom, Fluchtwege, Bühne, Bar, Lager, Security |
| `POOL-RANK-002` | `READY` | Hall of Tribute + saisonales Ranking | langfristige Konkurrenz und Prestige | bestätigte Statistiken; Titel wie Lärmadel, Bunkerbaron, Kabelkönig, Pegelpapst, Nachtminister |
| `POOL-MAP-001` | `DEPENDENCY` | Berlin Ops Map PRO | sichtbare lebendige Spielwelt | sinnvoll nach stabilem District-/Property-State |
| `POOL-STREET-002` | `READY` | Straßenereignis-Erweiterungspakete | mehr Abwechslung ohne neue Engine | nutzt denselben Street-Encounter-Vertrag; nur neue katalogisierte Inhalte |
| `POOL-RANK-003` | `READY` | Ranking-Bewegungsanzeige | Auf-/Abstieg sofort verständlich | Pfeile, Vorplatz, Veränderung; Reduced Motion ohne Informationsverlust |
| `POOL-PROFILE-002` | `READY` | Crew-/Profilfarben und Emblem-Auswahl | stärkere Personalisierung | nur Darstellungsdaten; IDs bleiben unverändert |

---

## C – Bereits umgesetzt

| ID | Status | Feature | Nachweis |
|---|---|---|---|
| `POOL-RANK-001` | `DONE` | Competitive Top-10 Ranking | 0.8.5-A / PR #75 sicher gemergt |
| `POOL-PROFILE-001` | `DONE` | A4-Profil personalisieren | 0.8.5-B / PR #76 sicher gemergt |
| `POOL-STREET-001` | `DONE` | Kleine Straßen-Gimmicks | 0.8.5-C / PR #77 sicher gemergt |

---

## D – Später / größere Systeme

| ID | Status | Feature | Nutzen | Voraussetzung |
|---|---|---|---|---|
| `POOL-NET-001` | `DEPENDENCY` | 0.9 Network / Telegram Sync | gemeinsames bestätigtes Ranking und Austausch | eigener Server-/Transportvertrag, keine UI-Objekte als Autorität |
| `POOL-RANK-004` | `DEPENDENCY` | echte Netzwerk-Rankingzyklen | mehrere Spieler konkurrieren über bestätigte Daten | `POOL-NET-001` |
| `POOL-WORLD-002` | `DEPENDENCY` | Bezirksbezogene Zufallsereignisse | Stadtteile fühlen sich unterschiedlich an | nutzt persistenten Living-City-/District-State |
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
8. **Kein Echtgeld-Minispiel:** Stadtspiele verwenden keine Echtgeldzahlung, keinen Cash-out und umgehen Economy-/Jugendschutzregeln nicht.
9. **Behördenereignisse bleiben abstrakt:** Entscheidungen dürfen Gameplay-Konsequenzen modellieren, aber keine reale Anleitung zum Entziehen, Verbergen oder Umgehen von Behörden liefern.

## Aktive Entnahme: 0.8.5-D Living City State

Die gezogenen Punkte werden unter einem gemeinsamen persistenten `world`-Vertrag umgesetzt, aber intern in klar getrennte Services/Funktionen zerlegt. Erst wenn Identität, Position, Bezirke und soziale Folgen stabil replaybar sind, folgt `POOL-PROPERTY-001 – Immobilien kaufen`.
