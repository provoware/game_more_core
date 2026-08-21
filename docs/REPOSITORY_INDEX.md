# Ordner- und Dateiindex

## Zweck und Pflege

Dieser Index beantwortet: **Wo liegt was?** Er beschreibt den versionierten Stand `0.5.2-alpha.1`. Bei neuen oder entfernten öffentlichen Bereichen wird er in derselben Iteration angepasst; einzelne gleichartige Test- oder Runtime-Dateien werden über ihre Bereichstabelle erschlossen.

## Einstieg im Wurzelverzeichnis

| Pfad | Rolle |
|---|---|
| `README.md` | kompakter Projekteinstieg und Schnellzugriff |
| `AGENTS.md` | verbindlicher Arbeitsablauf und Architekturgrenzen |
| `TODO.md` | kanonische nächste Arbeitseinheiten |
| `CHANGELOG.md` | fachliches Änderungsprotokoll |
| `VERSION.json` | aktuelle Version |
| `PROJEKTMANIFEST.json` | zentrale Pfade und Projektmetadaten |
| `PROJEKTSTATUS.json` | maschinenlesbarer Umsetzungsstand |

## Ordnerübersicht

| Ordner | Inhalt | Einstieg |
|---|---|---|
| `.github/workflows/` | gezielte Remote-CI | `runtime-core.yml` |
| `content/` | lokalisierte, sichtbare Inhalte | `content/de/` |
| `docs/` | Fachverträge, Erklärungen und Navigation | `GAME_SCHEMA.md` |
| `manifests/` | kanonische Kataloge und Regeln | `ARCHITEKTUR_MANIFEST.json` |
| `reports/` | versionierte lokale Prüfnachweise | `RUNTIME_VALIDATION_0.5.2.json` |
| `schemas/` | JSON-Strukturverträge | `character_state.schema.json` |
| `src/` | headless Spiel-Runtime | `src/bunkerfrequenz/` |
| `tests/` | Gameplay-, Runtime- und Simulationstests | Unterordner nach Prüfbereich |
| `tools/` | ausschließlich ausführbare Basiswerkzeuge | `validate_action_contract.py` |

## Dokumentation

| Datei | Thema |
|---|---|
| `docs/GAME_SCHEMA.md` | Gesamtbild von Spiel, Daten und Ereignisfluss |
| `docs/REPOSITORY_RULES.md` | professionelle Trennung von Tool, Doku und Vertrag |
| `docs/REPOSITORY_INDEX.md` | dieser Navigationsindex |
| `docs/ARCHITEKTURVERTRAG.md` | Ebenen und unveränderliche Architekturregeln |
| `docs/CHARACTER_FORGE.md` | Figuren, Skills, Traits und Biografie |
| `docs/PROGRESSION_CONTRACT.md` | XP, Level, Spezialisierung und Resonanz |
| `docs/GAMEPLAY_ACTION_CONTRACT.md` | Aufbau und Auflösung von Aktionen |
| `docs/CHARACTER_CORE_0.5.md` | implementierter Runtime-Kern |
| `docs/PERSISTENCE_CONTRACT.md` | Journal-, Save- und Transaktionsregeln |
| `docs/RECOVERY_0.5.1.md` | Snapshot, Wiederherstellung und Undo |
| `docs/UI_UX_BLUEPRINT.md` | spätere Character-Forge-Oberfläche |
| `docs/DATENMODELL.md` | fachliche Datenobjekte und Beziehungen |
| `docs/ENTWICKLERHANDBUCH.md` | Einstieg, Versionierung und Prüfstrategie |
| `docs/assets/` | eingebundene visuelle Referenzen |

## Runtime-Code

| Bereich | Dateien und Verantwortung |
|---|---|
| `src/bunkerfrequenz/domain/` | `character.py`, `progression.py`, `trait_effects.py`: reines Charakter- und Fortschrittsmodell |
| `src/bunkerfrequenz/application/` | Resolver sowie Action-, Profil- und Recovery-Services |
| `src/bunkerfrequenz/infrastructure/` | `persistence.py`: Journal, State, Snapshot und atomare Speicherung |

`__init__.py`-Dateien markieren Python-Pakete und enthalten keine parallelen Fachregeln.

## Maschinenlesbare Verträge

### Manifeste

- **Charakter und Entwicklung:** `CHARAKTER`, `SKILL`, `TRAIT`, `TRAIT_ENGINE`, `PROGRESSION`, `LEVEL`, `BIOGRAFIE`.
- **Aktionen und Laufzeit:** `ACTION`, `RUNTIME`, `JOURNAL`.
- **Speicherung und Zeit:** `PERSISTENCE`, `SAVEFORMAT`, `MIGRATION`, `ZEIT`, `SYNC`.
- **Darstellung und Texte:** `UI`, `ANIMATION`, `TEXT`.
- **Projektsteuerung:** `ARCHITEKTUR`, `TEST`, `RELEASE`.

Alle liegen als `manifests/<NAME>_MANIFEST.json` vor.

### Schemas

`schemas/` enthält Strukturverträge für Action, Character Definition, Character State, Journal, Persistence Transaction, Progression, Save, Trait, Trait Engine und UI. Ein Schema beschreibt Form und Typen; das zugehörige Manifest liefert die fachlichen Werte.

## Inhalte, Tests, Tools und Berichte

- `content/de/characters.json` und `level_titles.json` enthalten deutsche Spielinhalte; UI-Texte liegen unter `content/de/ui/`.
- `tests/gameplay/` prüft den Action-Vertrag, `tests/runtime/` den Kern und `tests/simulation/` den Simulator.
- `tools/validate_action_contract.py` ist der kleine Vertragsprüfer; `tools/simulate_characters/progression_simulator.py` ist das reproduzierbare Balance-Werkzeug.
- `reports/` bewahrt freigegebene Ergebnisse der Vertrags-, Simulations- und Runtime-Prüfungen. Berichte sind Nachweise, keine Eingaben der Runtime.

## Verbindlichkeit bei Widersprüchen

1. `AGENTS.md` bestimmt den Arbeitsprozess.
2. Fachverträge bestimmen Architektur und Verhalten.
3. Manifeste und Schemas bestimmen katalogisierte Werte und Datenformen.
4. Runtime und Tests setzen diese Verträge um und prüfen sie.
5. README, Index und Spielschema erleichtern den Einstieg, erzeugen aber keine zweite Fachregel.
