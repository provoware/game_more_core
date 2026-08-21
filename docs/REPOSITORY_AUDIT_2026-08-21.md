# Repository-Audit – 2026-08-21

## Ergebnis

Der vor dem Audit geprüfte `main`-Stand war **nicht fehlerfrei**. Der Runtime-Kern `0.5.2-alpha.1` war intakt, aber parallele 0.6-Presentation-Arbeit hatte einen kritischen Merge-Schaden erzeugt.

Der Audit ist inzwischen **abgeschlossen**: Die Presentation-Foundation wurde repariert, beide relevanten Remote-Gates waren auf demselben Reparatur-Head grün, PR #22 wurde nach `main` gemergt und die sieben konkurrierenden Presentation-PRs #15–#21 wurden mit dokumentierter Übernahme ihrer sinnvollen Anforderungen geschlossen.

## Kritischer Ausgangsbefund

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

Diese PRs enthielten fachlich sinnvolle Einzelideen, bearbeiteten aber teilweise dieselben kanonischen Dateien mit unterschiedlichen Strukturen. Alle sieben wurden nach der Reparatur geschlossen; die sinnvollen Anforderungen sind sequenziell in `TODO.md` erhalten.

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

## Validierter Reparaturstand

Reparatur-PR: **#22**

Geprüfter Head:

`fc9be2ca5cc4ca669fbb800899a0515dc2e543e6`

Remote-Gates auf genau diesem Head:

- `Runtime Core` → **SUCCESS**, Workflow Run `32505897397`
- `Presentation Core` → **SUCCESS**, Workflow Run `32505897399`

Merge nach `main`:

`73f9bb6aa2a10b30b4b2ba4b410a4b4451eea2ea`

Danach wurden #15–#21 geschlossen. Offene PRs nach dem Cleanup: **0**.

## Konsolidierte Folge-Reihenfolge

Die fachlich sinnvollen Inhalte der geschlossenen Parallel-PRs stehen in `TODO.md` in dieser Reihenfolge:

1. Application-Capabilities + ein Command-Dispatcher
2. lokaler Presentation-State + bestätigtes Feedback
3. gemeinsame Komponenten + A4 Ops Deck
4. A3 Cinematic Forge aus denselben Komponenten
5. Ranking/Network anschließend

Dadurch entsteht kein zweiter Presentation-Kern.

## Versionsentscheidung

Die Reparatur erhöht `VERSION.json` nicht künstlich. `0.5.2-alpha.1` bleibt die letzte freigegebene Runtime-Baseline. Die aktive Entwicklung steht nun bei `0.6.1` und wird in `PROJEKTSTATUS.json` und `TODO.md` geführt.

## Abschlussstatus

- [x] Reparatur-PR remote grün
- [x] Reparatur auf `main` gemergt
- [x] überlappende offene Presentation-PRs geschlossen
- [x] offener PR-Bestand auf 0 reduziert
- [x] Projektstatus auf 0.6.1 als nächsten kanonischen Schritt gesetzt

**Auditstatus: ABGESCHLOSSEN.**
