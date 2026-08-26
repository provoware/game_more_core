# Ereignis-Timeline – einfache Erklärung

## Was zeigt die Timeline?

BUNKERFREQUENZ zeigt bestätigte wichtige Ereignisse in einer gemeinsamen Verlaufsliste. Die Timeline ist eine reine Leseschicht: Sie erklärt vorhandene Journal-Evidenz, erzeugt aber selbst niemals Spielzustand.

Die Timeline liest derzeit:

- Straßenbegegnungen,
- gelöste Eventkrisen,
- bestätigte Bezirks-Weltereignisse,
- bestätigte Bezirks-Folgeereignisse.

## Woher weiß die Timeline, was wirklich passiert ist?

Nicht aus dem Browser und nicht aus einer zweiten Story-Datei mit eigener Wahrheit. Die Reihenfolge kommt direkt aus dem vorhandenen Journal. Jeder bestätigte Journal-Eintrag besitzt eine fortlaufende `sequence`. Genau diese Nummer bestimmt die Reihenfolge.

## Wie wird eine Ursache sichtbar?

Die erste District-Micro-Story kann jetzt auch als Zusammenhang gelesen werden. Ein bestätigtes Folgeereignis darf in der Timeline zum Beispiel anzeigen:

`Folge von: Das Netz flackert`

Dieser Hinweis erscheint nur, wenn die vorhandene Projection im Journal einen bestätigten Parent findet und drei Dinge zusammenpassen:

1. `causation_id` und `parent_event_id` zeigen auf denselben Parent,
2. Parent und Folge gehören zum selben Bezirk,
3. der Parent liegt in der bestätigten Reihenfolge vor der Folge.

Fehlt der Parent oder passt der Bezirk nicht, wird **keine Ursache erfunden**. Das Folgeereignis kann weiterhin als bestätigtes Ereignis sichtbar bleiben, aber ohne behaupteten Kausalitätshinweis.

## Woher kommen die sichtbaren Texte?

Die Spiellogik enthält weiterhin keine sichtbaren Storytexte. Straßen-, Bezirks- und District-Folgetexte verwenden die vorhandenen deutschen Textkataloge. Krisen verwenden ebenfalls ihren bestehenden UI-Textkatalog.

Fehlt ein benötigter Text oder ist ein Record unvollständig, wird kein Ersatz erfunden. Der Eintrag erscheint dann nicht in der Timeline.

## Was ändert diese Stufe nicht?

Die Timeline löst kein Ereignis aus, verändert keine Werte, schreibt nichts ins Journal und sortiert die Geschichte nicht neu. Auch der Browser darf die Ursache nicht selbst erraten: Er zeigt ausschließlich das von der read-only Projection bestätigte Feld `caused_by` an.

Weitere District-Folgegeschichten gehören in eigene kleine Story-Slices. Diese Darstellung ist nur die gemeinsame, vorhandene Leseschicht dafür.
