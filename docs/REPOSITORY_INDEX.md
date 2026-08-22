# Ordner- und Dateiindex

## Zweck

Dieser Index beantwortet: **Wo liegt was und welche Datei ist zuständig?**

- Runtime-Baseline: `0.5.2-alpha.1`
- zuletzt validierte Feature-Iteration: `0.7.2 – kompletter Character-Forge-Vertical-Slice`
- aktive Feature-Iteration: `0.8.1 – Event State Foundation`
- nächster Feature-Schritt: `0.8.2 – Equipment & Economy`
- Repository-Sicherheit: `/safe-merge` + Main Integrity End-to-End validiert

Bei neuen oder entfernten öffentlichen Bereichen wird dieser Index in derselben Iteration angepasst.

## Einstieg im Wurzelverzeichnis

| Pfad | Rolle |
|---|---|
| `README.md` | visueller Projekteinstieg, Status und Schnellzugriff |
| `AGENTS.md` | verbindlicher Entwicklungs-, PR- und Merge-Ablauf |
| `TODO.md` | kanonische offene Arbeit in Ausführungsreihenfolge |
| `CHANGELOG.md` | fachliche Änderungshistorie |
| `VERSION.json` | letzte versionierte Runtime-/Produkt-Baseline |
| `PROJEKTMANIFEST.json` | zentrale Pfade und Projektmetadaten |
| `PROJEKTSTATUS.json` | aktive Iteration, Validierungsstand und nächstes Ziel |

## Ordnerübersicht

| Ordner | Inhalt | Einstieg |
|---|---|---|
| `.github/workflows/` | stabile Remote-CI-/Merge-/Integritäts-Gates | `runtime-core.yml`, `presentation-core.yml`, `repository-health.yml`, `safe-merge.yml`, `main-integrity.yml` |
| `content/` | lokalisierte sichtbare Inhalte | `content/de/` |
| `docs/` | Spieleranleitung, Fachverträge, Erklärungen und Navigation | `SPIELERANLEITUNG.md`, `EVENT_STATE_0.8.1.md`, `GAME_SCHEMA.md` |
| `manifests/` | kanonische Kataloge und maschinenlesbare Regeln | `EVENT_STATE_MANIFEST.json`, `ARCHITEKTUR_MANIFEST.json` |
| `reports/` | reproduzierbare Prüfnachweise | `RUNTIME_VALIDATION_0.5.2.json` |
| `schemas/` | JSON-Strukturverträge | `event_state.schema.json`, `character_state.schema.json` |
| `src/` | headless Spielkern und Presentation | `src/bunkerfrequenz/` |
| `tests/` | Vertrags-, Runtime-, Simulation-, Presentation- und Repository-Tests | Unterordner nach Bereich |
| `tools/` | kleine ausführbare Entwicklerwerkzeuge | `validate_action_contract.py`, `repository_health.py`, `github_merge_guard.py`, `github_merge_guard_retry.py` |

## Dokumentation

| Datei | Thema |
|---|---|
| `docs/SPIELERANLEITUNG.md` | laienfreundlicher Spielablauf, Energie/Stress, Progression, Autosave, Undo und aktuelle Grenzen |
| `docs/EVENT_STATE_0.8.1.md` | EventState, Phasenmaschine, Safety-Gate, Journal, Blockkoexistenz und 0.8.2/0.8.3-Grenze |
| `docs/GAME_SCHEMA.md` | Gesamtbild von Spiel, Daten und Ereignisfluss |
| `docs/REPOSITORY_RULES.md` | Ablage, Informationshierarchie und PR-Lebenszyklus |
| `docs/REPOSITORY_GUARD.md` | Merge-Guard, Repository Health, `/safe-merge`, Main Integrity und Zielpolicy für `main` |
| `docs/SAFE_MERGE.md` | laienfreundliche Bedienung und Fehlerbilder des validierten `/safe-merge`-Pfads |
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
| `src/bunkerfrequenz/domain/` | Character State, Event State, Progression, Trait-Auswirkungen und Ressourcen-/Eventinvarianten |
| `src/bunkerfrequenz/application/` | Character-/Event-/Profil-/Recovery-Use-Cases, Blockkoordination, Character-Forge-Session, Biografieableitung, Capabilities und Command-Dispatcher |
| `src/bunkerfrequenz/infrastructure/` | Journal, State, Snapshot, atomare Speicherung und Recovery |
| `src/bunkerfrequenz/presentation/` | Character-/Biografieprojektion, lokaler State, Feedback, A4/A3, Ranking/Network und Action-Auswahl; keine Domain-Writes |

### Wichtige 0.8.1-Dateien

- `src/bunkerfrequenz/domain/event.py` – kanonischer `EventState`, strikte Feldvalidierung und Phasenmaschine.
- `src/bunkerfrequenz/application/event_state_service.py` – Event-Erstellung, Planungsupdates, Phasenwechsel, Idempotenz und Stale-Revision-Schutz.
- `src/bunkerfrequenz/application/state_blocks.py` – ersetzt genau einen abgeleiteten Save-Block und erhält alle anderen.
- `src/bunkerfrequenz/application/game_recovery.py` – kombiniertes Character+Event-Journal-Replay.
- `manifests/EVENT_STATE_MANIFEST.json` – maschinenlesbarer EventState- und Phasenvertrag.
- `schemas/event_state.schema.json` – Strukturvertrag für serialisierten EventState.
- `tests/runtime/test_event_state.py` – Domain-, Journal-, Koexistenz- und Fault-Injection-Regressionen.
- `docs/EVENT_STATE_0.8.1.md` – verbindliche fachliche Beschreibung.

### Wichtige 0.7.2-Dateien

- `src/bunkerfrequenz/application/action_resolver.py` – deterministische Action-Auflösung inklusive Energie-/Stresswirkung.
- `src/bunkerfrequenz/application/character_action_service.py` – atomarer Action-/Progressions-/Biografie-Commit; erhält seit 0.8.1 andere Save-Blöcke.
- `src/bunkerfrequenz/application/action_biography.py` – manifestgetriebene Biografieentscheidung aus Action-Ergebnis und Wichtigkeit.
- `src/bunkerfrequenz/application/character_forge_session.py` – bestätigter Character-Forge-Ablauf, 60-Sekunden-Autosave/Snapshot und Reload.
- `src/bunkerfrequenz/application/recovery_service.py` – Character-Replay inklusive `character.resources_changed`.
- `src/bunkerfrequenz/presentation/action_selection.py` – 20 Manifest-Actions mit echten Ressourcenwerten + Builder für dispatcher-fertige `action.execute`-Commands.
- `content/de/ui/actions.json` – sichtbare Action-Namen und Ressourcenhinweise.
- `content/de/ui/biography.json` – sichtbare Texte für actionbasierte Biografieeinträge.
- `content/de/ui/feedback.json` – sichtbare Progressionsfeedbacktexte.

Weitere zentrale Presentation-Dateien:

- `src/bunkerfrequenz/application/presentation_events.py` – detached Abfrage bestätigter Journal-Event-IDs.
- `src/bunkerfrequenz/presentation/state.py` – lokaler View-/Filter-/Dismiss-/Reduced-Motion-State.
- `src/bunkerfrequenz/presentation/feedback.py` – deterministisches Progressionsfeedback.
- `src/bunkerfrequenz/presentation/components.py` – acht gemeinsame frameworkfreie Character-Forge-Komponenten.
- `src/bunkerfrequenz/presentation/a4_ops_deck.py` – A4-Ops-Deck-View-Model, Primäraktionsvertrag und aktuelle Capability-Revalidierung.
- `src/bunkerfrequenz/presentation/a3_cinematic_forge.py` – A3-Komposition auf dem validierten A4-Vertrag.
- `src/bunkerfrequenz/presentation/ranking_network.py` – Ranking-/Network-Projektion aus bestätigten Daten.
- `content/de/ui/character_forge.json` – Character-Forge-, Workflow-, Ranking- und Cinematic-Texte.
- `manifests/ANIMATION_MANIFEST.json` – nicht blockierende Entwicklungsanimationen und Fallbacks.
- `manifests/RANKING_NETWORK_MANIFEST.json` – Ranking-/Network-Regeln.

`__init__.py`-Dateien exportieren vorhandene Funktionen; sie dürfen keine zweite Fachimplementierung enthalten.

## Repository-Sicherheit

- `.github/workflows/repository-health.yml` – Repository-/Merge-Vertrag auf jedem PR und `main`.
- `.github/workflows/safe-merge.yml` – autorisierter normaler Mergeweg über `/safe-merge`.
- `.github/workflows/main-integrity.yml` – nachgelagerte Main-Provenienzprüfung.
- `tools/repository_health.py` – Struktur-, Info-, Export- und Workflow-Prüfung.
- `tools/github_merge_guard.py` – Kandidatenprüfung, exakt-einmal-Merge und Main-Provenienz.
- `tools/github_merge_guard_retry.py` – begrenzter Retry ausschließlich für nachgelagerte GitHub-Provenienz-Leseabfragen.
- `manifests/REPOSITORY_GUARD_MANIFEST.json` – kanonische Sicherheitsregeln und geschützte Guard-Pfade.
- `tests/repository/` – Regressionen für Guard, Safe Merge und Eventual Consistency.

Der validierte `/safe-merge`-End-to-End-Nachweis ist PR #38 mit `SAFE MERGE PASS` und Merge `e1155db2d2a7eaddd313127d89635a1a3dac3ce6`. Der spätere Main-Integrity-Incident #40 für den Direkt-Commit `fb96a489...` wurde analysiert und geschlossen. Der versehentliche leere `tmp`-Direktcommit wurde über PR #47 mit drei grünen Gates und `SAFE MERGE PASS` entfernt.

## Tests

| Bereich | Zweck |
|---|---|
| `tests/runtime/` | Character, EventState, Action, Ressourcen, Persistence, Recovery, Resonanz, Session, Command-Dispatcher und bestätigte Eventabfrage |
| `tests/presentation/` | Projection, A4/A3, Feedback, Ranking/Network, Action-Auswahl, kompletter 0.7.2-Vertical-Slice und Dispatcher-Kompatibilität |
| `tests/gameplay/` | Action-Vertrag inklusive Ressourcenpflicht |
| `tests/simulation/` | reproduzierbare Progressions-/Balance-Regression |
| `tests/repository/` | Merge-Guard, Safe-Merge-Vertrag, Retry und Repository-Security |

Für 0.8.1 ist insbesondere `tests/runtime/test_event_state.py` relevant. Es prüft:

- EventState-Struktur und Roundtrip
- Eindeutigkeit von Acts/Crew/Equipment
- Zeitfenster
- Phasen-/Safety-Gates
- Journal-Idempotenz
- Stale-Revision
- Character↔Event-Blockerhalt
- Fault-Injection + kombiniertes Recovery-Replay

Validierte 0.7.2-Referenz PR #41 / Head `5f7ded400a5fca1ee25307797628ab2584de9812`:

- Runtime Core `32533954380` – grün
- Presentation Core `32533954387` – grün
- Repository Health `32533954406` – grün

## Remote-CI

- `runtime-core.yml`: Runtime-/Domain-/Application-/Infrastructure-Gate; liefert bei jedem PR den Check `runtime-core`.
- `presentation-core.yml`: Presentation und zugehörige Application-Grenze; liefert bei jedem PR den Check `presentation-core`.
- `repository-health.yml`: Repository-/Merge-Guard; liefert bei jedem PR den Check `repository-health`.
- `safe-merge.yml`: prüft normale Merge-Kandidaten unmittelbar vor Merge erneut und führt genau einen Merge-API-Aufruf aus.
- `main-integrity.yml`: prüft Main-Merge-Provenienz und eröffnet bei Fehler einen Integritäts-Incident.

Für normale PRs nach `main` gilt `/safe-merge`. Der PR-Head muss den aktuellen Base-Branch enthalten, alle drei Kern-Gates müssen grün und alle Review-Threads gelöst sein. Native GitHub-Branch-Protection bleibt eine zusätzliche noch offene serverseitige Härtung.

## Maschinenlesbare Verträge

### Manifeste

- **Charakter/Entwicklung:** `CHARAKTER`, `SKILL`, `TRAIT`, `TRAIT_ENGINE`, `PROGRESSION`, `LEVEL`, `BIOGRAFIE`
- **Event/Aktionen/Laufzeit:** `EVENT_STATE`, `ACTION`, `RUNTIME`, `JOURNAL`
- **Speicherung/Zeit:** `PERSISTENCE`, `SAVEFORMAT`, `MIGRATION`, `ZEIT`, `SYNC`
- **Darstellung/Text:** `UI`, `ANIMATION`, `TEXT`, `RANKING_NETWORK`
- **Projektsteuerung:** `ARCHITEKTUR`, `TEST`, `RELEASE`, `REPOSITORY_GUARD`

Alle liegen unter `manifests/`.

### Schemas

`schemas/` definiert Datenformen; Manifeste liefern die fachlichen Werte. Ein Schema ist keine zweite Balance- oder Storyquelle.

## Inhalte, Tools und Berichte

- `content/de/characters.json` und `level_titles.json` enthalten deutsche Spielinhalte.
- `content/de/ui/` enthält alle sichtbaren Character-Forge-/Action-/Biografie-/Feedbacktexte.
- `tools/validate_action_contract.py` prüft den Action-Vertrag.
- `tools/simulate_characters/progression_simulator.py` erzeugt reproduzierbare Balance-Läufe.
- `tools/repository_health.py` prüft den kanonischen Repository- und Merge-Vertrag aus `manifests/REPOSITORY_GUARD_MANIFEST.json`.
- `tools/github_merge_guard.py` und `tools/github_merge_guard_retry.py` implementieren den validierten sicheren Mergeweg.
- `reports/` enthält freigegebene Prüfnachweise; Berichte sind keine Runtime-Eingabe.

## Verbindlichkeit bei Widersprüchen

1. Fach-/Architekturvertrag
2. Manifest/Schema
3. Runtime und Tests
4. `PROJEKTSTATUS.json`
5. `TODO.md`
6. README/Index
7. CHANGELOG-Historie
