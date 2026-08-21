# Ordner- und Dateiindex

## Zweck

Dieser Index beantwortet: **Wo liegt was und welche Datei ist zuständig?**

- Runtime-Baseline: `0.5.2-alpha.1`
- zuletzt abgeschlossene Feature-Iteration: `0.7.1 – A4 Action-Auswahl`
- nächster Feature-Schritt: `0.7.2 – Ressourcenwirkung + vollständiger Character-Forge-Ablauf`

Bei neuen oder entfernten öffentlichen Bereichen wird dieser Index in derselben Iteration angepasst.

## Einstieg im Wurzelverzeichnis

| Pfad | Rolle |
|---|---|
| `README.md` | kompakter Projekteinstieg und Schnellzugriff |
| `AGENTS.md` | verbindlicher Entwicklungs-, PR- und Merge-Ablauf |
| `TODO.md` | kanonische offene Arbeit in Ausführungsreihenfolge |
| `CHANGELOG.md` | fachliche Änderungshistorie |
| `VERSION.json` | letzte versionierte Runtime-/Produkt-Baseline |
| `PROJEKTMANIFEST.json` | zentrale Pfade und Projektmetadaten |
| `PROJEKTSTATUS.json` | aktive Iteration, Validierungsstand und nächstes Ziel |

## Ordnerübersicht

| Ordner | Inhalt | Einstieg |
|---|---|---|
| `.github/workflows/` | stabile Remote-CI-/Merge-Gates | `runtime-core.yml`, `presentation-core.yml`, `repository-health.yml` |
| `content/` | lokalisierte sichtbare Inhalte | `content/de/` |
| `docs/` | Fachverträge, Erklärungen und Navigation | `GAME_SCHEMA.md` |
| `manifests/` | kanonische Kataloge und maschinenlesbare Regeln | `ARCHITEKTUR_MANIFEST.json` |
| `reports/` | reproduzierbare Prüfnachweise | `RUNTIME_VALIDATION_0.5.2.json` |
| `schemas/` | JSON-Strukturverträge | `character_state.schema.json` |
| `src/` | headless Spielkern und Presentation | `src/bunkerfrequenz/` |
| `tests/` | Vertrags-, Runtime-, Simulation- und Presentation-Tests | Unterordner nach Bereich |
| `tools/` | kleine ausführbare Entwicklerwerkzeuge | `validate_action_contract.py`, `repository_health.py` |

## Dokumentation

| Datei | Thema |
|---|---|
| `docs/GAME_SCHEMA.md` | Gesamtbild von Spiel, Daten und Ereignisfluss |
| `docs/REPOSITORY_RULES.md` | Ablage, Informationshierarchie und PR-Lebenszyklus |
| `docs/REPOSITORY_GUARD.md` | Merge-Guard, Repository Health und Zielpolicy für `main` |
| `docs/REPOSITORY_INDEX.md` | dieser Navigationsindex |
| `docs/ARCHITEKTURVERTRAG.md` | Ebenen und unveränderliche Architekturregeln |
| `docs/CHARACTER_FORGE.md` | Figuren, Skills, Traits und Biografie |
| `docs/PROGRESSION_CONTRACT.md` | XP, Level, Spezialisierung und Resonanz |
| `docs/GAMEPLAY_ACTION_CONTRACT.md` | Aufbau und Auflösung von Aktionen |
| `docs/CHARACTER_CORE_0.5.md` | implementierter Runtime-Kern |
| `docs/PERSISTENCE_CONTRACT.md` | Journal-, Save- und Transaktionsregeln |
| `docs/RECOVERY_0.5.1.md` | Snapshot, Wiederherstellung und Undo |
| `docs/UI_UX_BLUEPRINT.md` | A1–A4 Design-/UX-Richtung |
| `docs/PRESENTATION_CONTRACT_0.6.md` | Projection, Capabilities, bestätigte Events, lokaler State, Feedback und A4/A3-Grenzen |
| `docs/A4_OPS_DECK_0.6.3.md` | acht gemeinsame Komponenten und A4-Interaktionsvertrag |
| `docs/A3_CINEMATIC_FORGE_0.6.4.md` | A3-Komposition, A3↔A4-Invarianten und Animationsvertrag |
| `docs/RANKING_NETWORK_0.6.5.md` | bestätigte Ranking-/Network-Projektion und Server-Autoritätsgrenze |
| `docs/DATENMODELL.md` | fachliche Datenobjekte und Beziehungen |
| `docs/ENTWICKLERHANDBUCH.md` | Übernahme, Prüfstrategie und Release-/PR-Ablauf |
| `docs/REPOSITORY_AUDIT_2026-08-21.md` | Auditbefunde und frühere Reparaturentscheidungen |
| `docs/assets/` | visuelle Referenzen |

## Codebereiche

| Bereich | Verantwortung |
|---|---|
| `src/bunkerfrequenz/domain/` | Character State, Progression, Trait-Auswirkungen |
| `src/bunkerfrequenz/application/` | Action-/Profil-/Recovery-Use-Cases, Presentation-Capabilities, Command-Dispatcher und bestätigte Eventabfrage |
| `src/bunkerfrequenz/infrastructure/` | Journal, State, Snapshot, atomare Speicherung und Recovery |
| `src/bunkerfrequenz/presentation/` | Character-/Biografieprojektion, lokaler State, Feedback, A4/A3, Ranking/Network und Action-Auswahl; keine Domain-Writes |

Wichtige Presentation-Dateien:

- `src/bunkerfrequenz/application/presentation_events.py` – detached Abfrage bestätigter Journal-Event-IDs.
- `src/bunkerfrequenz/presentation/state.py` – lokaler View-/Filter-/Dismiss-/Reduced-Motion-State.
- `src/bunkerfrequenz/presentation/feedback.py` – deterministisches Progressionsfeedback.
- `src/bunkerfrequenz/presentation/components.py` – acht gemeinsame frameworkfreie Character-Forge-Komponenten.
- `src/bunkerfrequenz/presentation/a4_ops_deck.py` – A4-Ops-Deck-View-Model, Primäraktionsvertrag und aktuelle Capability-Revalidierung.
- `src/bunkerfrequenz/presentation/a3_cinematic_forge.py` – A3-Komposition auf dem validierten A4-Vertrag.
- `src/bunkerfrequenz/presentation/ranking_network.py` – Ranking-/Network-Projektion aus bestätigten Daten.
- `src/bunkerfrequenz/presentation/action_selection.py` – 20 Manifest-Actions als Auswahl + expliziter Builder für dispatcher-fertige `action.execute`-Commands.
- `content/de/ui/actions.json` – sichtbare Action-Namen und Ressourcenhinweis.
- `content/de/ui/feedback.json` – sichtbare Feedbacktexte.
- `content/de/ui/character_forge.json` – Character-Forge-, Workflow-, Ranking- und Cinematic-Texte.
- `manifests/ANIMATION_MANIFEST.json` – nicht blockierende Entwicklungsanimationen und Fallbacks.
- `manifests/RANKING_NETWORK_MANIFEST.json` – Ranking-/Network-Regeln.

`__init__.py`-Dateien exportieren vorhandene Funktionen; sie dürfen keine zweite Fachimplementierung enthalten.

## Tests

| Bereich | Zweck |
|---|---|
| `tests/runtime/` | Character, Action, Persistence, Recovery, Resonanz, Command-Dispatcher und bestätigte Eventabfrage |
| `tests/presentation/` | Projection, A4/A3, Feedback, Ranking/Network, Action-Auswahl und Dispatcher-Kompatibilität |
| `tests/gameplay/` | Action-Vertrag |
| `tests/simulation/` | reproduzierbare Progressions-/Balance-Regression |
| `tools/repository_health.py` | repositoryweite Struktur-/Info-/Export-/Merge-Guard-Prüfung |

Für 0.7.1 sind insbesondere `tests/presentation/test_action_selection.py` und `tests/presentation/test_a4_ops_deck.py` relevant.

## Remote-CI

- `runtime-core.yml`: Runtime-/Domain-/Application-/Infrastructure-Gate; liefert bei jedem PR den Check `runtime-core`.
- `presentation-core.yml`: Presentation und zugehörige Application-Grenze; liefert bei jedem PR den Check `presentation-core`.
- `repository-health.yml`: Repository-/Merge-Guard; liefert bei jedem PR den Check `repository-health`.

Für `main` sollen alle drei Check-IDs als Required Checks gelten. Der PR-Head muss zusätzlich den aktuellen Base-Branch enthalten. Der versehentliche PR #32 ist der dokumentierte Negativfall, gegen den diese Schicht eingeführt wurde.

## Maschinenlesbare Verträge

### Manifeste

- **Charakter/Entwicklung:** `CHARAKTER`, `SKILL`, `TRAIT`, `TRAIT_ENGINE`, `PROGRESSION`, `LEVEL`, `BIOGRAFIE`
- **Aktionen/Laufzeit:** `ACTION`, `RUNTIME`, `JOURNAL`
- **Speicherung/Zeit:** `PERSISTENCE`, `SAVEFORMAT`, `MIGRATION`, `ZEIT`, `SYNC`
- **Darstellung/Text:** `UI`, `ANIMATION`, `TEXT`, `RANKING_NETWORK`
- **Projektsteuerung:** `ARCHITEKTUR`, `TEST`, `RELEASE`, `REPOSITORY_GUARD`

Alle liegen unter `manifests/`.

### Schemas

`schemas/` definiert Datenformen; Manifeste liefern die fachlichen Werte. Ein Schema ist keine zweite Balance- oder Storyquelle.

## Inhalte, Tools und Berichte

- `content/de/characters.json` und `level_titles.json` enthalten deutsche Spielinhalte.
- `content/de/ui/` enthält alle sichtbaren Character-Forge-/Action-/Feedbacktexte.
- `tools/validate_action_contract.py` prüft den Action-Vertrag.
- `tools/simulate_characters/progression_simulator.py` erzeugt reproduzierbare Balance-Läufe.
- `tools/repository_health.py` prüft den kanonischen Repository- und Merge-Vertrag aus `manifests/REPOSITORY_GUARD_MANIFEST.json`.
- `reports/` enthält freigegebene Prüfnachweise; Berichte sind keine Runtime-Eingabe.

## Verbindlichkeit bei Widersprüchen

1. Fach-/Architekturvertrag
2. Manifest/Schema
3. Runtime und Tests
4. `PROJEKTSTATUS.json`
5. `TODO.md`
6. README/Index
7. CHANGELOG-Historie
