# A4-Laienspielhilfe – District-Events sicher verstehen

## Was wurde verbessert?

District-Events kommen aus einem festen Katalog. Jeder Eintrag enthält einen Namen, eine Gewichtung, Voraussetzungen und kleine Auswirkungen auf Bezirkswerte.

Ab dieser Qualitätsiteration wird der **gesamte Katalog bereits beim Start der District-Event-Runtime geprüft**. Ein beschädigter oder falsch bearbeiteter Eintrag wird nicht erst mitten im Spiel entdeckt.

## Was wird geprüft?

- jede Event-ID muss eindeutig sein,
- Titel- und Textschlüssel dürfen nicht leer sein,
- alle Gewichte müssen positive Ganzzahlen sein und zusammen zum Katalogvertrag passen,
- Voraussetzungen dürfen nur bekannte Bezirkswerte benutzen,
- Effekte müssen exakt die bekannten Bezirkswerte enthalten,
- Effekte müssen innerhalb der erlaubten kleinen Grenzen liegen,
- District-Event- und District-State-Vertrag müssen zusammenpassen.

## Was bedeutet das für Spieler?

Wenn der mitgelieferte Katalog unverändert ist, muss nichts eingestellt werden. Die Prüfung läuft automatisch im Hintergrund der Runtime.

Wird der Katalog später von Entwicklern oder Mods falsch verändert, soll das Spiel **früh und verständlich abbrechen**, statt erst nach einem Trigger einen teilweise ausgeführten oder schwer nachvollziehbaren Zustand zu erzeugen.

## Was ändert sich nicht?

- keine neuen Events,
- keine stärkeren oder schwächeren Effekte,
- keine neue Zufallslogik,
- kein Browser darf Events aktivieren oder Effektwerte liefern,
- bestehende Saves und Journal-Ereignisse werden nicht umgeschrieben.

## Merksatz

**Fehlerhafte Event-Daten werden vor dem ersten District-Event gestoppt – nicht mitten im Spiel.**
