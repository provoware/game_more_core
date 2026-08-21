# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## [0.4.4-alpha.1] – 2026-08-21

### Hinzugefügt
- Gameplay Action Contract mit 20 datengetriebenen Startaktionen.
- exakte Skill-XP- und Trait-Evidenz-Gewichte pro Aktion.
- deterministische Resolver-Pipeline und Ergebnisstufen.
- Journal-, Undo- und Biografie-Zuordnung je Aktion.
- Action-Schema, Validator, Testhülle und Validierungsbericht.
- Schutzregel: reale Location-Erkundung nur legal/autorisiert oder fiktionalisiert.

### Geändert
- README/TODO/Version/Projektstatus auf 0.4.4 aktualisiert.
- Testmanifest um Persistence-, UI- und Action-Vertragsgates erweitert.

### Validierung
- exakt 20 eindeutige Action-IDs; Skill- und Trait-Gewichte jeder Aktion = 1,0.
- Biografie-Relevanz 0–100; Systemzeit nicht als Zufallsseed.
- `reports/CONTRACT_VALIDATION_0.4.4.json` = PASS.

## [0.4.3-alpha.1] – 2026-08-21
- UI/UX Blueprint mit vier Varianten, Accessibility und Animation-Fallbacks.

## [0.4.2-alpha.1] – 2026-08-21
- Persistence Contract, 39 Journaltypen, Save-/Journal-Schema v2, Undo, Snapshots, Migration und Recovery.

## [0.4.1-alpha.1] – 2026-08-21
- Trait Engine, Progression Contract, Simulator und Referenzbericht.

## [0.4.0-alpha.1] – 2026-08-21
- Architekturvertrag und Character-Foundation.
