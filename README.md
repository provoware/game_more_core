# BUNKERFREQUENZ

**Version:** `0.4.2-alpha.1`  
**Phase:** 0.4.2 – Persistence Contract  
**Status:** Character Forge + Persistenzvertrag definiert; noch kein Spiel-Laufzeitcode

BUNKERFREQUENZ ist als modular erweiterbares Techno-/FreeTekno-Crew-RPG mit Charakterentwicklung, Eventmanagement, Club-/Bunker-Aufbau, Wirtschaft und späterer asynchroner Synchronisation geplant.

## Verbindliche Kernentscheidungen

- Industrial-Brutalist-Design als visuelle Leitlinie.
- 11 Hauptfiguren starten mit **identischen Spielwerten**.
- Verhalten, Training, Praxis, Krisen und Entscheidungen formen Skills, Traits und Spezialisierungen.
- Figurenidentität, Fortschritt, Texte, UI, Speicherung und Synchronisation bleiben getrennt.
- Spieltexte liegen außerhalb des Programmcodes.
- Autosave exakt alle 60 Sekunden, dirty-only plus kritische Flush-Punkte.
- Mindestens ein sicherer Undo-Schritt über kompensierende Journal-Ereignisse.
- Systemzeit wird nur über ein robustes Hybridzeit-Modell verwendet.
- Journal ist append-only; Snapshots und Recovery ergänzen es.
- Telegram/Netzwerk darf lokales Spielen niemals blockieren.

## Architektur
- [`docs/ARCHITEKTURVERTRAG.md`](docs/ARCHITEKTURVERTRAG.md)
- [`docs/CHARACTER_FORGE.md`](docs/CHARACTER_FORGE.md)
- [`docs/PROGRESSION_CONTRACT.md`](docs/PROGRESSION_CONTRACT.md)
- [`docs/PERSISTENCE_CONTRACT.md`](docs/PERSISTENCE_CONTRACT.md)
- [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md)

## Character Forge 0.4.1
11 gleiche Startbasen, 16 Kernskills, 165 individuelle Trait-Namen, 15 numerische Effektvorlagen, fünf Trait-Stufen, sechs Spezialisierungsrichtungen und deterministische Balance-Simulation.

## Persistence 0.4.2
- Append-only-Journal mit 39 katalogisierten Ereignistypen
- Transaktionsfolge `RECEIVED → VALIDATED → PREPARED → JOURNAL_DURABLE → STATE_APPLIED → COMMITTED`
- Autosave exakt alle 60 Sekunden, aber nur bei geändertem Zustand
- ein sicherer Undo-Schritt über Kompensationsereignis
- Snapshot spätestens nach 5 Minuten oder 50 bestätigten Events
- definierte Crash-/Korruptionsmatrix, Quarantäne und Recovery Receipt
- Save-/Journal-Schema v2 und vorbereitete Migration v1 → v2
- robuste Hybridzeit-Anker und begrenztes Offline-Catch-up

## TODO – aktueller Entwicklungsstand
- [x] 0.4.0 Architekturvertrag und Character-Forge-Foundation
- [x] 0.4.1 Trait Engine & Progression Simulator
- [x] 0.4.2 Persistence Contract
- [ ] 0.4.3 UI/UX Blueprint
- [ ] 0.4.4 Gameplay Action Contract
- [ ] 0.5 Character Core Implementation erst nach Abnahme der 0.4-Verträge

Die kanonische Arbeitsliste steht zusätzlich in [`TODO.md`](TODO.md).

## Entwicklungsprinzip
Jede Änderung benötigt einen fachlichen Grund, eine klar ermittelte Zielstelle, eine möglichst kleine Änderung, passende Validierung sowie Aktualisierung von README/TODO und CHANGELOG.
