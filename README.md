# BUNKERFREQUENZ

**Version:** `0.4.0-alpha.1`  
**Phase:** 0.4 – Architekturvertrag & Character Forge Foundation  
**Status:** Architektur-/Datenfundament, noch kein Laufzeitcode

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
- [`docs/DATENMODELL.md`](docs/DATENMODELL.md)
- [`docs/ENTWICKLERHANDBUCH.md`](docs/ENTWICKLERHANDBUCH.md)

## Aktueller Inhalt

- 11 Character Definitions mit gleicher Startbasis
- 16 Kernwerte
- 15 gemeinsame Trait-Effektvorlagen
- 165 individuelle potentielle Traits
- XP-/Level-Grundformel
- Resonanzmodell nach Level 50
- Biografie-Regeln
- Save-/Journal-/Recovery-Verträge
- Zeit-/Sync-Grenzen
- verbindliche Manifeste und JSON-Schemas

## TODO – aktueller Entwicklungsstand

- [x] 0.4.0 Architekturvertrag definieren
- [x] Character Definition und Character Progress trennen
- [x] identische Startwerte für alle 11 Figuren festlegen
- [x] 165 potentielle Traits registrieren
- [x] XP- und Level-Grundmodell definieren
- [x] Biografie-, Save-, Journal-, Zeit- und Sync-Verträge definieren
- [x] Entwicklerregeln und Validierungsprinzipien dokumentieren
- [ ] **0.4.1 Trait-/Progression-Details:** exakte Unlock-Schwellen, fünf Trait-Stufen, numerische Vor-/Nachteile, Konfliktregeln
- [ ] **0.4.2 Persistence Contract:** konkrete Transaktionszustände, Crash-Matrix, Migrationen und Recovery-Fälle
- [ ] **0.4.3 UI/UX Blueprint:** vier Industrial-Brutalist-Entwürfe für Character Forge, Skills, Biografie und Ranking
- [ ] 0.5 Character Core Implementation erst nach Abnahme der 0.4-Verträge

Die kanonische Arbeitsliste steht zusätzlich in [`TODO.md`](TODO.md).

## Entwicklungsprinzip

Jede Änderung benötigt einen fachlichen Grund, eine klar ermittelte Zielstelle, eine möglichst kleine Änderung, passende Validierung sowie Aktualisierung von README/TODO und CHANGELOG. Prüfungen werden nur ausgeführt, wenn sie die geänderten Bereiche tatsächlich absichern.
