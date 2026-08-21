# BUNKERFREQUENZ

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Aktive Entwicklung 0.6.4 Cinematic Forge" src="https://img.shields.io/badge/Aktive_Entwicklung-0.6.4_Cinematic_Forge-7dff00">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
</p>

> **Techno-/FreeTekno-Crew-RPG:** Verhalten, Training, Entscheidungen und Krisen formen individuelle Charaktere. Der robuste Runtime-Kern und der frameworkfreie Character-Forge-Unterbau stehen; A4 Ops Deck ist validiert, A3 Cinematic Forge wird auf exakt denselben Bausteinen umgesetzt.

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

## Status auf einen Blick

| Bereich | Stand |
|---|---|
| letzte versionierte Runtime-Baseline | `0.5.2-alpha.1` |
| aktive Entwicklungsiteration | `0.6.4 – A3 Cinematic Forge` |
| Runtime | Character State, Actions, Traits, Resonanz, Journal, Snapshot, Recovery |
| A4 Ops Deck | validiert und gemergt in PR #28 |
| A3 Cinematic Forge | gemeinsame Komponenten, Skillnetz/Traits/Animation-Cues in Arbeit |
| grafischer Renderer | noch kein Qt/Web/Game-Engine-Framework fest verdrahtet |
| Telegram/Sync | geplant, noch nicht implementiert |
| Wirtschaft/Clubs | geplant, noch nicht implementiert |

**Wichtig:** `VERSION.json` beschreibt weiterhin die letzte versionierte Runtime-Baseline. Die 0.6.x-Presentation-Entwicklung wird getrennt in `PROJEKTSTATUS.json` und `TODO.md` geführt.

## Schnellzugriff

| Ziel | Datei |
|---|---|
| aktueller Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Arbeitsschritte | [`TODO.md`](TODO.md) |
| Architektur und Grenzen | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Spiel-/Datenfluss verstehen | [`docs/GAME_SCHEMA.md`](docs/GAME_SCHEMA.md) |
| 0.6 Presentation-Schnitt | [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md) |
| A4 Ops Deck 0.6.3 | [`docs/A4_OPS_DECK_0.6.3.md`](docs/A4_OPS_DECK_0.6.3.md) |
| Datei finden | [`docs/REPOSITORY_INDEX.md`](docs/REPOSITORY_INDEX.md) |
| Ablageregeln | [`docs/REPOSITORY_RULES.md`](docs/REPOSITORY_RULES.md) |
| als Entwickler übernehmen | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

## Was bereits funktioniert

### Character / Progression

- 11 Hauptfiguren mit identischer Startbasis und stabilen technischen IDs
- editierbare Namen, Alias, zusätzliche Spitznamen und Motto im Domain-/Profilmodell
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
- sicherer kompensierender Ein-Schritt-Profil-Undo

### Character Forge Presentation

- schreibgeschützte Character-/Biografieprojektion
- bestätigte Capabilities und ein zentraler Schreibcommand-Dispatcher
- immutable lokaler Presentation-State
- bestätigtes deterministisches Progressionsfeedback
- exakt acht gemeinsame frameworkfreie Komponenten
- A4 Ops Deck als geführter Workflow
- Primäraktionen direkt dispatcher-kompatibel
- A3 Cinematic Forge verwendet dieselben Komponenten und denselben Action-Normalisierer
- nicht blockierende Animation-Cues für Level, Skill, Trait, Spezialisierung und Resonanz
- Reduced Motion ersetzt Bewegung durch statische Fallbacks
- alle sichtbaren Texte aus `content/de/ui/`

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
   ┌────┴────┐
   ▼         ▼
 A4 Ops    A3 Cinematic
 Deck       Forge
```

A3 und A4 dürfen Daten anders anordnen und inszenieren, aber keine unterschiedlichen Fachregeln, Commands oder Persistence-Wege besitzen.

## Architekturgrenzen

| Bereich | Verantwortung | Darf nicht |
|---|---|---|
| `domain` | Charakter, Progression, Traits | UI oder Infrastruktur kennen |
| `application` | Use Cases, Capabilities, Commands und bestätigte Abfragen | Persistenz umgehen |
| `infrastructure` | Journal, Save, Snapshot, Recovery | sichtbare UI-Texte verwalten |
| `presentation` | Projection, Komponenten, lokale Ansicht und Inszenierungs-Cues | Domain-/Save-Zustand direkt verändern |
| `content` | sichtbare/lokalisierte Texte | technische Regeln ersetzen |

## Gezielte Prüfungen

### Runtime

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

### Presentation

```bash
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

0.6.3 wurde auf PR #28 mit Runtime Core `32514970109` und Presentation Core `32514970398` erfolgreich geprüft.

### Verträge / Simulation

```bash
python3 tools/validate_action_contract.py
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Prüfungen werden risikobasiert ausgeführt; nicht jede Dokumentänderung löst unnötig alle Tests aus.

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
- [`docs/DATENMODELL.md`](docs/DATENMODELL.md)

## Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Parallelimplementierungen derselben kanonischen Datei werden nicht weitergeführt. Relevante CI-Gates müssen vor einem Merge grün sein. Details stehen in [`AGENTS.md`](AGENTS.md).
