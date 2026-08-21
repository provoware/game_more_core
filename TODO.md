# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Aktive Entwicklungsiteration:** `0.6.3 – gemeinsame Komponenten + A4 Ops Deck`
- **Abgeschlossen:** `0.6.2 – lokaler Presentation-State + bestätigtes Feedback`
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

- [x] unveränderlichen lokalen Zustand für `overview`, `skills_traits`, `biography` angelegt
- [x] `view.select`, `biography.filter`, `feedback.dismiss` als reine lokale Transitionen umgesetzt
- [x] Biografie-Filter nutzt Kategorien aus `BIOGRAFIE_MANIFEST.json` statt einer zweiten Handliste
- [x] bestätigte Journalrecords über Application-Leseabfrage `get_confirmed_events(...)` bereitgestellt
- [x] Level-, Skill-, Trait-, Spezialisierungs- und Resonanzereignisse in bestätigtes UI-Feedback projiziert
- [x] Feedback-IDs deterministisch aus bestätigten Event-IDs abgeleitet
- [x] nur katalogisierte bestätigte Journal-/Domain-Ereignisse als Feedback akzeptiert
- [x] sichtbare Feedbacktexte nach `content/de/ui/feedback.json` ausgelagert
- [x] Reduced Motion als statische, nicht blockierende Darstellungsoption abgesichert
- [x] Character-Projektion übernimmt Feedback detached und validiert dessen Textschlüssel
- [x] End-to-End `Command → Commit → Eventquery → Feedback → Projection` getestet
- [x] idempotenter Replay erzeugt keine neuen Commit-IDs und kein doppeltes Feedback
- [x] PR #26: Runtime Core `32511953788` + Presentation Core `32511953619` grün
- [x] PR #26 gemergt (`5161cb42c2b0d38fcb69ea6bd20f9dc5ce1b283a`)

## 0.6.3 – Gemeinsame Komponenten + A4 Ops Deck

**Aktiver Fokus.** Erst gemeinsame frameworkfreie Komponenten, dann A4 als geführter Workflow. Keine zweite Projection und keine zweite Command-Schicht.

- [ ] acht gemeinsame Komponenten implementieren: `CharacterHeader`, `StatusSummary`, `SkillList`, `TraitList`, `SpecializationCard`, `BiographyTimeline`, `ProfileEditor`, `ProgressFeedback`
- [ ] Komponenten erhalten ausschließlich ihren Projection-Block und lokalen Presentation-State
- [ ] `ProfileEditor` nutzt ausschließlich den bestehenden zentralen Command-Dispatcher
- [ ] `ProgressFeedback` nutzt nur bestätigte Feedback-Projektion und lokale Dismiss-/Reduced-Motion-Regeln
- [ ] A4 Ops Deck als Workflow `Ziel → Aktion → Ergebnis → Entwicklung → nächstes Ziel` zusammensetzen
- [ ] maximal drei Primäraktionen gleichzeitig zulassen
- [ ] große Klick-/Touch-Ziele, sichtbaren Tastaturfokus, High-Contrast und Farbe+Icon+Text absichern
- [ ] leere/fehlende optionale Bereiche robust darstellen, ohne erfundene Daten
- [ ] Namen, Alias, zusätzliche Spitznamen und Motto über den bestätigten 0.6.1-Command-Weg editierbar machen
- [ ] A4 bleibt frameworkfrei/testbar; konkrete grafische Toolkit-/Web-Runtime erst nach stabilem View-Model-Vertrag

## 0.6.4 – A3 Cinematic Forge aus denselben Bausteinen

- [ ] A3 verwendet exakt dieselbe Projection, Komponenten und Commands wie A4
- [ ] Skillnetz, Traits, Spezialisierung, Biografie und Resonanz visuell stärker inszenieren
- [ ] Level-/Skill-/Trait-/Resonanz-Up-Feedback anbinden
- [ ] keine zweite Fachlogik und keinen zweiten Persistence-Weg einführen
- [ ] Vertragstest A3↔A4 für Komponenten, Commands und Projection-Identität ergänzen

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

## PR-Regel

Für dieselbe Zielstelle wird nur **ein aktiver Implementierungs-PR** geführt. Alternative Ansätze werden nicht parallel gemergt; sinnvolle Aspekte werden zuerst hier konsolidiert und danach in der vorgesehenen Reihenfolge umgesetzt.
