# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Aktive Entwicklungsiteration:** `0.6.5 – Ranking / Network Foundation`
- **Abgeschlossen:** `0.6.4 – A3 Cinematic Forge`
- **Aktiver Entwicklungsbranch:** `presentation/0.6.5-ranking-network-foundation`

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

- [x] acht gemeinsame Komponenten implementiert: `CharacterHeader`, `StatusSummary`, `SkillList`, `TraitList`, `SpecializationCard`, `BiographyTimeline`, `ProfileEditor`, `ProgressFeedback`
- [x] Komponenten erhalten nur Projection-Blöcke und lokalen Presentation-State
- [x] `ProfileEditor` nutzt ausschließlich den bestehenden zentralen Command-Dispatcher-Vertrag
- [x] `ProgressFeedback` nutzt bestätigte Feedback-Projektion und lokale Dismiss-/Reduced-Motion-Regeln
- [x] A4 Ops Deck als Workflow `Ziel → Aktion → Ergebnis → Entwicklung → nächstes Ziel` umgesetzt
- [x] maximal drei Primäraktionen; vierte Aktion wird abgewiesen statt still abgeschnitten
- [x] 44-px-Ziele, 3-px-Fokus, High-Contrast und Farbe+Icon+Text aus Manifestvertrag eingebunden
- [x] leere/fehlende optionale Bereiche bleiben leer statt Daten zu erfinden
- [x] Namen, Alias, zusätzliche Spitznamen und Motto laufen über den bestätigten 0.6.1-Command-Weg
- [x] A4 bleibt frameworkfrei und testbar
- [x] PR #28: Runtime Core `32514970109` + Presentation Core `32514970398` grün
- [x] PR #28 gemergt (`49603304960147c326953474174aafcff366dcd7`)

## 0.6.4 – A3 Cinematic Forge aus denselben Bausteinen

- [x] A3 verwendet dieselbe Projection und exakt dieselben acht Komponenten wie A4
- [x] A3 übernimmt Primäraktionen direkt aus dem validierten A4-Interaktionsvertrag
- [x] Character Stage, Live-Status, radiales Skill-/Trait-Netz, Context-/Profile-/Story-Drawer und Development Overlay definiert
- [x] Level-, Skill-, Trait-Unlock-, Trait-Tier-, Spezialisierungs- und Resonanz-Up-Feedback an katalogisierte Animationen gebunden
- [x] `anim.trait_tier_up` und `anim.resonance_up` mit statischen Fallbacks ergänzt
- [x] Reduced Motion erzwingt statische Entwicklungskarten ohne Inhaltsverlust
- [x] fehlende oder blockierende Animation fällt fail-soft auf statische Karte zurück
- [x] Vertragstest A3↔A4 für Komponenten, Commands, Accessibility und Primäraktionslimit ergänzt
- [x] sichtbare A3-Texte in `content/de/ui/character_forge.json` ausgelagert
- [x] Runtime Core `32516833552` auf PR #29 grün
- [x] Presentation Core `32516833514` auf PR #29 grün
- [x] PR #29 gemergt (`53f0617ce0c00051c5fae481c43e4ff048dddf94`)

## 0.6.5 – Ranking / Network vorbereiten

**Aktiver Fokus.** Ranking nutzt bestätigte Character-Projections; Events/Clubs und Sync-Metadaten nur explizit serverbestätigt. Keine Online-/Presence-Erfindung.

- [x] Ranking-Projektion für beliebig viele Spieler definiert
- [x] Top 10 als Standard und `ALLE ANZEIGEN` für vollständige Liste vorgesehen
- [x] Sortierung nach Level, Skills, Ruf, Events, Clubs und Resonanz implementiert
- [x] Competition Ranking mit stabiler Gleichstandsregel implementiert
- [x] Network-Ansicht verarbeitet Events/Clubs nur aus `server_confirmed_transaction`-Datensätzen
- [x] fehlende Network-Metriken bleiben `null` und unranked statt als `0` zu erscheinen
- [x] fehlende Sync-Daten werden `unknown` / `NICHT BESTÄTIGT`, ohne Presence abzuleiten
- [x] Telegram/Sync weiterhin als eigene Infrastrukturphase behandelt
- [x] falsche Autorität, unbekannte Metriken, doppelte IDs und Character-Mismatch fail-closed
- [x] sichtbare Ranking-/Sync-Texte ausgelagert
- [x] gezielte Ranking-/Network-Vertragstests angelegt
- [ ] Runtime Core auf aktuellem 0.6.5-PR-Head grün
- [ ] Presentation Core auf aktuellem 0.6.5-PR-Head grün
- [ ] sauberen Diff prüfen und PR mergen

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
- [x] **0.6.3** gemeinsame Komponenten + A4 Ops Deck
- [x] **0.6.4** A3 Cinematic Forge auf gemeinsamem A4-Vertrag

## PR-Regel

Für dieselbe Zielstelle wird nur **ein aktiver Implementierungs-PR** geführt. Alternative Ansätze werden nicht parallel gemergt; sinnvolle Aspekte werden zuerst hier konsolidiert und danach in der vorgesehenen Reihenfolge umgesetzt.
