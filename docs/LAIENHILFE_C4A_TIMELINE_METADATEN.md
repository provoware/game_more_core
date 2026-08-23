# Laienhilfe – Warum die Ereignis-Timeline Metadaten filtert

## Worum geht es?

Die Ereignis-Timeline erzählt nur Dinge, die bereits im bestätigten Spieljournal stehen. Neben Titel und Text enthält ein Eintrag kleine Zusatzangaben, zum Beispiel den gewählten Straßen-Ansatz, Bezirksänderungen oder die Zielphase nach einer Krise.

Diese Zusatzangaben dürfen die spätere Browseranzeige nicht mit unerwarteten Datenformen überraschen. Deshalb lässt die Timeline ab 0.8.7-C4A-Härtung nur die erwarteten einfachen Anzeigeinformationen durch.

## Was wird jetzt geprüft?

- Ein Straßen-Ansatz muss ein nichtleerer Text sein. Ist er beschädigt oder hat eine falsche Datenform, zeigt die Projection den sicheren Standard `balanced`.
- Bezirksänderungen enthalten nur die vier bekannten Werte `heat`, `prestige`, `police_pressure` und `scene_activity`.
- Für Bezirksänderungen werden nur echte Ganzzahlen übernommen. Wahr/Falsch, Textwerte oder unbekannte Zusatzfelder werden verworfen.
- Eine Krisen-Zielphase wird nur übernommen, wenn sie ein nichtleerer Text ist; sonst bleibt sie leer (`null`).

## Was ändert sich dadurch nicht?

- Keine Gameplaywerte werden neu berechnet.
- Kein Journalrecord wird verändert oder gelöscht.
- Es entsteht keine zweite Timeline oder zweite Persistenz.
- Der Browser bekommt dadurch keine neue Schreib- oder Regelautorität.
- C4B, also die sichtbare Timeline im Control Deck, bleibt der nächste eigene Presentation-Schritt.

## Warum ist das sinnvoll?

Bevor Journaldaten sichtbar im Control Deck erscheinen, ist die Anzeigegrenze damit klarer: Die UI erhält nur erwartete primitive Metadaten und kann beschädigte oder manipulierte optionale Zusatzwerte nicht versehentlich als komplexe Browserdaten übernehmen.

## Spätere sinnvolle Erweiterung

Ein rein lesender Entwicklerhinweis könnte später zählen, wie viele optionale Metadaten beim Projizieren verworfen wurden. Er darf dabei weder Ersatzdaten erfinden noch den Journalinhalt verändern.
