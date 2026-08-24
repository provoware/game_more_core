# BUNKERFREQUENZ – RELEASE AUTOPILOT PRO

## Ziel

Der Release Autopilot PRO trennt **Build-Erfolg** strikt von **Auslieferungsfreigabe**. Ein technisch gebautes ZIP ist nur ein Kandidat. Ein Benutzer-Release entsteht ausschließlich durch bytegenaue Promotion genau dieses bereits validierten Kandidaten.

## Kanonische Zustände

- `RELEASE_READY` – alle Kandidatenprüfungen und alle verpflichtenden Promotion-Subgates sind grün; exakt der getestete Kandidat darf promoted werden.
- `QUARANTINE` – Kandidat ist technisch plausibel, aber mindestens ein verpflichtender Nachweis fehlt oder ist instabil; kein Benutzer-ZIP.
- `RELEASE_BLOCKED` – ein verpflichtender Nachweis ist fachlich fehlgeschlagen; kein Benutzer-ZIP.
- `RELEASE_INVALID` – Policy, Manifest oder Evidence ist widersprüchlich beziehungsweise nicht vertrauenswürdig; kein Benutzer-ZIP.

Die maschinenlesbare Autorität ist `manifests/RELEASE_POLICY.json`.

## Pipeline

1. Source Commit und Source Tree werden eingefroren.
2. Der bestehende deterministische Builder erzeugt den Kandidaten in zwei unabhängigen Build-Verzeichnissen.
3. Beide ZIP-Bytes und Build-Zusammenfassungen müssen identisch sein.
4. Das eingebettete `RELEASE_FILE_MANIFEST.json` wird gegen jede enthaltene Produktdatei geprüft: Pfad, SHA-256, Größe und Dateimodus.
5. Exakt der validierte Kandidat wird in einen frischen temporären Clean-Room entpackt.
6. Im Clean-Room läuft der reale `START_BUNKERFREQUENZ.sh`-Pfad bis `100 % BEREIT` und beendet den Testserver anschließend kontrolliert.
7. Die Policy bewertet die verpflichtenden Promotion-Subgates.
8. Nur bei `RELEASE_READY` wird der bereits geprüfte Kandidat per Bytekopie nach `release/` promoted und anschließend erneut gehasht.
9. `RELEASE_EVIDENCE.json` und dessen SHA-256 bilden den kanonischen Evidence Root.

## Kein Rebuild nach Abnahme

Nach erfolgreicher Validierung darf kein zweiter "finaler" Build erzeugt werden. Die Promotion kopiert ausschließlich den Kandidaten, dessen SHA-256 im Evidence Root steht. Kandidat und promoted ZIP müssen byteidentisch sein.

## Aktuelle Promotion-Grenze

Öffentliche Promotion verlangt zusätzlich:

- `desktop_browser_e2e_pro`
- `failure_containment_pro`

Diese beiden Subgates werden in nachfolgenden Slices implementiert. Bis dahin ist der korrekte Zustand `QUARANTINE`; der Release-Package-Workflow archiviert nur Evidence und veröffentlicht absichtlich kein Benutzer-ZIP.

## Anti-Flake

Ein widersprüchlicher oder flakiger Nachweis wird nicht durch Wiederholen "grün gerechnet". `FLAKY` führt zu `QUARANTINE`. Ein Retry darf Diagnose liefern, aber keinen vorherigen Widerspruch als Release-Beweis löschen.

## Sicherheitsgrenzen

Der Autopilot darf keine Systempakete installieren, kein `sudo` ausführen, keine Nutzerdaten löschen und keinen Gameplayzustand verändern. Er validiert und promotet Release-Artefakte; er ist keine zweite Runtime oder Recovery-Engine.

## Evidence Root

Der Evidence Root bindet mindestens:

- Policy-SHA-256,
- Source Commit,
- Source Tree,
- Kandidaten-SHA-256,
- Kandidatengröße,
- Datei-Manifest-SHA-256,
- Kandidatenchecks,
- Promotion-Subgates,
- finalen Release-Zustand.

## Präventiv vermiedene Fehlerklassen

Der Vertrag verhindert insbesondere:

- "im Repository vorhanden, im ZIP vergessen",
- unterschiedliche Bytes zwischen Test- und Download-ZIP,
- beschädigte oder falsch gemodete Paketdateien,
- erfolgreiche Tests gegen den Source-Checkout statt gegen das entpackte Release,
- versehentliche Promotion bei fehlenden E2E-/Robustheitsnachweisen,
- erneutes Bauen nach erfolgreicher Abnahme,
- Flaky-Retry als falschen Grünbeweis.

## Nächste verpflichtende Subgates

`0.8.8-DESKTOP-BROWSER-E2E-PRO` liefert den echten Desktop-/Browsernachweis. `0.8.8-FAILURE-CONTAINMENT-PRO` liefert Ressourcen-, Pfad-, Prozess-, Port-, Crash-/Save- und Anti-Flake-Evidence. Erst wenn beide an denselben Source Commit und Source Tree gebunden `PASS` melden, darf der Autopilot `RELEASE_READY` erzeugen.
