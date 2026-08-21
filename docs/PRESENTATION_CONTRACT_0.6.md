# Presentation-Vertrag 0.6 – Character Forge

## Status

Die 0.6-Foundation besitzt:

- eine schreibgeschützte Character-Projektion,
- eine getrennte Biografieprojektion aus validierten Journal-Ereignissen,
- deutsche Skill-/Trait-/Effekt-/Konsequenz-/Spezialisierungs-/Stufenkataloge,
- gezielte Presentation-Tests und einen eigenen Remote-CI-Gate.

0.6.1 ergänzt darauf genau eine Application-Grenze für Capabilities und Schreibbefehle. Lokaler Presentation-State, bestätigtes Progressionsfeedback, A4 Ops Deck und A3 Cinematic Forge bleiben gemäß `TODO.md` getrennte Folgeiterationen.

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
11. Der Command-Dispatcher verändert keine Domain-Regeln und schreibt niemals direkt in Persistenzdateien.
12. Application liefert nach Schreibaktionen bestätigten Character-State; erst Presentation erzeugt daraus die Anzeigeprojektion.

## Datenvertrag der Character-Projektion

`build_character_projection(character, journal_records, text_catalog, capabilities=None)` liefert ein neues Dictionary. Listen und Capabilities sind vom Eingabeobjekt getrennte Kopien; optionale Werte sind `null` oder leere Listen.

| Block | Pflichtfelder | Regel |
|---|---|---|
| `meta` | `projection_version`, `character_id` | Version `0.6`; ID bleibt technisch. |
| `overview` | `display_name`, `alias`, `additional_nicknames`, `motto`, `level`, `total_xp`, `resonance_xp`, `resonance_rank`, `energy`, `stress`, `reputation` | Kopien aus Domain-State. |
| `top_skills` | höchstens 3 × `skill_id`, `label_key`, `value`, `xp`, `trend` | Wert absteigend, danach stabile `skill_id`. |
| `skills` | 16 × `skill_id`, `label_key`, `value`, `xp`, `xp_to_next`, `progress_percent`, `trend` | `ProgressionRules`; Prozent 0–100. |
| `traits` | `trait_id`, `label_key`, `tier`, `evidence`, `next_tier`, `progress_percent`, `effect_key`, `consequence_key` | Nur bekannte Trait-Familien; gesperrte Traits verraten keine Evidenz/Prozentwerte. |
| `specialization` | `specialization_id`, `label_key`, `stage`, `stage_label_key` oder `null` | aus Domain-State, sichtbarer Name aus Content. |
| `biography` | `entry_id`, `event_id`, `category`, `title_key`, `body_key`, `placeholders`, `sequence` | nur validierte Biografie-Journalereignisse, sortiert nach Sequenz/Event-ID. |
| `capabilities` | `can_edit_profile`, `can_undo_profile`, `can_execute_action` | ohne bestätigte Application-Werte sicher `false`; fremde Capability-Felder werden nicht projiziert. |
| `feedback` | `feedback_id`, `kind`, `title_key`, `detail_keys`, `reduced_motion` | bis 0.6.2 leer; danach nur aus bestätigten Events. |

### Textschlüssel

Skill-, Trait-, Effekt-, Konsequenz-, Spezialisierungs- und Stufenschlüssel müssen im übergebenen Katalog existieren. Fehlende Schlüssel sind ein Entwicklungsfehler und werden nicht durch sichtbare Texte im Code kaschiert.

### Biografie

Die Character-Projektion verwendet `build_biography_projection(...)` als einzige zuständige Biografieaufbereitung. Eine zweite Biografie-Implementierung innerhalb der Character-Projektion ist nicht zulässig.

## 0.6.1 – Application-Capabilities

`get_presentation_capabilities(character, persistence)` ist eine reine Leseabfrage. Sie liefert ausschließlich:

- `can_edit_profile`
- `can_undo_profile`
- `can_execute_action`

Regeln:

- ohne bestätigten passenden Character-State sind alle Werte `false`,
- eine sichere Undo-Fähigkeit besteht nur, wenn die letzte Transaktion genau eine nicht kompensierte `character.profile_updated`-Änderung ist,
- beschädigte oder unlesbare Zustände führen nicht zu optimistischen Rechten,
- Presentation erhält nur die drei öffentlichen Booleans und keine Persistence-Details.

## 0.6.1 – Schreibcommands

Ein einziger Application-Dispatcher akzeptiert nur:

| Command | UI-Eingaben | Route |
|---|---|---|
| `profile.update` | `character_id`, `command_id`, `event_id`, `transaction_id`, erlaubte Profilfelder | `CharacterProfileService.update()` |
| `profile.undo_last` | `character_id`, `command_id`, `event_id`, `transaction_id` | `undo_last_profile_update()` |
| `action.execute` | `character_id`, `command_id`, `action_id`, `action_instance_id`, optionale fachliche Auswahl | `CharacterActionService.execute()` |

Der Dispatcher:

- prüft Character-Zuordnung und notwendige IDs,
- erlaubt beim Profil nur `display_name`, `alias`, `additional_nicknames`, `motto`,
- gibt keine UI-gesteuerten Balanceparameter wie `base_xp` frei,
- übernimmt bei Profilbefehlen Event-/Transaction-IDs unverändert,
- übernimmt bei Spielaktionen `action_instance_id` unverändert; Journal-/Transaction-IDs bleiben wie bisher deterministisch aus dieser ID abgeleitet,
- ersetzt im vertrauenswürdigen `JournalContext` ausschließlich `command_id` durch die bestätigte UI-Command-ID,
- liefert einen bestätigten `CharacterState`, Commit-Event-IDs und den Idempotenzstatus zurück,
- erzeugt noch kein UI-Feedback; das folgt separat in 0.6.2.

Wiederholte identische Profilupdates und Spielaktionen werden über die vorhandene Persistenz-/Action-Idempotenz nicht doppelt geschrieben. Ein wiederholtes identisches Undo wird anhand seines bereits bestätigten Kompensationsereignisses ebenfalls als idempotenter Replay behandelt.

## Geplante lokale UI-Commands ab 0.6.2

| Command | Eingabe | Ziel |
|---|---|---|
| `view.select` | `overview`, `skills_traits` oder `biography` | lokaler Presentation-State |
| `biography.filter` | Kategorie oder `all` | lokaler Presentation-State |
| `feedback.dismiss` | `feedback_id` | lokaler Presentation-State |

Diese lokalen Commands dürfen weder Domain-State noch Journal verändern.

## Gemeinsame Komponenten

A3 und A4 verwenden später dieselben acht Komponenten:

- `CharacterHeader`
- `StatusSummary`
- `SkillList`
- `TraitList`
- `SpecializationCard`
- `BiographyTimeline`
- `ProfileEditor`
- `ProgressFeedback`

A4 ordnet sie als geführten Hauptablauf an. A3 inszeniert dieselben Daten stärker visuell. Neue Fachlogik gehört weder in A3 noch in A4.

## Abnahme 0.6.1

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote-Gates:

- `.github/workflows/runtime-core.yml`
- `.github/workflows/presentation-core.yml`

Abnahmebedingungen:

- genau eine Character-Projection-Implementierung,
- keine Mutation von Domain-/Journal-/Capability-Eingaben,
- Capabilities kommen ausschließlich aus der Application-Leseabfrage,
- alle drei Schreibcommand-Typen laufen über einen Dispatcher,
- keine zweite Persistenz- oder Fachlogik im Dispatcher,
- wiederholte bestätigte UI-Aktionen erzeugen keine Doppelbuchung,
- alle ausgegebenen Progressions-Textschlüssel bleiben katalogisiert,
- beide Remote-Gates grün vor Merge.

## Nächste Umsetzung

Nach abgenommenem 0.6.1 folgt gemäß `TODO.md`:

1. lokaler Presentation-State + bestätigtes Feedback,
2. gemeinsame Komponenten + A4 Ops Deck,
3. A3 Cinematic Forge auf denselben Bausteinen,
4. Ranking/Network erst danach.
