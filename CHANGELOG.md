# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## Unveröffentlicht

### Hinzugefügt
- `presentation_capabilities.py` als reine Application-Leseabfrage für `can_edit_profile`, `can_undo_profile` und `can_execute_action`.
- `command_dispatcher.py` als einziger bestätigter Schreibweg für `profile.update`, `profile.undo_last` und `action.execute`.
- `PresentationState` als unveränderlicher lokaler Zustand für Ansicht, Biografie-Filter, ausgeblendetes Feedback und Reduced Motion.
- `presentation_events.py` als Application-Leseabfrage für detached Kopien bereits bestätigter Journal-Ereignisse.
- `feedback.py` für deterministisches Progressionsfeedback aus bestätigten Level-, Skill-, Trait-, Spezialisierungs- und Resonanzereignissen.
- `content/de/ui/feedback.json` für vollständig ausgelagerte sichtbare Feedbacktexte.
- End-to-End-Test für `Command → Commit → bestätigte Events → Feedback → Character-Projektion`.
- Zielgerichteter `Presentation Core`-Workflow für Presentation-Code, zugehörige Application-Grenzen, Tests und UI-Textkataloge.
- Repository-Audit und verbindliche Ein-PR-pro-Zielstelle-Regel.

### Geändert
- Character-Projektion übernimmt bestätigte Capabilities und Feedback als defensive Kopien und validiert deren sichtbare Textschlüssel.
- Biografie-Filter verwendet die Kategorien aus `BIOGRAFIE_MANIFEST.json` statt einer zweiten handgepflegten Liste.
- UI-Befehle dürfen keine Balanceparameter wie `base_xp` oder Evidenzquelle setzen.
- README, TODO, Projektstatus, Repository-Index und Testmanifest führen die aktive Entwicklung jetzt auf `0.6.3 – gemeinsame Komponenten + A4 Ops Deck`.

### Behoben
- Frühere parallele Presentation-Merges wurden durch PR #22 auf eine einzige kanonische Character-Projektion, eindeutige Package-Exporte und konsistente Tests zurückgeführt.
- Gesperrte Traits verraten keine versteckten Evidenzwerte; Skill-Fortschritt ist defensiv begrenzt.

### Validierung
- Repository-Reparatur PR #22: Runtime Core `32505897397` und Presentation Core `32505897399` erfolgreich.
- 0.6.1 PR #24: Runtime Core `32510846508` und Presentation Core `32510846537` erfolgreich; Merge `25006d07d33199fea2db8208c192ca2f6fa1095d`.
- 0.6.2 PR #26: Runtime Core `32511953788` und Presentation Core `32511953619` erfolgreich; Merge `5161cb42c2b0d38fcb69ea6bd20f9dc5ce1b283a`.
- Idempotenter Action-Replay erzeugt keine neuen Commit-IDs und damit keine zweite Feedbackquelle.
- Die Produktversion bleibt bewusst `0.5.2-alpha.1`; 0.6.x ist weiterhin aktive Presentation-Entwicklung.

## [0.5.2-alpha.1] – 2026-08-21

### Hinzugefügt
- Runtime-Wirkung für alle 15 Trait-Familien auf Ergebnis, Qualität und passende Skill-XP.
- positive/negative Caps und die beiden katalogisierten Soft-Konflikte.
- persistierte Resonanz-XP und offene Resonanzränge nach Level 50.
- Journaltyp `character.resonance_xp_gained` und Manifestabgleichstest für Trait-Regeln.
- `reports/RUNTIME_VALIDATION_0.5.2.json` als reproduzierbarer Runtime-Abnahmenachweis.

### Geändert
- Action Resolver bindet aktive, für die Aktion relevante Traits deterministisch ein.
- Character-State-Schema, Progression-/Level-/Runtime-/Testmanifeste und Runtime-CI-Pfade auf 0.5.2 abgeglichen.
- Projektversion auf `0.5.2-alpha.1`.

### Validierung
- `compileall`, 27 gezielte Runtime-/Recovery-Tests, Action-Vertragsprüfung und 0.4.1-Balance-Regression lokal bestanden.
- `Runtime Core` für PR #6 remote erfolgreich bestanden.

### Bewusst offen
- Character-Forge-Presentation baut modular auf diesem Runtime-Kern auf.
- grafisches Framework, Ranking/Network und Telegram/Sync folgen später.

## [0.5.1-alpha.1] – 2026-08-21

### Hinzugefügt
- State-Envelope mit Journal-Sequenz, Journal-Head und SHA-256-Datenhash.
- Snapshot Writer und rekonstruierbarer Snapshot-Index.
- Recovery aus gültigem State-/Snapshot-Checkpoint plus deterministischem Journal-Replay.
- Quarantäne für beschädigte Journal-Tails und `RECOVERY_RECEIPT.json`.
- Fault-Injection-Punkte nach `JOURNAL_DURABLE`, `STATE_APPLIED` und `META_COMMITTED`.
- `CharacterRecoveryService` und sicherer Ein-Schritt-Profil-Undo über Kompensationsereignis.

### Validierung
- `compileall` und 21/21 gezielte Runtime-/Recovery-Tests lokal bestanden.
- Crash- und Korruptionsfälle, Snapshot-Recovery, Quarantäne und idempotente Wiederherstellung bestanden.

## [0.5.0-alpha.1] – 2026-08-21

### Hinzugefügt
- erster headless Runtime-Kern ohne externe Python-Abhängigkeiten.
- `CharacterState`, deterministischer Action Resolver und `CharacterActionService`.
- Persistence Kernel mit Journal Schema v2, Sequenz, SHA-256-Kette, `fsync`, atomaren State-/Meta-Writes und Idempotenz.
- Runtime-/Integrationstests sowie GitHub-Workflow `runtime-core.yml`.

### Validierung
- 14/14 Runtime-/Integrationstests und 200 Action/Commit/Reload-Schritte bestanden.
- korrupter Journal-Tail wird erkannt; gleiche Event-ID ist bei gleichem Inhalt idempotent und bei abweichendem Inhalt ungültig.

## [0.4.4-alpha.1] – 2026-08-21

### Hinzugefügt
- `ACTION_MANIFEST.json` mit 20 datengetriebenen Startaktionen.
- Skill-XP-/Trait-Evidenz-Gewichte, Resolver-Pipeline, Ergebnisstufen und Anti-Grind-Bezüge.
- Action-Schema, Validator und Vertragsbericht.

### Validierung
- 20 eindeutige Action-IDs; Skill-/Trait-Gewichte je Action = 1.0; Journalreferenzen gültig; Systemzeit kein Zufallsseed.

## [0.4.3-alpha.1] – 2026-08-21

### Hinzugefügt
- UI/UX Blueprint mit A1 Control Room, A2 Compact Grid, A3 Cinematic Forge und A4 Ops Deck.
- UI-/Animation-Manifeste, UI-Schema und ausgelagerte deutsche Character-Forge-Texte.

### Validierung
- vier Layoutvarianten; Farbe nie alleinige Information; Tastatur, High Contrast und Reduced Motion vorgesehen.

## [0.4.2-alpha.1] – 2026-08-21

### Hinzugefügt
- Persistence Contract mit Journal-Eventtypen, Transaktionszuständen, Save-/Journal-Schema v2, Snapshot-, Undo-, Crash-, Recovery- und Migrationsregeln.
- Autosave exakt alle 60 Sekunden, dirty-only und zusätzliche kritische Flush-Punkte.

## [0.4.1-alpha.1] – 2026-08-21

### Hinzugefügt
- Trait Engine mit fünf Stufen, 15 numerischen Effektvorlagen, Stack-Caps und Soft-Konflikten.
- Progressionsvertrag mit Skillkurve, Trainings-Abwertung und sechs Spezialisierungen.
- deterministischer Progression-Simulator und Referenzbericht.

### Validierung
- 15 eindeutige Effektvorlagen, fünf monotone Trait-Stufen und Referenzsimulation 1.000 Charaktere × 720 Tage mit Seed `90409`; alle Balance-Gates bestanden.

## [0.4.0-alpha.1] – 2026-08-21

### Hinzugefügt
- Architekturvertrag für Domain, Application, Infrastructure, Presentation und Content.
- getrennte Character-Definition/Instanz/Fortschritt-Modelle.
- 11 Hauptfiguren mit identischen Startwerten, 15 Trait-Vorlagen und 165 individuellen Trait-Namen.
- XP-/Level-Grundformel, Resonanzmodell, Biografie-, Save-, Journal-, Snapshot-, Recovery-, Hybridzeit- und Sync-Verträge.
- Maschinenlesbare Manifeste, Schemas und Entwicklerregeln.

### Nicht enthalten
- noch kein Laufzeitcode, Telegram, Wirtschaft oder UI-Runtime.
