# Laienhilfe – Was bedeutet C5 und was kommt mit 0.8.8?

## Was ist jetzt wirklich fertig?

Die sichtbare Ereignis-Timeline ist fertig und sicher gemergt. District-Weltereignisse erscheinen nicht mehr bei jedem passenden Settlement, sondern besitzen einen globalen Abstand von 24 Stunden bestätigter Spielweltzeit.

Wichtig: Die Uhr des Computers entscheidet darüber nicht. Nur die im Spiel bestätigte Event-Zeit darf den Cooldown fortschreiben. Dadurch entstehen nach Reload, Neustart oder verstellter Systemuhr keine zusätzlichen Welt-Ereignisse.

## Warum bleibt die Produktversion 0.8.4-alpha.1?

`0.8.4-alpha.1` ist die letzte ausdrücklich freigegebene Produkt-/ZIP-Baseline. C4B und C5 sind neuere, validierte Entwicklungsstände auf `main`, aber noch kein neuer Produktrelease.

## Was ist 0.8.8-A?

Als nächster kleiner Baustein bekommt jede Crew eine eigene Identität als Logo oder Fahne. Dafür soll nicht einfach irgendeine Bilddatei in den Spielstand kopiert werden. Stattdessen wird eine kleine, klar validierbare Beschreibung gespeichert, zum Beispiel Symbol, Stil und Farben. Aus diesen Daten zeichnet die Oberfläche das Logo oder die Fahne.

Das hat drei Vorteile:

- alte Spielstände bleiben leichter kompatibel,
- spätere Synchronisation kann dieselben kleinen Daten an alle Spieler verteilen,
- Bilder können nicht unkontrolliert den Save oder Sync aufblähen.

## Was folgt danach?

Geplant sind normale Scene-Jobs zum Geldverdienen, der wiederholbar arbeitende "Secret Best Friend"-Assistent, Bank/Sparen/Anlagen, eine kompaktere Control-Deck-Arbeitsansicht und eine deutlich bessere zoombare Berlin-Karte. Diese Systeme werden getrennt umgesetzt, damit Fehler in Economy, UI oder Sync nicht gleichzeitig mehrere Bereiche beschädigen.
