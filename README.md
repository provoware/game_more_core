# BUNKERFREQUENZ

**Version:** `0.4.4-alpha.1`  
**Phase:** 0.4.4 – Gameplay Action Contract  
**Status:** 0.4-Foundationverträge für Progression, Persistenz, UI/UX und Gameplay-Aktionen definiert; noch kein Spiel-Laufzeitcode

BUNKERFREQUENZ ist als modular erweiterbares Techno-/FreeTekno-Crew-RPG mit Charakterentwicklung, Eventmanagement, Club-/Bunker-Aufbau, Wirtschaft und späterer asynchroner Synchronisation geplant.

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
- [ ] **0.5 Character Core Implementation:** zuerst headless Character/Action/Persistence-Kern, danach UI-Anbindung

Die kanonische Arbeitsliste steht zusätzlich in [`TODO.md`](TODO.md).

## Entwicklungsprinzip

Jede Änderung benötigt einen fachlichen Grund, eine klar ermittelte Zielstelle, eine möglichst kleine Änderung, passende Validierung sowie Aktualisierung von README/TODO und CHANGELOG. Prüfungen werden nur ausgeführt, wenn sie die geänderten Bereiche tatsächlich absichern.
