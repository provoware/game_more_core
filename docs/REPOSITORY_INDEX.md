# Ordner- und Dateiindex

## Zweck

Dieser Index beantwortet: **Wo liegt was und welche Datei ist zuständig?**

- Runtime-Baseline: `0.5.2-alpha.1`
- aktive Entwicklung: `0.6.3 – gemeinsame Komponenten + A4 Ops Deck`

## Einstieg

| Pfad | Rolle |
|---|---|
| `README.md` | kompakter Projekteinstieg |
| `AGENTS.md` | verbindlicher Entwicklungs-, PR- und Merge-Ablauf |
| `TODO.md` | kanonische offene Arbeit in Ausführungsreihenfolge |
| `CHANGELOG.md` | fachliche Änderungshistorie |
| `VERSION.json` | letzte versionierte Runtime-/Produkt-Baseline |
| `PROJEKTMANIFEST.json` | zentrale Projektpfade |
| `PROJEKTSTATUS.json` | aktive Iteration, Validierungsstand, nächstes Ziel |

## Hauptordner

| Ordner | Inhalt |
|---|---|
| `.github/workflows/` | `runtime-core.yml`, `presentation-core.yml` |
| `content/de/` | lokalisierte sichtbare Inhalte |
| `docs/` | Architektur-, Gameplay-, Persistence- und Presentation-Verträge |
| `manifests/` | kanonische Kataloge und maschinenlesbare Regeln |
| `reports/` | reproduzierbare Prüfnachweise |
| `schemas/` | Datenstrukturverträge |
| `src/bunkerfrequenz/` | Domain, Application, Infrastructure, Presentation |
| `tests/` | Runtime-, Gameplay-, Simulation- und Presentation-Tests |
| `tools/` | kleine ausführbare Entwicklerwerkzeuge |

## Codebereiche

### Domain

`src/bunkerfrequenz/domain/`

- `character.py` – Character State
- `progression.py` – Skills, Level, Traits, Spezialisierung, Resonanz
- `trait_effects.py` – tatsächliche Trait-Wirkungen

### Application

`src/bunkerfrequenz/application/`

| Datei | Zuständigkeit |
|---|---|
| `action_resolver.py` | deterministische fachliche Action-Auflösung |
| `character_action_service.py` | Action-Commit über Persistence |
| `profile_service.py` | Profiländerung und sicherer Profil-Undo |
| `presentation_capabilities.py` | fail-closed UI-Capabilities |
| `command_dispatcher.py` | einziger bestätigter UI-Schreibweg für Profil/Undo/Action |
| `presentation_events.py` | detached Abfrage bereits bestätigter Journal-Event-IDs |
| `recovery_service.py` | Character-Replay/Wiederherstellung |

### Infrastructure

`src/bunkerfrequenz/infrastructure/`

- `persistence.py` – Journal, atomarer State, Snapshot, Recovery und Idempotenz

### Presentation

`src/bunkerfrequenz/presentation/`

| Datei | Zuständigkeit |
|---|---|
| `character_projection.py` | kanonische schreibgeschützte Character-Projektion |
| `biography_projection.py` | validierte Biografieprojektion |
| `state.py` | immutable lokaler View-/Filter-/Dismiss-State |
| `feedback.py` | deterministisches Feedback aus bestätigten Progressionsereignissen |
| `__init__.py` | öffentliche Presentation-Exporte, keine Fachlogik |

## Sichtbare Character-Forge-Texte

`content/de/ui/`

- `skills.json`
- `traits.json`
- `trait_effects.json`
- `trait_consequences.json`
- `specializations.json`
- `stages.json`
- `feedback.json` – Level-/Skill-/Trait-/Spezialisierungs-/Resonanzfeedback
- `character_forge.json` – allgemeine UI-Begriffe

## Zentrale Dokumente

| Datei | Thema |
|---|---|
| `docs/ARCHITEKTURVERTRAG.md` | Schichten und Invarianten |
| `docs/CHARACTER_FORGE.md` | Figuren, Skills, Traits, Biografie |
| `docs/PROGRESSION_CONTRACT.md` | XP, Level, Spezialisierung, Resonanz |
| `docs/GAMEPLAY_ACTION_CONTRACT.md` | Actions und Progressionsevidenz |
| `docs/PERSISTENCE_CONTRACT.md` | Save-/Journal-/Transaktionsregeln |
| `docs/RECOVERY_0.5.1.md` | Recovery, Snapshot, Undo |
| `docs/UI_UX_BLUEPRINT.md` | A1–A4 Designrichtung |
| `docs/PRESENTATION_CONTRACT_0.6.md` | Projection, Application-Grenze, lokaler State, Feedback, spätere A4/A3-Komponenten |
| `docs/ENTWICKLERHANDBUCH.md` | Entwicklerübernahme und Prüfstrategie |
| `docs/REPOSITORY_AUDIT_2026-08-21.md` | Audit-/Reparaturnachweis |

## Tests

| Bereich | Zweck |
|---|---|
| `tests/runtime/` | Character, Action, Persistence, Recovery, Resonanz, Dispatcher, bestätigte Eventabfrage |
| `tests/presentation/` | Projection, Biografie, Capabilities, lokaler State, Feedback und End-to-End-Feedbackpipeline |
| `tests/gameplay/` | Action-Vertrag |
| `tests/simulation/` | Progressions-/Balance-Regression |

## Remote-CI

- `runtime-core.yml`: Domain/Application/Infrastructure/Runtime-Gate.
- `presentation-core.yml`: Presentation, zugehörige Application-Grenzdateien, UI-Textkataloge und Presentation-Tests.

Ein rotes für den Scope relevantes Gate blockiert den Merge.

## Informationshierarchie

1. Fach-/Architekturvertrag
2. Manifest/Schema
3. Runtime und Tests
4. `PROJEKTSTATUS.json`
5. `TODO.md`
6. README/Index
7. CHANGELOG-Historie
