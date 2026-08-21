# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Zuletzt abgeschlossene Feature-Iteration:** `0.7.1 – A4 Action-Auswahl`
- **Nächster Feature-Schritt:** `0.7.2 – Ressourcenwirkung + vollständiger Character-Forge-Ablauf`
- **Aktiver Feature-PR:** keiner

## Repository Guard vor 0.7.2

- [x] `REPOSITORY_GUARD_MANIFEST.json` als kanonische Merge-/Health-Policy angelegt
- [x] `tools/repository_health.py` ohne externe Abhängigkeiten implementiert
- [x] `Repository Health` als eigener PR-/main-/Merge-Group-Gate angelegt
- [x] Runtime Core und Presentation Core so umgestellt, dass sie bei jedem PR einen Required-Check-Status liefern
- [x] Guard prüft JSON, Python-Struktur/Compile, Konfliktmarker, Status-/Versionskonsistenz, öffentliche Exporte und kanonische Symbole
- [x] Guard blockiert veraltete versionsgebundene Feature-Branches
- [x] Workflow blockiert PR-Heads, die den aktuellen `main` nicht enthalten
- [x] erster Remote-Nachweis auf PR #34: Runtime Core `32522336221`, Presentation Core `32522336259`, Repository Health `32522336287` grün
- [ ] GitHub-Branch-Protection/Ruleset für `main` extern aktivieren: `runtime-core`, `presentation-core`, `repository-health` verpflichtend + Branch aktuell + Conversation Resolution
- [ ] erst danach 0.7.2-Gameplay fortsetzen

## 0.6.0 – Repository-/Presentation-Reparatur

- [x] beschädigte doppelte `character_projection.py` auf eine kanonische Implementierung zurückgeführt
- [x] widersprüchliche Projection-Tests konsolidiert
- [x] eindeutige Presentation-Package-Exporte wiederhergestellt
- [x] `Presentation Core` als eigener zielgerichteter CI-Gate angelegt
- [x] Release-Baseline und aktive Entwicklungsiteration in den Info-Dateien getrennt
- [x] PR #22 mit Runtime Core + Presentation Core grün gemergt
- [x] konkurrierende Presentation-PRs #15–#21 mit Begründung geschlossen

## 0.6.1 – Application-Grenze für Presentation

- [x] `can_edit_profile`, `can_undo_profile`, `can_execute_action` ausschließlich aus der Application ableiten
- [x] Profilupdate, Profil-Undo und Action-Ausführung über **einen** Command-Dispatcher routen
- [x] notwendige IDs validieren und über die zuständigen bestehenden Services führen
- [x] UI-gesteuerte Balanceparameter nicht freigeben
- [x] Profilupdate, Undo und Action-Wiederholung idempotent testen
- [x] Projection erhält bestätigte Capabilities als begrenzte defensive Kopie
- [x] PR #24: Runtime Core `32510846508` + Presentation Core `32510846537` grün
- [x] PR #24 gemergt (`25006d07d33199fea2db8208c192ca2f6fa1095d`)

## 0.6.2 – Lokaler Presentation-State + bestätigtes Feedback

- [x] unveränderlichen Zustand für `overview`, `skills_traits`, `biography` angelegt
- [x] lokale View-/Filter-/Dismiss-Transitionen ohne Persistenzwirkung umgesetzt
- [x] Biografie-Filter nutzt `BIOGRAFIE_MANIFEST.json`
- [x] bestätigte Journalrecords über Application-Abfrage bereitgestellt
- [x] Level-, Skill-, Trait-, Spezialisierungs- und Resonanzfeedback projiziert
- [x] deterministische Feedback-IDs aus bestätigten Event-IDs
- [x] sichtbare Feedbacktexte ausgelagert
- [x] Reduced Motion fachlich zustandsneutral
- [x] End-to-End `Command → Commit → Eventquery → Feedback → Projection`
- [x] idempotenter Replay erzeugt kein doppeltes Feedback
- [x] PR #26: Runtime Core `32511953788` + Presentation Core `32511953619` grün
- [x] PR #26 gemergt (`5161cb42c2b0d38fcb69ea6bd20f9dc5ce1b283a`)

## 0.6.3 – Gemeinsame Komponenten + A4 Ops Deck

- [x] acht gemeinsame Komponenten implementiert
- [x] Komponenten erhalten nur Projection-Blöcke und lokalen Presentation-State
- [x] `ProfileEditor` nutzt ausschließlich den zentralen Command-Dispatcher-Vertrag
- [x] `ProgressFeedback` nutzt bestätigte Feedback-Projektion und lokale Dismiss-/Reduced-Motion-Regeln
- [x] A4 Ops Deck als Workflow `Ziel → Aktion → Ergebnis → Entwicklung → nächstes Ziel`
- [x] maximal drei Primäraktionen; vierte Aktion wird abgewiesen
- [x] 44-px-Ziele, 3-px-Fokus, High-Contrast und Farbe+Icon+Text aus Manifestvertrag
- [x] leere optionale Bereiche erfinden keine Daten
- [x] Profiländerungen laufen über den bestätigten Application-Weg
- [x] PR #28: Runtime Core `32514970109` + Presentation Core `32514970398` grün
- [x] PR #28 gemergt (`49603304960147c326953474174aafcff366dcd7`)

## 0.6.4 – A3 Cinematic Forge

- [x] A3 verwendet dieselbe Projection und exakt dieselben acht Komponenten wie A4
- [x] A3 übernimmt Primäraktionen direkt aus dem validierten A4-Interaktionsvertrag
- [x] Character Stage, Live-Status, Skill-/Trait-Netz und Drawer definiert
- [x] sechs Progressionsfeedbackarten an katalogisierte Animationen gebunden
- [x] Reduced Motion und fail-soft statische Fallbacks
- [x] Vertragstest A3↔A4 für Komponenten, Commands, Accessibility und Primäraktionslimit
- [x] Runtime Core `32516833552` + Presentation Core `32516833514` auf PR #29 grün
- [x] PR #29 gemergt (`53f0617ce0c00051c5fae481c43e4ff048dddf94`)

## 0.6.5 – Ranking / Network Foundation

- [x] Ranking-Projektion für beliebig viele Spieler
- [x] Top 10 als Standard und `ALLE ANZEIGEN`
- [x] Sortierung nach Level, Skills, Ruf, Events, Clubs und Resonanz
- [x] Competition Ranking mit stabiler Gleichstandsregel
- [x] Events/Clubs nur aus `server_confirmed_transaction`-Datensätzen
- [x] fehlende Network-Metriken bleiben `null` und unranked
- [x] fehlende Sync-Daten werden `unknown` / `NICHT BESTÄTIGT`, ohne Presence abzuleiten
- [x] falsche Autorität, unbekannte Metriken, doppelte IDs und Character-Mismatch fail-closed
- [x] sichtbare Ranking-/Sync-Texte ausgelagert
- [x] Runtime Core `32517683276` + Presentation Core `32517683263` auf PR #30 grün
- [x] PR #30 gemergt (`4090c3e2118e81d0927fbc7a5cfcdf48190631e9`)

## 0.7 – Spielbarer Character-Forge-Vertical-Slice

`Profil → Training/Aktion → Skill-/Trait-Fortschritt → Feedback → Biografie → Autosave → Undo → Reload`

### 0.7.1 – A4 Action-Auswahl

- [x] alle 20 Manifest-Actions als kanonische A4-Auswahlliste projiziert
- [x] Dauer, Voraussetzungen und gewichtete erwartete Skillwirkung angezeigt
- [x] nicht bestätigte Voraussetzungen sperren die Action fail-closed
- [x] fehlende Energie-/Stresswerte ausdrücklich als nicht festgelegt markiert
- [x] PR #31: Runtime Core `32519042006` + Presentation Core `32519041908` grün
- [x] PR #31 gemergt (`888be18146197272578f4baa5516f78a894d9464`)
- [x] Review-P1 behoben: Auswahl enthält kein scheinbar ausführbares Teil-Command mehr
- [x] `build_action_execute_command(...)` erzeugt erst mit `command_id` und `action_instance_id` einen dispatcher-fertigen Command
- [x] Review-P2 behoben: A4 prüft `can_execute_action` beim Zusammensetzen erneut und sperrt stale Auswahlzustände
- [x] Regressionstests für Dispatcher-Kompatibilität und Capability-Entzug ergänzt

### 0.7.2 – Ressourcenwirkung + vollständiger Ablauf

- [ ] Energie-/Stresskosten fachlich je Action katalogisieren
- [ ] Energie-/Stresswirkung im Resolver deterministisch anwenden
- [ ] Training/Aktion → Progression → bestätigtes Feedback verbinden
- [ ] Biografie-Eintrag aus bestätigten relevanten Ereignissen in den Ablauf integrieren
- [ ] 60-Sekunden-Autosave und kritische Flush-Punkte im spielbaren Ablauf verwenden
- [ ] Undo nur über bestehende kompensierende Regeln anbieten
- [ ] Reload/Recovery im vollständigen Vertical-Slice testen
- [ ] A4 und A3 auf denselben bestätigten Ergebniszustand zurückprojizieren

## Später

### 0.8 – Event-/Wirtschafts-Integration

Eventplanung, dynamischer Equipmentmarkt, Clubbetrieb und Clubbewertung auf dem validierten Character-/Persistence-Kern.

### 0.9 – Network / Telegram Sync

Asynchroner Crew-Abgleich über versionierte Events und serverbestätigte gemeinsame Ressourcen.

## Abgeschlossene Meilensteine

- [x] **0.4.0** Architekturvertrag, Character-Forge-Foundation, 11 Figuren und gleiche Startwerte
- [x] **0.4.1** Trait Engine, Progression, Spezialisierungen und deterministischer Simulator
- [x] **0.4.2** Persistence Contract, Autosave, Undo, Snapshot-/Recovery-Regeln
- [x] **0.4.3** vier Industrial-Brutalist-UI/UX-Blueprints
- [x] **0.4.4** 20 datengetriebene Gameplay Actions
- [x] **0.5.0** Headless Character-/Action-/Persistence-Core
- [x] **0.5.1** Snapshot-Replay, Recovery, Fault Injection und Profil-Undo
- [x] **0.5.2** Trait-Auswirkungen, Soft-Konflikte und Open-End-Resonanz
- [x] **0.6 Foundation** Presentation-Vertrag und Character-/Biografieprojektion
- [x] **0.6.1** Application-Capabilities + zentraler Command-Dispatcher
- [x] **0.6.2** lokaler Presentation-State + bestätigtes Progressionsfeedback
- [x] **0.6.3** gemeinsame Komponenten + A4 Ops Deck
- [x] **0.6.4** A3 Cinematic Forge
- [x] **0.6.5** Ranking / Network Foundation
- [x] **0.7.1** A4 Action-Auswahl

## PR-Regel

Für dieselbe Zielstelle wird nur **ein aktiver Implementierungs-PR** geführt. Für `main` müssen `runtime-core`, `presentation-core` und `repository-health` vorhanden und grün sein. Ein veralteter Branch oder ein rotes/fehlendes Gate blockiert den Merge.
