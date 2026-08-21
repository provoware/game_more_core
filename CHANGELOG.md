# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## Unveröffentlicht

### Behoben
- `/safe-merge` behandelt GitHubs verzögerte Commit→PR-Zuordnung robust: Der Merge wird exakt einmal ausgeführt; nur die nachgelagerte Provenienz-Leseprüfung wird begrenzt nach `0/1/2/4/8` Sekunden wiederholt.
- Der erste echte `/safe-merge`-Smoke-Test PR #36 wurde korrekt gemergt, meldete wegen GitHub-Eventual-Consistency aber zunächst fälschlich `SAFE MERGE BLOCKED`; PR #37 trennt jetzt sauber Vor-Merge-Blockade von bereits geschriebenem Merge mit noch nicht bestätigter Nachprüfung.
- Der versehentliche Merge von PR #32 aus einem alten `0.6.4`-Branch wurde vollständig aus dem Repository-Baum zurückgenommen; wiederhergestellt wurde der letzte grüne Stand nach PR #31 (`888be18146197272578f4baa5516f78a894d9464`).
- Der durch PR #32 eingeführte Syntaxfehler `unmatched ')'` in `a3_cinematic_forge.py` und die parallel zurückgebrachten Presentation-Helfer wurden entfernt.
- Offener Review-P1 aus PR #31 behoben: Action-Auswahlkarten geben kein unvollständiges scheinbar ausführbares `action.execute`-Payload mehr aus. `build_action_execute_command(...)` ergänzt `command_id` und `action_instance_id` erst unmittelbar vor der Ausführung.
- Offener Review-P2 aus PR #31 behoben: A4 prüft `can_execute_action` beim Zusammensetzen erneut und deaktiviert stale zuvor freigegebene Auswahlkarten fail-closed.
- Die durch parallele Presentation-Merges beschädigte `character_projection.py` wurde auf genau eine kanonische, kompilierbare Implementierung zurückgeführt.
- Die zusammenkopierten, widersprüchlichen Character-Projection-Tests wurden zu einem eindeutigen Vertragstest-Satz konsolidiert.
- `presentation/__init__.py` exportiert Character- und Biografieprojektion wieder eindeutig, ohne konkurrierende `__all__`-Blöcke.
- Die Character-Projektion bindet die bestehende `build_biography_projection(...)` als einzige Biografie-Aufbereitung ein, statt eine zweite Implementierung zu führen.
- Gesperrte bekannte Traits geben keine versteckten Evidenz- oder Fortschrittswerte an die Presentation weiter.
- Skill-Fortschritt wird für negative/überlaufende XP defensiv begrenzt und zeigt am Skillmaximum keinen falschen Restbedarf.

### Hinzugefügt
- `/safe-merge` als operativer normaler Mergeweg: Berechtigung, aktueller `main`, exakter PR-Head, drei grüne Kern-Gates und ungelöste Review-Threads werden unmittelbar vor Merge erneut geprüft.
- `Main Integrity` als nachgelagerte Provenienzprüfung für Änderungen auf `main`; bei Fehler wird ein idempotenter `[MAIN-INTEGRITY]`-Incident erzeugt.
- Schutz vor Selbständerung: normale `/safe-merge`-PRs dürfen die Guard-/CI-Sicherheitsdateien nicht selbst verändern; Security-Änderungen benötigen einen ausdrücklich auditierten Bootstrap-PR.
- `tools/github_merge_guard.py` für Kandidatenprüfung, exakt-einmal-Merge und Main-Provenienz sowie `tools/github_merge_guard_retry.py` für begrenzte nachgelagerte GitHub-Lese-Retries.
- End-to-End-Nachweis PR #38: drei grüne Gates, keine offenen Review-Threads, Merge ausschließlich über `/safe-merge`, Bot-Rückkanal `SAFE MERGE PASS`, Merge `e1155db2d2a7eaddd313127d89635a1a3dac3ce6`.
- Repository Guard vor 0.7.2 mit `manifests/REPOSITORY_GUARD_MANIFEST.json`, `tools/repository_health.py`, `docs/REPOSITORY_GUARD.md` und dem neuen Workflow `Repository Health`.
- `repository-health` prüft JSON, Python-Struktur/Compile, Git-Konfliktmarker, Informationskonsistenz, kanonische Presentation-Symbole, öffentliche Exporte und Required-Workflow-Verträge.
- PR-Heads werden gegen den aktuellen Base-Branch geprüft; versionsgebundene alte Feature-Branches unterhalb der aktiven Iteration werden fail-closed abgewiesen.
- 0.7.1 startet den spielbaren Character-Forge-Slice mit einer A4-Auswahlprojektion für alle 20 katalogisierten Actions.
- Die Auswahl zeigt Dauer, bestätigte Voraussetzungen und gewichtete erwartete Skillwirkung; fehlende Energie-/Stressverträge bleiben ausdrücklich unbekannt.
- Nicht bestätigte Voraussetzungen sperren Actions fail-closed, ohne Domain-Zustand aus der Presentation zu verändern.
- `build_action_execute_command(...)` als expliziter Konstruktor für vollständige, bereits mit dem bestehenden Dispatcher kompatible Action-Commands.
- Regressionstests für direkte Dispatcher-Ausführung eines erzeugten Action-Commands und für Capability-Entzug zwischen Auswahlaufbau und A4-Projektion.
- Zielgerichteter GitHub-Workflow `Presentation Core` für Presentation-Code, relevante Application-Grenzdateien, Presentation-Tests und UI-Textkataloge.
- Repository-Audit `docs/REPOSITORY_AUDIT_2026-08-21.md` mit Ursache, Befunden, Reparatur- und PR-Konsolidierungsentscheidung.
- Explizite Informationshierarchie und PR-/Merge-Disziplin in `AGENTS.md` und `docs/REPOSITORY_RULES.md`.
- Sequenzielle 0.6-Roadmap für Application-Capabilities/Command-Dispatcher, lokalen Presentation-State/Feedback, A4, A3 und Ranking/Network.
- `presentation_capabilities.py` als reine Application-Leseabfrage für `can_edit_profile`, `can_undo_profile` und `can_execute_action`.
- `command_dispatcher.py` als einziger 0.6.1-Schreibweg für `profile.update`, `profile.undo_last` und `action.execute`.
- gezielte Tests für Capability-Fail-Closed, defensive Projection-Copies, ID-Erhalt, Action-/Profil-Idempotenz und wiederholtes Undo.
- `PresentationState` als unveränderlicher lokaler Zustand für View, Biografie-Filter, ausgeblendete Feedback-IDs und Reduced Motion.
- `presentation_events.py` als Application-Leseabfrage für detached Records bereits bestätigter Journal-Ereignisse.
- deterministisches Progressionsfeedback für Level-, Skill-, Trait-, Spezialisierungs- und Resonanzsprünge sowie ausgelagerte Texte in `content/de/ui/feedback.json`.
- End-to-End-Test `Command → Commit → bestätigte Eventabfrage → Feedback → Character-Projektion`.

### Geändert
- Normale PRs nach `main` werden nach erfolgreicher End-to-End-Abnahme ausschließlich über `/safe-merge` übernommen; native GitHub-Branch-Protection bleibt eine zusätzliche noch offene serverseitige Härtung.
- `Runtime Core` und `Presentation Core` laufen künftig auf jedem Pull Request ohne PR-Pfadfilter, damit ihre Check-IDs zuverlässig als Required Checks konfiguriert werden können.
- Zielpolicy für `main`: Pull Request erforderlich, Branch aktuell, Conversation Resolution, keine Force Pushes/Branch-Löschung sowie `runtime-core`, `presentation-core`, `repository-health` verpflichtend. Die native GitHub-Aktivierung bleibt extern, weil die verbundene Schnittstelle Branch-Protection nicht sicher schreiben kann.
- README, TODO, Projektstatus, Repository Guard, Repository-Index und Testmanifest auf den validierten `/safe-merge`-/Main-Integrity-Stand abgeglichen; 0.7.2 ist danach für Gameplay-Entwicklung freigegeben.
- README, TODO, Projektstatus, Projektmanifest, Repository-Index und Testmanifest auf den tatsächlich validierten Stand bis 0.7.1 und den nächsten Schritt 0.7.2 abgeglichen.
- `PROJEKTMANIFEST.json` führt die aktive Entwicklungsphase jetzt als `0.7` und referenziert das Ranking-/Network-Manifest.
- `TEST_MANIFEST.json` katalogisiert die 0.7.1-Action-Auswahl- und Review-Regressionen.
- README, Projektstatus und Projektmanifest trennen klar die versionierte Runtime-Baseline `0.5.2-alpha.1` von der aktiven Entwicklung.
- `TODO.md` führt nur noch eine sequenzielle Implementierung statt paralleler Teilansätze.
- Presentation-Vertrag, Repository-Index und Entwicklerhandbuch wurden auf die tatsächlich implementierte Foundation und die CI-/PR-Regeln abgeglichen.
- Die Character-Projektion akzeptiert bestätigte Capabilities optional, begrenzt sie auf drei öffentliche Booleans und kopiert sie defensiv.
- Der Dispatcher gibt bestätigten `CharacterState`, Commit-Event-IDs und Idempotenzstatus zurück; er erzeugt bewusst keine zweite Presentation-Projektion.
- UI-Befehle dürfen keine Balanceparameter wie `base_xp` oder Evidenzquelle setzen.
- Der Biografie-Filter erhält seine erlaubten Kategorien aus `BIOGRAFIE_MANIFEST.json` statt aus einer zweiten Handliste.
- Die Character-Projektion kann bestätigtes Feedback detached übernehmen und prüft dessen Textschlüssel gegen den Content-Katalog.
- `Presentation Core` beobachtet zusätzlich die bestätigte Application-Eventabfrage.

### Auditabschluss
- PR #14 war trotz fehlgeschlagenem relevantem Compile-Gate gemergt worden und hatte einen früheren Presentation-Schaden verursacht.
- Reparatur-PR #22 bestand Runtime Core und Presentation Core und wurde nach `main` gemergt.
- Die konkurrierenden Presentation-PRs #15–#21 wurden mit Begründung geschlossen; ihre sinnvollen Inhalte wurden in die kanonische TODO-Reihenfolge übernommen.
- PR #32 wurde später ebenfalls trotz zweier roter Kern-Gates gemergt; dieser Merge wird nicht als gültige Entwicklungsbasis behandelt und durch die aktuelle Reparatur vollständig entfernt.
- Die Produktversion wurde durch Wartungs-/Presentation-Arbeit nicht künstlich erhöht; `VERSION.json` bleibt bis zur nächsten abgenommenen Produktstufe auf `0.5.2-alpha.1`.

### Validierung
- Safe-Merge-Bootstrap / PR #35 Head `73b3594bdc015865364cf297b99e05bec7261649`: Runtime Core `32527116025` = erfolgreich; Presentation Core `32527115999` = erfolgreich; Repository Health `32527116022` = erfolgreich.
- Erster `/safe-merge`-Smoke-Test / PR #36: Merge `8214187c441123a786ca6581c544d3bcdd745f3b` wurde tatsächlich geschrieben; GitHub-API-Race-Condition direkt danach reproduziert.
- Eventual-Consistency-Hotfix / PR #37 Head `91cbe190247be0e40355bedaed2313eb6af517b8`: Runtime Core `32527882811` = erfolgreich; Presentation Core `32527882838` = erfolgreich; Repository Health `32527882791` = erfolgreich.
- Zweiter `/safe-merge`-End-to-End-Test / PR #38 Head `c97d02b29a6d6de33c32bf7113179c65d9e3e2f4`: Runtime Core `32528078989` = erfolgreich; Presentation Core `32528078992` = erfolgreich; Repository Health `32528078926` = erfolgreich; Bot meldete `SAFE MERGE PASS`; Merge `e1155db2d2a7eaddd313127d89635a1a3dac3ce6`.
- Repository Guard / PR #34 erster Implementierungs-Head `081c08f5ca1c660fb0d384879414142893571cb0`: Runtime Core `32522336221` = erfolgreich; Presentation Core `32522336259` = erfolgreich; Repository Health `32522336287` = erfolgreich.
- Repository-Reparatur #22: Runtime Core `32505897397` = erfolgreich; Presentation Core `32505897399` = erfolgreich.
- 0.6.1 PR #24: Runtime Core `32510846508` = erfolgreich; Presentation Core `32510846537` = erfolgreich.
- 0.6.2 PR #26: Runtime Core `32511953788` = erfolgreich; Presentation Core `32511953619` = erfolgreich.
- 0.6.3 PR #28: Runtime Core `32514970109` = erfolgreich; Presentation Core `32514970398` = erfolgreich.
- 0.6.4 PR #29: Runtime Core `32516833552` = erfolgreich; Presentation Core `32516833514` = erfolgreich.
- 0.6.5 PR #30: Runtime Core `32517683276` = erfolgreich; Presentation Core `32517683263` = erfolgreich.
- 0.7.1 PR #31: Runtime Core `32519042006` = erfolgreich; Presentation Core `32519041908` = erfolgreich.
- PR #32: Runtime Core `32519874996` = fehlgeschlagen; Presentation Core `32519875016` = fehlgeschlagen; beide stoppten beim Compile wegen `SyntaxError: unmatched ')'` in `a3_cinematic_forge.py`.
- Idempotenter Action-Replay erzeugt keine neuen Commit-IDs und damit keine zweite Feedbackquelle.

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
- Arbeitsregeln um prüfbare Vorplanung, reproduzierbare Update-Nachweise und ein eindeutiges Iterationsende ergänzt.

### Validierung
- `compileall`, 27 gezielte Runtime-/Recovery-Tests, Action-Vertragsprüfung und 0.4.1-Balance-Regression lokal bestanden.
- `Runtime Core` für PR #6 remote erfolgreich bestanden.

### Bewusst offen
- 0.6 setzt die gemeinsame Character-Forge-Presentation auf den validierten Runtime-Kern.
- grafisches Framework, Ranking/Network und Telegram/Sync bleiben späteren Iterationen vorbehalten.

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