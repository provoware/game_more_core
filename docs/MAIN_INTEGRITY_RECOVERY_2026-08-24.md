# Main-Integrity-Recovery – 2026-08-24

## Anlass

Beim Anlegen von `manifests/RELEASE_POLICY.json` wurde durch einen Werkzeugfehler eine leere Platzhalterdatei versehentlich direkt auf `main` geschrieben (`f5a1facda804cffa34795319573c57776d218025`). Die Datei wurde unmittelbar danach ebenfalls direkt wieder entfernt (`071736296ba60f5e732694cf90f993c19497da33`). Beide Direktcommits wurden vom Main-Integrity-Guard korrekt als Provenienzverletzung erkannt und in den Issues #140 und #141 dokumentiert.

## Inhaltliche Prüfung

Der Vergleich des letzten gültigen Safe-Merge-Stands

`ecd373ffdb89681b06d6b69e8f97141c3e3aca1b`

mit dem Revert-Stand

`071736296ba60f5e732694cf90f993c19497da33`

liefert **0 geänderte Dateien**. Der Produkt-/Repository-Baum nach dem Revert ist damit inhaltlich identisch zum letzten gültigen Safe-Merge-Baum; beschädigt war ausschließlich die Commit-Provenienz.

## Recovery-Vertrag

- keine Feature-Änderung wird über die beiden Direktcommits übernommen;
- kein Force-Push und kein Umschreiben von `main`;
- dieser Recovery-PR enthält ausschließlich diese Dokumentation;
- alle regulären Pflichtchecks müssen grün sein;
- der Abschluss erfolgt ausschließlich über `/safe-merge`;
- erst nach bestätigtem Safe-Merge und erneuter Main-Integrity-Prüfung werden Feature-PRs fortgeführt.

## Prävention

Vor jedem künftigen Contents-API-Write wird der Zielbranch explizit geprüft beziehungsweise zuerst angelegt. Ein fehlender Branch darf nicht durch Weglassen des Branchparameters auf den Default-Branch zurückfallen.
