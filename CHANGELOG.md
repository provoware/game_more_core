# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## [0.4.1-alpha.1] – 2026-08-21

### Hinzugefügt
- `TRAIT_ENGINE_MANIFEST.json` mit fünf Freischaltstufen, 15 numerischen Effektvorlagen, Trait-Evidenzquellen, Stack-Caps und zwei begründeten Soft-Konflikten.
- `PROGRESSION_MANIFEST.json` mit Skillkurve 10–100, Trainings-Abwertung und sechs datengetriebenen Spezialisierungen.
- deterministischer Progression-Simulator unter `tools/simulate_characters/`.
- gezielte Simulationstests für Manifest-Invarianten, Determinismus und Balance-Gate.
- versionierter Referenzbericht `reports/PROGRESSION_SIMULATION_0.4.1.json`.
- JSON-Schemas für Trait Engine und Progression.
- `docs/PROGRESSION_CONTRACT.md`.

### Geändert
- Projektversion auf `0.4.1-alpha.1`.
- `README.md`, `TODO.md`, `PROJEKTSTATUS.json` und `PROJEKTMANIFEST.json` auf den validierten 0.4.1-Stand aktualisiert.
- `SKILL_MANIFEST.json` auf die verbindliche Skill-XP-Formel und Progression-Referenz präzisiert.
- `LEVEL_MANIFEST.json` mit Referenz auf den Progression-Vertrag ergänzt.
- `TEST_MANIFEST.json` um ausschließlich für 0.4.1 relevante Prüfungen erweitert.
- `docs/CHARACTER_FORGE.md` um konkrete Trait-/Spezialisierungsregeln erweitert, ohne bestehende Foundation-Inhalte zu entfernen.

### Bewusst unverändert
- `TRAIT_MANIFEST.json` mit seinen 165 individuellen Namen und Zuordnungen bleibt byte-identisch; numerische Regeln werden über die referenzierten Effektvorlagen in `TRAIT_ENGINE_MANIFEST.json` ergänzt.
- kein Spiel-Laufzeitcode, keine UI, keine Telegram- oder Persistenzimplementierung.

### Validierung
- alle neuen/geänderten JSON-Dateien syntaktisch gültig.
- exakt 15 eindeutige numerische Trait-Effektvorlagen.
- fünf monoton steigende Trait-Stufen.
- Referenzsimulation: 1.000 Charaktere × 720 Spieltage, Seed `90409`.
- Ergebnis: alle sechs Balance-Gates bestanden.
- Unit-Tests: Manifest-Invarianten, deterministische Wiederholbarkeit und Balance-Gate bestanden.

## [0.4.0-alpha.1] – 2026-08-21

### Hinzugefügt
- Architekturvertrag für modulare Trennung von Domain, Application, Infrastructure, Presentation und Content.
- Character-Definition/Instanz/Fortschritt als getrennte Datenmodelle.
- 11 Hauptfiguren mit identischen Startwerten und narrativ getrennten Grundstorys.
- 15 gemeinsame Trait-Effektvorlagen und 165 individuelle Trait-Namen.
- XP-/Level-Grundformel und Resonanzmodell nach Level 50.
- Regeln für dynamische Biografie.
- Grundverträge für Save, Autosave, Undo, Journal, Snapshot, Recovery, Hybridzeit und Synchronisation.
- Maschinenlesbare Manifeste und JSON-Schemas.
- Entwicklerregeln in `AGENTS.md`.

### Geändert
- `README.md` von Platzhalter auf kanonische Projektübersicht und aktuellen TODO-Stand erweitert.

### Validierung
- JSON-Strukturen müssen syntaktisch gültig sein.
- Trait-IDs müssen eindeutig sein und exakt 165 registrierte Traits ergeben.
- alle 11 Character Definitions müssen dieselben Startwerte referenzieren.
- alle Manifest-/Schema-Pfade müssen innerhalb des dokumentierten 0.4-Scopes liegen.

### Nicht enthalten
- Kein Laufzeitcode.
- Keine Telegram-Implementierung.
- Keine Wirtschaftssimulation.
- Keine UI-Implementierung.
