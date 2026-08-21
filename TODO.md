# TODO – BUNKERFREQUENZ

## Aktueller Stand

- **Versionierte Runtime-Baseline:** `0.5.2-alpha.1`
- **Aktive Entwicklungsiteration:** `0.6.5 – Ranking / Network Foundation`
- **Abgeschlossen:** `0.6.4 – A3 Cinematic Forge`
- **Aktiver Entwicklungsbranch:** `presentation/0.6.5-ranking-network-foundation`

## 0.6.0 – Repository-/Presentation-Reparatur
- [x] kanonische Character-Projektion, Tests und Package-Exporte repariert
- [x] eigener `Presentation Core` CI-Gate
- [x] konkurrierende PRs #15–#21 geschlossen

## 0.6.1 – Application-Grenze
- [x] bestätigte Capabilities
- [x] zentraler Dispatcher für Profil, Undo und Action
- [x] idempotente Schreibwege
- [x] PR #24 gemergt (`25006d07d33199fea2db8208c192ca2f6fa1095d`)

## 0.6.2 – Lokaler State + bestätigtes Feedback
- [x] immutable lokaler Presentation-State
- [x] bestätigte Eventabfrage und deterministisches Feedback
- [x] Reduced Motion und lokales Dismiss
- [x] PR #26 gemergt (`5161cb42c2b0d38fcb69ea6bd20f9dc5ce1b283a`)

## 0.6.3 – Gemeinsame Komponenten + A4 Ops Deck
- [x] exakt acht gemeinsame Komponenten
- [x] A4-Workflow und dispatcher-fertige Primäraktionen
- [x] 3-Aktions-Limit, 44-px-Ziele, 3-px-Fokus, High Contrast
- [x] PR #28 grün und gemergt (`49603304960147c326953474174aafcff366dcd7`)

## 0.6.4 – A3 Cinematic Forge
- [x] dieselben acht Komponenten, Commands und Accessibility-Verträge wie A4
- [x] Character Stage, Growth Web, Drawer und Development Overlay
- [x] sechs Progressionsfeedbackarten mit nicht blockierenden Animationen
- [x] Reduced-Motion- und fail-soft Fallbacks
- [x] Runtime Core `32516833552` + Presentation Core `32516833514` grün
- [x] PR #29 gemergt (`53f0617ce0c00051c5fae481c43e4ff048dddf94`)

## 0.6.5 – Ranking / Network Foundation

**Aktiver Fokus.** Ranking darf lokale bestätigte Character-Werte verwenden; Events/Clubs und Sync-Metadaten nur aus explizit serverbestätigten Datensätzen. Keine Presence-Erfindung.

- [x] Ranking-Manifest mit Top-10/Alle, Sortiermodi, Tie- und Missing-Data-Regeln angelegt
- [x] Ranking-Projektion für beliebig viele Spieler implementiert
- [x] Sortierung nach Level, Ruf, Resonanz und Skill implementiert
- [x] Events-/Clubranking nur aus `server_confirmed_transaction`-Datensätzen
- [x] Competition Ranking für Gleichstände mit stabilem `character_id`-Tiebreaker
- [x] fehlende Netzwerkmetriken als `null`/unranked statt `0`
- [x] fehlender Sync-Datensatz als `unknown` / `NICHT BESTÄTIGT`, ohne Online-Inferenz
- [x] falsche Autorität, unbekannte Metriken und Identity-Mismatch fail-closed
- [x] sichtbare Ranking-/Sync-Texte ausgelagert
- [x] gezielte Tests für >10 Spieler, Show-All, Gleichstände, Skill/Events/Clubs, Authority und defensive Kopien angelegt
- [ ] Runtime Core auf 0.6.5-PR-Head grün
- [ ] Presentation Core auf 0.6.5-PR-Head grün
- [ ] PR prüfen und mergen

## Danach

### 0.7 – Spielbarer Character-Forge-Vertical-Slice
`Profil → Training/Aktion → Skill-/Trait-Fortschritt → Feedback → Biografie → Autosave → Undo → Reload`

### 0.8 – Event-/Wirtschafts-Integration
Eventplanung, dynamischer Equipmentmarkt, Clubbetrieb und Clubbewertung auf dem validierten Character-/Persistence-Kern.

### 0.9 – Network / Telegram Sync
Asynchroner Crew-Abgleich über versionierte Events und serverbestätigte gemeinsame Ressourcen.

## PR-Regel

Für dieselbe Zielstelle wird nur **ein aktiver Implementierungs-PR** geführt. Relevante Gates müssen vor Merge grün sein.
