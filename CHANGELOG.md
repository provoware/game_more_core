# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## [0.5.0-alpha.1] – 2026-08-21

### Hinzugefügt
- erster headless Runtime-Kern unter `src/bunkerfrequenz/` ohne externe Python-Abhängigkeiten.
- `CharacterState` mit identischer Startbasis, Skills, Trait-Fortschritt und Spezialisierung.
- deterministischer Action Resolver mit Skill-/Risiko-Einfluss und Trait-Evidenzquellen.
- `CharacterActionService` als Application-Grenze zwischen Domain und Persistenz.
- Persistence Kernel mit Journal Schema v2, monotone Sequenz, SHA-256-Kette, `fsync`, atomaren State-/Meta-Writes und Idempotenzprüfung.
- `RUNTIME_MANIFEST.json`, `character_state.schema.json` und `CHARACTER_CORE_0.5.md`.
- gezielte Runtime-/Integrationstests sowie GitHub-Actions-Workflow `runtime-core.yml`.
- übersichtlichere visuelle Referenz `docs/assets/BUNKERFREQUENZ_SYSTEM_BLUEPRINT_0.4.3.webp`.
- versionierter Runtime-Abnahmebericht `reports/RUNTIME_VALIDATION_0.5.0.json`.

### Geändert
- Projektversion auf `0.5.0-alpha.1`.
- README, TODO, Projektstatus und Projektmanifest auf den ersten Runtime-Stand aktualisiert.
- UI/UX Blueprint und UI-Manifest mit der kanonischen visuellen Referenz verknüpft.
- Agentenregeln um Journal-Katalogtreue für Runtime-Events präzisiert.

### Validierung
- `compileall` für `src/` bestanden.
- 14/14 gezielte Runtime-/Integrationstests bestanden.
- 200 aufeinanderfolgende Action/Commit/Reload-Schritte ohne Journal- oder Zustandsfehler.
- korrupter Journal-Tail wird zuverlässig erkannt.
- gleiche Event-ID mit gleichem Inhalt ist idempotent; abweichender Inhalt wird abgelehnt.

### Bewusst offen
- automatische Recovery/Quarantäne nach erkanntem Fehler, Snapshot-Replay und Fault-Injection folgen in 0.5.1.
- noch keine grafische Game-Runtime, Telegram- oder Wirtschaftsimplementierung.

## [0.4.4-alpha.1] – 2026-08-21

### Hinzugefügt
- `ACTION_MANIFEST.json` mit 20 datengetriebenen Startaktionen.
- exakte Skill-XP- und Trait-Evidenz-Gewichte je Aktion.
- deterministische Action-Resolver-Pipeline, Ergebnisstufen und Anti-Grind-Bezüge.
- Action-Schema, Validator, Testhülle und `reports/CONTRACT_VALIDATION_0.4.4.json`.
- Schutzregel für reale Locations: nur legal/autorisiert oder klar fiktionalisiert.

### Geändert
- README/TODO/Version/Projektstatus auf `0.4.4-alpha.1`.
- `TEST_MANIFEST.json` um Persistence-, UI- und Action-Vertragsgates erweitert.

### Validierung
- exakt 20 eindeutige Action-IDs.
- Skill- und Trait-Evidenz-Gewichte jeder Aktion summieren sich jeweils auf 1,0.
- Journal-Referenzen liegen im 0.4.2-Katalog; Systemzeit ist kein Zufallsseed.
- Vertragsbericht = PASS.

## [0.4.3-alpha.1] – 2026-08-21

### Hinzugefügt
- UI/UX Blueprint mit A1 Control Room, A2 Compact Grid, A3 Cinematic Forge und A4 Ops Deck.
- UI- und Animation-Manifeste, UI-Schema und ausgelagerte deutsche Character-Forge-Texte.

### Validierung
- exakt vier Layoutvarianten innerhalb derselben Designfamilie.
- Farbe nie als alleinige Information; Tastatur, High-Contrast und Reduced-Motion vorgesehen.
- Animationen blockieren keinen Game-State und besitzen statische Fallbacks.

## [0.4.2-alpha.1] – 2026-08-21

### Hinzugefügt
- exakter Persistence Contract mit 39 Journal-Eventtypen, Transaktionszuständen und Commit-Invariante.
- Save-/Journal-Schema v2, Snapshot-/Undo-/Crash-/Recovery-Regeln und Migration v1 → v2.
- robuste Zeitanker- und Offline-Catch-up-Regeln.

### Geändert
- Autosave auf exakt 60 Sekunden, dirty-only und kritische Flush-Punkte konkretisiert.

### Validierung
- Eventtypen eindeutig; Snapshot-Schwellen numerisch fest.
- Migration nicht destruktiv und mit Snapshot/Backup/Validierung/Rollback.

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
