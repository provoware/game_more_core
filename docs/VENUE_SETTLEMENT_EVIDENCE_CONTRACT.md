# Versionierter Venue-Nachweis in der Eventabrechnung

## Ziel und Änderungssatz

Iteration `0.8.8-VENUE-SETTLEMENT-EVIDENCE` vervollständigt den bereits freigegebenen Evidence-Pfad. Sie verändert weder die fünf Settlement-Effekte noch Besitz, Ausbau oder Browserautorität. Ein Publikumskraft-Bonus bleibt **NO-GO**.

Geplanter Lesesatz: `domain/settlement.py`, `application/settlement_service.py`, `application/venue_settlement_evidence.py`, die bestehende Session-Anbindung, Settlement-/Property-/Upgrade-Schemas und Manifeste sowie deren direkte Runtime-Regressionen. Die Authority-/Mechanik-Audits, Laienhilfe, TODO, Feature-Pool und Projektstatus werden nur in den betroffenen Abschnitten aktualisiert. Kein Repository-Breitenscan und keine parallele Engine.

Begründete Erweiterung: Der vollständige Runtime-/Repository-Check meldete die veraltete Iteration in README/Statusregression; diese Basis-/Testdateien wurden gezielt einbezogen. Der zusätzliche Status-Sync-Check belegte einen bereits vorhandenen Drift von PR #273 auf den lokalen Safe-Merge-Commit von PR #276. Nur der Statusanker wird daraus aktualisiert, kein neuer Remote-PASS abgeleitet.

## Vertrag und Kompatibilität

- Historische Receipts mit `contract_version = 0.8.3-c1` bleiben unverändert: **kein** `venue_evidence`-Feld. Laden und Wiederholen ergänzt keine nachträglich erfundene Evidence.
- Der neue Vertrag `0.8.8-venue-evidence1` benötigt ausdrücklich `venue_evidence`: Objekt bei bestätigtem eigenem Event-Ort, sonst `null`.
- Der bestehende `SettlementService` aktiviert den neuen Vertrag nur mit gemeinsam übergebenem City-Map- und Upgrade-Katalog. Die normale Game-Session reicht ihre vorhandenen Kataloge weiter. Unkonfigurierte Legacy-Verbraucher bleiben kompatibel.
- Nur `resolve_owned_venue_evidence(...)` bestimmt den Wert beim Abschluss. Keine Caller-/Browser-Evidence und kein zweiter Werte-Rechner.
- Ohne `property_upgrades`-Block existieren keine bestätigten Ausbauten: Revision 0, Basiswerte desselben Katalogs. Fehlender Besitz ergibt keine Evidence.
- Die Evidence enthält exakt `schema_version`, `location_id`, `owner_character_id`, `audience_pull`, `city_map_manifest_version`, `property_upgrade_manifest_version`, `property_revision`, `property_upgrade_revision`. Integer sind keine Booleschen Werte; Publikumskraft liegt in 0–100, Revisionen sind nichtnegativ, Textwerte sind nichtleer und ohne Rand-Leerzeichen.

## Atomarer Abschluss und historische Wahrheit

Die Evidence wird im bestehenden `event.completed.payload.settlement` zusammen mit dem Settlement-State in **demselben** atomaren Sechs-Record-Commit gespeichert. Kein neuer Journaltyp, keine zusätzliche Buchung, keine Save-Envelope-Migration und keine Neuberechnung der Effekte.

Beim Recovery wird die gespeicherte Evidence auf Event-Ort, abrechnenden Character, damaligen Besitz und damalige Property-/Upgrade-Revision geprüft. Struktur, Grenzen und Vertragsversionen werden ebenfalls geprüft. Der gespeicherte historische Wert wird **nicht mit später veränderten Katalogen neu berechnet**. Quellversionen dokumentieren seine Herkunft; die vorhandene Journal-Hashkette schützt die gespeicherten Werte. Dies ist kein Beweis gegen einen Angreifer, der einen gesamten Save samt Hashkette neu fälscht.

Eine vorhandene Evidence ohne eigenen Ort, eine fehlende Evidence bei eigenem Ort, falsche Revisionen oder ungültige Felder führen zum Abbruch ohne Teil-Commit. Ein wiederholter Abschlussbefehl liefert den ursprünglichen Beleg ohne weitere Buchung. Auch ein Legacy-Abschluss bleibt nach Aktivierung des neuen Vertrags ein Legacy-Beleg.

## Abnahme

Direkte Tests beweisen Legacy-Roundtrip, Grenzen und beschädigte Evidence, eigenen/fremden/fehlenden Besitz, fehlenden Ausbau-State, identische Effekte, defensive Kopien, genau einen Commit, Retry sowie Recovery nach `after_journal_durable`. Manipulierte Orts-/Revisionsbindungen werden beim Replay abgewiesen. Bestehende Settlement-, Session-, Runtime-, Presentation- und Repository-Gates bleiben verbindlich.

Lokal geprüft am 17.10.2026 im uncommitteten Arbeitsstand auf Baseline `15b440c974acb3bc594d2d4c8e7ecd3f53d28c31`:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests/runtime -v`: **314 bestanden**, einschließlich 11 neuer Receipt-Tests und realer HTTP-First-Run-/Restart-/Recovery-Prüfung.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests/presentation -v`: **291 bestanden**.
- `PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v`: **22 bestanden**.
- `PYTHONPATH=src python3 tools/repository_health.py`: **PASS**.
- `python3 tools/status_sync.py check`: **PASS**, lokal belegter Safe-Merge-Anker PR #276.
- Zusätzliche Draft-2020-12-Schemavalidierung mit dem vorhandenen Cloud-`jsonschema`: drei gültige Legacy-/neue/null-Belege akzeptiert, acht beschädigte bzw. versionswidrige Belege abgewiesen; keine neue Projektabhängigkeit.

Keine Remote-CI, kein PR-/Merge- oder Release-PASS für diesen Arbeitsstand behauptet. Aktuelle Entwicklungsstufe **77,8 % = 7/9 Abnahmepunkte**; die beiden verbleibenden Punkte sind Remote-Abnahme und Safe Merge.

## Nächster fachlicher Schritt

Der Beleg schafft Nachvollziehbarkeit, noch keinen Spielvorteil. Als nächster separater Slice ist eine read-only Anzeige des **gespeicherten** Belegs sinnvoll: Spieler erkennen Ort und bestätigten Wert ohne Browserberechnung. Anschließend kann genau ein begrenzter Publikumskraft-Effekt mit messbarem Balancevertrag bewertet werden. Produktversion und Releasefreigabe bleiben davon getrennt.
