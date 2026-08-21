# TODO – BUNKERFREQUENZ

## 0.4 – Foundation

- [x] Architekturvertrag
- [x] Modulgrenzen
- [x] Character-Datenmodell
- [x] identische Startwerte
- [x] Skill-Grundmodell
- [x] 165 Trait-Namen + Effektvorlagen
- [x] XP-/Level-Grundformel
- [x] Resonanzmodell
- [x] 11 Grundstorys
- [x] Biografie-Regeln
- [x] Autosave-/Undo-Grundvertrag
- [x] Journal-/Snapshot-/Recovery-Grundvertrag
- [x] Hybridzeit-Grundvertrag
- [x] Sync-Grenzen
- [x] Textauslagerung
- [x] Pflicht-Manifeste
- [x] Entwicklerübergabe-Regeln

## 0.4.1 – Character Progression Contract

- [x] 165 Traits über 15 gemeinsame numerische Effektvorlagen vollständig abgedeckt
- [x] exakte Unlock- und Upgrade-Schwellen für fünf Trait-Stufen definiert
- [x] Trait-Konflikte als begrenzte Soft-Konflikte definiert
- [x] Trainings-Diminishing-Returns festgelegt
- [x] Skill-XP-Kurve 10–100 definiert
- [x] sechs Spezialisierungen samt Konsequenzen definiert
- [x] kein harter Klassenzwang; Generalisten bleiben möglich
- [x] deterministischen Progression-Simulator implementiert
- [x] gezielte Unit-Tests für Manifestregeln, Determinismus und Balance-Gate
- [x] Referenzsimulation 1.000 × 720 Tage mit Seed 90409 bestanden
- [x] Simulationsbericht versioniert abgelegt

## 0.4.2 – Persistence Contract

- [x] 39 Journal-Eventtypen vollständig katalogisiert
- [x] Snapshot-Trigger präzisiert
- [x] Undo-/Kompensationsregeln je Ereignisgruppe definiert
- [x] Crash-/Korruptionsmatrix definiert
- [x] Save-/Journal-Schema v2 und Migration v1 → v2 vorbereitet
- [x] Zeitanker-/Offline-Regeln konkretisiert
- [x] 60-Sekunden-Autosave dirty-only und kritische Flush-Punkte festgelegt

## 0.4.3 – UI/UX Blueprint

- [x] vier klar unterschiedliche Industrial-Brutalist-Layouts spezifiziert; gemeinsames Entwurfsbild erzeugen
- [x] Character Overview
- [x] Skills/Traits
- [x] dynamische Biografie
- [x] Ranking/Network
- [x] Level-/Skill-/Trait-/Spezialisierungs-Animationen
- [x] Kontrast-/Fokusregeln
- [x] Tastatur, High-Contrast, Reduced-Motion und statische Fallbacks
- [x] sichtbare UI-Texte ausgelagert

## 0.4.4 – Gameplay Action Contract

- [x] 20 spielbare Startaktionen katalogisiert
- [x] Skill-XP- und Trait-Evidenz-Gewichte je Aktion exakt definiert
- [x] Voraussetzungen, Dauer, Risiko, Kosten und Resolver-Pipeline
- [x] Journal-/Undo-/Biografie-Zuordnung je Aktion
- [x] deterministischer Zufallsvertrag ohne Systemzeit-Seed
- [x] Schutzregel für reale Locations: legal/autorisiert oder fiktionalisiert
- [x] Action-Contract-Validator + Testhülle
- [x] maschinenlesbarer Vertragsbericht PASS

## Danach

- [ ] 0.5 Character Core Implementation
