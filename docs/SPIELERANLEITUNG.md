# BUNKERFREQUENZ – Spieleranleitung

> **Stand: 0.8.3-B Spiellogik in Abnahme · HTML-Blueprint weiterhin schreibgeschützt**

Diese Anleitung erklärt den aktuellen Spielablauf ohne Entwicklerwissen. Der Spielkern kann inzwischen Charakteraktionen, Eventphasen, Equipment/Economy und Krisen sicher speichern und wiederherstellen. Die anklickbare HTML-Ansicht ist trotzdem noch kein fertiger Game-Client und verändert keine Spielstände.

**Woran erkenne ich den Release-Stand?** Das erste spielbare Alpha ist erreicht, wenn du ohne Codewissen eine Crew wählen, ein Event planen, Equipment beschaffen, eine Krise lösen, abrechnen und den gespeicherten Stand nach einem Neustart wieder laden kannst. 0.8.3-B bringt dafür jetzt die Krisenlogik und die Datenbasis der Berlin-Karte; Settlement und der schreibende Client fehlen noch.

## 0. HTML-Ansicht starten – ohne Vorwissen

1. Öffne ein Terminal im Projektordner.
2. Gib `python3 tools/start_web_blueprint.py` ein.
3. Warte auf `STATUS: BEREIT` und `ADRESSE:`.
4. Prüfe im Browser `● BEREIT` und den Bereich **Diagnose**.
5. Beende den Server mit `Strg+C`.

Falls kein Browser aufgeht, kopiere die hinter `ADRESSE:` genannte Adresse in den Browser. Bei belegtem Port hilft:

```bash
python3 tools/start_web_blueprint.py --port 0
```

Die Ansicht bleibt absichtlich **read-only**. Sie darf Spielregeln anzeigen, aber nicht selbst erfinden oder Zustände direkt schreiben.

## 1. Worum geht es?

BUNKERFREQUENZ ist ein Crew-RPG rund um Techno, FreeTekno, Orte, Events, Aufbau, Krisen und Charakterentwicklung. Alle Figuren beginnen spielmechanisch gleich. Erst deine Entscheidungen formen Stärken, Schwächen, Traits und Biografie.

Der langfristige Grundablauf:

```text
Ort wählen
  ↓
Crew / Event planen
  ↓
Equipment beschaffen
  ↓
Event aufbauen und starten
  ↓
Krise erkennen und reagieren
  ↓
abbauen und abrechnen
  ↓
Skills / Traits / Ruf / Biografie entwickeln
  ↓
Ort oder Immobilie weiterentwickeln
```

## 2. A4 und A3

### A4 Ops Deck

A4 ist die klare Arbeitsansicht. Sie soll später der schnellste Weg sein, um Voraussetzungen, Aktionen, Krisen und Ergebnisse zu verstehen.

### A3 Cinematic Forge

A3 zeigt dieselben bestätigten Daten stärker inszeniert. Animation entscheidet niemals über das Spielergebnis und darf keine Eingabe blockieren.

## 3. Energie und Stress

- Energie und Stress liegen zwischen `0` und `100`.
- Aktionen können Energie verbrauchen oder Stress erhöhen/senken.
- Die Runtime berechnet und speichert die Werte.
- Die Oberfläche darf sie nicht selbst verändern.

## 4. Skills, Traits und Level

Aktionen trainieren Skills mit festen Gewichten. Traits entstehen aus wiederholter Praxis, Krisen, Teamplay, Entdeckung, Erfolg und Scheitern. Nach Level 50 geht die Entwicklung in offene Resonanzränge über.

## 5. Dynamische Biografie

Bedeutende bestätigte Ereignisse können Biografieeinträge erzeugen. Die Oberfläche erfindet keine Geschichte; sie projiziert bestätigte Journal-Ereignisse.

## 6. Speichern und Recovery

Der Schutz besteht aus:

- append-only Journal,
- SHA-256-Hashkette,
- atomaren Zustandsdateien,
- Snapshots,
- Journal-Replay,
- Recovery aus dem letzten gültigen Stand,
- Quarantäne eines beschädigten Journal-Endes.

Eine ausgeführte Aktion oder Krise wird sofort bestätigt. Der 60-Sekunden-Autosave ist ein zusätzlicher Checkpoint und bedeutet nicht, dass Aktionen 60 Sekunden ungespeichert bleiben.

Bei Recovery-Fehlern: Programm beenden, Spielstandsordner unverändert lassen und keine Journal-/Snapshot-Dateien löschen.

## 7. Undo

Undo löscht keine bestätigte Geschichte. Erlaubte Rücknahmen werden durch neue kompensierende Ereignisse abgebildet. Gameplay-Actions und Krisen werden nicht pauschal halb zurückgedreht, weil sonst Budget, XP, Stress oder Biografie auseinanderlaufen könnten.

## 8. Character Forge – bereits validiert

Der Character-Forge-Pfad verbindet:

```text
Action
→ Energie / Stress
→ Progression
→ bestätigte Events
→ Feedback
→ Biografie
→ Autosave / Snapshot
→ Reload / Recovery
→ gleiche Daten in A4 und A3
```

## 9. Equipment und Budget

0.8.2 arbeitet wie eine gemeinsame Kasse mit Lager:

1. **Kaufen:** Besitz steigt, bestätigte Transaktion verändert das Event-Budget.
2. **Reservieren:** Equipment muss für das Event reserviert sein, um als bereit zu gelten.
3. **Verbrauchen/verkaufen:** nur freie, nicht reservierte Mengen.
4. **Recovery:** Lager, Ledger, Budget und Readiness werden gemeinsam rekonstruiert.

Wichtig: Das Budget darf nach Economy-Start nicht durch irgendeine andere Spiellogik direkt geändert werden.

## 10. Event-Aktionen in 0.8.3-A

Der verbindliche Weg lautet:

```text
Planung beginnen
→ Beschaffung beginnen
→ Transport starten
→ Aufbau beginnen
→ Soundcheck bestätigen
→ Event starten
→ Event beenden
→ Abbau beenden
→ Abrechnung vorbereiten
```

Die Runtime prüft dabei Acts, Crew, Budget, Equipment, Ort, Zugang, Zeitfenster und Sicherheitsfreigabe. Ein späterer Client zeigt diese Blockaden nur an; er berechnet sie nicht noch einmal selbst.

## 11. Krise erkennen und lösen – neu in 0.8.3-B1

Während `live` kann ein Incident eröffnet werden. Das Event wechselt dann atomar in `crisis`: Es gibt keinen Zustand „Krise gespeichert, Event aber noch live“ oder umgekehrt.

### Startkatalog

- Stromausfall
- Security-Probleme
- Equipment-Ausfall
- verspäteter Act
- zu hoher Besucherandrang
- Lärmdruck

Jede Krise bietet **drei konkrete Reaktionen**. Beispiel Stromausfall:

```text
Strom frisst Bass
├─ Notstrom anwerfen
├─ Crew verkabelt neu
└─ Event kontrolliert beenden
```

### Schweregrad

Incidents besitzen Severity `1–5`. Je höher der Wert, desto stärker werden die katalogisierten Folgen. Die Skalierung ist deterministisch: gleicher bestätigter Zustand + gleiche Reaktion = gleiche Wirkung.

### Was passiert nach deiner Entscheidung?

Die Crisis Engine bestätigt zunächst Folgen für:

- Budget,
- Ruf,
- Crew-Stress,
- Event-Stabilität,
- Heat.

Diese Werte werden in 0.8.3-B **vorgemerkt**, aber noch nicht direkt gebucht. Warum? Weil Geld nur über die Economy verändert werden darf. 0.8.3-C übernimmt die bestätigten Krisenfolgen anschließend kontrolliert in Economy, Character und Ruf.

### Sicherheitsregeln

- höchstens eine aktive Krise gleichzeitig,
- nur erlaubte Reaktionen werden angenommen,
- wiederholter gleicher Command wirkt nicht doppelt,
- Crash nach Journal-Schreibvorgang kann per Recovery rekonstruiert werden.

## 12. Berlin Ops Map – neu in 0.8.3-B2

Die Berlin-Karte ist zunächst eine **stilisierte Handlungskarte**, keine echte Navigation. Sie verwendet eine eigene 0–100-Kartenfläche statt exakter Straßenadressen. Dadurch funktioniert sie offline und kann später auf kleinen wie großen Displays skaliert werden.

### Startbezirke

- Mitte
- Friedrichshain
- Kreuzberg
- Neukölln
- Wedding
- Lichtenberg
- Treptow
- Charlottenburg

### Orte und Immobilien

Die Foundation enthält 12 Spielorte, darunter 7 vorbereitete kaufbare Objekte. Beispiele:

- Concrete Orbit
- Signalwerk
- Sublevel 44
- Frequenzdach
- Ringlager
- West-Kontor

Jeder Ort besitzt Werte für:

- **Prestige** – wie angesehen der Ort ist,
- **Audience Pull** – wie stark er Publikum zieht,
- **Risk** – wie anspruchsvoll/riskant die Nutzung ist,
- **Underground Factor** – Szenefaktor,
- **Utility** – praktischer Nutzen.

Aus diesen Werten entsteht ein sichtbares Tier:

`standard → strong → prime → legendary`

So werden starke Orte nicht einfach nur willkürlich bunt markiert, sondern wegen nachvollziehbarer Werte hervorgehoben.

### Bezirkslage – vorbereitet

Jeder Bezirk kann später dynamische Werte bekommen:

- Heat
- Prestige
- Polizeidruck
- Szeneaktivität

0.8.3-B kann diese Werte bereits darstellen, verändert sie aber noch nicht dauerhaft. Das folgt nach dem kompletten Event-/Settlement-Kern.

## 13. Immobilien-Ausbaupfade

Die Datenbasis kennt bereits mögliche Ausbau-Slots:

- Schallschutz
- Stromversorgung
- Fluchtwege
- Deko
- Bühne
- Bar
- Lager
- Sicherheitsraum
- Studio
- Büro

Kaufen und Ausbau sind noch nicht schreibend angebunden. Später müssen Kosten ausschließlich über bestätigte Economy-Transaktionen laufen.

## 14. Hall of Tribute

Die Berlin Ops Map besitzt genau eine **Hall of Tribute**. Sie ist der spätere Prestige- und Ranking-Ort.

Vorgesehene Anzeigen:

- beste Events,
- stärkste Krisenlösungen,
- Top-Orte,
- wertvollste Immobilien,
- Crew-/Karrierewerte,
- Wochen-/Monatsranking.

Vorbereitete satirische Titel:

- Lärmadel
- Bunkerbaron
- Kabelkönig
- Pegelpapst
- Stromheiland
- Bassbeauftragter
- Betonlegende
- Nachtminister

Spätere Effekte wie Pulse, Halo oder Ranking-Show sind **Darstellung**. Bei Reduced Motion bleibt die komplette Ranginformation statisch sichtbar.

## 15. Was kann man noch nicht normal spielen?

Noch offen:

- vollständige Settlement-Buchung der Krisenfolgen,
- `event.completed` nach bestätigter Abrechnung,
- schreibender A4-Game-Client,
- bedienbarer Kartenrenderer,
- Immobilienkauf/-ausbau,
- persistente Bezirksdynamik,
- saisonales Hall-of-Tribute-Ranking,
- Telegram-/Server-Synchronisation.

## 16. Was kann ich jetzt sinnvoll prüfen?

1. Starte den HTML-Blueprint wie in Abschnitt 0.
2. Prüfe Leseweg und Diagnose.
3. Verwechsle die statische Ansicht nicht mit dem bereits getesteten Runtime-Kern.
4. Für technische Details zu Krise und Berlin-Karte: [`CRISIS_CITY_0.8.3-B.md`](CRISIS_CITY_0.8.3-B.md).

## 17. Welche Beschreibung hilft mir weiter?

- **Spielwelt verstehen:** [`SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](SPIELBESCHREIBUNG_OHNE_TECHNIK.md)
- **aktuellen Prototyp starten:** diese Anleitung, Abschnitt 0
- **programmieren/anbinden:** [`SPIELBESCHREIBUNG_TECHNISCH.md`](SPIELBESCHREIBUNG_TECHNISCH.md)
- **nächste echte Aufgaben:** [`../TODO.md`](../TODO.md)

Der nächste fachliche Pflichtschritt ist **0.8.3-C – Settlement & Consequences**. Erst danach wird der schreibende Client angebunden.
