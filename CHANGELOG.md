# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## Unveröffentlicht

### Hinzugefügt
- Zusätzliche Spitznamen sind im Character-State serialisierbar und über den bestehenden Profilservice inklusive Undo und Recovery editierbar.
- Ein Ordner-/Dateiindex, ein übergreifendes Spielschema und verbindliche Ablageregeln trennen Basistools, Dokumentation und maschinenlesbare Verträge.

### Geändert
- Die README führt nun über eine kompakte, farblich markierte Projektübersicht zu Status, Architektur, Werkzeugen und verbindlichen Detaildokumenten.

### Bewusst offen
- Die grafische Profilanbindung folgt weiterhin gemeinsam mit A4 Ops Deck und A3 Cinematic Forge in 0.6.

## [0.5.2-alpha.1] – 2026-08-21

### Hinzugefügt
- Runtime-Wirkung für alle 15 Trait-Familien auf Ergebnis, Qualität und passende Skill-XP.
- positive/negative Caps und die beiden katalogisierten Soft-Konflikte.
- persistierte Resonanz-XP und offene Resonanzränge nach Level 50.
- Journaltyp `character.resonance_xp_gained` und Manifestabgleichstest für Trait-Regeln.
- `reports/RUNTIME_VALIDATION_0.5.2.json` als lokale Diff-Abnahme; Remote-CI bleibt bis zum Pull Request ausdrücklich ausstehend.

### Geändert
- Action Resolver bindet aktive, für die Aktion relevante Traits deterministisch ein.
- Character-State-Schema, Progression-/Level-/Runtime-/Testmanifeste und Runtime-CI-Pfade auf 0.5.2 abgeglichen.
- Projektversion auf `0.5.2-alpha.1`; README/TODO/Projektstatus auf den abgeschlossenen lokalen Stand gesetzt.
- Arbeitsregeln um prüfbare Vorplanung, reproduzierbare Update-Nachweise und ein eindeutiges Iterationsende ergänzt.
- Phase 0.6 mit dem gemeinsamen Presentation-Vertrag als kleinster nächster Arbeitseinheit konkretisiert, ohne Runtime-Status oder Version vorzeitig zu ändern.

### Validierung
- `compileall`, 27 gezielte Runtime-/Recovery-Tests, Action-Vertragsprüfung und 0.4.1-Balance-Regression lokal bestanden.
- Remote-CI wird erst nach dem Commit über den Pull Request als grün bestätigt; kein lokaler Bericht behauptet vorzeitig einen Remote-Erfolg.

### Bewusst offen
- 0.6 setzt A4 Ops Deck und A3 Cinematic Forge auf den Runtime-Kern.
- 0.6.1 führt die getrennte Presentation-Testschicht ein.

## [0.5.1-alpha.1] – 2026-08-21

### Hinzugefügt
- State-Envelope mit angewandter Journal-Sequenz, Journal-Head und SHA-256-Datenhash.
- Snapshot Writer und aus gültigen Snapshot-Dateien rekonstruierbarer Snapshot-Index.
- Recovery aus letztem gültigem State-/Snapshot-Checkpoint plus deterministischem Journal-Replay.
- Quarantäne für beschädigte Journal-Tails und `RECOVERY_RECEIPT.json` als Wiederherstellungsnachweis.
- Fault-Injection-Punkte nach `JOURNAL_DURABLE`, `STATE_APPLIED` und `META_COMMITTED`.
- `CharacterRecoveryService` für idempotentes Character-Replay.
- `CharacterProfileService` mit sicherem Ein-Schritt-Undo für Name/Alias/Motto über ein kompensierendes Journal-Ereignis.
- `docs/RECOVERY_0.5.1.md` und `reports/RUNTIME_VALIDATION_0.5.1.json`.

### Geändert
- Projektversion auf `0.5.1-alpha.1`.
- Runtime-Manifest um Recovery-, Snapshot- und Undo-Fähigkeiten ergänzt.
- README/TODO/Projektstatus auf 0.5.1 und die getrennten Folgephasen 0.5.2/0.6 aktualisiert.
- 0.5.0-State bleibt als Legacy-Checkpoint lesbar; keine destruktive Migration.

### Validierung
- `compileall` lokal bestanden.
- 21/21 gezielte Runtime-/Recovery-Tests lokal bestanden.
- Crash nach durablem Journal wird aus dem bestätigten Checkpoint rekonstruiert.
- Crash nach State-Write wird ohne doppelte Progressionsanwendung korrigiert.
- Crash nach vollständig geschriebenem Meta-Zustand benötigt keine unnötige Recovery.
- beschädigter State wird aus Snapshot + nachfolgendem Journal wiederhergestellt.
- korrupter Journal-Tail wird vor Reparatur quarantänisiert.
- erneute Recovery auf gesundem Stand ist idempotent.

### Bewusst offen
- konkrete Laufzeitanwendung der 15 Trait-Effekte und Soft-Konflikte folgt in 0.5.2.
- Open-End-Resonanz nach Level 50 folgt in 0.5.2.
- grafische Character-Forge-Runtime folgt in 0.6.

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
