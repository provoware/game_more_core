# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Aktive Entwicklungsiteration:** `0.6.2 – lokaler Presentation-State + bestätigtes Feedback`
- **Abgeschlossen:** `0.6.1 – Application-Grenze für Presentation`
- **Offene konkurrierende PRs:** `0`

## 0.6.0 – Repository-/Presentation-Reparatur

- [x] beschädigte doppelte `character_projection.py` auf eine kanonische Implementierung zurückgeführt
- [x] widersprüchlich zusammenkopierte Projection-Tests zu einem Vertragstest-Satz konsolidiert
- [x] `presentation/__init__.py` auf eindeutige Exporte für Character- und Biografieprojektion repariert
- [x] eigener zielgerichteter `Presentation Core`-CI-Workflow angelegt
- [x] Release-Baseline und aktive Entwicklungsiteration in den Info-Dateien getrennt
- [x] konkurrierende PR-Ideen in diese sequenzielle Roadmap überführt
- [x] Runtime Core und Presentation Core auf Reparatur-Head grün
- [x] Reparatur-PR #22 nach `main` gemergt
- [x] konkurrierende Presentation-PRs #15–#21 mit Begründung geschlossen

## 0.6.1 – Application-Grenze für Presentation

- [x] `can_edit_profile`, `can_undo_profile`, `can_execute_action` ausschließlich aus der Application ableiten
- [x] Profile-Update, Profil-Undo und Action-Ausführung über **einen** Command-Dispatcher routen
- [x] Character-/Command-/Profil-Event-/Profil-Transaction-/Action-Instance-IDs validieren und über die zuständigen bestehenden Services führen
- [x] UI-gesteuerte Balanceparameter wie `base_xp` und Evidenzquelle nicht freigeben
- [x] idempotente Wiederholung von Profilupdate, Undo und Action gezielt testen
- [x] Projection erhält bestätigte Capabilities als begrenzte, defensive Kopie und errät keine Rechte
- [x] Runtime Core für PR #24 grün (`32510846508`)
- [x] Presentation Core für PR #24 grün (`32510846537`)
- [x] PR #24 nach `main` gemergt (`25006d07d33199fea2db8208c192ca2f6fa1095d`)

## 0.6.2 – Lokaler Presentation-State + bestätigtes Feedback

- [ ] unveränderlichen lokalen Zustand für `overview`, `skills_traits`, `biography` anlegen
- [ ] `view.select`, `biography.filter`, `feedback.dismiss` als reine lokale Transitionen implementieren
- [ ] Level-, Skill-, Trait-, Spezialisierungs- und Resonanzereignisse in bestätigtes UI-Feedback projizieren
- [ ] Feedback-IDs deterministisch aus bestätigten Event-IDs ableiten
- [ ] nur katalogisierte bestätigte Journal-/Domain-Ereignisse als Feedback akzeptieren
- [ ] Reduced Motion als statische, nicht blockierende Darstellung absichern
- [ ] sicherstellen, dass lokaler Presentation-State niemals Save, Journal oder CharacterState verändert

## 0.6.3 – Gemeinsame Komponenten + A4 Ops Deck

- [ ] acht gemeinsame Komponenten implementieren: `CharacterHeader`, `StatusSummary`, `SkillList`, `TraitList`, `SpecializationCard`, `BiographyTimeline`, `ProfileEditor`, `ProgressFeedback`
- [ ] Komponenten erhalten nur ihren Projection-Block und lokalen Presentation-State
- [ ] A4 Ops Deck als geführten Workflow `Ziel → Aktion → Ergebnis → Entwicklung → nächstes Ziel` zusammensetzen
- [ ] maximal drei Primäraktionen, große Ziele, sichtbarer Fokus und High-Contrast prüfen
- [ ] editierbare Namen, Alias, zusätzliche Spitznamen und Motto über den Command-Weg anbinden

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
- [x] **0.6 Foundation** Presentation-Vertrag, deutsche Textkataloge, Character-/Biografieprojektion und Repository-Reparatur
- [x] **0.6.1** bestätigte Application-Capabilities + zentraler Command-Dispatcher

## PR-Regel

Für dieselbe Zielstelle wird künftig nur **ein aktiver Implementierungs-PR** geführt. Alternative Ansätze werden nicht parallel gemergt; nützliche Aspekte werden zuerst in dieser Roadmap konsolidiert und danach in der vorgesehenen Reihenfolge umgesetzt.
