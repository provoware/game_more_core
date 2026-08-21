# Presentation-Vertrag 0.6 – Character Forge

## Worum geht es?

Die Presentation ist die Schicht zwischen Spielkern und sichtbarer Oberfläche. Sie
liefert fertig sortierte Anzeigedaten und nimmt Bedienwünsche entgegen. A4 Ops Deck
und A3 Cinematic Forge verwenden **denselben** Vertrag und dieselben Komponenten.

Einfach gesagt:

```text
Spielkern → schreibgeschützte Projektion → A4 oder A3
Spielkern ← Application-Command       ← Klick oder Tastatur
```

Eine **Projektion** ist eine nur zum Anzeigen vorbereitete Sicht auf gespeicherte
Daten. Ein **Command** ist ein klar benannter Auftrag an die Application-Schicht.
Die UI verändert niemals selbst `CharacterState`, Journal oder Save-Dateien.

## Verbindliche Grenzen

1. Die Projektion erhält einen geladenen `CharacterState` und Journal-Einträge als
   Eingabe. Sie verändert beides nicht.
2. Jeder sichtbare Text ist ein Schlüssel aus `content/<sprache>/`; technische IDs
   werden nicht als sichtbare Namen benutzt.
3. A3 und A4 dürfen Daten nur anders anordnen. Feldnamen, Commands und Komponenten
   bleiben gleich.
4. Profiländerungen gehen ausschließlich an `CharacterProfileService.update()`;
   Undo geht an `undo_last_profile_update()`.
5. Spielaktionen gehen ausschließlich an `CharacterActionService.execute()`.
6. Die Biografie entsteht nur aus validierten Journal-Ereignissen. Die UI erfindet
   oder speichert keine Chronik-Einträge.
7. Animationen reagieren erst auf ein bestätigtes Ergebnis und blockieren keine
   weitere Bedienung. Reduced Motion zeigt statisches Feedback.
8. Ranking und Sync sind noch nicht angebunden. Platzhalter enthalten keine
   erfundenen Netzwerkdaten.

## Datenvertrag der Projektion

Die spätere Funktion `build_character_projection(character, journal_records,
text_catalog)` liefert ein neues Dictionary in dieser Form. Listen sind bereits in
Anzeigereihenfolge; fehlende optionale Werte sind `null` oder leere Listen.

| Block | Pflichtfelder | Herkunft und Regel |
|---|---|---|
| `meta` | `projection_version`, `character_id` | Version ist `0.6`; ID bleibt technisch und unsichtbar. |
| `overview` | `display_name`, `alias`, `additional_nicknames`, `motto`, `level`, `total_xp`, `resonance_xp`, `resonance_rank`, `energy`, `stress`, `reputation` | Kopien aus `CharacterState`; keine UI-Referenz auf das Domain-Objekt. |
| `top_skills` | höchstens drei Einträge mit `skill_id`, `label_key`, `value`, `xp`, `trend` | Absteigend nach Wert, dann stabil nach `skill_id`; `trend` ist zunächst `null`. |
| `skills` | 16 Einträge mit `skill_id`, `label_key`, `value`, `xp`, `xp_to_next`, `progress_percent`, `trend` | Berechnung nutzt `ProgressionRules`; Prozent liegt zwischen 0 und 100. |
| `traits` | `trait_id`, `label_key`, `tier`, `evidence`, `next_tier`, `progress_percent`, `effect_key`, `consequence_key` | Nur bekannte Manifest-IDs; verdeckte Traits geben keine geheimen Prozentwerte aus. |
| `specialization` | `specialization_id`, `label_key`, `stage`, `stage_label_key` oder `null` | Aus `CharacterState.specialization`; sichtbarer Name kommt aus Content. |
| `biography` | `entry_id`, `event_id`, `category`, `title_key`, `body_key`, `placeholders`, `sequence` | Nur aus gültigen Journal-Ereignissen; aufsteigend nach `sequence`, bei Gleichstand `event_id`. |
| `capabilities` | `can_edit_profile`, `can_undo_profile`, `can_execute_action` | Von der Application-Schicht geliefert; die UI errät Berechtigungen nicht. |
| `feedback` | Liste aus `feedback_id`, `kind`, `title_key`, `detail_keys`, `reduced_motion` | Aus bestätigten Domain-Ereignissen, niemals aus einem bloßen Klick. |

`label_key`, `title_key`, `body_key`, `effect_key` und `consequence_key` sind
Textschlüssel. Die Oberfläche löst sie über den übergebenen `text_catalog` auf.
Fehlt ein Schlüssel, zeigt die Entwicklungsansicht den Schlüssel deutlich an und
schreibt keinen Ersatztext in die Spiellogik.

## UI-Aktionen

Die Oberfläche darf nur diese einfachen Wünsche an einen Adapter senden. Der
Adapter prüft die Eingabe und ruft danach den zuständigen Application-Service auf.

| Command | Eingabe | Zuständiges Ziel | Bestätigtes Ergebnis |
|---|---|---|---|
| `profile.update` | `character_id`, Teilmenge aus `display_name`, `alias`, `additional_nicknames`, `motto`, plus eindeutige Command-/Event-/Transaktions-IDs | `CharacterProfileService.update()` | neue Projektion nach erfolgreichem Commit |
| `profile.undo_last` | `character_id` und eindeutige Command-/Event-/Transaktions-IDs | `CharacterProfileService.undo_last_profile_update()` | neue Projektion oder verständlicher Fehler |
| `action.execute` | `character_id`, `action_id`, `action_instance_id` und nötige Auswahl-IDs | `CharacterActionService.execute()` | neue Projektion und Feedback aus bestätigten Ereignissen |
| `view.select` | `view_id` aus `overview`, `skills_traits`, `biography` | nur lokaler Presentation-Zustand | andere Ansicht; keine Domain-Änderung |
| `biography.filter` | katalogisierte Kategorie oder `all` | nur lokale Projektion | gefilterte Kopie; kein Journal-Write |
| `feedback.dismiss` | `feedback_id` | nur lokaler Presentation-Zustand | Hinweis verschwindet; Gameplay bleibt unverändert |

Freie sichtbare Namen sind niemals IDs. Jeder wiederholte Schreibauftrag besitzt
dieselbe Command-/Event-ID, damit ein Doppelklick nicht doppelt gespeichert wird.

## Gemeinsame Komponenten

Beide Layouts bauen ausschließlich aus `CharacterHeader`, `StatusSummary`,
`SkillList`, `TraitList`, `SpecializationCard`, `BiographyTimeline`,
`ProfileEditor` und `ProgressFeedback`. A4 ordnet sie als geführten Hauptablauf an;
A3 inszeniert dieselben Daten als Charakteransicht. Neue Fachlogik gehört nicht in
eine Komponente.

## Schritt für Schritt: nächste Umsetzung für Einsteiger

Alle Befehle werden im Repository-Root ausgeführt. Eine Zeile mit `#` ist nur eine
Erklärung und wird nicht benötigt.

### 1. Repository öffnen und Ausgangslage prüfen

```bash
cd /workspace/game_more_core
git status --short --branch
```

**Erwartung:** Die erste Zeile nennt den Branch. Vor neuen Änderungen sollte keine
unbekannte Datei erscheinen. Vorhandene fremde Änderungen niemals löschen.

### 2. Die vier direkten Verträge lesen

```bash
sed -n '1,220p' docs/PRESENTATION_CONTRACT_0.6.md
sed -n '1,120p' docs/ARCHITEKTURVERTRAG.md
sed -n '1,120p' docs/UI_UX_BLUEPRINT.md
sed -n '1,140p' src/bunkerfrequenz/domain/character.py
```

**Tipp:** Erst Feldnamen nachschlagen, dann Code schreiben. So entstehen keine fast
gleichen Namen wie `name` neben dem vorhandenen `display_name`.

### 3. Genau eine kleine Folgeiteration planen

Als nächster Patch wird nur die reine Projektionsfunktion samt gezieltem Unit-Test
angelegt. Adapter, A4, A3 und grafisches Framework bleiben späteren Iterationen
vorbehalten. Im Plan stehen Ziel, Abnahme, Dateien, Risiken und Nicht-Ziele.

### 4. Kleine Zielprüfung ausführen

Nach dem Patch werden nur Syntax und der neue Presentation-Test geprüft:

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest tests.presentation.test_character_projection -v
```

**Erwartung:** Beide Befehle enden ohne `FAILED` oder `ERROR`. Gibt es den Ordner
oder Test noch nicht, ist das vor der Folgeiteration normal; dann nicht behaupten,
die Prüfung sei gelaufen.

### 5. Änderung vor dem Commit ansehen

```bash
git diff --check
git diff -- src/bunkerfrequenz/presentation tests/presentation
git status --short
```

`git diff --check` findet unter anderem störende Leerzeichen. Der zweite Befehl
zeigt nur den geplanten Scope. Erst danach wird mit einer eindeutigen Nachricht
committet.

## Abnahme dieses Vertrags

- Overview, Skills, Traits, Spezialisierung und Biografie besitzen eindeutige
  Projektionsfelder.
- Profil- und Spieländerungen besitzen genau einen Application-Weg.
- A3 und A4 teilen Datenvertrag und Komponenten.
- Texte, IDs, Journal, Accessibility und Reduced Motion haben klare Grenzen.
- Noch nicht vorhandener UI-Code, Frameworkwahl, Ranking und Sync bleiben bewusst
  unverändert.
