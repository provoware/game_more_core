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
4. Der ursprüngliche Vertrag `0.8.3-c1` besaß noch keine Venue-Evidence. Der Folgevertrag `0.8.8-venue-evidence1` übernimmt jetzt die bestätigte Evidence in denselben atomaren Settlement-Commit; die historische Form bleibt lesbar.

## Warum der Authority-Bridge grundsätzlich GO ist

Die Identität muss nicht neu erfunden werden: Event, Besitz und Ausbau teilen bereits denselben fachlichen Schlüssel `location_id`. Ein späterer Authority-Slice darf deshalb nur die vorhandenen Zustände lesen, die Übereinstimmung beweisen und diesen Beweis in das Settlement-Receipt übernehmen.

Das ist eine Ergänzung der bestehenden Settlement-Evidence, keine neue Wirkungsarchitektur.

## Gemeinsame Wertautorität

Die effektiven Ortswerte werden jetzt durch `domain.property_upgrade.effective_venue_values(...)` deterministisch und read-only aus City-Map-Basiswerten, bestätigten Upgrade-Leveln und dem vorhandenen Upgrade-Katalog berechnet. Die bestehende `presentation/property_upgrade_projection.py` verwendet genau diese Domain-Funktion und besitzt keine eigene Kopie der Wertformel mehr.

Damit ist das frühere Vor-Gate erfüllt: Eine spätere Venue-Evidence darf dieselbe gemeinsame Wertautorität verwenden, ohne aus der Application-Schicht die Presentation-Schicht importieren oder die Berechnung der effektiven Ortswerte im Settlement duplizieren zu müssen. Die Werte bleiben auf 0–100 begrenzt; es wurde weder ein Settlement-Effekt noch eine Balanceänderung eingeführt.

## Read-only Evidence-Resolver

`application.venue_settlement_evidence.resolve_owned_venue_evidence(...)` löst die bereits freigegebene Kette jetzt erstmals als reine Application-Abfrage auf. Der Resolver liest ausschließlich den Event-Ort, den bestätigten Besitz, den bestätigten Upgrade-State sowie City-Map- und Upgrade-Katalog und verwendet für den effektiven Wert die gemeinsame Domain-Autorität.

Für einen eigenen Event-Ort liefert er eine kleine, versionierte Evidence-Struktur mit `location_id`, `owner_character_id`, bestätigtem `audience_pull` sowie den gelesenen Property-/Upgrade-Revisionen. Ein nicht eigener oder einem anderen Character gehörender Ort liefert keine Evidence. Katalog- oder Upgrade-Widersprüche schlagen fail-closed fehl.

Der Resolver selbst bleibt read-only. Der bestehende Settlement-Service übernimmt sein Ergebnis jetzt explizit in `SettlementState`, Journal und Save; er verändert damit keinen Effekt. Details: [Venue-Evidence-Vertrag](VENUE_SETTLEMENT_EVIDENCE_CONTRACT.md).

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

## Versionierte Receipt-Brücke

Der `SettlementState` bleibt `additionalProperties: false`. Der neue Vertrag benötigt das explizite Feld `venue_evidence`; alte `0.8.3-c1`-Belege dürfen dieses Feld weiterhin nicht besitzen. Es gibt kein unsichtbares Zusatzfeld und keine Umdeutung alter Saves.

Settlement speichert die Evidence jetzt versioniert; Retry und Crash-Recovery erhalten denselben Beleg. Recovery bindet ihn an den damaligen Event-Ort und bestätigten Besitz-/Ausbauzustand, ohne neue Katalogstände rückwirkend anzuwenden. Eine zweite Publikumskraft-Berechnung, ein Application→Presentation-Import oder bereits jetzt ein Publikumskraft-Bonus bleibt NO-GO.

## Ergebnis

**Architektur-GO für Evidence-Plumbing, Mechanik-NO-GO bleibt bestehen; gemeinsame Wertautorität und read-only Resolver sind erfüllt.**

Die versionierte Aufnahme ist lokal umgesetzt und regressionsgesichert. Als nächster Schritt kann der gespeicherte Beleg read-only sichtbar werden. Über eine begrenzte Spielwirkung entscheidet erst ein weiterer, separat geprüfter Balancevertrag; Remote-Gates und Releasefreigabe bleiben getrennt.
