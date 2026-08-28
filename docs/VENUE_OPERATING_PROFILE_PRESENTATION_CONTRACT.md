# Venue-Betriebsprofil – Presentation-Vertrag

Iteration: `0.8.8-UX-VENUE-OPERATING-PROFILE-READONLY`

## Ziel

Den sichtbaren Venue-Slice so begrenzen, dass die Oberfläche ausschließlich bereits bestätigte Property-/Upgrade-Fakten erklärt und keine neue Gameplay- oder Datenautorität erzeugt.

## Autoritative Quelle

Das Betriebsprofil liest ausschließlich `property_upgrades.entries[*].effective_values` aus der bestehenden `build_property_upgrade_projection()`.

Diese per Eintrag sichtbaren `effective_values` werden nur für besessene Locations ausgegeben. Nicht besessene Locations behalten ihre Basiswerte ausschließlich in der bereits bestehenden internen `effective_values_by_location`-Map, damit District-/Map-Projections weiterhin dieselbe Quelle nutzen können, ohne daraus ein eigenes Betriebsprofil vorzutäuschen.

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

Der Slice ist korrekt begrenzt, wenn Regressionen beweisen, dass die Projection für besessene Locations weiterhin genau die fünf katalogisierten Werte liefert, nicht besessene Locations in `entries[*].effective_values` kein Betriebsprofil erhalten, die interne Map-Grundlage unverändert bleibt, der Presentation-Vertrag keine mechanischen Boni freigibt und keine neue Persistenz oder Browserautorität entsteht.
