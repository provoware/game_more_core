# BUNKERFREQUENZ – Spieleranleitung

> **Stand: 0.8.4-alpha.1 ist das reproduzierbare lokale Alpha · 0.8.5-D Living City befindet sich in der laufenden, noch nicht gemergten Abnahme**

Diese Anleitung erklärt BUNKERFREQUENZ ohne Entwicklerwissen. Der lokale A4-Client kann inzwischen ein neues Spiel anlegen, Profilwerte ändern, den Eventpfad bedienen, Equipment verwalten, Krisen lösen, abrechnen, speichern und nach einem Neustart wiederherstellen. In 0.8.5-D kommt eine dauerhaft reagierende Stadt hinzu. Die Spielregeln bleiben dabei in der Runtime; der Browser zeigt bestätigte Daten und löst erlaubte Commands aus, er berechnet die Regeln nicht selbst.

**Woran erkenne ich den Release-Stand?** `0.8.4-alpha.1` ist die letzte veröffentlichte Produkt-Baseline. Die hier beschriebenen Living-City-Funktionen gehören zum laufenden 0.8.5-D-Entwicklungsstand und werden erst nach grüner Remote-Abnahme und `/safe-merge` Bestandteil von `main`. Eine neue Produktversion entsteht deshalb noch nicht.

## 0. Lokales Spiel starten – ohne Vorwissen

Im Projektordner kannst du den schreibenden A4-Client starten:

```bash
./START_BUNKERFREQUENZ.sh
```

Alternativ direkt über Python:

```bash
python3 tools/start_a4_game_client.py --port 0
```

Danach:

1. Warte im Terminal auf `STATUS: BEREIT` und `ADRESSE:`.
2. Falls der Browser nicht automatisch öffnet, kopiere die angezeigte Adresse in Firefox oder Chrome.
3. Der Server läuft nur lokal auf `127.0.0.1`.
4. Beende ihn mit `Strg+C`.
5. Dein Spielstand liegt außerhalb der ausgelieferten Webdateien und wird nicht als statische Webseite veröffentlicht.

Der ältere visuelle Blueprint kann weiterhin separat mit `python3 tools/start_web_blueprint.py --port 0` gestartet werden. Er ist eine schreibgeschützte Entwurfs-/Prüfansicht und nicht der eigentliche A4-Spielclient.

## 1. Worum geht es?

BUNKERFREQUENZ ist ein Crew-RPG rund um Techno, FreeTekno, Orte, Events, Aufbau, Krisen, Beziehungen und Charakterentwicklung. Alle Figuren beginnen spielmechanisch vergleichbar. Erst Entscheidungen, Erlebnisse, Erfolg, Pech und Konflikte formen Stärken, Schwächen, Traits, Ruf und Biografie.

Der langfristige Grundablauf:

```text
Figur / Crew anlegen
  ↓
Stadt und Ort erleben
  ↓
Crew / Event planen
  ↓
Equipment beschaffen
  ↓
Event aufbauen und starten
  ↓
Krise erkennen und reagieren – falls eine auftritt
  ↓
abbauen und abrechnen
  ↓
Bezirk / Ruf / Biografie reagieren
  ↓
Skills / Traits / Titel / große Werke entwickeln
  ↓
später Immobilien kaufen und ausbauen
```

## 2. A4 und A3

### A4 Ops Deck

A4 ist die klare Arbeitsansicht und im lokalen Alpha bereits schreibend angebunden. Sie ruft vorhandene Application-Services auf. Deshalb gilt: Wenn ein Button gesperrt ist, stammt der Grund aus derselben Runtime-Regel, die auch den eigentlichen Command prüfen würde.

### A3 Cinematic Forge

A3 zeigt dieselben bestätigten Daten stärker inszeniert. Animation entscheidet niemals über ein Spielergebnis und darf Eingaben nicht blockieren. Der hochwertige Kartenrenderer bleibt ein späterer Darstellungsschritt.

## 3. Energie und Stress

- Energie und Stress liegen zwischen `0` und `100`.
- Aktionen können Energie verbrauchen oder Stress erhöhen/senken.
- Die Runtime berechnet und speichert die Werte.
- Die Oberfläche darf sie nicht selbst verändern.
- Auch Living-City-Ereignisse, etwa eine schwierige Entscheidung während einer Party, benutzen dieselben bestätigten Character-Regeln.

## 4. Skills, Traits und Level

Aktionen trainieren Skills mit festen Gewichten. Traits entstehen aus wiederholter Praxis, Krisen, Teamplay, Entdeckung, Erfolg und Scheitern. Nach Level 50 geht die Entwicklung in offene Resonanzränge über.

Wichtig für Beziehungen: Eine spätere Skill-/Fähigkeitswirkung auf eine andere Figur kann durch eine bestätigte Misstrauensfolge vorübergehend auf `0 %` gesetzt werden. Der Skill selbst wird dadurch nicht gelöscht oder heruntergestuft.

## 5. Dynamische Biografie

Bedeutende bestätigte Ereignisse können Biografieeinträge erzeugen. Die Oberfläche erfindet keine Geschichte; sie projiziert bestätigte Journal-Ereignisse. Auch ein vollständig abgerechnetes Event kann genau einen bestätigten Event-Eintrag in deiner Biografie erzeugen.

Living City ergänzt dazu Ehrenruf-Titel und „große Werke“. Diese dürfen positiv, negativ oder ambivalent sein: Eine legendäre Nacht und ein berüchtigter Hoch-Heat-Abschluss sind beides erinnerungswürdige Geschichte, aber nicht dasselbe moralische Ergebnis.

## 6. Speichern und Recovery

Der Schutz besteht aus:

- append-only Journal,
- SHA-256-Hashkette,
- atomaren Zustandsdateien,
- Snapshots,
- Journal-Replay,
- Recovery aus dem letzten gültigen Stand,
- Quarantäne eines beschädigten Journal-Endes.

Eine ausgeführte Aktion, Krise, World-Aktion oder Abrechnung wird sofort bestätigt. Der 60-Sekunden-Autosave ist ein zusätzlicher Checkpoint und bedeutet nicht, dass Aktionen 60 Sekunden ungespeichert bleiben.

### Living-City-Recovery

World-Ereignisse werden ebenfalls aus dem Journal rekonstruiert. Dabei gilt eine wichtige Trennung: Ein `world.*`-Record rekonstruiert nur den World-State. Character-Stress oder Ruf werden weiterhin ausschließlich über die zuständigen `character.*`-Events wiederhergestellt.

Falls ein Absturz exakt zwischen zwei zusammengehörigen Schritten passiert – das Settlement ist bereits dauerhaft `completed`, aber die anschließende Bezirksfolge konnte noch nicht geschrieben werden – erkennt der nächste A4-Start diese Lücke. Er zieht ausschließlich die fehlende World-Folge aus dem bereits bestätigten Settlement nach. Ein bereits angewandtes Settlement wird nicht ein zweites Mal gebucht.

Bei Recovery-Fehlern: Programm beenden, Spielstandsordner unverändert lassen und keine Journal-/Snapshot-Dateien löschen.

## 7. Undo

Undo löscht keine bestätigte Geschichte. Erlaubte Rücknahmen werden durch neue kompensierende Ereignisse abgebildet. Gameplay-Actions, Krisen, Living-City-Folgen und ein abgeschlossenes Settlement werden nicht pauschal halb zurückgedreht, weil sonst Budget, XP, Stress, Ruf, Bezirk oder Biografie auseinanderlaufen könnten.

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
→ gleiche bestätigte Daten in den Ansichten
```

## 9. Equipment und Budget

0.8.2 arbeitet wie eine gemeinsame Kasse mit Lager:

1. **Kaufen:** Besitz steigt, bestätigte Transaktion verändert das Event-Budget.
2. **Reservieren:** Equipment muss für das Event reserviert sein, um als bereit zu gelten.
3. **Verbrauchen/verkaufen:** nur freie, nicht reservierte Mengen.
4. **Recovery:** Lager, Ledger, Budget und Readiness werden gemeinsam rekonstruiert.

Wichtig: Das Budget darf nach Economy-Start nicht durch irgendeine andere Spiellogik direkt geändert werden.

### Andere Stadt, anderer Preis

Living City versieht Städte mit einem bestätigten Preisfaktor. Der Faktor kommt aus deiner gespeicherten Position und wird serverseitig an den Economy-Service übergeben. Der Browser kann keinen eigenen Rabattwert mitsenden.

Aktueller Startvertrag:

- Berlin: `100 %`
- Leipzig: `92 %`
- Hamburg: `115 %`

Eine wiederholte Economy-Command-ID ist auch an den damals verwendeten Stadtpreis gebunden. Ein alter Command kann daher nicht nach einem Stadtwechsel mit einem anderen Preis „neu interpretiert“ werden. Alte 0.8.4-Records ohne Stadtpreiskontext bleiben als historischer Faktor `100 %` lesbar.

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

Die Runtime prüft dabei Acts, Crew, Budget, Equipment, Ort, Zugang, Zeitfenster und Sicherheitsfreigabe. A4 zeigt diese Blockaden an; es berechnet sie nicht noch einmal selbst.

## 11. Krise erkennen und lösen – validiert in 0.8.3-B1

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

Incidents besitzen Severity `1–5`. Je höher der Wert, desto stärker werden die katalogisierten Einzelfolgen. Die Skalierung ist deterministisch: gleicher bestätigter Zustand + gleiche Reaktion = gleiche Wirkung. Mehrere Krisen dürfen sich bis zur Abrechnung zu größeren Gesamtsummen addieren.

### Was passiert nach deiner Entscheidung?

Die Crisis Engine bestätigt zunächst Folgen für:

- Budget,
- Ruf,
- Crew-Stress,
- Event-Stabilität,
- Heat.

Diese Werte werden während der Krise **vorgemerkt**, aber nicht direkt an Economy oder Character vorbeigeschrieben. Die Abrechnung aus 0.8.3-C übernimmt sie kontrolliert.

### Sicherheitsregeln

- höchstens eine aktive Krise gleichzeitig,
- nur erlaubte Reaktionen werden angenommen,
- wiederholter gleicher Command wirkt nicht doppelt,
- auch ein Replay muss zum richtigen Event-Kontext gehören,
- ein offener Incident wird nicht mit einem nachträglich anderen Regelstand aufgelöst,
- Crash nach Journal-Schreibvorgang kann per Recovery rekonstruiert werden.

## 12. Event abrechnen – 0.8.3-C remote validiert

Nach dem Abbau landet das Event in der Phase **`settlement`**. Jetzt werden die bereits bestätigten Folgen in einem einzigen, zusammengehörigen Abschluss verbucht.

Einfach gesagt:

```text
Abrechnung vorbereiten
→ offene Krise? dann STOP
→ bestätigte Folgen lesen
→ Budget buchen
→ Stress buchen
→ Ruf buchen
→ Biografieeintrag bestätigen
→ Event auf completed setzen
→ alles gemeinsam speichern
→ Living City übernimmt danach bestätigte Bezirksfolgen
```

### Was wird tatsächlich verändert?

- **Budget:** ausschließlich über das Economy-Ledger.
- **Stress:** bleibt immer zwischen `0` und `100`.
- **Ruf:** eine neue Abrechnung kann den Ruf höchstens bis `0` senken, nicht darunter.
- **Stabilität und Heat:** liegen zunächst als bestätigtes Settlement-Ergebnis vor; 0.8.5-D nutzt diese bestätigten Werte anschließend für den zuständigen District-State.
- **Biografie:** der Abschluss wird eindeutig deinem Character zugeordnet.

### Was passiert, wenn es gar keine Krise gab?

Das Event kann trotzdem normal abgeschlossen werden. Dann sind die fünf Krisenfolgen einfach `0`. Du musst also **keine künstliche Krise auslösen**, nur um ein Event abrechnen zu können.

### Was passiert bei einem alten Save mit negativem Ruf?

Ältere Spielstände dürfen weiterhin geladen werden, auch wenn sie einen früher zulässigen negativen Rufwert besitzen. Die neue Abrechnung normalisiert erst beim Abschluss das Ergebnis auf mindestens `0`. Der alte Spielstand wird also nicht allein wegen seines Rufwerts unlesbar.

### Warum ist die Abrechnung atomar?

„Atomar“ bedeutet hier: **alles oder nichts** innerhalb des Settlement-Commits. Budget, Stress, Ruf, Eventabschluss und Settlement-Beleg gehören zusammen. Die Living-City-Folge ist ein eigener idempotenter Folgecommit; genau deshalb besitzt der A4-Start die oben beschriebene Reconciliation für den seltenen Absturz dazwischen.

Recovery prüft außerdem, ob die im Settlement-Beleg genannten Budget-, Stress- und Rufänderungen exakt zu den tatsächlich gebuchten Deltas passen. Widersprüche werden nicht geraten oder repariert, sondern kontrolliert abgewiesen.

### Wichtige Sperren

Die Abrechnung wird gestoppt, wenn:

- das Event noch nicht in `settlement` ist,
- noch eine Krise aktiv ist,
- der betroffene Character nicht zur Event-Crew gehört,
- das Endbudget negativ würde,
- eine Command-ID mit anderem Inhalt wiederverwendet wird,
- gespeicherte Folgen und tatsächlich angewandte Deltas widersprüchlich sind.

Erst nach erfolgreichem Abschluss entsteht **`event.completed`**.

Die finale 0.8.3-C-Abnahme erfolgte auf PR #65 / Head `ccfb145547b241a179bd0135d34a7470d690821c` mit Runtime Core `32568683844`, Presentation Core `32568683898` und Repository Health `32568683863`; der Merge erfolgte ausschließlich über `/safe-merge` als `5ae811333878ae67947417ccb72e791caafe4ba9`.

## 13. Berlin Ops Map – Foundation und Living-City-Daten

Die Karte ist eine **stilisierte Handlungskarte**, keine echte Navigation. Sie verwendet eine eigene 0–100-Kartenfläche statt exakter Straßenadressen. Dadurch funktioniert sie offline und kann später auf kleinen wie großen Displays skaliert werden.

### Berliner Startbezirke

- Mitte
- Friedrichshain
- Kreuzberg
- Neukölln
- Wedding
- Lichtenberg
- Treptow
- Charlottenburg

### Orte und Immobilien

Die Foundation enthält Spielorte und vorbereitete kaufbare Objekte, zum Beispiel:

- Concrete Orbit
- Signalwerk
- Sublevel 44
- Frequenzdach
- Ringlager
- West-Kontor

Jeder Kartenort kann Darstellungswerte wie Prestige, Audience Pull, Risk, Underground Factor und Utility besitzen. Der spätere hochwertige Renderer darf diese Daten darstellen, aber nicht verändern.

### Bezirkslage – in 0.8.5-D persistent

Living City führt dauerhaft vier Werte je Stadt/Bezirk:

- **Heat** – wie aufgeheizt/auffällig die Lage ist,
- **Prestige** – Ansehen des Bezirks im Spiel,
- **Polizeidruck** – Spielrisiko durch erhöhte Aufmerksamkeit,
- **Szeneaktivität** – wie lebendig die lokale Szene ist.

Bestätigte Settlement-Ergebnisse verändern diese Werte deterministisch und werden über `settlement_id` genau einmal angewandt. Die Werte bleiben zwischen Neustarts erhalten und werden per Journal-Replay rekonstruiert.

## 14. Immobilien-Ausbaupfade

Die Datenbasis kennt mögliche Ausbau-Slots:

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

Kaufen und Ausbau sind im 0.8.5-D-Scope noch nicht schreibend angebunden. Der nächste Immobilien-Schritt muss Kosten ausschließlich über bestätigte Economy-Transaktionen buchen und Besitz/Upgrade-Level als eigenen persistenten Vertrag führen. Die Living-City-Werte sind dafür die stabile Grundlage.

## 15. Hall of Tribute, Ehrenruf und große Werke

Die Berlin Ops Map besitzt genau eine **Hall of Tribute** als späteren Prestige- und Ranking-Ort. Living City kann bereits bestätigte Ehrenruf-/Infamy-Titel und große Werke speichern.

Beispiele für vorbereitete Titel:

- Lärmadel
- Bunkerbaron
- Kabelkönig
- Pegelpapst
- Stromheiland
- Bassbeauftragter
- Betonlegende
- Nachtminister

Ein Titel ist nicht automatisch „gut“. Ein hohes-Heat-Ereignis kann einen berüchtigten Titel erzeugen; ein positiver Abschluss kann einen Ehrentitel hervorbringen. Große Werke speichern zusätzlich ihre Herkunft aus einem bestätigten Event. Saisonale Ranglisten und die eigentliche Hall-of-Tribute-Show folgen später.

## 16. Living City – Einbuchungs-ID und Wohnungsengpass

### Deine Einbuchungs-ID

Beim Eintritt in die Living City erhält jede Figur eine technische Einbuchungs-ID wie:

```text
BF-000001
BF-000002
BF-000003
```

Diese ID ist nicht dein Anzeigename. Sie ist ein Integritätsmerkmal und darf niemals doppelt vergeben werden. Der Spielstand prüft außerdem, dass der nächste Nummernzähler **hinter allen bereits ausgegebenen IDs** liegt. Ein beschädigter Save, der den Zähler zurücksetzt, wird abgewiesen statt irgendwann eine alte ID erneut zu benutzen.

Der derzeitige World-State besitzt keine Spieler-Löschfunktion. Falls später Löschen/Archivieren hinzukommt, muss vorab ein dauerhafter Tombstone-/Issued-ID-Vertrag ergänzt werden; eine bereits ausgegebene Nummer darf auch dann nicht recycelt werden.

### „Auf wundersame Weise“ immer ein Zuhause zu wenig

Bei `N` registrierten Figuren gibt es absichtlich nur `N-1` unabhängige Wohnplätze. Deshalb ist **genau eine Figur** immer:

- `homeless` – ohne eigenes Zuhause, oder
- `guest` – bei einer anderen Figur untergebracht.

Kommt eine neue Figur dazu, erhält die bisherige Mangelperson einen unabhängigen Platz und der Neuzugang übernimmt den Mangel. So bleibt der Engpass dauerhaft erhalten.

Ein Gast darf nur bei einer Figur mit **eigenem unabhängigen Zuhause** unterkommen. Man kann nicht bei sich selbst und auch nicht bei einer ebenfalls obdachlosen/Gast-Figur wohnen. Diese Regeln werden beim Laden des Saves erneut geprüft.

## 17. Bewegung, Städte und andere Sitten

Figuren können ihren bestätigten Aufenthaltsort wechseln. Der aktuelle Startvertrag enthält Berlin, Leipzig und Hamburg. Jede Stadt kann eigene:

- Bezirke,
- Orte,
- Preisfaktoren,
- lokale Sitten/Flavor-Regeln

besitzen.

Bewegung wird journalisiert und ist replaybar. Ein `location_id` muss zur gewählten Stadt und zum Bezirk gehören; falsche Kombinationen werden abgewiesen.

Der Event-Ort und die momentane Position deiner Figur sind bewusst getrennte Informationen. Ein Behörden-Risikocheck eines laufenden Events richtet sich nach dem **bestätigten Event-Ort**. Du kannst ihn nicht dadurch verändern, dass du deine Figur in der Oberfläche nachträglich in einen anderen Bezirk bewegst.

## 18. Misstrauen, Betrug und einseitige Wirkungsblockade

Bestätigte Taten vom Typ:

- Täuschung (`deception`),
- Verrat (`betrayal`),
- Betrug (`fraud`)

können einen gerichteten Trust-Block erzeugen.

Beispiel: Ria betrügt Mika.

```text
Ria → Mika: 0 % wirksame Skill-/Fähigkeitswirkung für 12 bestätigte Wirkzyklen
Mika → Ria: 100 % – Gegenrichtung bleibt wirksam
```

Die Skills von Ria werden dabei nicht gelöscht. Nur ihre Wirkung **auf genau Mika** ist für diese zwölf bestätigten Wirkzyklen blockiert. Jeder tatsächlich verbrauchte Zyklus wird persistent gezählt. Der zwölfte bestätigte Versuch bleibt für diesen Versuch wirkungslos; erst der nächste neue Versuch ist wieder normal wirksam. Ein Retry derselben Command-ID verbraucht keinen zusätzlichen Zyklus.

Der lokale Einzelspieler-A4 bietet absichtlich keinen frei manipulierbaren „Betrug gegen Spieler“-Button. Der Trust-Service ist die Runtime-Grundlage für spätere echte Interaktionen/Netzwerkspieler; die auslösende Tat muss dort als bestätigtes Gameplay-Ereignis entstehen.

## 19. Introgeschichte mit deinem Namen

Beim Living-City-Einstieg wird die Introgeschichte mit dem aktuellen bestätigten Anzeigenamen der Figur formuliert. Anzeigename und technische Character-/Einbuchungs-ID bleiben getrennt.

Das Intro kann einmal bestätigt werden. Ein Reload würfelt keine neue Herkunft oder ID aus. Eine spätere Profilumbenennung ändert deinen aktuellen sichtbaren Namen, aber die technische Identität bleibt stabil.

## 20. Kleine Spiele in der Stadt

Bestimmte Orte können kleine echte Spiele anbieten. Die aktuelle Foundation enthält:

### 5-Karten-Poker

- fünf Karten gegen ein deterministisches Hausblatt,
- vollständige normale 5-Karten-Wertung von High Card bis Straight Flush,
- Ass-2-3-4-5 wird als niedrige Straße erkannt,
- korrekte Tie-Breaks,
- **kein Geldeinsatz, kein Echtgeld, kein Cash-out**,
- Ergebnis gibt nur Spielpunkte.

### Punkte-Casinoautomat

- drei Symbole,
- Paar oder Jackpot kann Punkte geben,
- kein Geld- oder Besitzgewinn,
- derselbe bestätigte Command liefert beim Replay dasselbe Ergebnis und zahlt nicht doppelt aus.

### XOXO

- persistentes 3×3-Brett gegen eine deterministische KI,
- Siege/Niederlagen/Unentschieden werden gezählt,
- ungültige oder logisch unmögliche Boards werden beim Laden abgewiesen,
- Reload erzeugt keinen neuen KI-Zug für einen bereits bestätigten Command.

## 21. Schaufenster und versteckte Spielgeheimnisse

An bestimmten Schaufenstern findest du mehrere kurze Notizen. Manche sind belanglos, manche absurd und manche enthalten echte Spielhinweise.

Die wichtige Regel: **Der Client erhält keine Markierung „dieser Satz ist das Geheimnis“.** Er zeigt eine flache Liste gleich behandelter Texte. Dadurch bleibt Entdecken echtes Lesen statt ein leuchtender „Secret“-Datensatz im Browser.

Auch das Lesen wird bestätigt. Ein Retry derselben Aktion erzeugt keine zweite Entdeckung.

## 22. Inoffizielle Party und Behördenbegegnung

Bei einem bestätigten Event an einem dafür katalogisierten Bunker-, Open-Air- oder Waldort kann die Party vor `LIVE` als `unofficial` markiert werden. Während `LIVE` darf genau ein reproduzierbarer Risikocheck stattfinden.

Der Check berücksichtigt den bestätigten Event-Ort sowie Heat und Polizeidruck des dazugehörigen Bezirks. Er benutzt einen stabilen Spielseed – nicht die Uhrzeit. Speichern und neu laden erzeugt deshalb keinen bequemeren neuen Wurf.

Falls die Begegnung ausgelöst wird, erscheinen **genau drei abstrakte Entscheidungen**. Der aktuelle Vertrag verwendet deeskalierende Spielentscheidungen, zum Beispiel kontrolliert beenden, transparent kooperieren oder die Lage ruhig ordnen. Die Entscheidung kann Stress, Ruf, Heat, Polizeidruck und Szeneaktivität verändern.

Die Mechanik enthält **keine reale Anleitung**, wie man Behörden täuscht, Kontrollen umgeht, flieht oder Beweise versteckt. Sie ist eine fiktionale Konsequenz-/Entscheidungsmechanik.

Ein Party-Check besitzt strikte Zustände: Nicht ausgelöst bedeutet bereits abgeschlossen; ausgelöst und offen besitzt noch keine Entscheidung; ausgelöst und abgeschlossen muss genau eine bestätigte Entscheidung besitzen. Widersprüchliche Saves werden abgewiesen.

## 23. Command-IDs und warum sie wichtig sind

Jede schreibende Aktion besitzt eine Command-ID. Das schützt gegen Doppelklick, Netzwerk-Retry und Neustart-Wiederholung.

Grundregel:

```text
gleiche Command-ID + gleicher Inhalt
→ idempotenter Replay, keine Doppelwirkung

gleiche Command-ID + anderer Inhalt
→ Fehler, kein stilles Umschreiben
```

Diese Bindung gilt in Living City unter anderem für Bewegung, Housing, Misstrauen, Party-Modus/-Entscheidung, Minispiele und Stadtpreise. Auch Profiländerungen werden im A4-Adapter gegen eine geänderte Wiederverwendung derselben Command-ID geschützt.

## 24. Was kann man noch nicht normal spielen?

Nach 0.8.5-D bleiben insbesondere offen:

- Immobilienkauf und echte Ausbau-Level,
- hochwertiger Kartenrenderer,
- saisonales Hall-of-Tribute-Ranking,
- echte Mehrspieler-/Telegram-/Server-Synchronisation,
- die tatsächliche Multiplayer-Auslösung der vorbereiteten Trust-/Misstrauensmechanik.

Der lokale A4-Client, Event-/Economy-/Krisen-/Settlement-Loop, Street Encounters und die Living-City-Grundlage sind technisch getrennte, journalfähige Schichten. `0.8.5-D` wird erst nach dem finalen Remote-Merge als abgeschlossen bezeichnet.

## 25. Was kann ich jetzt sinnvoll prüfen?

1. Starte den A4-Client wie in Abschnitt 0.
2. Lege ein neues Spiel an und prüfe deine Einbuchungs-ID sowie Introgeschichte.
3. Wechsle Städte/Bezirke und beobachte den bestätigten Preisfaktor.
4. Spiele an passenden Orten die kleinen Spiele; ein Reload darf bestätigte Ergebnisse nicht neu würfeln.
5. Lies Schaufenstertexte, ohne eine technische Secret-Markierung zu erwarten.
6. Spiele den normalen Eventpfad bis Settlement; nach Abschluss soll der passende Bezirkszustand genau einmal reagieren.
7. Speichere einen Checkpoint und starte neu; bestätigte World-Werte müssen identisch bleiben.
8. Technische Details: [`LIVING_CITY_0.8.5-D.md`](LIVING_CITY_0.8.5-D.md).

## 26. Welche Beschreibung hilft mir weiter?

- **Spielwelt verstehen:** [`SPIELBESCHREIBUNG_OHNE_TECHNIK.md`](SPIELBESCHREIBUNG_OHNE_TECHNIK.md)
- **aktuellen lokalen Client starten:** diese Anleitung, Abschnitt 0
- **Living-City-Vertrag:** [`LIVING_CITY_0.8.5-D.md`](LIVING_CITY_0.8.5-D.md)
- **Krise und Berlin-Map-Foundation:** [`CRISIS_CITY_0.8.3-B.md`](CRISIS_CITY_0.8.3-B.md)
- **Settlement:** [`SETTLEMENT_0.8.3-C.md`](SETTLEMENT_0.8.3-C.md)
- **programmieren/anbinden:** [`SPIELBESCHREIBUNG_TECHNISCH.md`](SPIELBESCHREIBUNG_TECHNISCH.md)
- **nächste echte Aufgaben:** [`../TODO.md`](../TODO.md)

Der nächste fachliche Pflichtschritt nach dem sicheren Merge von 0.8.5-D ist der **Immobilienkauf/-ausbau über den bestehenden Economy-Vertrag**. Erst auf dem stabilen World-/Property-State folgen Hall-of-Tribute-Ausbau und hochwertiger Kartenrenderer.
