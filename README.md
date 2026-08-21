# BUNKERFREQUENZ

**Version:** `0.4.4-alpha.1`  
**Phase:** 0.4.4 – Gameplay Action Contract  
**Status:** 0.4-Foundationverträge für Progression, Persistenz, UI/UX und Gameplay-Aktionen definiert; noch kein Spiel-Laufzeitcode

BUNKERFREQUENZ ist als modular erweiterbares Techno-/FreeTekno-Crew-RPG mit Charakterentwicklung, Eventmanagement, Club-/Bunker-Aufbau, Wirtschaft und späterer asynchroner Synchronisation geplant.

## Verträge
- [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/UI_UX_BLUEPRINT.md`](docs/UI_UX_BLUEPRINT.md)
- [`docs/GAMEPLAY_ACTION_CONTRACT.md`](docs/GAMEPLAY_ACTION_CONTRACT.md)

## Character Forge 0.4.1
165 Traits, 15 Effektvorlagen, fünf Trait-Stufen, sechs Spezialisierungen und deterministische Balance-Simulation.

## Persistence 0.4.2
39 Journal-Ereignisse, Save-/Journal-Schema v2, 60-Sekunden-Autosave, Undo, Snapshot-/Crash-/Migration-/Recovery-Vertrag.

## UI/UX 0.4.3
A1 Control Room, A2 Compact Grid, A3 Cinematic Forge und A4 Ops Deck. Gemeinsame Komponenten, externe UI-Texte, High-Contrast, Reduced-Motion und nicht blockierende Animationen.

## Gameplay Actions 0.4.4
20 datengetriebene Startaktionen verbinden Verhalten direkt mit Character Forge: Training, Soundcheck, Erkundung, Kauf, Ausbau, Booking, Eventvorbereitung/-betrieb/-krise, Reparatur, Networking, Recherche, Transport, Clubplanung/-betrieb, Clubanteile, Crew-Konflikt, Abbau, Dekoration und Musikprogramm.

Jede Aktion definiert exakt: Voraussetzungen, Dauer, Kostenmodell, Risiko, Skill-XP-Gewichte, Trait-Evidenz, Journal-Bundle, Undo-Regel und Biografie-Relevanz. Zufall ist seedbar und reproduzierbar; Systemzeit ist kein Zufallsseed.

## TODO – aktueller Entwicklungsstand
- [x] 0.4.0 Architekturvertrag und Foundation
- [x] 0.4.1 Trait Engine & Progression Simulator
- [x] 0.4.2 Persistence Contract
- [x] 0.4.3 UI/UX Blueprint
- [x] 0.4.4 Gameplay Action Contract
- [ ] **0.5 Character Core Implementation:** zuerst headless Character/Action/Persistence-Kern, danach UI-Anbindung

Die kanonische Arbeitsliste steht in [`TODO.md`](TODO.md).
