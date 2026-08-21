# Repository Guard – Merge- und Health-Vertrag

## Zweck

Der Repository Guard verhindert, dass ein alter oder widersprüchlicher Entwicklungsstand einen bereits validierten `main` überschreibt. Er ergänzt die fachlichen Runtime-/Presentation-Tests; er ersetzt sie nicht.

## Drei Pflichtchecks

Für Pull Requests nach `main` gelten drei stabile Check-IDs:

1. `runtime-core`
2. `presentation-core`
3. `repository-health`

`Runtime Core` und `Presentation Core` laufen deshalb bei jedem Pull Request. So existieren die Required-Check-Ergebnisse auch dann, wenn ein PR nur Dokumentation oder Prozessdateien ändert.

## Repository Health

`.github/workflows/repository-health.yml` führt auf jedem Pull Request, auf `main`, in Merge Groups und manuell folgende kompakte Prüfungen aus:

- vollständiger Python-Compile-Check für `src/`, Guard und Repository-Guard-Tests,
- JSON-Syntax aller getrackten JSON-Dateien,
- echte Git-Merge-Konfliktmarker in Textdateien,
- Übereinstimmung von `VERSION.json`, `PROJEKTMANIFEST.json` und `PROJEKTSTATUS.json`,
- aktive Entwicklungsphase gegen `README.md` und `TODO.md`,
- eindeutige kanonische Presentation-Symbole,
- keine mehrfachen `__all__`-Definitionen,
- keine doppelten Top-Level-Definitionen innerhalb eines Python-Moduls,
- alle öffentlichen `__all__`-Exporte sind tatsächlich importierbar,
- alle drei Pflichtworkflows existieren und laufen ohne PR-Pfadfilter,
- versionsgebundene Feature-Branches dürfen nicht hinter der aktiven Iteration liegen,
- PR-Head muss den aktuellen Base-Branch enthalten,
- Guard-/Merge-Verträge besitzen eigene Regressionstests.

Der letzte Punkt verhindert einen Merge aus einer veralteten Branch-Basis. Vor dem Merge muss der Branch auf den aktuellen `main` gebracht werden.

## Maschinenlesbarer Vertrag

`manifests/REPOSITORY_GUARD_MANIFEST.json` definiert:

- geschützten Zielbranch,
- gewünschte Branch-Policy,
- Required-Check-IDs,
- kanonische Informationsdateien,
- kanonische Presentation-Symbole,
- öffentliche Packages,
- Pflichtworkflows,
- Safe-Merge-Regeln,
- geschützte Guard-/CI-Pfade,
- Retry-Vertrag für GitHub-Eventual-Consistency,
- Ausnahmen für ausdrücklich als Wartung/Hotfix/Recovery gekennzeichnete Branches.

`tools/repository_health.py` prüft den Repository-Vertrag. `tools/github_merge_guard.py` prüft Kandidaten und Main-Provenienz. `tools/github_merge_guard_retry.py` kapselt ausschließlich die begrenzte Nachprüfung gegen GitHubs eventual consistency.

## Operativer Mergeweg: `/safe-merge`

Normale Pull Requests nach `main` werden über den PR-Kommentar

```text
/safe-merge
```

übernommen.

Der Workflow `.github/workflows/safe-merge.yml` läuft aus dem vertrauenswürdigen `main` und prüft unmittelbar vor dem Merge:

- auslösender Benutzer besitzt `write`, `maintain` oder `admin`,
- PR ist offen und kein Draft,
- Zielbranch ist exakt `main`,
- PR ist mergefähig,
- PR-Head enthält den aktuellen `main`,
- `Runtime Core`, `Presentation Core` und `Repository Health` sind auf exakt diesem Head erfolgreich,
- keine ungelösten Review-Threads,
- der erwartete Head-SHA stimmt,
- der normale PR verändert keine geschützte Guard-/CI-Sicherheitsdatei.

Der eigentliche Merge-API-Aufruf wird **exakt einmal** ausgeführt.

### Schutz vor Selbständerung

Normale `/safe-merge`-PRs dürfen insbesondere diese Sicherheitsgrenze nicht selbst verändern:

- Runtime-/Presentation-/Repository-Health-Workflows,
- `safe-merge.yml`,
- `main-integrity.yml`,
- Repository-/Merge-Guard-Tools,
- `REPOSITORY_GUARD_MANIFEST.json`,
- Repository-Guard-Tests.

Solche Änderungen benötigen einen ausdrücklich auditierten Security-Bootstrap-PR mit denselben drei grünen Kern-Gates und ohne offene Review-Threads.

## Main Integrity

`.github/workflows/main-integrity.yml` kontrolliert Änderungen auf `main` zusätzlich nachträglich.

Geprüft werden unter anderem:

- lokaler Repository-Health-Vertrag,
- normaler Zwei-Eltern-PR-Merge,
- genau ein zugehöriger gemergter PR nach `main`,
- ursprünglicher PR-Head mit allen drei grünen Pflichtworkflows,
- keine ungelösten Review-Threads.

Ein nicht bestätigter Main-Stand erzeugt einen idempotenten `[MAIN-INTEGRITY]`-Incident und blockiert weitere Feature-Merges bis zur Klärung.

## GitHub Eventual Consistency

Der erste echte `/safe-merge`-Smoke-Test auf PR #36 deckte eine reale GitHub-Race-Condition auf: Der Merge war bereits geschrieben, die API-Zuordnung `Merge-Commit → Pull Request` war unmittelbar danach jedoch noch nicht sichtbar.

Der Hotfix aus PR #37 löst dies bewusst ohne zweiten Mergeversuch:

```text
Merge: exakt 1×
Nachgelagerte Provenienz-Leseprüfung: 0 / 1 / 2 / 4 / 8 Sekunden
```

Damit werden drei Zustände klar unterschieden:

- `SAFE MERGE BLOCKED` – vor dem Merge ist eine Vertragsbedingung nicht erfüllt; nichts wird gemergt.
- `SAFE MERGE COMMITTED – POST-VERIFY NICHT BESTÄTIGT` – Merge ist bereits geschrieben, nur die nachgelagerte GitHub-Provenienz konnte noch nicht bestätigt werden.
- `SAFE MERGE PASS` – Merge und Main-Provenienz sind vollständig bestätigt.

Regressionstests stellen sicher, dass Retry niemals einen zweiten Merge-API-Aufruf erzeugt.

## End-to-End-Nachweis

Der gehärtete Weg wurde mit PR #38 vollständig geprüft:

- Head: `c97d02b29a6d6de33c32bf7113179c65d9e3e2f4`
- Runtime Core `32528078989` → erfolgreich
- Presentation Core `32528078992` → erfolgreich
- Repository Health `32528078926` → erfolgreich
- Review-Threads → 0
- Merge ausschließlich über `/safe-merge`
- Bot-Rückkanal → `SAFE MERGE PASS`
- bestätigter Merge-Commit → `e1155db2d2a7eaddd313127d89635a1a3dac3ce6`

Damit ist der operative sichere Mergeweg End-to-End bestätigt.

## Native Branch Protection für `main`

Native GitHub-Branch-Protection bleibt als zusätzliche serverseitige Härtung sinnvoll. Zielzustand:

- Änderungen nur über Pull Request,
- Branch muss vor Merge aktuell zu `main` sein,
- offene Review-Konversationen müssen aufgelöst sein,
- Force Pushes aus,
- Branch-Löschen aus,
- Required Status Checks:
  - `runtime-core`
  - `presentation-core`
  - `repository-health`

Die verbundene GitHub-Schnittstelle dieses Projekts kann den Schutzstatus lesen, stellt aber weiterhin keinen sicheren Admin-Schreibbefehl für Branch Protection/Rulesets bereit. Deshalb wird die native Regel **nicht** als aktiviert behauptet.

Sobald geeigneter Admin-Zugriff verfügbar ist, kann diese Regel zusätzlich aktiviert werden. Der bereits validierte `/safe-merge`-Pfad bleibt davon unabhängig als operative Merge-Disziplin bestehen.

## Warum Runtime/Presentation immer einen Status liefern

GitHub kann einen verpflichtenden Check nicht erfüllen, wenn der dazugehörige Workflow wegen eines `paths:`-Filters gar nicht gestartet wurde. Daher besitzen `runtime-core.yml` und `presentation-core.yml` keine PR-Pfadfilter mehr.

Das ist bewusst: Ein Merge hat genau drei stabile, leicht erkennbare Gate-Ergebnisse. Der zusätzliche Aufwand ist klein und verhindert fehlende oder umgehbare Check-Zustände.

## Alte Branches

Ein Branchname mit einer Entwicklungsnummer unterhalb der aktiven Iteration wird für einen normalen PR nach `main` abgewiesen. Beispiel bei aktiver `0.7.2`:

```text
presentation/0.6.4-cinematic-forge  → BLOCK
feature/0.7.2-resource-effects       → OK
maintenance/repository-cleanup       → Wartungsausnahme
```

Die Namensprüfung ist nur eine zusätzliche Schranke. Entscheidend bleibt außerdem, dass der PR-Head den aktuellen `main` enthält.

## Lokaler Aufruf

Vom Repository-Root:

```bash
PYTHONPATH=src python3 -m compileall -q \
  src \
  tools/repository_health.py \
  tools/github_merge_guard.py \
  tools/github_merge_guard_retry.py \
  tests/repository
PYTHONPATH=src:. python3 -m unittest discover -s tests/repository -v
PYTHONPATH=src python3 tools/repository_health.py
```

Für eine simulierte PR-Branchprüfung:

```bash
PYTHONPATH=src python3 tools/repository_health.py \
  --head-ref feature/0.7.2-example \
  --base-ref main
```

## Fehlerstrategie

Der Guard arbeitet fail-closed bei widersprüchlichen oder nicht eindeutig lesbaren Verträgen. Er repariert Dateien nicht automatisch und verändert keine Spielstände oder Runtime-Daten.

Ein Guard-Fehler nennt die konkrete Datei oder Regel. Korrekturen erfolgen an der kanonischen Quelle und werden erneut auf demselben PR-Head geprüft. Ein bereits geschriebener Merge wird niemals durch einen automatischen zweiten Mergeversuch „repariert“.