# CHANGELOG

Alle relevanten Änderungen werden hier nachvollziehbar geführt.

## Unveröffentlicht

### Release-Planung

- veralteten 0.8.1-Mergevorbehalt nach dem belegten Merge von PR #48 entfernt, 0.8.2 als aktive Iteration gesetzt und den Pflichtpfad auf die drei tatsächlich offenen Release-Pakete reduziert.
- Release-Manifest von der überholten Architektur-Foundation auf die unverändert gültige Runtime-Baseline `0.5.2-alpha.1` samt Journal-/Save-Schemastand 2 abgeglichen.
- Spieleranleitung nennt jetzt eine sofort ausführbare, schreibgeschützte Prüfung und grenzt sie klar von der kommenden Equipment-/Economy-Stufe ab.
- README und TODO trennen den verpflichtenden Pfad zum ersten lokal spielbaren Alpha von nachgelagerter Härtung und späterem Netzwerkbetrieb.
- prüfbare Release-Abnahme für Runtime-Client, Ersteinstieg, vollständigen Event-/Economy-Loop sowie Save/Recovery aus einem frischen Checkout ergänzt; eine Versionsanhebung erfolgt weiterhin erst nach grüner Abnahme.
- Spieleranleitung erklärt laiengerecht, woran der aktuelle Prototyp und das spätere spielbare Alpha zu unterscheiden sind.
- 0.8.2 wird nur als gemeinsamer Economy-Vertical-Slice abgenommen und der schreibende A4-Client beginnt erst nach bestätigtem 0.8.3.

### HTML-Blueprint-Auswertung

- grafische Hierarchie des statischen Blueprints mit Control-Room-Orientierung, stärkerem Referenzrahmen, gerichteter Workflow-Linie, klarer Variantenstaffelung und ruhiger responsiver Anordnung verbessert; Reduced Motion, Tastaturfokus und der schreibgeschützte Modus bleiben erhalten.
- statische, frameworkfreie HTML-Übertragung ergänzt: Die kanonische WebP-Grafik bleibt als unveränderte Pixelreferenz sichtbar, während Workflow und vier UI-Varianten aus dem bestehenden UI-Manifest auswertbar gerendert werden.
- vollautomatische Standardbibliothek-Startroutine mit Dateivorprüfung, lokalem Server, Browseröffnung, verständlicher Statusausgabe und belegbarem Portfehler ergänzt.
- lokalen Serverstart atomar gebunden, Portbereich vor dem Start validiert und die sofort ausgegebene Adresse bei automatischer Portwahl aus dem tatsächlich gestarteten Server abgeleitet.
- kopierbarer Browser-Prüfbericht einschließlich Prüfung sichtbarer Pixelfläche, Tastaturfokus, Responsive Layout, Reduced Motion und High-Contrast-Fallback verbessern Diagnose und Zugänglichkeit; das aktuell überwiegend transparente WebP wird als eingeschränkt gemeldet und die Ansicht bleibt ausdrücklich ohne Domain-Schreibzugriff.
- Spieleranleitung um einen laiengerechten Ein-Befehl-Start, Stopp, manuellen Browserweg und Port-Fehlerhilfe erweitert.

### 0.8.1 – Event State Foundation

- `EventState` als eigener, streng validierter Domain-State mit Ort, Budgetrahmen, Acts, Crew, Equipment-Readiness, Zeitfenster, Sicherheitsstatus, Eventphase und monotoner Revision eingeführt.
- Phasenmaschine `draft → planning → procurement → transport → setup → soundcheck → live/crisis → teardown → settlement → completed` mit begründeten Rück-/Abbruchwegen implementiert.
- physische Eventphasen verlangen gesetzten Ort, explizit verifizierten Zugangsstatus, gültiges offset-aware Zeitfenster und `safety_status=cleared`.
- neue Journaltypen `event.created` und `event.phase_changed` ergänzt; vorhandenes `event.planning_updated` als zustandsbildender Planungsweg konkretisiert. `event.started`, `event.incident_resolved` und `event.completed` bleiben für 0.8.3 reserviert.
- `EventStateService` für Event-Erstellung, Planungsupdates, Phasenwechsel, Command-Idempotenz und Stale-Revision-Schutz ergänzt.
- abgeleitete Save-Zustände werden blockweise aktualisiert: Character-/Profil-Commits erhalten `event`, Event-Commits erhalten `character` und weitere bestehende Blöcke.
- `GameRecoveryService` kombiniert Character- und Event-Replay, ohne den bestehenden `PersistenceKernel` unnötig zu verändern.
- Fault-Injection-Regression für einen bereits journal-durablen, aber noch nicht in den State geschriebenen Event-Commit ergänzt.
- `EVENT_STATE_MANIFEST.json`, `event_state.schema.json` und `docs/EVENT_STATE_0.8.1.md` als maschinenlesbarer und menschlich lesbarer Vertrag ergänzt.
- README, TODO, Projektstatus, Projektmanifest, Runtime-/Testmanifest und Repository-Index auf die aktive Iteration 0.8.1 abgeglichen; Runtime-Produktbaseline bleibt bewusst `0.5.2-alpha.1`.
- 0.8.2 bleibt klar getrennt: Marktpreise, Inventarbesitz, Kaufen/Verkaufen/Verbrauchen und Economy-Ledger sind nicht Bestandteil von 0.8.1.
- versehentlich angelegter leerer `tmp`-Direktcommit wurde vor Fortsetzung von 0.8.1 über PR #47 mit drei grünen Gates und `SAFE MERGE PASS` vollständig entfernt.
- erste 0.8.1-Remote-Abnahme auf PR #48 / Head `79cc26bec0a780322874ea6f3ced458e8ee72bd6`: Runtime Core `32537531324`, Presentation Core `32537531305`, Repository Health `32537531303` erfolgreich; finale Informationsänderungen werden anschließend auf ihrem eigenen Head erneut geprüft.

### 0.7.2 – Character-Forge-Vertical-Slice

- alle 20 Manifest-Actions besitzen verbindliche Energie-/Stresswirkungen; der Character State begrenzt beide Ressourcen auf `0–100`.
- `character.resources_changed` wird vor den Progressionsereignissen journalisiert und beim Recovery mit Alt-/Neuwertprüfung deterministisch replayt.
- Action, Progression und ausreichend bedeutende dynamische Biografieeinträge werden atomar über denselben bestätigten Action-Commit geführt.
- `CharacterForgeSessionService` verbindet bestätigte Commands mit 60-Sekunden-Autosave, Recovery-Snapshot und Reload.
- Undo bleibt auf vorhandene kompensierende Regeln beschränkt; Gameplay-Actions werden nicht inkonsistent teilweise zurückgedreht.
- A4 Ops Deck zeigt reale Ressourcenwerte; A4 und A3 projizieren denselben bestätigten Status-, Biografie- und Feedbackzustand.
- vollständiger Integrationstest für `Action → Ressourcen → Progression → Feedback → Biografie → Autosave → Undo → Reload → A4/A3` ergänzt.
- erste Remote-Abnahme auf PR #41 deckte zwei veraltete synthetische Action-Fixtures ohne neuen Pflicht-Ressourcenvertrag auf; ausschließlich diese Test-Fixtures wurden neutral angepasst, die Produktlogik blieb unverändert.
- validierter PR-Head `5f7ded400a5fca1ee25307797628ab2584de9812`: Runtime Core `32533954380`, Presentation Core `32533954387`, Repository Health `32533954406` erfolgreich.
- PR #41 wurde nach grüner Abnahme als Merge `a7544abd923787d20e174c9eced54f548753c801` übernommen, jedoch außerhalb des vorgeschriebenen `/safe-merge`-Kommandos. Folgende normale PRs verwenden wieder ausschließlich `/safe-merge`.
- README visuell neu strukturiert; eigene laienfreundliche `docs/SPIELERANLEITUNG.md` für den Character-Forge-Ablauf ergänzt.
- TODO, Projektstatus, Projektmanifest, Testmanifest und Repository-Index auf den abgeschlossenen 0.7.2-Stand und den nächsten Schritt 0.8 abgeglichen.
- Main-Integrity-Incident #40 zum direkten `fb96a489...`-Commit analysiert und geschlossen: Guard reagierte korrekt auf fehlende PR-Provenienz; der betroffene AGENTS-Inhalt wurde in PR #41 erneut dreifach grün validiert.

### Behoben
- Snapshot-Recovery prüft Snapshot-Dateien und rekonstruierte Indexeinträge vollständig, überspringt strukturell beschädigte oder aus dem Snapshot-Verzeichnis führende Kandidaten einzeln und fällt kontrolliert auf den neuesten gültigen Checkpoint zurück.
- Journal-Recovery weist strukturell ungültige JSON-Datensätze kontrolliert zurück und quarantänisiert den vollständigen ungültigen Rest, statt interne Python-Fehler weiterzugeben.
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
- Zielpolicy für `main`: Pull Request erforderlich, Branch aktuell, Conversation Resolution, keine Force Pushes/Branch-Löschung sowie `runtime-core`, `presentation-core`, `repository-health` verpflichtend. Die GitHub-Aktivierung bleibt extern, weil die verbundene Schnittstelle Branch-Protection nicht sicher schreiben kann.
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
- Skill- und Trait-Gewichte je Action = 1.0.
- Biografie-Relevanz 0–100.
- Systemzeit nicht als Zufallsseed.
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
- kein Spiel-Laufzeitcode, keine UI, kein Telegram, keine Persistenzimplementierung.

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
