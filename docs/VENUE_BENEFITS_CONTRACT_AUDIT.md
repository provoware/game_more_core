# Venue Benefits / Betriebsprofil – Contract Audit

Iteration: `0.8.8-GAMEPLAY-VENUE-BENEFITS-CONTRACT-AUDIT`

## Ziel

Prüfen, welcher kleine Venue-Nutzen auf bestehenden Autoritäten aufbauen kann, ohne eine zweite Property-, Event- oder Bonusengine zu erzeugen.

## Geprüfte Autoritäten

- `PROPERTY_MANIFEST.json`: bestätigtes Eigentum; kein Verkauf, keine Miete und kein laufender Ertrag.
- `PROPERTY_UPGRADE_MANIFEST.json`: katalogisierte Ausbaulevel und fünf bestätigte Location-Werte (`prestige`, `audience_pull`, `risk`, `underground_factor`, `utility`). Die Projection darf diese Werte aus bestätigten Upgrades ableiten; `gameplay_event_rules_changed` bleibt ausdrücklich `false`.
- `EventExecutionService.availability()`: Event-Verfügbarkeit wird ausschließlich aus `EventState`, Aktionsphase und bestehenden Event-Voraussetzungen ermittelt. Property-/Upgrade-Zustand ist dort keine Autorität.

## Drei Nutzenmodelle

| Modell | Entscheidung | Begründung |
|---|---|---|
| Event-Verfügbarkeit durch Besitz/Ausbau verändern | **NO-GO** | Der aktuelle Availability-Vertrag kennt keinen Property-/Upgrade-Zustand. Ein stiller Zusatz im Browser oder in der Projection würde die Event-Autorität umgehen. |
| Kosten-, Kapazitäts- oder laufender Ertragsbonus | **NO-GO** | Dafür existiert kein katalogisierter Fachvertrag. `PROPERTY_MANIFEST` schließt Miete/Ertrag aus; die Upgrade-Werte sind noch keine Economy-/Settlement-Regeln. |
| Read-only Betriebsprofil aus bestätigten Besitz-/Ausbauwerten | **GO für nächsten kleinen Slice** | Besitz und effektive Location-Werte sind bereits bestätigt und read-only projizierbar. Eine Anzeige kann diese Fakten erklären, ohne Save, Journal, Replay oder Gameplaywerte zu verändern. |

## Save / Journal / Replay

Für den freigegebenen read-only Betriebsprofil-Slice ist **keine** neue Persistenz nötig: Die Anzeige muss ausschließlich aus dem bereits bestätigten `properties`-/`property_upgrades`-State und deren vorhandenen Projections entstehen. Keine neuen Journaltypen, keine Systemzeit, keine Browserautorität.

Ein späterer mechanischer Venue-Bonus benötigt dagegen vor Implementierung einen eigenen katalogisierten Domain-/Application-Vertrag einschließlich Zuständigkeit, Journal-/Replay-Semantik und gezielter Regression.

## Ergebnis

**GO ausschließlich für ein read-only Betriebsprofil. NO-GO für mechanische Event-, Kosten-, Kapazitäts- oder Ertragsboni im aktuellen Vertrag.**

Damit bleibt `POOL-PROPERTY-003` fachlich offen, aber der nächste sichere Produkt-Slice ist klar begrenzt: bestätigte Venue-Werte sichtbar erklären statt neue Werte zu erfinden.
