# Venue→Settlement Authority Audit

## Entscheidung

**GO für einen rein evidenzbasierten Authority-Bridge-Folgeslice; weiterhin NO-GO für jeden Publikumskraft-Bonus.** Die freigegebene Evidence-Brücke ist in der lokalen Entwicklungsstufe jetzt einschließlich versioniertem Receipt, Replay/Recovery und lesender Spielanzeige umgesetzt.

Die bestätigte Kette bleibt:

`event.location.location_id → property_state.owned[location_id] → property_upgrades.properties[location_id] → Settlement-Receipt-Evidence`

Es gibt keine Venue-Bonusengine und keinen zweiten Property-State.

## Gemeinsame Wertautorität

`domain.property_upgrade.effective_venue_values(...)` berechnet dieselben effektiven Ortswerte für Betriebsprofil und Evidence. Die Application-Schicht darf weiterhin nicht die Presentation-Schicht importieren oder die Berechnung der effektiven Ortswerte im Settlement duplizieren. Der vorhandene Resolver `application.venue_settlement_evidence.resolve_owned_venue_evidence(...)` bleibt die einzige lesende Evidence-Auflösung.

## Explizite Vertragsversion statt verstecktem Zusatzfeld

Der neue Settlement-Vertrag `0.8.8-venue-evidence-v1` verlangt das Feld `venue_evidence` mit genau einem Objekt oder `null`. Der alte Vertrag `0.8.3-c1` bleibt ohne dieses Feld lesbar und exakt serialisierbar. Das Schema bleibt `additionalProperties: false`. Ein Legacy-Receipt mit heimlich hinzugefügtem Evidence-Feld wird abgewiesen.

Erforderliche State-Blöcke bleiben Event, Economy und Character. Besitz und Ausbau werden optional gelesen. Für einen eigenen Event-Ort sind die Quellverträge erforderlich; fehlender Besitz oder ein fremder Besitzer ergeben `null`. Ein eigener Ort ohne bisherigen Ausbau verwendet die bestätigten Basiswerte und Ausbau-Revision 0. Widersprüchliche Quellen werden vor jedem Commit abgewiesen.

## Gespeicherter Nachweis

Das Evidence-Objekt enthält ausschließlich:

- `schema_version: 1`, `location_id`, `owner_character_id`,
- `audience_pull` als Ganzzahl in 0–100,
- `city_map_manifest_version`, `property_upgrade_manifest_version`,
- `property_revision`, `property_upgrade_revision`.

Der Besitzer muss zum abrechnenden Character gehören. Der Ortsbezug stammt vom bestätigten Event; zusätzliche Client-Fachwerte werden nicht akzeptiert. Der Browser zeigt nur den gespeicherten Nachweis an.

## Atomarer Commit, Replay und Recovery

Evidence ist Bestandteil desselben `event.completed`-Payloads und desselben atomaren Commits wie das vorhandene Receipt. Neue Journaltypen oder eine zweite Speicherung entstehen nicht.

Beim Replay werden Event-Ort, Character, damaliger Besitz, Besitzrevision, Ausbaurevision und Ausbauvertragsversion gegen die chronologisch rekonstruierten Zustände geprüft. Der gespeicherte Wert wird nicht mit heutigen Manifestdaten neu berechnet. Damit bleiben historische Abrechnungen nach späteren Katalogänderungen unverändert.

Legacy-Replay und ein erneuter Abschluss desselben alten Commands bleiben unterstützt. Eine Absturz-Injektion nach dauerhaft geschriebenem Journal belegt Recovery ohne doppelte Ledgerbuchung. Direkter Replay eines identischen Records bleibt idempotent; widersprüchliche Evidence schlägt vor Zustandsänderungen fehl.

## Harte Mechanikgrenze

Budget, Reputation, Stress, Heat und Stability folgen weiter ausschließlich den bisherigen Source Effects. Kein Publikumskraft-Multiplikator, keine neue Auszahlung und keine Änderung des Property-/Upgrade-Zustands wird eingeführt. Die lesbare Anzeige erklärt ausdrücklich, dass der Nachweis keinen zusätzlichen Gewinn oder Bonus erzeugt.

## Ergebnis und nächster Schritt

**Architektur-GO für Evidence-Plumbing, Mechanik-NO-GO bleibt bestehen; gemeinsame Wertautorität, Resolver und Receipt-Brücke sind lokal umgesetzt.** Lokale Testergebnisse stehen im Iterationsabschluss; sie sind kein Remote-CI- oder Merge-Nachweis.

Als nächster fachlicher Slice darf genau eine begrenzte Wirkung gesondert geprüft werden: Formel, Cap, Grenzwerte, Einfluss auf bestehende Deltas und reproduzierbare Balance-Abnahme. Ein vorhandener Ortsnachweis allein ist keine Freigabe für einen Bonus.
