# BUNKERFREQUENZ

<p>
  <img alt="Runtime Baseline 0.5.2 alpha 1" src="https://img.shields.io/badge/Runtime_Baseline-0.5.2--alpha.1-ff4d00">
  <img alt="Aktive Entwicklung 0.6.3 A4 Ops Deck" src="https://img.shields.io/badge/Aktive_Entwicklung-0.6.3_A4_Ops_Deck-7dff00">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
</p>

> **Techno-/FreeTekno-Crew-RPG:** Verhalten, Training, Entscheidungen und Krisen formen individuelle Charaktere. Der robuste Character-/Action-/Persistence-Kern und die bestätigte Presentation-Datenpipeline stehen; als Nächstes entsteht daraus der intuitive A4-Ops-Deck-Workflow.

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

## Status auf einen Blick

| Bereich | Stand |
|---|---|
| letzte versionierte Runtime-Baseline | `0.5.2-alpha.1` |
| aktive Entwicklungsiteration | `0.6.3 – gemeinsame Komponenten + A4 Ops Deck` |
| Runtime | Character State, Actions, Traits, Resonanz, Journal, Snapshot, Recovery |
| Application | bestätigte Capabilities, zentraler Schreibcommand-Dispatcher, bestätigte Eventabfrage |
| Presentation | Character-/Biografieprojektion, lokaler immutable State, bestätigtes Progressionsfeedback |
| grafische Spieloberfläche | noch kein Framework; A4-View-Model ist nächster Schritt |
| Telegram/Sync | geplant, noch nicht implementiert |
| Wirtschaft/Clubs | geplant, noch nicht implementiert |

`VERSION.json` beschreibt weiterhin die letzte versionierte Runtime-Baseline. Die laufende 0.6-Presentation-Entwicklung wird bewusst separat in `PROJEKTSTATUS.json` und `TODO.md` geführt.

## Schnellzugriff

| Ziel | Datei |
|---|---|
| aktueller Entwicklungsstand | [`PROJEKTSTATUS.json`](PROJEKTSTATUS.json) |
| nächste Arbeitsschritte | [`TODO.md`](TODO.md) |
| Architektur und Grenzen | [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md) |
| Spiel-/Datenfluss | [`docs/GAME_SCHEMA.md`](docs/GAME_SCHEMA.md) |
| Character-Forge-Presentation | [`docs/PRESENTATION_CONTRACT_0.6.md`](docs/PRESENTATION_CONTRACT_0.6.md) |
| Datei finden | [`docs/REPOSITORY_INDEX.md`](docs/REPOSITORY_INDEX.md) |
| Entwicklungsregeln | [`AGENTS.md`](AGENTS.md) |
| Entwicklerübernahme | [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md) |
| Änderungshistorie | [`CHANGELOG.md`](CHANGELOG.md) |

## Was bereits funktioniert

### Character / Progression

- 11 Hauptfiguren mit identischer Startbasis und stabilen technischen IDs
- editierbare Namen, Alias, zusätzliche Spitznamen und Motto
- 16 Skills, 165 individuelle Trait-Namen über 15 Effektfamilien
- Spezialisierungen mit Vorteilen und Konsequenzen
- Level 1–50 plus offene Resonanzränge
- deterministische Action Resolution

### Persistenz / Recovery

- append-only Journal mit Sequenz und SHA-256-Kette
- atomare Zustandsdateien und 60-Sekunden-Autosave-Vertrag
- Snapshots, Journal-Replay und Quarantäne beschädigter Journal-Tails
- Recovery Receipt
- sicherer kompensierender Ein-Schritt-Profil-Undo

### Application-/Presentation-Grenze

- Application liefert `can_edit_profile`, `can_undo_profile`, `can_execute_action` fail-closed
- genau ein Dispatcher für `profile.update`, `profile.undo_last`, `action.execute`
- idempotente Wiederholung verhindert Doppelbuchungen
- Presentation liest Persistence nicht direkt
- `get_confirmed_events(...)` liefert detached Records für bestätigte Commit-Event-IDs

### Presentation 0.6.2

- immutable lokaler State für `overview`, `skills_traits`, `biography`
- Biografie-Filter nutzt den kanonischen Manifest-Katalog
- lokale `view.select`, `biography.filter`, `feedback.dismiss` ohne Save-/Journal-Wirkung
- deterministische Feedback-IDs aus bestätigten Event-IDs
- Feedback für Level-, Skill-, Trait-, Spezialisierungs- und Resonanzsprünge
- alle sichtbaren Feedbacktexte ausgelagert unter `content/de/ui/feedback.json`
- Reduced Motion verändert nur Darstellung, nicht Spielzustand
- End-to-End-Pfad `Command → Commit → bestätigte Events → Feedback → Projection` getestet

## Kanonischer Datenfluss

```text
Content + Manifeste
        │
        ▼
Spielaktion ─► Domain/Action Resolver ─► Application Service
                                      │
                                      ▼
                               Persistence Kernel
                                │            │
                                ▼            ▼
                             Journal       Zustand
                                │            │
                                └─────┬──────┘
                                      ▼
                           bestätigte Application-Abfragen
                              │                 │
                              ▼                 ▼
                         Capabilities      Eventrecords
                              │                 │
                              └───────┬─────────┘
                                      ▼
                          schreibgeschützte Projection
                                      │
                          lokaler Presentation-State
                                      │
                          bestätigtes Progressionsfeedback
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
                  A4 Ops Deck                A3 Cinematic Forge
                  0.6.3 nächster Schritt      0.6.4 danach
```

## Architekturgrenzen

| Bereich | Verantwortung | Darf nicht |
|---|---|---|
| `domain` | Charakter, Progression, Traits | UI/Infrastruktur kennen |
| `application` | Use Cases, Capabilities, Commands, bestätigte Abfragen | UI-Layout erzeugen oder Persistenz umgehen |
| `infrastructure` | Journal, Save, Snapshot, Recovery | sichtbare UI-Texte verwalten |
| `presentation` | Anzeigeprojektionen und rein lokaler UI-State | Domain-/Save-Zustand direkt verändern |
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

Remote-Gates:

- `.github/workflows/runtime-core.yml`
- `.github/workflows/presentation-core.yml`

0.6.2 wurde auf PR #26 mit Runtime Core `32511953788` und Presentation Core `32511953619` erfolgreich geprüft.

### Verträge / Simulation

```bash
python3 tools/validate_action_contract.py
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Prüfungen werden risikobasiert ausgeführt. Reine Status-/Dokumentänderungen lösen keine unnötigen Volltests aus.

## Entwicklungsregel

Eine Iteration bearbeitet eine klar begründete Zielstelle. Für dieselbe kanonische Zielstelle existiert höchstens ein aktiver Implementierungs-PR. Relevante CI-Gates müssen vor Merge grün sein. Details: [`AGENTS.md`](AGENTS.md).
