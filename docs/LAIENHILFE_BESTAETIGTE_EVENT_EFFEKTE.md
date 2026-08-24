# Laienhilfe – bestätigte Ereignis-Effekte

## Was ist neu?

Nach einer **wirklich bestätigten** Spielaktion reagiert das Control Deck jetzt kurz sichtbar:

- eine bestätigte Straßenrunde hebt ihr Ergebnis kurz hervor,
- bestätigte Regeneration hebt das Recovery-Feedback und geänderte Ressourcen kurz hervor,
- eine bestätigte Krisenantwort hebt den Krisenbereich kurz hervor,
- geänderte HUD-Werte wie Energie, Stress, Ruf oder Budget bekommen einen kurzen Impuls.

## Wichtig: Die Animation entscheidet nichts

Die Oberfläche startet diese Rückmeldung erst **nachdem** der vorhandene Command-Pfad erfolgreich zurückgekehrt ist. Sie sendet keinen neuen Spielbefehl und berechnet keine Spielwerte selbst.

Wenn eine Aktion abgewiesen wird oder ein sicherer Replay keine sichtbare Änderung erzeugt, erfindet die Oberfläche auch keinen Erfolgseffekt.

## Farben

- **Grün:** günstige bestätigte Änderung, zum Beispiel mehr Energie oder Ruf beziehungsweise weniger Stress.
- **Orange/Rot:** belastende bestätigte Änderung, zum Beispiel mehr Stress oder weniger Energie/Ruf/Budget.
- **Blau:** neutrale bestätigte Rückmeldung, etwa ein Krisen- oder Recovery-Status ohne eindeutige Gut/Schlecht-Wertung.

## Weniger Bewegung

Ist im Browser oder Betriebssystem **reduzierte Bewegung** aktiviert, wird die Animation abgeschaltet. Stattdessen erscheint nur kurz ein statischer Rahmen. Spielinhalt und Information bleiben vollständig erhalten.

## Bewusst nicht enthalten

- keine Soundeffekte,
- keine Bildschirmerschütterung,
- kein blockierendes Overlay,
- keine neue Runtime-, Journal- oder Save-Logik,
- kein eigener Browser-Spielzustand.

## Sinnvolle spätere Erweiterung

Als eigener späterer Presentation-Slice kann ein **kompakter bestätigter Ereignis-Stempel** direkt an Timeline- oder Map-Einträgen erscheinen. Nutzen: Der Spieler erkennt noch schneller, welche sichtbare Veränderung gerade zu welchem bestätigten Ereignis gehört. Voraussetzung bleibt: Der Stempel darf ausschließlich aus bereits vorhandenen Runtime-/Projection-Signalen entstehen und niemals selbst Ereignisse erzeugen.
