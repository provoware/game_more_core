# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## [0.4.2-alpha.1] – 2026-08-21

### Hinzugefügt
- exakter Persistence Contract mit Transaktionszuständen und Commit-Invariante.
- 39 katalogisierte Journal-Eventtypen.
- Undo-Klassen und Kompensationsregeln.
- Snapshot-, Crash-, Korruptions- und Recovery-Regeln.
- Save-/Journal-Schema v2 sowie Persistence-Transaction-Schema.
- Migration v1 → v2 und robuste Zeitanker-/Offline-Catch-up-Regeln.

### Geändert
- Autosave auf exakt 60 Sekunden, dirty-only und zusätzliche kritische Flush-Punkte konkretisiert.
- README/TODO/Version/Projektstatus auf 0.4.2 aktualisiert.

### Validierung
- Eventtypen eindeutig, Transaktionszustände vollständig, Snapshot-Schwellen numerisch fest.
- Migration ist nicht destruktiv und verlangt Snapshot/Backup/Validierung/Rollback.

## [0.4.1-alpha.1] – 2026-08-21
- Trait Engine, Progression Contract, deterministischer Simulator und Referenzbericht ergänzt.

## [0.4.0-alpha.1] – 2026-08-21
- Architekturvertrag, Character-Foundation, 11 Hauptfiguren, 165 Traits und Grundverträge ergänzt.
