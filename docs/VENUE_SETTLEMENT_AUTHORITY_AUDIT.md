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

## Neu bestätigte Layering-Grenze

Der bestätigte effektive Ortswert wird heute in `presentation/property_upgrade_projection.py` aus City-Map-Basiswerten und bestätigten Upgrade-Leveln abgeleitet. `SettlementService` liegt dagegen in der Application-Schicht. Deshalb wäre es **kein** zulässiger Shortcut, die Presentation-Projection aus dem Settlement zu importieren oder deren Wertformel dort zu kopieren.

Vor einer echten Venue-Evidence-Implementierung muss die bereits vorhandene effektive Wertableitung an eine gemeinsam nutzbare, nicht darstellungsgebundene Autoritätsstelle verschoben oder als kleiner read-only Domain/Application-Resolver bereitgestellt werden. Presentation und Settlement müssen anschließend dieselbe Funktion verwenden.

Damit bleibt der Evidence-Bridge fachlich GO, aber ihre Implementierungsreihenfolge ist jetzt präziser: **zuerst gemeinsame Wertautorität, dann Receipt-Evidence.**

## Harte Grenzen des nächsten Slices

Der nächste Slice darf ausschließlich:

- `event.location.location_id` lesen,
- für genau diesen Ort bestätigten Besitz des abrechnenden Charakters verlangen,
- den bestätigten Upgrade-Zustand desselben Orts als Wertquelle referenzieren,
- dieselbe gemeinsame effektive Wertautorität wie die bestehende Projection verwenden,
- `location_id`, Ownership-Bezug und den bestätigten `audience_pull`-Wert als read-only Evidence im Settlement-Receipt festhalten,
- Replay/Recovery gegen dieselbe gespeicherte Evidence prüfen.

Er darf **nicht**:

- Budget, Reputation, Stress, Heat oder Stability verändern,
- `audience_pull` multiplizieren oder in eine Auszahlung umrechnen,
- einen neuen Property-/Upgrade-State einführen,
- einen Browserwert als Autorität akzeptieren,
- aus der Application-Schicht die Presentation-Schicht importieren,
- die Berechnung der effektiven Ortswerte im Settlement duplizieren,
- fehlenden Besitz oder fehlende Upgrade-Evidence still durch Defaultwerte ersetzen.

## Noch offene Implementierungsarbeit

Der aktuelle `SettlementState` ist `additionalProperties: false` und besitzt kein Venue-Evidence-Feld. Ein echter Authority-Bridge-Slice muss deshalb den Settlement-Vertrag explizit und versioniert erweitern; ein unsichtbares Zusatzfeld wäre kein zulässiger Shortcut.

Ebenso speichert `PropertyUpgradeState` die Upgrade-Level, nicht die projizierten `effective_values` direkt. Der bestehende effektive Wert wird aktuell in der Presentation-Projection abgeleitet. Vor der Settlement-Erweiterung muss diese Ableitung deshalb so entkoppelt werden, dass Application und Presentation dieselbe read-only Wertautorität verwenden können. Eine zweite Publikumskraft-Berechnung oder ein Application→Presentation-Import bleibt NO-GO.

## Ergebnis

**Architektur-GO für Evidence-Plumbing, Mechanik-NO-GO bleibt bestehen; die gemeinsame Wertautorität ist jetzt explizites Vor-Gate.**

Damit ist präzise geklärt, was als nächster minimaler Implementierungsschritt erlaubt ist: die vorhandene effektive Wertableitung ohne Verhaltensänderung aus der Presentation-Abhängigkeit lösen. Erst danach dürfen `location_id`-Autoritäten im Settlement verbunden und als Evidence bewiesen werden; ein weiterer, separat geprüfter Slice entscheidet über eine begrenzte Spielwirkung.