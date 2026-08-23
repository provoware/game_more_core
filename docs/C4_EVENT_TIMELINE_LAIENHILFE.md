# Ereignis-Timeline – einfache Erklärung

## Was wurde jetzt vorbereitet?

BUNKERFREQUENZ kann bestätigte wichtige Ereignisse künftig in einer gemeinsamen Verlaufsliste anzeigen. Diese erste C4-Stufe baut dafür bewusst nur die sichere Leseschicht.

Die Timeline darf drei vorhandene Ereignisarten lesen:

- Straßenbegegnungen,
- gelöste Eventkrisen,
- bestätigte Bezirks-Weltereignisse.

## Woher weiß die Timeline, was wirklich passiert ist?

Nicht aus dem Browser und nicht aus einer zweiten Story-Datei mit eigener Wahrheit. Die Reihenfolge kommt direkt aus dem vorhandenen Journal. Jeder bestätigte Journal-Eintrag besitzt eine fortlaufende `sequence`. Genau diese Nummer bestimmt die Reihenfolge.

## Woher kommen die sichtbaren Texte?

Die Spiellogik enthält weiterhin keine sichtbaren Storytexte. Straßen- und Bezirksereignisse verwenden ihre vorhandenen deutschen Textkataloge. Für die bereits existierenden Krisen-Schlüssel gibt es nun ebenfalls einen deutschen UI-Textkatalog.

Fehlt ein benötigter Text oder ist ein Record unvollständig, wird kein Ersatz erfunden. Der Eintrag erscheint dann nicht in der Timeline.

## Was kann diese Stufe noch nicht?

Die Projection ist fertig, aber noch nicht an das sichtbare Control Deck angeschlossen. Das folgt als nächster kleiner C4-Schritt. Dadurch bleibt dieser Patch leicht prüfbar: erst sichere Datenquelle und Reihenfolge, danach Darstellung.

## Wichtig

Die Timeline ist rein lesend. Sie kann keine Werte ändern, kein Ereignis auslösen, nichts speichern und keine neue Reihenfolge erzeugen.
