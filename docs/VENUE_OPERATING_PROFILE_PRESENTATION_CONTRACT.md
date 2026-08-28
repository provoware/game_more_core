# Venue-Betriebsprofil – Presentation-Vertrag

Iteration: `0.8.8-UX-VENUE-OPERATING-PROFILE-PRESENTATION-CONTRACT`

## Ziel

Den nächsten sichtbaren Venue-Slice so begrenzen, dass die Oberfläche ausschließlich bereits bestätigte Property-/Upgrade-Fakten erklärt und keine neue Gameplay- oder Datenautorität erzeugt.

## Autoritative Quelle

Das Betriebsprofil liest ausschließlich `property_upgrades.entries[*].effective_values` aus der bestehenden `build_property_upgrade_projection()`.

Erlaubte Werte sind exakt:

- `prestige`
- `audience_pull`
- `risk`
- `underground_factor`
- `utility`

## Verbindliche Grenzen

- keine zweite Berechnung derselben Werte im Browser;
- keine neuen Save-, Journal- oder Replay-Daten;
- keine Ableitung von Event-Verfügbarkeit, Kosten, Kapazität oder laufendem Ertrag;
- keine versteckten Bonusregeln aus sichtbaren Labels;
- sichtbare deutsche Bezeichnungen gehören in die vorhandene Text-/Presentation-Schicht, nicht in Domain- oder Runtime-Code;
- nicht besessene Locations dürfen kein eigenes Betriebsprofil vortäuschen.

## Kleinster freigegebener UI-Slice

Eine bereits vorhandene Property-/Location-Ansicht darf für besessene Orte die fünf bestätigten effektiven Werte read-only gruppiert anzeigen. Die Anzeige darf erklären und priorisieren, aber weder Werte verändern noch neue Wirkungen behaupten.

## Abnahme

Der Slice ist korrekt begrenzt, wenn Regressionen beweisen, dass die Projection weiterhin genau die fünf katalogisierten Werte liefert, der Presentation-Vertrag keine mechanischen Boni freigibt und keine neue Persistenz oder Browserautorität entsteht.
