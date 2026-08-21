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

- [x] vier klar unterschiedliche Industrial-Brutalist-Layouts spezifiziert
- [x] übersichtlichen gemeinsamen System-/UI-Blueprint als Projekt-Asset aufgenommen
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

## 0.5 – Headless Character Core

- [x] Python-Standardbibliothek ohne neue Runtime-Abhängigkeiten
- [x] `CharacterState` mit 16 identischen Startskills
- [x] Skill-XP, Skill-Level und Gesamtlevel implementiert
- [x] Trait-Evidenz mit fünf Freischaltstufen implementiert
- [x] sechs Spezialisierungen und XP-Konsequenzen implementiert
- [x] Action Resolver deterministisch; Skills und Risiko beeinflussen Ergebnis
- [x] Eingabe-Character wird bei Action Resolution nicht direkt mutiert
- [x] Character Action Service trennt Domain und Persistenz
- [x] Journal Schema v2 mit Pflichtmetadaten, globaler Sequenz und SHA-256-Kette
- [x] Event-Katalogprüfung und idempotente Event-IDs
- [x] Journal vor State-Write mit `fsync` dauerhaft schreiben
- [x] State und Meta atomar schreiben
- [x] Autosave-Regel exakt 60 Sekunden dirty-only abgebildet
- [x] 14 gezielte Runtime-/Integrationstests bestanden
- [x] 200 Action/Commit/Reload-Schritte als Stresstest bestanden
- [x] gezielten GitHub-Actions-Workflow für Runtime-Code angelegt

## 0.5.1 – Recovery & Fault Injection

- [x] Snapshot Writer und Snapshot-Index implementiert
- [x] Replay aus Snapshot + Journal implementiert
- [x] korrupten Journal-Tail automatisch quarantänisiert
- [x] `RECOVERY_RECEIPT.json` implementiert
- [x] Crashpunkte nach Journal Durable / State Applied / Meta Commit simuliert
- [x] Recovery idempotent getestet
- [x] State-Envelope mit Sequenz, Journal-Head und Prüfsumme eingeführt
- [x] Legacy-State aus 0.5.0 weiterhin lesbar
- [x] Runtime-Undo/Kompensation für editierbare Profilfelder Name/Alias/Motto implementiert
- [x] Recovery aus beschädigtem State über Snapshot + nachfolgendes Journal getestet
- [x] 21/21 gezielte Runtime-/Recovery-Tests lokal bestanden

## 0.5.2 – Progression Effects & Resonance

- [x] 15 Trait-Effektfamilien auf konkrete Action-Metriken anwenden
- [x] positive/negative Stack-Caps zur Runtime hinzufügen
- [x] Soft-Konflikte Planer↔Improvisierer und Detailmensch↔Opportunist berechnen
- [x] Trait-Effekte deterministisch in Action Resolution einbinden
- [x] Level 50 als Übergang in Resonanz statt Enddeckel implementieren
- [x] Resonanz-XP/-Ränge journalisieren und testen
- [x] Balance-Regression gegen 0.4.1-Simulator absichern

## 0.6 – Character Forge Runtime

- [ ] A4 Ops Deck als normalen Hauptworkflow implementieren
- [ ] A3 Cinematic Forge als Charakter-/Entwicklungsansicht implementieren
- [ ] editierbare Namen, Alias, zusätzliche Spitznamen und Motto anbinden
- [ ] Skillnetz, Traits, Spezialisierung und dynamische Biografie darstellen
- [ ] Level-/Skill-/Trait-Up-Feedback und Reduced-Motion-Fallbacks anbinden
- [ ] Ranking-/Network-Ansicht vorbereiten, aber Sync weiterhin getrennt halten
