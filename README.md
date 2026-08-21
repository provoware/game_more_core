# BUNKERFREQUENZ

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Nächste Entwicklung 0.7.2 Character Forge" src="https://img.shields.io/badge/Nächste_Entwicklung-0.7.2_Character_Forge-7dff00">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
</p>

> **Techno-/FreeTekno-Crew-RPG:** Verhalten, Training, Entscheidungen und Krisen formen individuelle Charaktere. Runtime, Recovery, Character-Forge-Presentation, Ranking/Network und die erste A4-Action-Auswahl stehen als getestete Grundlage.

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

## Status auf einen Blick

| Bereich | Stand |
|---|---|
| letzte versionierte Runtime-Baseline | `0.5.2-alpha.1` |
| zuletzt abgeschlossene Feature-Iteration | `0.7.1 – A4 Action-Auswahl` |
| nächster logischer Feature-Schritt | `0.7.2 – Ressourcenwirkung + vollständiger Character-Forge-Ablauf` |
| Repository Guard | implementiert und remote validiert; GitHub-Branch-Protection für `main` noch extern zu aktivieren |
| Runtime | Character State, Actions, Traits, Resonanz, Journal, Snapshot, Recovery |
| A4 Ops Deck | validiert; geführter Workflow + Action-Auswahl |
| A3 Cinematic Forge | validiert; gleiche Komponenten/Commands wie A4 |
| Ranking / Network | validiert; Top 10/Alle, Skill-/Level-/Ruf-/Resonanzranking, bestätigte Network-Metriken |
| grafischer Renderer | noch kein Qt/Web/Game-Engine-Framework fest verdrahtet |
| Telegram/Sync | geplant, Transport-/Serverphase noch nicht implementiert |
| Wirtschaft/Clubs | geplant, noch nicht in der Runtime |

**Wichtig:** `VERSION.json` beschreibt weiterhin die letzte versionierte Runtime-Baseline. Die laufende Entwicklungsphase wird getrennt in `PROJEKTSTATUS.json` und `TODO.md` geführt.

## Schnellzugriff

| Ziel | Datei |
|---|---|
| aktueller Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Arbeitsschritte | [`TODO.md`](TODO.md) |
| Architektur und Grenzen | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Spiel-/Datenfluss verstehen | [`docs/GAME_SCHEMA.md`](docs/GAME_SCHEMA.md) |
| Repository Guard / Branch-Policy | [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md) |
| Presentation-Schnitt | [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md) |
| A4 Ops Deck | [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md) |
| A3 Cinematic Forge | [`docs/A3_CINEMATIC_FORGE_0.6.4.md`](docs/A3_CINEMATIC_FORGE_0.6.4.md) |
| Ranking / Network | [`docs/RANKING_NETWORK_0.6.5.md`](docs/RANKING_NETWORK_0.6.5.md) |
| Datei finden | [`docs/REPOSITORY_INDEX.md`](docs/REPOSITORY_INDEX.md) |
| Ablageregeln | [`docs/REPOSITORY_RULES.md`](docs/REPOSITORY_RULES.md) |
| als Entwickler übernehmen | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

## Was bereits funktioniert

### Character / Progression

- 11 Hauptfiguren mit identischer Startbasis und stabilen technischen IDs
- editierbare Namen, Alias, zusätzliche Spitznamen und Motto
- 16 Skills
- 165 individuelle Trait-Namen über 15 gemeinsame Effektfamilien
- Spezialisierungen mit Vor- und Nachteilen
- Level 1–50 und anschließend offene Resonanzränge
- deterministische Action Resolution

### Persistenz / Recovery

- append-only Journal mit Sequenz und SHA-256-Kette
- atomare Zustandsdateien
- 60-Sekunden-Autosave-Regel, dirty-only
- Snapshots und Journal-Replay
- Quarantäne beschädigter Journal-Tails
- Recovery Receipt
- kompensierender Ein-Schritt-Profil-Undo

### Character Forge / Presentation

- schreibgeschützte Character-/Biografieprojektion
- bestätigte Capabilities und ein zentraler Schreibcommand-Dispatcher
- immutable lokaler Presentation-State
- deterministisches bestätigtes Progressionsfeedback
- exakt acht gemeinsame frameworkfreie Komponenten
- A4 Ops Deck und A3 Cinematic Forge auf derselben Fachbasis
- nicht blockierende Level-/Skill-/Trait-/Spezialisierungs-/Resonanz-Cues mit Reduced-Motion-Fallback
- Ranking-/Network-Projektion ohne erfundene Presence-Daten
- A4-Auswahl für alle 20 Manifest-Actions mit Dauer, Voraussetzungen und erwarteter Skillwirkung
- Action-Auswahl erzeugt erst beim Ausführen einen vollständigen Dispatcher-Command mit `command_id` und `action_instance_id`
- A4 prüft `can_execute_action` beim Rendern erneut und sperrt stale Auswahlzustände fail-closed
- alle sichtbaren Texte liegen unter `content/de/ui/`

### Repository Guard

- `repository-health` prüft JSON, Python-Compile/Struktur, Merge-Konfliktmarker und Informationskonsistenz
- kanonische Presentation-Symbole und öffentliche Package-Exporte werden auf Eindeutigkeit geprüft
- versionsgebundene alte Feature-Branches werden gegen die aktive Iteration blockiert
- PR-Heads müssen den aktuellen Base-Branch enthalten
- `runtime-core`, `presentation-core` und `repository-health` liefern bei jedem Pull Request einen stabilen Check-Status
- Zielpolicy für `main` ist maschinenlesbar in `manifests/REPOSITORY_GUARD_MANIFEST.json`
- GitHub-Branch-Protection ist noch nicht technisch aktiviert, da die verbundene GitHub-Schnittstelle dafür keine sichere Schreibaktion bereitstellt

## Gemeinsamer Datenfluss

```text
Domain / Persistence
        ↓
Application
        ↓
Character Projection + bestätigtes Feedback
        ↓
PresentationState
        ↓
8 gemeinsame Komponenten
        ↓
   ┌──────────────┬─────────────────┐
   ▼              ▼                 ▼
 A4 Ops        A3 Cinematic     Ranking / Network
 Deck           Forge
   │
   ▼
Action-Auswahl → vollständiger action.execute-Command → Application
```

Presentation darf Fachzustand nicht direkt verändern. Schreibaktionen laufen über den bestehenden Application-Dispatcher.

## Architekturgrenzen

| Bereich | Verantwortung | Darf nicht |
|---|---|---|
| `domain` | Charakter, Progression, Traits | UI oder Infrastruktur kennen |
| `application` | Use Cases, Capabilities, Commands und bestätigte Abfragen | Persistenz umgehen |
| `infrastructure` | Journal, Save, Snapshot, Recovery | sichtbare UI-Texte verwalten |
| `presentation` | Projection, Komponenten, lokale Ansicht und Inszenierung | Domain-/Save-Zustand direkt verändern |
| `content` | sichtbare/lokalisierte Texte | technische Regeln ersetzen |

## Gezielte Prüfungen

### Runtime

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

### Presentation

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

### Repository Health

```bash
PYTHONPATH=src python3 -m compileall -q src tools/repository_health.py
PYTHONPATH=src python3 tools/repository_health.py
```

### Bisherige Remote-Abnahmen

- 0.6.3 / PR #28: Runtime Core `32514970109`, Presentation Core `32514970398`
- 0.6.4 / PR #29: Runtime Core `32516833552`, Presentation Core `32516833514`
- 0.6.5 / PR #30: Runtime Core `32517683276`, Presentation Core `32517683263`
- 0.7.1 / PR #31: Runtime Core `32519042006`, Presentation Core `32519041908`
- Repository Guard / PR #34 erster Implementierungs-Head: Runtime Core `32522336221`, Presentation Core `32522336259`, Repository Health `32522336287`

Der versehentliche PR #32 wurde trotz roter Compile-Gates gemergt und durch Reparatur-PR #33 vollständig aus dem kanonischen Baum entfernt. Der neue Repository Guard ist die technische Folgemaßnahme gegen dieselbe Fehlerklasse.

### Verträge / Simulation

```bash
python3 tools/validate_action_contract.py
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Fachliche Prüfungen bleiben risikobasiert. Für Pull Requests nach `main` liefern Runtime Core, Presentation Core und Repository Health jedoch immer einen eindeutigen Merge-Status.

## Verbindliche Dokumente

- [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md)
- [`docs/CHARACTER_CORE_0.5.md`](docs/CHARACTER_CORE_0.5.md)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md)
- [`docs/UI_UX_BLUEPRINT.md`](docs/UI_UX_BLUEPRINT.md)
- [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md)
- [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md)
- [`docs/A3_CINEMATIC_FORGE_0.6.4.md`](docs/A3_CINEMATIC_FORGE_0.6.4.md)
- [`docs/RANKING_NETWORK_0.6.5.md`](docs/RANKING_NETWORK_0.6.5.md)
- [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md)
- [`docs/DATENMODELL.md`](docs/DATENMODELL.md)

## Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Parallelimplementierungen derselben kanonischen Datei werden nicht weitergeführt. Für `main` müssen `runtime-core`, `presentation-core` und `repository-health` grün sein; der PR-Head muss den aktuellen Base-Stand enthalten. Details stehen in [`AGENTS.md`](AGENTS.md) und [`docs/REPOSITORY_GUARD.md`](docs/REPOSITORY_GUARD.md).
