# BUNKERFREQUENZ

**Version:** `0.4.3-alpha.1`  
**Phase:** 0.4.3 – Character Forge UI/UX Blueprint  
**Status:** Progression + Persistenz + UI/UX-Vertrag definiert; noch kein Spiel-Laufzeitcode

BUNKERFREQUENZ ist als modular erweiterbares Techno-/FreeTekno-Crew-RPG mit Charakterentwicklung, Eventmanagement, Club-/Bunker-Aufbau, Wirtschaft und späterer asynchroner Synchronisation geplant.

## Kernentscheidungen
- Industrial-Brutalist-Design als visuelle Leitlinie.
- 11 Hauptfiguren starten mit identischen Spielwerten; Verhalten und Training formen sie.
- Texte, UI, Spiellogik, Persistenz und Synchronisation bleiben getrennt.
- Autosave 60 Sekunden, Undo über Kompensation, Append-only-Journal und Recovery.
- Animationen verändern keinen Game-State und besitzen Fallbacks.

## Verträge
- [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/UI_UX_BLUEPRINT.md`](docs/UI_UX_BLUEPRINT.md)

## Character Forge 0.4.1
165 Traits, 15 Effektvorlagen, fünf Trait-Stufen, sechs Spezialisierungen und deterministische Balance-Simulation.

## Persistence 0.4.2
39 Journal-Ereignisse, Save-/Journal-Schema v2, 60-Sekunden-Autosave, ein sicherer Undo-Schritt, Snapshot-/Crash-/Migration-/Recovery-Vertrag.

## UI/UX 0.4.3
Vier Varianten innerhalb der Industrial-Brutalist-Linie:
- **A1 Control Room** – Desktop-Gesamtübersicht
- **A2 Compact Grid** – hohe Informationsdichte
- **A3 Cinematic Forge** – Charakteridentität und Level-/Trait-Inszenierung
- **A4 Ops Deck** – stärkste intuitive Workflow-Führung

Gemeinsame Regeln: klare Kontrastsemantik, maximal drei Primäraktionen, externe UI-Texte, Tastaturnavigation, High-Contrast, Reduced-Motion und niemals gameplay-blockierende Animationen.

## TODO – aktueller Entwicklungsstand
- [x] 0.4.0 Architekturvertrag und Foundation
- [x] 0.4.1 Trait Engine & Progression Simulator
- [x] 0.4.2 Persistence Contract
- [x] 0.4.3 UI/UX Blueprint
- [ ] 0.4.4 Gameplay Action Contract
- [ ] 0.5 Character Core Implementation

Die kanonische Arbeitsliste steht in [`TODO.md`](TODO.md).
