# BUNKERFREQUENZ

**Version:** `0.5.1-alpha.1`  
**Phase:** 0.5.1 – Recovery & Fault Injection  
**Status:** Headless Character-/Action-/Persistence-Kern um Snapshot-Replay, Quarantäne, Recovery Receipt, Fault Injection und sicheren Profil-Undo erweitert; grafische Game-UI, Telegram und Wirtschaft bleiben bewusst nachgelagert.

BUNKERFREQUENZ ist als modular erweiterbares Techno-/FreeTekno-Crew-RPG mit Charakterentwicklung, Eventmanagement, Club-/Bunker-Aufbau, Wirtschaft und späterer asynchroner Synchronisation geplant.

## System-/UI-Blueprint

![BUNKERFREQUENZ System- und Character-Forge-Blueprint](docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp)

Der übersichtlichere Blueprint ist ab 0.5 die kanonische visuelle Referenz für Persistence, Character Forge und Gameplay Actions. Detailregeln bleiben weiterhin in den maschinenlesbaren Manifesten und den Fach-Dokumenten verbindlich.

## Verbindliche Kernentscheidungen

- Industrial-Brutalist-Design als visuelle Leitlinie.
- 11 Hauptfiguren starten mit **identischen Spielwerten**.
- Grundstory und Name definieren keine Klasse oder Startboni.
- Verhalten, Training, Praxis, Krisen und Entscheidungen formen Skills, Traits und Spezialisierungen.
- Figurenidentität, Fortschritt, Texte, UI, Speicherung und Synchronisation bleiben getrennt.
- Sichtbare Namen/Aliase sind editierbar; technische IDs bleiben stabil.
- Spieltexte liegen außerhalb des Programmcodes.
- Autosave-Ziel: alle 60 Sekunden plus kritische Ereignisse.
- Mindestens ein sicherer Undo-Schritt über kompensierende Journal-Ereignisse.
- Systemzeit wird nur über ein robustes Hybridzeit-Modell verwendet.
- Journal ist append-only; Snapshots und Recovery ergänzen es.
- Telegram/Netzwerk darf lokales Spielen niemals blockieren.
- Erweiterungen müssen datengetrieben bleiben.

## Architektur

Siehe:
- [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md)
- [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/UI_UX_BLUEPRINT.md`](docs/UI_UX_BLUEPRINT.md)
- [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md)
- [`docs/CHARACTER_CORE_0.5.md`](docs/CHARACTER_CORE_0.5.md)
- [`docs/RECOVERY_0.5.1.md`](docs/RECOVERY_0.5.1.md)
- [`docs/DATENMODELL.md`](docs/DATENMODELL.md)
- [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md)

## Character Forge 0.4.1

- 11 Character Definitions mit gleicher Startbasis
- 16 Kernskills
- 165 individuelle Trait-Namen als unveränderter Katalog
- 15 gemeinsame numerische Trait-Effektvorlagen
- fünf Trait-Stufen: Neigung → Gewohnheit → Charakterzug → Markenzeichen → Legendenmerkmal
- Trait-Evidenz aus Training, Praxis, Krisen, Teamarbeit, Entdeckung, Erfolg und Fehlschlag
- Training liefert nur 35 % normaler Trait-Evidenz und kann Praxis nicht ersetzen
- zwei bewusst begrenzte Soft-Konflikte, keine harten Klassenausschlüsse
- sechs datengetriebene Spezialisierungsrichtungen
- Spezialisierung entsteht aus dauerhaftem Skill-Vorsprung und besitzt Vor- sowie Nachteile
- Skillbereich 10–100 mit eigener XP-Kurve
- Gesamtlevel bleibt bis Level 50 nummeriert, danach Resonanzsystem

Die numerischen Regeln liegen getrennt in:
- [`manifests/TRAIT_ENGINE_MANIFEST.json`](manifests/TRAIT_ENGINE_MANIFEST.json)
- [`manifests/PROGRESSION_MANIFEST.json`](manifests/PROGRESSION_MANIFEST.json)

Der 165-Trait-Katalog in `TRAIT_MANIFEST.json` wurde bewusst **nicht unnötig umgeschrieben**, weil seine Namen und Zuordnungen unverändert bleiben.

## Progression-Simulator

Der Simulator ist ein Entwicklerwerkzeug, kein Spiel-Laufzeitcode. Er verwendet ausschließlich die Python-Standardbibliothek.

```bash
python3 tools/simulate_characters/progression_simulator.py
```

Reproduzierbarer Abnahmelauf:

```bash
python3 tools/simulate_characters/progression_simulator.py \
  --runs 1000 \
  --days 720 \
  --seed 90409 \
  --output reports/PROGRESSION_SIMULATION_0.4.1.json
```

Validierter Referenzlauf: **1.000 Charaktere × 720 Spieltage**, alle sechs Balance-Gates bestanden.

## Persistence 0.4.2

- 39 katalogisierte Journal-Eventtypen
- Save-/Journal-Schema v2 mit Transaktions-ID, Sequenz und Payload
- Autosave exakt alle 60 Sekunden, dirty-only plus kritische Flush-Punkte
- ein sicherer Undo-Schritt über Kompensationsereignisse
- Snapshot spätestens nach 5 Minuten oder 50 bestätigten Ereignissen
- definierte Crash-/Korruptionsmatrix, Quarantäne, Recovery Receipt und Migration v1 → v2
- Hybridzeit mit Zeitanker und begrenztem Offline-Catch-up

## Character Forge UI/UX 0.4.3

Vier Varianten innerhalb derselben Industrial-Brutalist-Komponenten:
- **A1 Control Room** – Desktop-Gesamtübersicht
- **A2 Compact Grid** – hohe Informationsdichte
- **A3 Cinematic Forge** – Charakteridentität und Level-/Trait-Inszenierung
- **A4 Ops Deck** – stärkste intuitive Workflow-Führung

Gemeinsam: klare Kontrastsemantik, maximal drei Primäraktionen, ausgelagerte UI-Texte, Tastaturnavigation, High-Contrast, Reduced-Motion und nicht blockierende Animationen.

## Gameplay Action Contract 0.4.4

20 datengetriebene Startaktionen verbinden Handlung direkt mit Character Forge. Jede Aktion definiert Voraussetzungen, Dauer, Kostenmodell, Risiko, Skill-XP-Gewichte, Trait-Evidenz, Journal-Bundle, Undo-Regel und Biografie-Relevanz. Zufall ist seedbar und reproduzierbar; die Systemzeit ist kein Zufallsseed.

## Headless Character Core 0.5

Der erste Laufzeitkern verwendet ausschließlich die Python-Standardbibliothek:

- `CharacterState` mit identischer Startbasis und stabiler technischer ID
- Skill-XP, Skill-Level, Gesamtlevel, Trait-Evidenz und Trait-Stufen
- Spezialisierung ohne erzwungene Startklasse und mit XP-Konsequenzen
- deterministischer `ActionResolver`, bei dem Skills und Risikoprofil das Ergebnis beeinflussen
- `CharacterActionService` als Grenze zwischen Domain und Persistenz
- Journal Schema v2 mit monotone Sequenz, SHA-256-Hashkette und Event-Katalogprüfung
- `fsync` vor abgeleitetem State-Write sowie atomare State-/Meta-Dateien
- idempotente Event-IDs; abweichende Doppelereignisse werden abgewiesen
- 60-Sekunden-Autosave-Regel auf monotoner Laufzeitbasis

## Recovery & Fault Injection 0.5.1

Die 0.4.2-Recovery-Verträge sind jetzt als Laufzeit umgesetzt:

- State-Envelope mit Sequenz, Journal-Head und SHA-256-Prüfsumme
- Snapshot Writer + automatisch neu aufgebauter Snapshot-Index
- Snapshot-Fälligkeit nach spätestens **50 bestätigten Events oder 300 Sekunden**
- Recovery aus letztem gültigem State- oder Snapshot-Checkpoint plus Journal-Replay
- beschädigter Journal-Tail wird vor Reparatur nach `recovery/quarantine/` verschoben
- `recovery/RECOVERY_RECEIPT.json` dokumentiert die Wiederherstellung
- definierte Fault-Injection-Punkte nach `JOURNAL_DURABLE`, `STATE_APPLIED` und `META_COMMITTED`
- idempotente Recovery verhindert doppelte Skill-/Trait-Anwendung
- editierbare Profilfelder Name/Alias/Motto besitzen einen sicheren Ein-Schritt-Undo über ein kompensierendes Journal-Ereignis
- 0.5.0-States bleiben als Legacy-Checkpoint lesbar

Gezielte Prüfung:

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Lokaler Abnahmestand: **21/21 Runtime-/Recovery-Tests PASS**. Der versionierte Bericht liegt in [`reports/RUNTIME_VALIDATION_0.5.1.json`](reports/RUNTIME_VALIDATION_0.5.1.json).

## TODO – aktueller Entwicklungsstand

- [x] 0.4.0 Architekturvertrag und Character-Forge-Foundation
- [x] **0.4.1 Trait Engine:** numerische Effekte, fünf Trait-Stufen und Freischaltschwellen
- [x] **0.4.1 Progression:** Trainings-Abwertung, Skillkurve und Spezialisierungsfolgen
- [x] **0.4.1 Konfliktregeln:** Soft-Konflikte ohne harte Klassenbindung
- [x] **0.4.1 Progression Simulator:** deterministisch, Standardbibliothek, Balance-Gates
- [x] **0.4.1 Referenzsimulation:** 1.000 × 720 Tage, Seed 90409
- [x] **0.4.2 Persistence Contract:** Transaktionen, Autosave, Undo, Snapshots, Crash/Recovery und Migration
- [x] **0.4.3 UI/UX Blueprint:** vier Industrial-Brutalist-Entwürfe, Character Forge, Ranking und Animationen
- [x] **0.4.4 Gameplay Action Contract:** 20 Aktionen mit Skill-/Trait-/Journal-Zuordnung
- [x] **0.5 Headless Character Core:** Character State, Progression, Action Resolver und Persistence Kernel
- [x] **0.5.1 Recovery & Fault Injection:** Snapshot-Replay, Quarantäne, Crashpunkte, Recovery Receipt und Profil-Undo
- [ ] **0.5.2 Progression Effects & Resonance:** Trait-Effekte/Soft-Konflikte anwenden und Open-End-Resonanz implementieren
- [ ] **0.6 Character Forge Runtime:** A4 Ops Deck + A3 Cinematic Forge auf den getesteten Kern setzen

Die kanonische Arbeitsliste steht zusätzlich in [`TODO.md`](TODO.md).

## Entwicklungsprinzip

Jede Änderung benötigt einen fachlichen Grund, eine klar ermittelte Zielstelle, eine möglichst kleine Änderung, passende Validierung sowie Aktualisierung von README/TODO und CHANGELOG. Prüfungen werden nur ausgeführt, wenn sie die geänderten Bereiche tatsächlich absichern.
