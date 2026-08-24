# Laienhilfe – bestätigte Crew-Marke im HUD

## Was wurde verbessert?

Deine kleine Crew-Marke oben im Live-HUD zeigt jetzt zuverlässig den **zuletzt bestätigten** Stand.

Wenn du Logo/Fahne, Symbol, Farben oder Kurzmarke änderst und speicherst, kann der Editor während der Server-Antwort weiter fokussiert bleiben. Trotzdem wird die HUD-Marke direkt aus der bestätigten Spielprojektion aktualisiert.

## Wichtig: Vorschau und bestätigter Stand sind getrennt

- Änderungen im Editor sind zunächst nur Vorschau.
- Erst ein erfolgreich bestätigtes Speichern macht sie zum gültigen Crew-Stand.
- Die HUD-Marke übernimmt nur diesen bestätigten Stand.
- Ein abgewiesener Save verändert die HUD-Marke nicht.
- Dafür gibt es keinen zusätzlichen Serverabruf und keinen zweiten Avatar-Speicher.

## Warum ist das sinnvoll?

Vorher konnte ein seltener Ablauf entstehen: Du speicherst und klickst während der Antwort wieder in den Editor. Der Editor wurde zum Schutz deiner Eingabe nicht neu aufgebaut – dadurch konnte auch die HUD-Kopie bis zum nächsten Rendern alt bleiben.

Jetzt wird zuerst die bestätigte Crew-Projektion ins HUD gespiegelt. Danach darf der Editor-Fokusschutz wie bisher greifen.

## Spätere sinnvolle Erweiterung

Die gleiche bestätigte Crew-Marke kann später read-only auf der Berlin-Karte bei eigenem Eigentum erscheinen. Nutzen: stärkere Spielidentität ohne neue Avatar- oder Besitzlogik.
