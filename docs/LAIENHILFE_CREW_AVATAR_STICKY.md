# Crew-Avatar – sichtbare Vorschau ohne Überlagerung

## Was wurde verbessert?

Die Crew-Vorschau bleibt beim Bearbeiten des Profils weiterhin sichtbar. In mittleren Fensterbreiten zwischen 721 und 860 Pixeln berücksichtigt sie jetzt aber die zweizeilige Statusleiste und die darunterliegende Schnellnavigation.

Dadurch klebt die Vorschau nicht mehr unter HUD oder Navigation fest, sondern beginnt mit ausreichendem Abstand darunter.

## Verhalten nach Fensterbreite

- **Breit:** Die Vorschau bleibt seitlich sticky und nutzt den normalen Abstand.
- **721–860 px:** Der Abstand wird aus der vorhandenen HUD-Höhe abgeleitet und um Platz für die Schnellnavigation ergänzt.
- **Bis 720 px:** Sticky wird weiterhin vollständig abgeschaltet; die Vorschau steht normal im Dokumentfluss und kann keine Eingabefelder verdecken.

## Was wurde nicht verändert?

Keine Crew-Daten, keine Profilwerte, keine Speicherung, keine API-Kommandos und keine Spielregeln wurden geändert. Es handelt sich ausschließlich um eine responsive Darstellungsreparatur.

## Spätere sinnvolle Erweiterung

Die bestätigte Crew-Marke kann als nächster Identitäts-Slice read-only in den vorhandenen Berlin-Map-Details wiederverwendet werden. Dadurch wird Besitz stärker als eigene Crew-Fläche erkennbar, ohne eine zweite Avatar- oder Kartenlogik einzuführen.
