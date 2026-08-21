# Repository Guard – Merge- und Health-Vertrag

## Zweck

Der Repository Guard verhindert, dass ein alter oder widersprüchlicher Entwicklungsstand einen bereits validierten `main` überschreibt. Er ergänzt die fachlichen Runtime-/Presentation-Tests; er ersetzt sie nicht.

## Drei Pflichtchecks

Für Pull Requests nach `main` sind drei Check-IDs vorgesehen:

1. `runtime-core`
2. `presentation-core`
3. `repository-health`

`Runtime Core` und `Presentation Core` laufen deshalb künftig bei jedem Pull Request. So existieren die Required-Check-Ergebnisse auch dann, wenn ein PR nur Dokumentation oder Prozessdateien ändert.

## Repository Health

`.github/workflows/repository-health.yml` führt auf jedem Pull Request, auf `main`, in Merge Groups und manuell folgende kompakte Prüfungen aus:

- vollständiger Python-Compile-Check für `src/` und den Guard,
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
- PR-Head muss den aktuellen Base-Branch enthalten.

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
- Ausnahmen für ausdrücklich als Wartung/Hotfix/Recovery gekennzeichnete Branches.

Das Prüfskript `tools/repository_health.py` liest diese Werte. Die Regeln werden nicht parallel im Python-Code als zweite Liste gepflegt.

## Branch Protection für `main`

Der Zielzustand in GitHub lautet:

- Änderungen nur über Pull Request,
- Branch muss vor Merge aktuell zu `main` sein,
- offene Review-Konversationen müssen aufgelöst sein,
- Force Pushes aus,
- Branch-Löschen aus,
- Required Status Checks:
  - `runtime-core`
  - `presentation-core`
  - `repository-health`

Je nach GitHub-Oberfläche erscheinen die Checks zusätzlich mit ihren Workflow-Namen `Runtime Core`, `Presentation Core` und `Repository Health`.

### Aktivierung in GitHub

Die verbundene GitHub-Schnittstelle dieses Projekts kann Repository-Branch-Regeln derzeit lesen, aber nicht sicher schreiben. Deshalb wird die Policy nicht als aktiviert behauptet.

In GitHub:

1. Repository **Settings** öffnen.
2. **Rules** → **Rulesets** beziehungsweise **Branch protection rules** öffnen.
3. Regel für `main` anlegen oder bearbeiten.
4. Pull Request vor Merge verlangen.
5. **Require branches to be up to date before merging** aktivieren.
6. **Require status checks to pass before merging** aktivieren.
7. `runtime-core`, `presentation-core` und `repository-health` als Required Checks wählen.
8. **Require conversation resolution** aktivieren.
9. Force Pushes und Branch-Löschen nicht erlauben.

Die Regel darf erst aktiviert werden, nachdem der PR mit dem neuen `repository-health`-Workflow einmal erfolgreich gelaufen ist; dadurch kennt GitHub den neuen Check-Namen.

## Warum Runtime/Presentation immer einen Status liefern

GitHub kann einen Required Check nicht erfüllen, wenn der dazugehörige Workflow wegen eines `paths:`-Filters gar nicht gestartet wurde. Daher besitzen `runtime-core.yml` und `presentation-core.yml` keine PR-Pfadfilter mehr.

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
PYTHONPATH=src python3 -m compileall -q src tools/repository_health.py
PYTHONPATH=src python3 tools/repository_health.py
```

Für eine simulierte PR-Branchprüfung:

```bash
PYTHONPATH=src python3 tools/repository_health.py \
  --head-ref feature/0.7.2-example \
  --base-ref main
```

## Fehlerstrategie

Der Guard arbeitet fail-closed bei widersprüchlichen oder nicht eindeutig lesbaren Verträgen. Er repariert Dateien nicht automatisch und verändert keine Spielstände, Runtime-Daten oder Branches.

Ein Guard-Fehler soll die konkrete Datei oder Regel nennen. Korrekturen erfolgen anschließend an der kanonischen Quelle und werden erneut über denselben PR-Head geprüft.
