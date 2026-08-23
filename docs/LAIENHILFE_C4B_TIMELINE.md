# C4B – Ereignis-Timeline im Control Deck

## Was ist neu?

Im Control Deck gibt es jetzt den Bereich **„Was bisher passiert ist“**. Dort erscheinen die letzten bestätigten Ereignisse aus drei Bereichen:

- Straße,
- Krisen,
- Bezirks-/Welt-Ereignisse.

Die Timeline ist eine **Anzeige**, kein neuer Spielmechanismus. Sie verändert keine Werte und kann nichts im Spielstand speichern.

## Woher kommen die Einträge?

Die Runtime liest das bereits vorhandene Journal. C4A wandelt passende bestätigte Journal-Einträge in verständliche Titel und Texte um. C4B zeigt exakt diese fertige Liste an.

Wichtig:

- Der Browser würfelt nichts neu.
- Der Browser sortiert die Geschichte nicht neu.
- Der Browser erfindet keine fehlenden Texte.
- Die Reihenfolge stammt aus dem bestätigten Journal.
- Maximal die letzten 12 bestätigten Einträge werden angezeigt.

## Bedienung

Oben in der Schnellnavigation gibt es **TIMELINE**. Ein Klick springt direkt zur Chronik. Die Liste kann normal mit Tastatur, Browser-Zoom und Screenreader gelesen werden.

Der Status oberhalb der Liste meldet, wie viele bestätigte Ereignisse sichtbar sind. Ist die Chronik leer, bedeutet das nur, dass noch kein passendes bestätigtes Ereignis im Journal liegt.

## Was passiert bei einer Störung?

Kann die lokale Runtime kurzzeitig nicht gelesen werden, bleibt das Gameplay unberührt. Die Timeline zeigt dann nur eine verständliche Statusmeldung. Sie besitzt keinen eigenen Save- oder Recovery-Pfad.

## Bewusste Grenze

C4B fügt keine Filter, keine neue Story-Autorität, keine Cadence/Cooldown-Regeln und keine Gameplay-Effekte hinzu. Solche Erweiterungen müssen später separat geprüft werden.
