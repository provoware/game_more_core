# Repository-Audit – 2026-08-21

## Ergebnis

Der geprüfte `main`-Stand war **nicht fehlerfrei**. Der Runtime-Kern `0.5.2-alpha.1` besitzt einen erfolgreichen Remote-Nachweis, aber die danach parallel entstandene 0.6-Presentation-Arbeit hatte einen kritischen Merge-Schaden erzeugt.

## Kritischer Befund

PR #14 wurde gemergt, obwohl der für `src/**` relevante GitHub-Workflow `Runtime Core` bereits beim Compile-Schritt fehlgeschlagen war. Im resultierenden `main` waren zwei konkurrierende Versionen von `character_projection.py` und ihres Tests ineinanderkopiert. Auch `presentation/__init__.py` enthielt doppelte, konkurrierende Exportblöcke.

Auswirkung:

- Presentation-Code auf `main` war nicht zuverlässig kompilierbar.
- Tests enthielten widersprüchliche Erwartungen für dieselben Projektionsfelder.
- mehrere offene Folge-PRs bauten gleichzeitig auf derselben beschädigten Grundlage auf.

## PR-Befund

Zum Auditzeitpunkt waren sieben überlappende Presentation-PRs offen:

- #15 Application-Capabilities
- #16 Command-Dispatcher
- #17 bestätigtes Progressionsfeedback
- #18 lokaler Presentation-State
- #19 A4 Ops Deck inklusive eigener alternativer Projection/Komponentenstruktur
- #20 alternative Komponenten-/Adapterstruktur
- #21 A3/A4-Gesamtprojektion mit erneut eigener Projection-Variante

Diese PRs enthalten fachlich sinnvolle Einzelideen, bearbeiten aber teilweise dieselben kanonischen Dateien mit unterschiedlichen Strukturen. Ein seriöser Merge aller Varianten würde die gerade festgelegte Architektur erneut aufspalten.

## Reparaturentscheidung

### Beibehalten

- Runtime-Baseline `0.5.2-alpha.1`
- bestehender `CharacterState`
- `build_biography_projection(...)` als zuständige Biografieprojektion
- flache deutsche Textschlüssel aus `content/de/ui/*.json`
- bestehender Presentation-Vertrag als Schichtengrenze

### Repariert

- genau eine `build_character_projection(...)`
- eindeutige Package-Exporte
- ein konsolidierter Character-Projection-Test
- gesperrte Traits verbergen Evidenz/Fortschritt
- Skill-Fortschritt defensiv begrenzt
- Biografie wird über den vorhandenen Helper integriert

### Neu als Schutz

- `.github/workflows/presentation-core.yml`
- PR-Regel: pro kanonischer Zielstelle höchstens ein aktiver Implementierungs-PR
- rotes relevantes CI-Gate blockiert Merge
- Release-Baseline und aktive Entwicklungsiteration werden getrennt geführt

## Konsolidierte Folge-Reihenfolge

Die fachlich sinnvollen Inhalte der parallelen PRs gehen nicht verloren. Sie sind in `TODO.md` geordnet:

1. Application-Capabilities + ein Command-Dispatcher
2. lokaler Presentation-State + bestätigtes Feedback
3. gemeinsame Komponenten + A4 Ops Deck
4. A3 Cinematic Forge aus denselben Komponenten
5. Ranking/Network anschließend

Dadurch entsteht kein zweiter Presentation-Kern.

## Validierungsstrategie

Für diese Reparatur sind relevant:

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote müssen der bestehende `Runtime Core` und der neue `Presentation Core` für den tatsächlichen Reparatur-Head grün sein, bevor nach `main` gemergt wird.

## Versionsentscheidung

Die Reparatur erhöht `VERSION.json` nicht künstlich. `0.5.2-alpha.1` bleibt die letzte freigegebene Runtime-Baseline. Die aktive 0.6-Arbeit wird in `PROJEKTSTATUS.json` und `TODO.md` geführt, bis daraus eine eigenständig abgenommene Produktstufe wird.

## Abschlusskriterium

Der Audit ist erst abgeschlossen, wenn:

- Reparatur-PR remote grün ist,
- Reparatur auf `main` gemergt ist,
- die überlappenden offenen Presentation-PRs geschlossen sind,
- `main` danach erneut den erwarteten Status zeigt.
