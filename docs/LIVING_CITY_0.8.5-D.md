# BUNKERFREQUENZ 0.8.5-D – Living City State

## Ziel

0.8.5-D macht aus der bisher read-only vorbereiteten Stadt einen persistierten, replaybaren Spielzustand. Die Schicht ist bewusst die fachliche Grundlage für spätere Immobilien, den hochwertigen Berlin-Renderer und saisonale Hall-of-Tribute-Systeme.

Die Produktversion bleibt bis zu einer eigenen Release-Abnahme **`0.8.4-alpha.1`**.

---

## 1. Ein World-State statt vieler UI-Sonderfälle

Der kanonische Block heißt `world` und enthält:

- Spielerregister mit Einbuchungs-ID
- aktuelle Stadt, Bezirk und Ort je registriertem Character
- Wohnsituation
- Bezirksmetriken
- gerichtete Misstrauenssperren
- Ehrenruf-/Infamy-Titel
- bestätigte große Werke/Taten
- Party-Modus und bestätigte Risikochecks
- gelesene Schaufenster
- Minispielzustände und Punkte
- bereits auf die Stadt angewandte Settlement-IDs

Der Browser besitzt davon keine Schreibautorität. A4 sendet Commands, `WorldService` prüft und persistiert, `world_projection` liest anschließend den bestätigten Zustand.

---

## 2. Einbuchungs-ID: nie doppelt

Neue Spieler erhalten monoton:

```text
BF-000001
BF-000002
BF-000003
...
```

Vor jedem Commit wird geprüft, dass keine zwei registrierten Spieler dieselbe ID besitzen. Zusätzlich wird der nächste Zähler nie aus Browserdaten übernommen.

Die Einbuchungs-ID ist nicht der Anzeigename und nicht die bestehende technische `character_id`. Ein Spieler kann seinen sichtbaren Namen ändern, ohne seine Identität zu wechseln.

Ein Save mit doppelter Einbuchungs-ID wird fail-closed abgewiesen.

---

## 3. „Auf wundersame Weise immer ein Haus zu wenig“

Die Regel ist eine echte State-Invariante:

```text
registrierte Spieler = N
unabhängige Wohnplätze = höchstens N - 1
exakt eine Person = guest ODER homeless
```

Beispiele:

| Spieler | Eigenes Zuhause | Gast/obdachlos |
|---:|---:|---:|
| 1 | 0 | 1 |
| 2 | 1 | 1 |
| 5 | 4 | 1 |

Kommt ein weiterer Spieler hinzu, wird die bisherige Engpassperson unabhängig untergebracht und der neue Spieler übernimmt den Engpass. Dadurch bleibt die absurde Regel dauerhaft exakt bei **einer** Person.

Ein Gast muss bei einem anderen registrierten Spieler unterkommen. Selbst-Hosting oder zwei gleichzeitig fehlende Wohnungen sind ungültiger State.

---

## 4. Persönlicher Story-Einstieg

Beim First Run wird der bestätigte Anzeigename in eine lokalisierte Geschichte eingesetzt. Beispielstruktur:

```text
{name}, du steigst nicht als Held aus irgendeinem glänzenden Wagen ...
Deine Einbuchungs-ID ist echt, dein Ruf noch nicht ...
Irgendwo fehlt – auf wundersame Weise – schon wieder genau eine Wohnung ...
```

Die Story wird aus `content/de/world.json` gelesen. Der World-State speichert nur, ob sie bestätigt wurde. Das verhindert sichtbare Langtexte im Domain-Code.

---

## 5. Figuren bewegen sich wirklich

Position ist persistiert als:

```json
{
  "city_id": "berlin",
  "district_id": "neukoelln",
  "location_id": "tape_kiosk"
}
```

Ein Ort muss tatsächlich zu Stadt und Bezirk gehören. Ein falsches Tupel wie `berlin + plagwitz` wird abgewiesen.

Startstädte:

| Stadt | Preisfaktor | Spielcharakter |
|---|---:|---|
| Berlin | 100 % | direkt, improvisiert, starke Bezirksidentität |
| Leipzig | 92 % | gemeinschaftlicher, experimenteller, günstiger |
| Hamburg | 115 % | hafen-/logistikgeprägt, höhere Kosten |

Die Sitten sind Content/Presentation. Der Preisfaktor ist dagegen ein bestätigter serverseitiger Economy-Kontext.

### Wichtige Integritätsregel

Der Browser darf bei `economy.transact` **keinen Preisfaktor mitsenden**. `GameClientSession` liest die bestätigte Position aus `WorldState` und übergibt daraus den Faktor an `EconomyService`.

Kompensationen verwenden weiterhin exakt den historischen Stückpreis der ursprünglichen Transaktion; ein späterer Stadtwechsel verändert die Vergangenheit nicht.

---

## 6. Persistente Bezirkslage

Jede Stadt besitzt Bezirke mit vier Werten `0..100`:

- `heat`
- `prestige`
- `police_pressure`
- `scene_activity`

Startwerte:

```text
Heat             20
Prestige         20
Polizeidruck     15
Szeneaktivität   30
```

Nur bestätigte Settlement-Ergebnisse dürfen die Eventfolgen in diesen Zustand übertragen.

### Aktuelle deterministische Übersetzung

- `heat_delta` → Heat direkt
- 50 % des `reputation_delta` → Prestige
- 50 % von positivem Heat → zusätzlicher Polizeidruck
- 25 % von positiver Stabilität → Entlastung beim Polizeidruck
- 20 % Ruf + 30 % Stabilität → Szeneaktivität
- alle Ziele werden auf `0..100` begrenzt

Jede `settlement_id` steht maximal einmal in `world.applied_settlements`. Ein Retry darf keine Bezirksfolge doppeln.

---

## 7. Misstrauen, Betrug und Verrat

Katalogisierte Auslöser:

- `deception`
- `betrayal`
- `fraud`

Die Folge ist **gerichtet**, nicht symmetrisch.

Wenn A gegen B betrügt:

```text
A → B: Skill-/Fähigkeitswirkung = 0 %
B → A: Skill-/Fähigkeitswirkung = 100 %
Dauer: 12 bestätigte Wirkzyklen
```

Es gibt bewusst keinen Uhrzeit-Timer. Ein Systemzeit-Sprung darf die Strafe weder verkürzen noch verlängern. Nur bestätigte Interaktionszyklen verbrauchen die Sperre.

Der aktuelle lokale Alpha besitzt noch keinen allgemeinen Multiplayer-Skill-gegen-Spieler-Command. Deshalb wird die Sperre nicht als erfundener Browserknopf angeboten. `WorldService.effectiveness_bps(source, target)` ist die verbindliche Gate-Funktion, die ein späterer Player-to-Player-Service vor jeder solchen Wirkung verwenden muss.

---

## 8. Ehrenruf, Infamy und große Werke

Bestätigte Settlements können dauerhafte Werke erzeugen. Ein Werk besitzt eine Valenz:

- `positive`
- `negative`
- später optional `ambiguous`

Startbeispiele:

- erste vollständig abgeschlossene Nacht → **Betonstarter**
- Event trotz bestätigter Krise abgeschlossen → **Krisenlotse**
- Nacht mit massivem Heat → berüchtigtes Werk + **Pegelphantom**
- deutlicher Rufgewinn → **Nachtminister**

Damit kann eine Figur sowohl für gute als auch für schlechte große Taten bekannt werden. Titel sind bestätigte IDs; der Client darf keine Titel frei setzen.

---

## 9. Schaufenster-Geheimnisse

Bestimmte Orte besitzen vier sichtbare Notizen. Eine davon enthält einen echten Spielhinweis, die anderen sind absichtlich belanglos oder absurd.

Beispiel:

```text
Öffnungszeiten können sich spontan ändern ...
Drei Kassetten für zwei ...
[echter Hinweis ohne Kennzeichnung]
Gesucht: Deckel für eine Brotdose ...
```

Die read-only A4-Projection verrät **nicht**, welche Notiz das Geheimnis ist. Die HTTP-Antwort liefert nur die sichtbaren Texte in derselben Liste. Es gibt kein `is_secret`, keinen `secret_index` und keine farbliche Sondermarkierung.

---

## 10. Kleine echte Stadtspiele

### Poker

- fünf Karten Spieler gegen fünf Karten Haus
- deterministische Kartenreihenfolge aus World-Seed + Command-ID
- kein Echtgeld
- kein Einsatz
- kein Cash-out
- Ergebnis erzeugt nur lokale Spielpunkte

### Casinoautomat

- drei Symbole
- drei gleiche = Jackpotpunkte
- Paar = kleiner Punktgewinn
- sonst 0
- ebenfalls ohne Einsatz oder Echtgeld

### XOXO

- Spieler = `X`
- deterministische KI = `O`
- echtes persistiertes 3×3-Board
- Gewinn/Niederlage/Unentschieden und Rundenzähler bleiben im World-State

Alle drei Spiele sind replaybar. Dieselbe Command-ID darf kein zweites anderes Ergebnis erzeugen.

---

## 11. Inoffizielle Party + Gesetzeshüter

Die Mechanik gilt nur, wenn:

1. das Event als `unofficial` bestätigt wurde,
2. es sich in `live` befindet,
3. der Event-Ort katalogisiert als Bunker/Open-Air/Wald-Risikopunkt gilt,
4. für dieses Event noch kein Check existiert.

Der Check ist deterministisch und wird **genau einmal** gespeichert. Reloaden erzeugt keinen neuen Würfelwurf.

Aktuelle Wahrscheinlichkeit:

```text
Basis 25 %
+ Heat / 2
+ Polizeidruck / 3
maximal 85 %
```

### Exakt drei Entscheidungen

1. **Kooperieren und geordnet beenden**
2. **Auflagen akzeptieren und kontrolliert herunterfahren**
3. **Abbrechen und bestätigte Folgen tragen**

Jede Wahl verändert Stress/Ruf sowie Bezirkswerte unterschiedlich.

> Diese Szene ist eine fiktionale Entscheidungsmechanik. Sie enthält ausdrücklich keine reale Anleitung, Kontrollen zu umgehen, sich zu verstecken, zu fliehen, Beweismittel zu beseitigen oder Behörden zu täuschen.

---

## 12. Replay, Idempotenz und Recovery

World-Events sind im Journal katalogisiert:

```text
world.player_registered
world.intro_acknowledged
world.character_moved
world.housing_changed
world.trust_violation_recorded
world.trust_cycle_consumed
world.party_mode_changed
world.party_encounter_checked
world.party_encounter_resolved
world.storefront_inspected
world.minigame_played
world.settlement_applied
```

`GameRecoveryService` rekonstruiert den World-Block gemeinsam mit Character, Event, Economy, Incident und Settlement.

### Getrennte Replay-Verantwortung

Ein `world.*`-Record setzt ausschließlich World-State. Wenn dieselbe Transaktion zusätzlich Stress oder Ruf verändert, werden diese Werte ausschließlich durch `character.resources_changed` bzw. `character.reputation_changed` rekonstruiert. Damit entsteht keine doppelte Character-Anwendung.

### Fault-Injection

Der Test bricht einen World-Move direkt **nach durablem Journal**, aber vor State-Write ab. Beim Recovery wird die bestätigte Bewegung aus dem Journal wiederhergestellt.

---

## 13. Settlement-/World-Brücke

`SettlementService` bleibt alleinige Autorität für `event.completed`, Economy-, Character- und Incident-Abrechnung.

Danach übernimmt `WorldService.apply_confirmed_settlement(...)` ausschließlich die Stadtfolgen und Titel. Die World-Buchung ist durch die `settlement_id` idempotent.

Wenn der erste Aufruf nach Settlement wiederholt werden muss, darf niemals Geld, Stress, Ruf, Heat oder Titel doppelt entstehen.

---

## 14. Was bewusst noch nicht Teil dieser Stufe ist

- Immobilienkauf
- Immobilien-Upgrade-Level und deren Economy-Kosten
- hochwertiger Kartenrenderer
- echte Netzwerk-/Telegram-Spieler
- allgemeine Player-to-Player-Skillaktionen
- Hall-of-Tribute-Saisonabrechnung
- Echtgeld-/Glücksspiel

Die nächste logische Stufe ist **Immobilienkauf und Ausbau über den bestehenden Economy-Vertrag**. Erst danach sollte der hochwertige Kartenrenderer die stabilen Besitz-/District-Daten visualisieren.
