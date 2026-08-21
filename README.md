# BUNKERFREQUENZ

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Aktive Entwicklung 0.6.2 Presentation" src="https://img.shields.io/badge/Aktive_Entwicklung-0.6.2_Presentation-7dff00">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
</p>

> **Techno-/FreeTekno-Crew-RPG:** Verhalten, Training, Entscheidungen und Krisen formen individuelle Charaktere. Der headless Character-/Action-/Persistence-Kern ist vorhanden; Character Forge, Wirtschaft und Synchronisation werden modular darauf aufgebaut.

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

## Status auf einen Blick

| Bereich | Stand |
|---|---|
| letzte versionierte Runtime-Baseline | `0.5.2-alpha.1` |
| aktive Entwicklungsiteration | `0.6.2 – lokaler Presentation-State + bestätigtes Feedback` |
| Runtime | Character State, Actions, Traits, Resonanz, Journal, Snapshot, Recovery |
| Application-Grenze | Capabilities + zentraler Dispatcher für Profil, Undo und Actions abgeschlossen |
| Presentation | Character-/Biografieprojektion mit bestätigten Capabilities; lokaler State/Feedback folgt |
| grafische Spieloberfläche | noch nicht implementiert |
| Telegram/Sync | geplant, noch nicht implementiert |
| Wirtschaft/Clubs | geplant, noch nicht implementiert |

**Wichtig:** `VERSION.json` beschreibt die letzte versionierte Runtime-Baseline. Die laufende 0.6-Entwicklung steht in `PROJEKTSTATUS.json` und `TODO.md`. Dadurch wird eine noch nicht abgeschlossene Presentation-Stufe nicht fälschlich als Release ausgegeben.

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
- bestätigte Application-Capabilities: Profil bearbeiten, Undo möglich, Action ausführbar
- ein zentraler Command-Dispatcher für `profile.update`, `profile.undo_last`, `action.execute`
- wiederholte bestätigte UI-Schreibaktionen werden idempotent behandelt
- deutsche Skill-, Trait-, Effekt-, Konsequenz-, Spezialisierungs- und Stufenkataloge
- keine sichtbaren Texte in der Spiellogik
- Runtime Core und Presentation Core als getrennte zielgerichtete CI-Gates

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
                              Application-Capabilities / Commands
                                                │
                                                ▼
                                   schreibgeschützte Projection
                                                │
                                      ┌─────────┴─────────┐
                                      ▼                   ▼
                                 A4 Ops Deck      A3 Cinematic Forge
```

A4 und A3 dürfen Daten später unterschiedlich anordnen, aber keine unterschiedlichen Fachregeln oder Schreibwege besitzen.

## Architekturgrenzen

| Bereich | Verantwortung | Darf nicht |
|---|---|---|
| `domain` | Charakter, Progression, Traits | UI oder Infrastruktur kennen |
| `application` | Use Cases, Capabilities und Commands koordinieren | Persistenz umgehen oder UI-Layout erzeugen |
| `infrastructure` | Journal, Save, Snapshot, Recovery | sichtbare UI-Texte verwalten |
| `presentation` | schreibgeschützte Anzeigeprojektionen | Domain-Zustand direkt verändern |
| `content` | sichtbare/lokalisierte Texte | technische Regeln ersetzen |

## Gezielte Prüfungen

### Runtime

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Die Runtime-Baseline `0.5.2-alpha.1` und die 0.6.1-Application-Grenze wurden über **Runtime Core** erfolgreich geprüft.

### Presentation

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Die 0.6.1-Grenze wurde zusätzlich über **Presentation Core** erfolgreich geprüft.

### Verträge / Simulation

```bash
python3 tools/validate_action_contract.py
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Prüfungen werden risikobasiert ausgeführt; reine Status-/Dokumentänderungen lösen keine unnötigen Volltests aus.

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
