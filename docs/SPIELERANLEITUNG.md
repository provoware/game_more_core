# BUNKERFREQUENZ – Spieleranleitung

> **Stand: HTML-Blueprint auf Basis des Character-Forge-Vertical-Slice**

Diese Anleitung erklärt den aktuellen Spielablauf ohne Entwicklerwissen. Es gibt jetzt eine anklickbare HTML-Ansicht zum Prüfen des Designs. Sie ist noch kein fertiger Game-Client: Die getestete Spiellogik bleibt getrennt und die Ansicht verändert keine Spielstände.

## 0. HTML-Ansicht starten – ohne Vorwissen

1. Öffne ein Terminal im Projektordner.
2. Gib genau `python3 tools/start_web_blueprint.py` ein.
3. Warte auf `STATUS: BEREIT`. Der Browser öffnet sich automatisch.
4. Prüfe oben `● BEREIT` und unten den Bereich **Diagnose**.
5. Beende den lokalen Server im Terminal mit `Strg+C`.

Falls kein Browser aufgeht, kopiere die hinter `ADRESSE:` genannte Adresse in einen Browser. Für einen bewusst manuellen Start kann `python3 tools/start_web_blueprint.py --no-browser` verwendet werden. Meldet die Routine einen belegten Port, starte einmal mit `--port 0`; dann wird automatisch ein freier Port gewählt.

**Was bedeutet die Ansicht?** **Pixelreferenz** zeigt die vorhandene Grafik unverändert. **Spielfluss** und **Ansichten** werden aus dem gültigen UI-Manifest aufgebaut. **Diagnose** zeigt getrennt, welche Dateien und Verträge geladen wurden. Mit **Prüfbericht kopieren** lassen sich die technischen Angaben weitergeben, ohne einen Spielstand offenzulegen.

## 1. Worum geht es?

BUNKERFREQUENZ ist ein Crew-RPG rund um Techno, FreeTekno, Orte, Events, Aufbau und Charakterentwicklung. Die Figuren beginnen spielmechanisch gleich. Erst das, was du mit ihnen tust, verändert ihre Stärken, Schwächen und Biografie.

Der Grundablauf lautet:

```text
Ort / Ziel wählen
      ↓
Aktion auswählen
      ↓
Voraussetzungen + Energie/Stress prüfen
      ↓
Aktion ausführen
      ↓
Ergebnis erhalten
      ↓
Skills / Traits / Level / Biografie entwickeln sich
      ↓
Spielstand wird sicher gespeichert
      ↓
nächstes Ziel wählen
```

## 2. Die zwei Character-Forge-Ansichten

### A4 Ops Deck – normaler Spielablauf

A4 ist die sachliche Arbeitsansicht. Sie soll später der schnellste Weg sein, um eine Aktion auszuwählen, deren Voraussetzungen und Folgen zu sehen und anschließend das bestätigte Ergebnis zu prüfen.

### A3 Cinematic Forge – Charakterentwicklung inszeniert

A3 verwendet dieselben bestätigten Daten und dieselben acht Kernkomponenten wie A4. Es verändert nur die Darstellung: Level-Ups, Skill-Ups, Traits, Spezialisierung und Resonanz können stärker inszeniert werden. Die Animation entscheidet niemals über das Spielergebnis und blockiert keine Eingabe.

## 3. Energie und Stress

Jede der 20 Startaktionen besitzt seit 0.7.2 eine feste Energie-/Stresswirkung.

- **Energie** liegt zwischen `0` und `100`.
- **Stress** liegt zwischen `0` und `100`.
- Eine Aktion kann Energie verbrauchen oder Stress erhöhen.
- Einige ruhigere oder kreative Handlungen können Stress auch senken.
- Die Werte werden von der Spiellogik berechnet und als bestätigte Zustandsänderung gespeichert. Die Oberfläche darf sie nicht selbst erfinden oder verändern.

Beispiel:

```text
Vorher:   Energie 100 | Stress 0
Aktion:   Event durchführen
Wirkung:  Energie -28 | Stress +18
Nachher:  Energie 72  | Stress 18
```

## 4. Skills, Traits und Level

Eine Aktion kann mehrere Skills gleichzeitig trainieren. Wie stark ein Skill beteiligt ist, steht im Action-Vertrag.

Traits entstehen nicht durch eine Klassenwahl. Wiederholte Praxis, Training, Krisen, Erkundung, Teamplay, Erfolg und Scheitern liefern unterschiedliche Trait-Evidenz. Dadurch kann derselbe Startcharakter langfristig völlig unterschiedlich werden.

Nach Level 50 endet die Entwicklung nicht: Fortschritt geht in offene **Resonanzränge** über.

## 5. Dynamische Biografie

Bedeutende bestätigte Aktionen können einen Biografieeintrag erzeugen. Die Biografie wird nicht frei von der Oberfläche erfunden. Sie wird aus bestätigten Journal-Ereignissen abgeleitet.

Dadurch gilt:

- ein wichtiges Event kann dauerhaft Teil der Geschichte werden,
- große Erfolge und Niederlagen können anders gewichtet werden,
- dieselbe gespeicherte Historie wird in A4 und A3 gleich interpretiert.

## 6. Speichern, Autosave und Recovery

Eine ausgeführte Action wird sofort über den Persistence-Kern dauerhaft bestätigt. Zusätzlich verwendet der Character-Forge-Ablauf einen 60-Sekunden-Autosave-Checkpoint, wenn seit der letzten Sicherung Änderungen vorliegen.

Der Schutz besteht aus:

- append-only Journal,
- SHA-256-Hashkette,
- atomaren Zustandsdateien,
- Snapshots,
- Journal-Replay,
- Recovery aus dem letzten gültigen Stand,
- Quarantäne eines beschädigten Journal-Endes.

Enthält eine Journalzeile keinen vollständigen Datensatz oder falsche Datentypen, wird sie nicht teilweise übernommen. Die Wiederherstellung legt diese Zeile und den gesamten folgenden Rest getrennt in Quarantäne ab und arbeitet nur mit den davor bestätigten Einträgen weiter.

Ist eine einzelne Snapshot-Sicherung unvollständig oder stimmt ihre Prüfsumme nicht, bricht die Wiederherstellung nicht ab. Sie überspringt diesen beschädigten Stand und verwendet den neuesten älteren Snapshot, der vollständig geprüft werden kann. Gibt es gar keinen gültigen Checkpoint, meldet das Spiel einen kontrollierten Recovery-Fehler, statt mit einem internen Programmfehler weiterzulaufen.

Der 60-Sekunden-Autosave bedeutet also **nicht**, dass eine ausgeführte Action bis zu 60 Sekunden ungespeichert bleibt. Er ist ein zusätzlicher Recovery-Checkpoint.

## 7. Undo – was kann rückgängig gemacht werden?

Undo löscht keine Journalhistorie. Eine erlaubte Rücknahme wird als neues kompensierendes Ereignis gespeichert.

Im aktuellen 0.7.2-Vertical-Slice ist der sichere Ein-Schritt-Undo für Profiländerungen vorhanden, zum Beispiel für Alias oder Motto.

Eine bereits ausgeführte Gameplay-Action wird nicht pauschal zurückgedreht. Das verhindert widersprüchliche Zustände wie „Energie zurück, aber XP und Biografie bleiben erhalten“.

## 8. Was ist in 0.7.2 bereits getestet?

Der komplette Character-Forge-Pfad wird als Integration getestet:

```text
Action
→ Energie / Stress
→ Progression
→ bestätigte Events
→ Feedback
→ Biografie
→ 60-Sekunden-Autosave + Snapshot
→ sicherer Profil-Undo
→ Reload
→ gleiche bestätigte Daten in A4 und A3
```

Der validierte Implementierungsstand von PR #41 bestand auf Head `5f7ded400a5fca1ee25307797628ab2584de9812`:

- Runtime Core `32533954380` ✅
- Presentation Core `32533954387` ✅
- Repository Health `32533954406` ✅

## 9. Was kann man noch nicht normal spielen?

Noch offen sind insbesondere:

- ein fertiger, mit der Runtime verbundener Desktop-/Web-/Game-Engine-Client (der HTML-Blueprint ist nur eine schreibgeschützte Designauswertung),
- vollständige Event- und Wirtschaftssimulation,
- dynamischer Equipmentmarkt,
- kompletter Clubbetrieb,
- Telegram-/Server-Synchronisation.

Diese Systeme werden auf dem jetzt getesteten Character-, Persistence- und Presentation-Kern aufgebaut.

## 10. Nächster Spielentwicklungsschritt

Als nächste größere Stufe ist **0.8 – Event-/Wirtschafts-Integration** vorgesehen. Damit sollen die bisher einzelnen Character-Actions in einen dauerhaften Spielkontext mit Eventplanung, Equipmentmarkt, Clubbetrieb und Clubbewertung eingebettet werden.
