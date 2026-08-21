# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Aktive Entwicklungsiteration:** `0.6.4 – A3 Cinematic Forge`
- **Abgeschlossen:** `0.6.3 – gemeinsame Komponenten + A4 Ops Deck`
- **Offene konkurrierende PRs:** `0`

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

- [x] exakt acht gemeinsame frameworkfreie Komponenten implementiert
- [x] Komponenten erhalten ausschließlich Projection-Blöcke und lokalen Presentation-State
- [x] `ProfileEditor` verweist ausschließlich auf den bestehenden zentralen Dispatcher
- [x] `ProgressFeedback` filtert Dismiss/Reduced Motion im tatsächlichen Komponentenpayload
- [x] A4 Ops Deck als Workflow `Ziel → Aktion → Ergebnis → Entwicklung → nächstes Ziel`
- [x] Primäraktionslimit direkt aus `UI_MANIFEST.json`, aktuell maximal drei
- [x] 44-px-Ziele, 3-px-Fokus, Tastatur, Screenreader, High Contrast und Text+Icon+Tone aus Manifestvertrag
- [x] leere optionale Bereiche erzeugen keine erfundenen Daten
- [x] Profilfelder bleiben auf Name, Alias, Spitznamen und Motto begrenzt
- [x] Primäraktionen sind direkt dispatcher-kompatibel; keine Übersetzungsschicht
- [x] alte PR-#19-Regressionspunkte gezielt ausgeschlossen
- [x] PR #28: Runtime Core `32514970109` + Presentation Core `32514970398` grün
- [x] PR #28 gemergt (`49603304960147c326953474174aafcff366dcd7`)

## 0.6.4 – A3 Cinematic Forge aus denselben Bausteinen

**Aktiver Fokus.** A3 darf nur Inszenierung ergänzen; Projection, Komponenten, Capabilities, lokale Zustände und Schreibcommands bleiben dieselben wie in A4.

- [x] A3-Composer `a3_cinematic_forge.py` angelegt
- [x] exakt dieselben acht Komponenten wie A4 verwenden
- [x] gemeinsamen Action-Normalisierer für A3 und A4 extrahieren statt Commandregeln zu duplizieren
- [x] gemeinsame Textschlüsselprüfung für A3/A4 zentralisieren
- [x] Charakterbühne, radiales Skillnetz, Trait-Orbit, Spezialisierungsfokus, Kontext-Drawer und Biografie-Schiene als reine Layoutprojektion definieren
- [x] Progress-Overlay ausschließlich aus bestätigtem `ProgressFeedback` ableiten
- [x] Animation-Cues aus bestätigten sichtbaren Feedbackereignissen erzeugen
- [x] Level-, Skill-, Trait-, Spezialisierungs- und Resonanz-Up an `ANIMATION_MANIFEST.json` anbinden
- [x] `anim.resonance_up` mit statischem Fallback ergänzen
- [x] Animationen bleiben immer überspringbar und `max_blocking_ms = 0`
- [x] Reduced Motion ersetzt Bewegung durch statische Fallbacks, ohne Inhalt zu ändern
- [x] Dismissed Feedback erzeugt weder Karte noch Animation-Cue
- [x] A3 und A4 erzeugen identische normalisierte Schreibaktionen
- [x] doppelte Primäraktions-IDs werden fail-closed abgewiesen
- [x] A3 erfindet keine Avatar-/Portraitdaten, solange keine bestätigte Quelle existiert
- [x] gezielte A3-, Animation- und A3↔A4-Vertragstests angelegt
- [ ] Runtime Core auf finalem PR-Head grün
- [ ] Presentation Core auf finalem PR-Head grün
- [ ] PR mergen und 0.6.4-Abschluss dokumentieren

## 0.6.5 – Ranking / Network vorbereiten

- [ ] Ranking-Projektion für beliebig viele Spieler definieren
- [ ] Filter/Sortierung nach Level, Skills, Ruf, Events, Clubs und Resonanz vorbereiten
- [ ] Network-Ansicht zunächst mit bestätigten synchronisierten Daten versorgen
- [ ] Telegram/Sync weiterhin als eigene Infrastrukturphase behandeln
- [ ] keine erfundenen Online-, Ranking- oder Presence-Daten anzeigen

## Danach

### 0.7 – Spielbarer Character-Forge-Vertical-Slice

`Profil → Training/Aktion → Skill-/Trait-Fortschritt → Feedback → Biografie → Autosave → Undo → Reload`

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
- [x] **0.6 Foundation** Presentation-Vertrag, Textkataloge, Character-/Biografieprojektion und Repository-Reparatur
- [x] **0.6.1** bestätigte Application-Capabilities + zentraler Command-Dispatcher
- [x] **0.6.2** immutable lokaler Presentation-State + bestätigtes deterministisches Progressionsfeedback
- [x] **0.6.3** acht gemeinsame Komponenten + manifestgesteuertes A4 Ops Deck

## PR-Regel

Für dieselbe Zielstelle wird nur **ein aktiver Implementierungs-PR** geführt. Alternative Ansätze werden nicht parallel gemergt; sinnvolle Aspekte werden zuerst hier konsolidiert und danach in der vorgesehenen Reihenfolge umgesetzt.
