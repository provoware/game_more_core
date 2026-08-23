# Timeline filtern – einfach erklärt

Die Timeline zeigt nur Ereignisse, die das Spiel bereits bestätigt hat. Der neue Filter verändert **nicht**, was passiert ist.

## Die vier Filter

- **ALLE** – zeigt die komplette bestätigte Timeline.
- **STRASSE** – zeigt nur bestätigte Straßenereignisse.
- **KRISE** – zeigt nur bestätigte Krisenereignisse.
- **BEZIRK** – zeigt nur bestätigte Bezirksereignisse.

## Was passiert beim Filtern?

Der Browser blendet nicht passende Einträge nur vorübergehend aus. Er erstellt keine neuen Ereignisse und löscht nichts.

Die Reihenfolge bleibt exakt so, wie sie von der Runtime geliefert wurde. Es wird weder neu sortiert noch umgedreht.

## Wird mein Filter gespeichert?

Nein. Der Filter ist nur lokaler Anzeigezustand im geöffneten Browserfenster. Er landet weder im Spielstand noch im Journal und wird auch nicht in Local Storage oder Session Storage abgelegt.

## Warum ist das wichtig?

Die Timeline bleibt damit eine verlässliche Chronik der bestätigten Spielereignisse. Der Filter hilft nur beim Lesen – er bekommt keine Gameplay- oder Story-Autorität.

## Wenn ein Filter nichts zeigt

Dann gibt es in der aktuell bestätigten Timeline einfach keinen passenden Eintrag. Mit **ALLE** siehst du wieder die vollständige Chronik.
