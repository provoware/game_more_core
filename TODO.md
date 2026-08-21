# TODO – BUNKERFREQUENZ

## 0.4 – Foundation
- [x] Architekturvertrag, Modulgrenzen und Character-Datenmodell
- [x] identische Startwerte, Skill-/Level-/Resonanzmodell
- [x] 11 Grundstorys, Biografie-Regeln, Textauslagerung
- [x] Pflicht-Manifeste und Entwicklerübergabe-Regeln

## 0.4.1 – Character Progression Contract
- [x] 165 Traits über 15 numerische Effektvorlagen
- [x] fünf Trait-Stufen und Freischaltschwellen
- [x] Trainings-Diminishing-Returns und Skillkurve 10–100
- [x] sechs Spezialisierungen ohne harten Klassenzwang
- [x] deterministischer Simulator + Referenzlauf 1.000 × 720 Tage

## 0.4.2 – Persistence Contract
- [x] 39 Journal-Eventtypen katalogisiert
- [x] Transaktionszustände und Commit-Invariante definiert
- [x] Autosave alle 60 Sekunden, dirty-only
- [x] Undo-/Kompensationsregeln je Ereignisgruppe
- [x] Snapshot-Trigger exakt definiert
- [x] Crash-/Korruptionsmatrix und Recovery-Reihenfolge
- [x] Save-/Journal-Schema v2
- [x] Migration v1 → v2 vorbereitet
- [x] Zeitanker- und Offline-Catch-up-Regeln konkretisiert

## 0.4.3 – UI/UX Blueprint
- [ ] vier klar unterschiedliche Industrial-Brutalist-Layouts auf einem Entwurfsbild
- [ ] Character Overview, Skills/Traits, Biografie, Ranking/Network
- [ ] Level-/Skill-Up-Inszenierung
- [ ] Kontrast-, Fokus-, Tastatur- und Fallbackregeln
- [ ] UI-Texte außerhalb des Codes

## 0.4.4 – Gameplay Action Contract
- [ ] spielbare Aktionen katalogisieren
- [ ] Skill-XP-Gewichte und Trait-Evidenz je Aktion
- [ ] Voraussetzungen, Dauer, Risiko, Kosten und Resultate
- [ ] Journal-/Undo-/Biografie-Zuordnung je Aktion
- [ ] Action-Contract-Validator

## Danach
- [ ] 0.5 Character Core Implementation
