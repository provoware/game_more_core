# BUNKERFREQUENZ

<p>
  <img alt="Version 0.5.2 alpha 1" src="https://img.shields.io/badge/Version-0.5.2--alpha.1-ff4d00">
  <img alt="Phase Progression Effects und Resonance" src="https://img.shields.io/badge/Phase-Progression_%26_Resonance-7dff00">
  <img alt="Runtime Python Standardbibliothek" src="https://img.shields.io/badge/Runtime-Python_Standardbibliothek-00c2ff">
  <img alt="Status Headless Core" src="https://img.shields.io/badge/Status-Headless_Core-222222">
</p>

> **Techno-/FreeTekno-Crew-RPG:** Charaktere, Entscheidungen und Krisen formen eine Crew. Der deterministische Kern läuft bereits ohne grafische Oberfläche; Character Forge, Wirtschaft und Synchronisation folgen modular.

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

## Schnellzugriff

| Ziel | Einstieg |
|---|---|
| Projekt verstehen | [Spielschema](docs/GAME_SCHEMA.md) |
| Datei finden | [Ordner- und Dateiindex](docs/REPOSITORY_INDEX.md) |
| Tool oder Dokument richtig ablegen | [Repository-Regeln](docs/REPOSITORY_RULES.md) |
| Architektur prüfen | [Architekturvertrag](docs/ARCHITEKTURVERTRAG.md) |
| Weiterarbeiten | [Entwicklerhandbuch](docs/ENTWICKLERHANDBUCH.md) · [TODO](TODO.md) |
| Änderungen verfolgen | [Changelog](CHANGELOG.md) |

## Aktueller Stand

**Version:** `0.5.2-alpha.1` · **Nächste Phase:** `0.6 Character Forge Runtime`

Der headless Kern bietet:

- 11 Figuren mit identischer Startbasis, stabilen IDs und editierbarem Profil,
- 16 Skills, 165 Trait-Namen und 15 deterministische Effektfamilien,
- Action Resolver mit begrenzten Trait-Modifikatoren und Soft-Konflikten,
- Level 1–50 mit offener Resonanz-Progression danach,
- append-only Journal, atomare Zustände, Snapshots, Recovery und sicheren Profil-Undo,
- ausschließlich Python-Standardbibliothek im Runtime-Kern.

Noch **nicht** enthalten sind grafische Game-UI, Telegram-Anbindung und Wirtschaft. Der verbindliche Arbeitsstand steht in [`TODO.md`](TODO.md).

## Spiel in einem Ablauf

```text
Inhalt + Manifeste
        │
        ▼
Spielaktion ──► deterministische Auflösung ──► Domain-Ereignisse
                                                   │
                                                   ▼
                                       Persistence Kernel
                                         │             │
                                         ▼             ▼
                                      Journal        Zustand
                                         │
                                         ▼
                              Projektion für die spätere UI
```

Die fachlichen Begriffe, Grenzen und Datenflüsse erklärt das [`GAME_SCHEMA`](docs/GAME_SCHEMA.md). Maschinenlesbare Manifeste und JSON-Schemas bleiben verbindlich.

## Architekturgrenzen

| Bereich | Verantwortung | Darf nicht |
|---|---|---|
| `domain` | Charakter, Progression, Trait-Regeln | Infrastruktur oder UI kennen |
| `application` | Aktionen koordinieren, Ereignisse liefern | Zustand an der Persistenz vorbei speichern |
| `infrastructure` | Journal, Save, Snapshot, Recovery | sichtbare Texte oder UI-Objekte verwalten |
| `content` | sichtbare Texte und Figureninhalte | technische IDs ersetzen |
| `presentation` *(ab 0.6)* | Zustand anzeigen, Aktionen auslösen | Domain-Zustand direkt schreiben |

Weitere Invarianten stehen im [`Architekturvertrag`](docs/ARCHITEKTURVERTRAG.md).

## Repository-Prinzip

<table>
  <tr><th>🟧 Tool</th><th>📘 Dokumentation</th><th>🟦 Vertrag/Daten</th></tr>
  <tr>
    <td>Kleines ausführbares Entwicklerwerkzeug unter <code>tools/</code>.</td>
    <td>Erklärung, Entscheidung oder Anleitung unter <code>docs/</code>.</td>
    <td>Maschinenlesbare Regeln in <code>manifests/</code> und <code>schemas/</code>.</td>
  </tr>
</table>

Ein Tool erklärt keine Fachregel neu, sondern führt vorhandene Verträge aus oder prüft sie. Ausführliche Nutzungshinweise gehören in die Dokumentation. Die vollständige Ablageregel steht in [`docs/REPOSITORY_RULES.md`](docs/REPOSITORY_RULES.md).

## Basiswerkzeuge

Es gibt bewusst nur kleine, direkt ausführbare Entwicklerwerkzeuge:

```bash
# Action-Vertrag prüfen
python3 tools/validate_action_contract.py

# deterministische Progression simulieren
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 --days 720 --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Der Simulator ist **kein** Spiel-Laufzeitcode. Werkzeuge verwenden nur die Python-Standardbibliothek und lesen die kanonischen Manifeste.

## Gezielte Runtime-Prüfung

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Lokaler Referenzstand: **27/27 Runtime-/Recovery-Tests bestanden**. Der versionierte Nachweis liegt in [`reports/RUNTIME_VALIDATION_0.5.2.json`](reports/RUNTIME_VALIDATION_0.5.2.json); Remote-CI ist davon getrennt zu bewerten.

## Verbindliche Dokumente

- [Character Forge](docs/CHARACTER_FORGE.md) und [Progression](docs/PROGRESSION_CONTRACT.md)
- [Gameplay Actions](docs/GAMEPLAY_ACTION_CONTRACT.md)
- [Character Core](docs/CHARACTER_CORE_0.5.md)
- [Persistence](docs/PERSISTENCE_CONTRACT.md) und [Recovery](docs/RECOVERY_0.5.1.md)
- [UI/UX Blueprint](docs/UI_UX_BLUEPRINT.md)
- [Datenmodell](docs/DATENMODELL.md)

## Arbeitsweise

Jede Iteration ist eine kleine geplante Änderungseinheit: Ziel und Abnahme festlegen, direkte Verträge lesen, minimal patchen, einmal gezielt validieren und den Diff vor dem Commit prüfen. Die verbindlichen Regeln stehen in [`AGENTS.md`](AGENTS.md).
