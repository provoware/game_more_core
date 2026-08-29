# Venue→Settlement Authority Audit

## Entscheidung

**GO für einen rein evidenzbasierten Authority-Bridge-Folgeslice; weiterhin NO-GO für jeden Publikumskraft-Bonus.**

Der kleinste saubere Pfad kann vorhandene Autoritäten wiederverwenden:

`event.location.location_id → property_state.owned[location_id] → property_upgrades.properties[location_id] → Settlement-Receipt-Evidence`

Es wird dafür kein zweiter Property-State, keine Venue-Bonusengine und keine Browser-Autorität benötigt.

## Bestätigte Autoritätskette

1. `EventState.location.location_id` ist bereits ein kanonischer, persistierter Ortsbezug des Events.
2. `PropertyState.owned` ist nach `location_id` adressierbar und enthält den bestätigten `owner_character_id`.
3. `PropertyUpgradeState.properties` ist ebenfalls nach `location_id` adressierbar. Der Upgrade-Vertrag katalogisiert `audience_pull` und begrenzt projizierte Ortswerte auf 0–100.
4. Der aktuelle Settlement-Vertrag nimmt `properties` und `property_upgrades` noch nicht als State-Blöcke an und das Receipt besitzt noch keine Venue-Evidence. Genau diese fehlende Brücke ist damit klar abgegrenzt.

## Warum der Authority-Bridge grundsätzlich GO ist

Die Identität muss nicht neu erfunden werden: Event, Besitz und Ausbau teilen bereits denselben fachlichen Schlüssel `location_id`. Ein späterer Authority-Slice darf deshalb nur die vorhandenen Zustände lesen, die Übereinstimmung beweisen und diesen Beweis in das Settlement-Receipt übernehmen.

Das ist eine Ergänzung der bestehenden Settlement-Evidence, keine neue Wirkungsarchitektur.

## Gemeinsame Wertautorität

Die effektiven Ortswerte werden jetzt durch `domain.property_upgrade.effective_venue_values(...)` deterministisch und read-only aus City-Map-Basiswerten, bestätigten Upgrade-Leveln und dem vorhandenen Upgrade-Katalog berechnet. Die bestehende `presentation/property_upgrade_projection.py` verwendet genau diese Domain-Funktion und besitzt keine eigene Kopie der Wertformel mehr.

Damit ist das frühere Vor-Gate erfüllt: Eine spätere Venue-Evidence darf dieselbe gemeinsame Wertautorität verwenden, ohne aus der Application-Schicht die Presentation-Schicht importieren oder die Berechnung der effektiven Ortswerte im Settlement duplizieren zu müssen. Die Werte bleiben auf 0–100 begrenzt; es wurde weder ein Settlement-Effekt noch eine Balanceänderung eingeführt.

## Read-only Evidence-Resolver

`application.venue_settlement_evidence.resolve_owned_venue_evidence(...)` löst die bereits freigegebene Kette jetzt erstmals als reine Application-Abfrage auf. Der Resolver liest ausschließlich den Event-Ort, den bestätigten Besitz, den bestätigten Upgrade-State sowie City-Map- und Upgrade-Katalog und verwendet für den effektiven Wert die gemeinsame Domain-Autorität.

Für einen eigenen Event-Ort liefert er eine kleine, versionierte Evidence-Struktur mit `location_id`, `owner_character_id`, bestätigtem `audience_pull` sowie den gelesenen Property-/Upgrade-Revisionen. Ein nicht eigener oder einem anderen Character gehörender Ort liefert keine Evidence. Katalog- oder Upgrade-Widersprüche schlagen fail-closed fehl.

Wichtig: Der Resolver schreibt noch **nichts** in `SettlementState`, Journal oder Save und verändert keinen Effekt. Damit ist nur die lesende Autoritätsauflösung umgesetzt; die persistierte Receipt-Brücke bleibt ein eigener Vertragsschritt.

## Harte Grenzen des nächsten Slices

Der nächste Slice darf ausschließlich:

- `event.location.location_id` lesen,
- für genau diesen Ort bestätigten Besitz des abrechnenden Charakters verlangen,
- den bestätigten Upgrade-Zustand desselben Orts als Wertquelle referenzieren,
- dieselbe gemeinsame effektive Wertautorität wie die bestehende Projection verwenden,
- die bereits aufgelöste Evidence explizit und versioniert in den Settlement-Vertrag übernehmen,
- Replay/Recovery gegen dieselbe gespeicherte Evidence prüfen.

Er darf **nicht**:

- Budget, Reputation, Stress, Heat oder Stability verändern,
- `audience_pull` multiplizieren oder in eine Auszahlung umrechnen,
- einen neuen Property-/Upgrade-State einführen,
- einen Browserwert als Autorität akzeptieren,
- aus der Application-Schicht die Presentation-Schicht importieren,
- die Berechnung der effektiven Ortswerte im Settlement duplizieren,
- fehlenden Besitz oder fehlende Upgrade-Evidence still durch erfundene Werte ersetzen.

## Noch offene Implementierungsarbeit

Der aktuelle `SettlementState` ist `additionalProperties: false` und besitzt kein Venue-Evidence-Feld. Ein echter Receipt-Bridge-Slice muss deshalb den Settlement-Vertrag explizit und versioniert erweitern; ein unsichtbares Zusatzfeld wäre kein zulässiger Shortcut.

Die gemeinsame Wertautorität und die read-only Auflösung sind nun vorhanden. Offen bleibt damit bewusst der nächste getrennte Vertragsschritt: Settlement muss diese bestätigte Evidence versioniert aufnehmen und Replay/Recovery dafür beweisen. Eine zweite Publikumskraft-Berechnung, ein Application→Presentation-Import oder bereits jetzt ein Publikumskraft-Bonus bleibt NO-GO.

## Ergebnis

**Architektur-GO für Evidence-Plumbing, Mechanik-NO-GO bleibt bestehen; gemeinsame Wertautorität und read-only Resolver sind erfüllt.**

Damit ist der nächste minimale Implementierungsschritt klar: die versionierte Aufnahme der bereits bestätigten Venue-Evidence in den Settlement-Vertrag. Erst danach darf ein weiterer, separat geprüfter Slice über eine begrenzte Spielwirkung entscheiden.