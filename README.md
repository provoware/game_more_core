# BUNKERFREQUENZ

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Aktive Entwicklung 0.6.3 Presentation" src="https://img.shields.io/badge/Aktive_Entwicklung-0.6.3_Presentation-7dff00">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
</p>

> **Techno-/FreeTekno-Crew-RPG:** Verhalten, Training, Entscheidungen und Krisen formen individuelle Charaktere. Der headless Character-/Action-/Persistence-Kern ist vorhanden; Character Forge, Wirtschaft und Synchronisation werden modular darauf aufgebaut.

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

## Status auf einen Blick

| Bereich | Stand |
|---|---|
| letzte versionierte Runtime-Baseline | `0.5.2-alpha.1` |
| aktive Entwicklungsiteration | `0.6.3 – gemeinsame Komponenten + A4 Ops Deck` |
| Runtime | Character State, Actions, Traits, Resonanz, Journal, Snapshot, Recovery |
| Presentation | Character-/Biografieprojektion, bestätigte Capabilities/Commands, lokaler immutable State und bestätigtes Feedback |
| grafische Spieloberfläche | noch nicht implementiert; A4 Ops Deck ist nächster Schritt |
| Telegram/Sync | geplant, noch nicht implementiert |
| Wirtschaft/Clubs | geplant, noch nicht implementiert |

**Wichtig:** `VERSION.json` beschreibt die letzte versionierte Runtime-Baseline. Die laufende nächste Entwicklungsiteration steht in `PROJEKTSTATUS.json` und `TODO.md`. Dadurch wird eine noch nicht abgeschlossene 0.6-Arbeit nicht fälschlich als neues Release ausgegeben.

## Schnellzugriff

| Ziel | Datei |
|---|---|
| aktueller Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Arbeitsschritte | [`TODO.md`](TODO.md) |
| Architektur und Grenzen | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Spiel-/Datenfluss verstehen | [`docs/GAME_SCHEMA.md`](docs/GAME_SCHEMA.md) |
| 0.6 Presentation-Schnitt | [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md) |
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

### Presentation-Foundation 0.6

- gemeinsamer Presentation-Vertrag für A4 Ops Deck und A3 Cinematic Forge
- schreibgeschützte Character-Projektion
- getrennte Biografieprojektion aus validierten Journal-Ereignissen
- bestätigte Application-Capabilities und ein zentraler Schreibcommand-Dispatcher
- immutable lokaler Presentation-State für Ansicht, Filter, Feedback-Dismiss und Reduced Motion
- bestätigte Eventabfrage über die Application-Grenze statt direktem Journalzugriff aus Presentation
- deterministisches Feedback für Level-, Skill-, Trait-, Spezialisierungs- und Resonanzsprünge
- sichtbare Feedbacktexte vollständig in `content/de/ui/feedback.json` ausgelagert
- keine sichtbaren Texte in der Spiellogik
- eigener zielgerichteter Presentation-CI-Gate

## Datenfluss

```text
Content + Manifeste
        │
        ▼
Spielaktion ──► deterministische Auflösung ──► Domain-Ereignisse
                                                   │
                                                   ▼
                                       Persistence Kernel
                                         │             │
                                         ▼             ▼
                                      Journal        Zustand
                                         │             │
                                         └──────┬──────┘
                                                ▼
                              Application-Capabilities / bestätigte Events
                                                │
                                                ▼
                                   schreibgeschützte Projection
                                                │
                                     lokaler Presentation-State
                                                │
                                      ┌─────────┴─────────┐
                                      ▼                   ▼
                                 A4 Ops Deck      A3 Cinematic Forge
```

A4 und A3 dürfen Daten später unterschiedlich anordnen, aber keine unterschiedlichen Fachregeln besitzen.

## Architekturgrenzen

| Bereich | Verantwortung | Darf nicht |
|---|---|---|
| `domain` | Charakter, Progression, Traits | UI oder Infrastruktur kennen |
| `application` | Use Cases, Capabilities, Commands und bestätigte Abfragen koordinieren | Persistenz umgehen |
| `infrastructure` | Journal, Save, Snapshot, Recovery | sichtbare UI-Texte verwalten |
| `presentation` | schreibgeschützte Anzeigeprojektionen und rein lokalen UI-State | Domain-Zustand direkt verändern |
| `content` | sichtbare/lokalisierte Texte | technische Regeln ersetzen |

## Gezielte Prüfungen

### Runtime

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Die Runtime-Baseline `0.5.2-alpha.1` wurde im zugehörigen PR zusätzlich über den GitHub-Workflow **Runtime Core** erfolgreich geprüft.

### Presentation

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Für Änderungen an der Presentation existiert zusätzlich `.github/workflows/presentation-core.yml`. 0.6.2 bestand auf PR #26 sowohl Runtime Core (`32511953788`) als auch Presentation Core (`32511953619`).

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
- [`docs/DATENMODELL.md`](docs/DATENMODELL.md)

## Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Parallelimplementierungen derselben kanonischen Datei werden nicht weitergeführt. Relevante CI-Gates müssen vor einem Merge grün sein. Details stehen in [`AGENTS.md`](AGENTS.md).
