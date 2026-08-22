# BUNKERFREQUENZ – Spieleranleitung

> **Stand: HTML-Blueprint auf Basis des Character-Forge-Vertical-Slice**

Diese Anleitung erklärt den aktuellen Spielablauf ohne Entwicklerwissen. Es gibt jetzt eine anklickbare HTML-Ansicht zum Prüfen des Designs. Sie ist noch kein fertiger Game-Client: Die getestete Spiellogik bleibt getrennt und die Ansicht verändert keine Spielstände.

**Woran erkenne ich den Release-Stand?** Aktuell kannst du die Oberfläche ansehen und ihre Diagnose prüfen, aber noch keinen vollständigen Eventablauf darin spielen. Das erste spielbare Alpha ist erreicht, wenn du ohne Codewissen eine Crew wählen, ein Event planen, Equipment beschaffen, das Event abschließen und den gespeicherten Stand nach einem Neustart wieder laden kannst. Bis dahin ist die HTML-Ansicht ausdrücklich ein Prototyp.

Die Ansicht wird erst dann mit Schreibfunktionen verbunden, wenn der vollständige Eventablauf geprüft ist. Dadurch bleibt sie eine einfache Bedienoberfläche und baut keine zweite, abweichende Spiellogik auf.

## 0. HTML-Ansicht starten – ohne Vorwissen

1. Öffne ein Terminal im Projektordner.
2. Gib genau `python3 tools/start_web_blueprint.py` ein.
3. Warte auf `STATUS: BEREIT` und eine Zeile `ADRESSE:`. Erst dann ist der Start abgeschlossen; der Browser öffnet sich automatisch.
4. Prüfe im Browser oben `● BEREIT` und unten den Bereich **Diagnose**. Damit sind Server und Oberfläche gemeinsam geprüft.
5. Beende den lokalen Server im Terminal mit `Strg+C`.

Falls kein Browser aufgeht, kopiere die hinter `ADRESSE:` genannte Adresse in einen Browser. Für einen bewusst manuellen Start kann `python3 tools/start_web_blueprint.py --no-browser` verwendet werden. Meldet die Routine `Port 8043 ist belegt`, starte einmal mit `python3 tools/start_web_blueprint.py --port 0`; die danach ausgegebene Adresse enthält den automatisch gewählten freien Port.

**Was bedeutet die Ansicht?** Der schmale Block **Leseweg** erklärt zuerst Reihenfolge, Modus und Datenquelle. Danach zeigen die nummerierten Sektoren **Pixelreferenz** die vorhandene Grafik unverändert, **Spielfluss** die fünf Schritte und **Ansichten** die vier Darstellungsvarianten aus dem gültigen UI-Manifest. **Diagnose** zeigt getrennt, welche Dateien und Verträge geladen wurden. Mit **Prüfbericht kopieren** lassen sich die technischen Angaben weitergeben, ohne einen Spielstand offenzulegen.

**Einfache Sichtprüfung:** Lies zuerst nur die gelben Sektornummern von `01` bis `04`. Im Spielfluss zeigen gelbe Pfeile die Richtung. Ein roter Rand an **A4 Ops Deck** kennzeichnet die bevorzugte Einsteigeransicht. Wenn Text oder Grafik zu klein sind, vergrößere die Browseransicht mit `Strg` und `+`; die Blöcke ordnen sich auf schmalen Fenstern untereinander an.

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

## 9. Equipment und Budget einfach verstehen

Die Spiellogik für **0.8.2 – Equipment & Economy** arbeitet jetzt wie eine gemeinsame Kasse mit Lagerliste:

1. **Kaufen:** Das Equipment kommt ins Lager, und erst die bestätigte Buchung zieht Geld vom Event-Budget ab.
2. **Reservieren:** Besitz allein reicht nicht. Equipment muss für das Event zurückgelegt sein, bevor die Anforderung als bereit gilt.
3. **Verbrauchen oder verkaufen:** Nur nicht reservierte Mengen können das Lager verlassen.
4. **Wiederherstellen:** Nach einem Abbruch werden Lager, Buchungen, Budget und Bereitschaft gemeinsam aus dem Journal aufgebaut.

Der aktuelle HTML-Blueprint kann diese Schritte noch nicht auslösen. Die Regeln sind im Spielkern prüfbar; die Bedienoberfläche folgt bewusst erst nach dem vollständigen Event-Loop.

## 10. Was kann man noch nicht normal spielen?

Noch offen sind insbesondere:

- ein fertiger, mit der Runtime verbundener Desktop-/Web-/Game-Engine-Client (der HTML-Blueprint ist nur eine schreibgeschützte Designauswertung),
- vollständiger Event-Ablauf von Planung bis Abrechnung,
- bedienbarer Equipmentmarkt im Client,
- kompletter Clubbetrieb,
- Telegram-/Server-Synchronisation.

Diese Systeme werden auf dem jetzt getesteten Character-, Persistence- und Presentation-Kern aufgebaut.

## 11. Was kann ich jetzt sinnvoll prüfen?

Starte die HTML-Ansicht mit dem Befehl aus Abschnitt 0, prüfe den Leseweg und kopiere bei einem Problem den Prüfbericht. Erwarte dort noch keine speicherbare Eventplanung: So lässt sich der Prototyp testen, ohne ihn mit dem späteren Spiel zu verwechseln.

Die nächste Stufe ist **0.8.3 – vollständiger Event-Loop**. Bis zu ihrer Abnahme bleiben Client-, Netzwerk- und Clubentwicklung bewusst ausgesetzt.

## 12. Welche Beschreibung hilft mir weiter?

Wähle nach deiner Frage, nicht nach deinem Vorwissen:

- **Ich möchte Spielwelt, Ziele und Systeme vollständig verstehen:** Lies die [`Spielbeschreibung ohne Technik`](SPIELBESCHREIBUNG_OHNE_TECHNIK.md).
- **Ich möchte den vorhandenen Prototyp jetzt starten:** Bleibe in dieser Anleitung und beginne mit Abschnitt 0.
- **Ich möchte das Spiel programmieren oder anbinden:** Nutze die [`technische Spielbeschreibung`](SPIELBESCHREIBUNG_TECHNISCH.md).
- **Ich möchte wissen, was als Nächstes wirklich gebaut wird:** Öffne [`../TODO.md`](../TODO.md).

So bleibt klar getrennt, was die vollständige Spielvision beschreibt, was heute bereits bedienbar ist und was erst in einer späteren Entwicklungsstufe folgt.
