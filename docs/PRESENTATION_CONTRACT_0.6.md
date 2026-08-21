# Presentation-Vertrag 0.6 – Character Forge

## Status

Die 0.6-Foundation besitzt bereits:

- eine schreibgeschützte Character-Projektion,
- eine getrennte Biografieprojektion aus validierten Journal-Ereignissen,
- deutsche Skill-/Trait-/Effekt-/Konsequenz-/Spezialisierungs-/Stufenkataloge,
- gezielte Presentation-Tests und einen eigenen Remote-CI-Gate.

Noch **nicht** Teil der kanonischen Baseline sind Application-Capabilities, Command-Dispatcher, lokaler Presentation-State, bestätigtes Progressionsfeedback, A4 Ops Deck und A3 Cinematic Forge. Diese Punkte werden gemäß `TODO.md` sequenziell umgesetzt.

## Zweck

Presentation ist die Schicht zwischen Spielkern und sichtbarer Oberfläche:

```text
Spielkern → schreibgeschützte Projection → A4 oder A3
Spielkern ← Application-Command         ← Klick oder Tastatur
```

Eine Projection bereitet Daten nur zur Anzeige auf. Ein Command ist ein klar benannter Auftrag an die Application-Schicht. Die UI verändert niemals selbst `CharacterState`, Journal oder Save-Dateien.

## Verbindliche Grenzen

1. Projection erhält geladenen `CharacterState` und Journal-Einträge, verändert beides aber nicht.
2. Jeder sichtbare Text wird über Schlüssel aus `content/<sprache>/` aufgelöst.
3. A3 und A4 dürfen Daten nur anders anordnen; Feldnamen, Commands und Komponenten bleiben gleich.
4. Profiländerungen gehen ausschließlich an `CharacterProfileService.update()`; Undo an `undo_last_profile_update()`.
5. Spielaktionen gehen ausschließlich an `CharacterActionService.execute()`.
6. Biografie entsteht nur aus validierten Journal-Ereignissen.
7. Feedback/Animation reagiert erst auf bestätigte Domain-Ereignisse und blockiert keine Bedienung.
8. Ranking und Sync werden erst angebunden, wenn bestätigte Datenquellen existieren.
9. Presentation liest keine Persistence-Interna, um Berechtigungen zu erraten; Capabilities werden von Application geliefert.
10. Für dieselbe Projektion existiert genau eine kanonische Implementierung.

## Datenvertrag der Character-Projektion

`build_character_projection(character, journal_records, text_catalog)` liefert ein neues Dictionary. Listen sind bereits in stabiler Anzeigereihenfolge; optionale Werte sind `null` oder leere Listen.

| Block | Pflichtfelder | Regel |
|---|---|---|
| `meta` | `projection_version`, `character_id` | Version `0.6`; ID bleibt technisch. |
| `overview` | `display_name`, `alias`, `additional_nicknames`, `motto`, `level`, `total_xp`, `resonance_xp`, `resonance_rank`, `energy`, `stress`, `reputation` | Kopien aus Domain-State. |
| `top_skills` | höchstens 3 × `skill_id`, `label_key`, `value`, `xp`, `trend` | Wert absteigend, danach stabile `skill_id`. |
| `skills` | 16 × `skill_id`, `label_key`, `value`, `xp`, `xp_to_next`, `progress_percent`, `trend` | `ProgressionRules`; Prozent 0–100. |
| `traits` | `trait_id`, `label_key`, `tier`, `evidence`, `next_tier`, `progress_percent`, `effect_key`, `consequence_key` | Nur bekannte Trait-Familien; gesperrte Traits verraten keine Evidenz/Prozentwerte. |
| `specialization` | `specialization_id`, `label_key`, `stage`, `stage_label_key` oder `null` | aus Domain-State, sichtbarer Name aus Content. |
| `biography` | `entry_id`, `event_id`, `category`, `title_key`, `body_key`, `placeholders`, `sequence` | nur validierte Biografie-Journalereignisse, sortiert nach Sequenz/Event-ID. |
| `capabilities` | `can_edit_profile`, `can_undo_profile`, `can_execute_action` | bis 0.6.1 sicher `false`; danach von Application geliefert. |
| `feedback` | `feedback_id`, `kind`, `title_key`, `detail_keys`, `reduced_motion` | bis 0.6.2 leer; danach nur aus bestätigten Events. |

### Textschlüssel

Skill-, Trait-, Effekt-, Konsequenz-, Spezialisierungs- und Stufenschlüssel müssen im übergebenen Katalog existieren. Fehlende Schlüssel sind ein Entwicklungsfehler und werden nicht durch sichtbare Texte im Code kaschiert.

### Biografie

Die Character-Projektion verwendet `build_biography_projection(...)` als einzige zuständige Biografieaufbereitung. Eine zweite Biografie-Implementierung innerhalb der Character-Projektion ist nicht zulässig.

## Geplante UI-Commands

| Command | Eingabe | Ziel |
|---|---|---|
| `profile.update` | `character_id`, erlaubte Profilfelder, eindeutige IDs | `CharacterProfileService.update()` |
| `profile.undo_last` | `character_id`, eindeutige IDs | `undo_last_profile_update()` |
| `action.execute` | `character_id`, `action_id`, `action_instance_id`, Auswahlen | `CharacterActionService.execute()` |
| `view.select` | `overview`, `skills_traits` oder `biography` | lokaler Presentation-State |
| `biography.filter` | Kategorie oder `all` | lokaler Presentation-State |
| `feedback.dismiss` | `feedback_id` | lokaler Presentation-State |

Schreibbefehle erhalten stabile Command-/Event-/Transaction-IDs, damit wiederholte Klicks nicht doppelt persistiert werden.

## Gemeinsame Komponenten

A3 und A4 verwenden dieselben acht Komponenten:

- `CharacterHeader`
- `StatusSummary`
- `SkillList`
- `TraitList`
- `SpecializationCard`
- `BiographyTimeline`
- `ProfileEditor`
- `ProgressFeedback`

A4 ordnet sie als geführten Hauptablauf an. A3 inszeniert dieselben Daten stärker visuell. Neue Fachlogik gehört weder in A3 noch in A4.

## Abnahme der aktuellen Foundation

```bash
PYTHONPATH=src python3 -m compileall -q src/bunkerfrequenz/presentation
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote-Gate: `.github/workflows/presentation-core.yml`

Abnahmebedingungen:

- genau eine Character-Projection-Implementierung,
- keine Mutation von Domain-/Journal-Eingaben,
- alle ausgegebenen Progressions-Textschlüssel katalogisiert,
- Progressionswerte begrenzt,
- gesperrte Traits ohne versteckte Fortschrittswerte,
- Biografie nur aus validierten Ereignissen,
- Package-Exporte eindeutig,
- Remote-Gate grün vor Merge.

## Nächste Umsetzung

Siehe `TODO.md`. Die Reihenfolge ist verbindlich:

1. Application-Capabilities + ein Command-Dispatcher,
2. lokaler Presentation-State + bestätigtes Feedback,
3. gemeinsame Komponenten + A4 Ops Deck,
4. A3 Cinematic Forge auf denselben Bausteinen,
5. Ranking/Network erst danach.
