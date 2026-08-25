# Runtime-Owned Evidence Receipt – Laienhilfe

## Wozu dient dieser Nachweis?

Der Browser-Test konnte bereits beweisen, dass eine Immobilie wirklich über den vorhandenen Spielweg gekauft wurde und danach als eigener Kartenort erscheint. Bisher stand im Release-Nachweis aber nur sinngemäß: **Runtime-Eigentum vorhanden**.

Diese Iteration macht den vorhandenen Nachweis genauer, ohne einen neuen Spiel- oder Speicherweg einzubauen.

## Was wird jetzt zusätzlich festgehalten?

Im bereits vorhandenen `DESKTOP_BROWSER_E2E_EVIDENCE.json` steht beim Chromium- und Firefox-Szenario ein kompakter `runtime_owned_evidence_receipt`.

Er enthält nur Daten, die der bestehende Runtime-Kauf bereits bestätigt hat:

- `location_id` – welche katalogisierte Immobilie gekauft wurde,
- `command_type = property.purchase` und den vorhandenen `command_id`,
- `status = confirmed`,
- die bestehenden Economy- und Property-Event-IDs,
- die bestehende Economy-Transaktions-ID,
- `ledger_kind = property_purchase` sowie die vorhandene Ledger-Item-ID,
- bestätigten Kaufpreis, Besitzer-ID und Event-ID.

## Was wird ausdrücklich nicht getan?

- kein zweiter Property-Kauf,
- kein neuer Browser-Command,
- keine neue Receipt-Datei,
- keine zweite Release-Evidence-Architektur,
- keine Änderung von Kaufpreis, Eigentum, Save, Journal, Map oder Gameplay.

Der Receipt wird aus demselben isolierten Testspielstand gelesen, der ohnehin für den Browser-E2E vorbereitet wird. Fehlt die Property-Event-Referenz oder die passende Ledger-Buchung, schlägt der Release-Nachweis fehl statt einen Erfolg zu behaupten.

## Warum ist das hilfreich?

Bei einem späteren Fehler kann man im vorhandenen Evidence-JSON direkt nachvollziehen, **welche Immobilie**, **welcher bestätigte Runtime-Command**, **welche Journal-Ereignisse** und **welche Economy-Buchung** zur sichtbaren eigenen Kartenmarke gehörten.

## Spätere sinnvolle Verbesserung

Wenn sich der read-only Status-Sync im Alltag weiter bewährt, kann später ein normaler Status-Korrektur-PR automatisch vorbereitet werden. Er darf weiterhin niemals direkt nach `main` schreiben.
