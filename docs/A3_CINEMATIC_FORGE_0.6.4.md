# A3 Cinematic Forge – Presentation-Vertrag 0.6.4

## Ziel

A3 Cinematic Forge ist die visuell stärkere Character-Forge-Anordnung. Es führt **keine neue Fachlogik** ein.

A3 und A4 teilen:

- dieselbe `CharacterState`-Quelle,
- dieselbe Character Projection,
- denselben lokalen `PresentationState`,
- exakt dieselben acht Komponenten,
- dieselben bestätigten Capabilities,
- denselben Action-Normalisierer,
- denselben Application-Dispatcher,
- dieselben Textkataloge.

A3 ergänzt ausschließlich räumliche Anordnung, Visualisierungsmetadaten und nicht blockierende Animation-Cues.

## Datenfluss

```text
Character Projection
       │
       ├─ overview
       ├─ skills
       ├─ traits
       ├─ specialization
       ├─ biography
       ├─ capabilities
       └─ feedback
              │
              ▼
       8 gemeinsame Komponenten
              │
       ┌──────┴────────┐
       ▼               ▼
   A4 Ops Deck      A3 Cinematic Forge
                        │
                        ├─ Charakterbühne
                        ├─ Skillnetz
                        ├─ Trait-Orbit
                        ├─ Kontext-Drawer
                        ├─ Biografie-Schiene
                        ├─ Progress-Overlay
                        └─ Action-Dock
```

## Zonen

### `character_stage`

Verwendet ausschließlich:

- `CharacterHeader`
- `StatusSummary`

A3 reserviert einen Portraitbereich, aber `portrait_source` bleibt `null`, solange keine bestätigte Avatar-/Portraitquelle im Datenmodell existiert. Es werden keine Bilder, IDs oder Avatare erfunden.

### `skill_web`

Quelle: `SkillList`.

A3 ordnet die bereits projizierten Skills deterministisch radial an. Jeder Knoten übernimmt nur vorhandene Werte:

- `skill_id`
- `label_key`
- `value`
- `xp`
- `xp_to_next`
- `progress_percent`
- `trend`

Der Winkel ist reine Layoutinformation und verändert keine Progressionsregel.

### `trait_orbit`

Quelle: `TraitList`.

Traits werden als Orbit um den Spezialisierungsbereich angeordnet. Verdeckte oder nicht vorhandene fachliche Werte werden nicht ergänzt.

### `specialization_focus`

Quelle: `SpecializationCard`.

Keine aktive Spezialisierung ergibt einen echten Leerzustand.

### `context_drawer`

Der lokale `PresentationState.selected_view` entscheidet nur, welche bereits vorhandenen Komponenten sichtbar referenziert werden:

| View | Komponenten |
|---|---|
| `overview` | `ProfileEditor`, `SpecializationCard` |
| `skills_traits` | `SkillList`, `TraitList`, `SpecializationCard` |
| `biography` | `BiographyTimeline` |

### `biography_rail`

Quelle: `BiographyTimeline` inklusive lokalem, bereits angewendetem Biografie-Filter.

### `progress_overlay`

Quelle: `ProgressFeedback` plus `build_animation_cues(...)`.

Ausgeblendetes Feedback wird vor der Animationserzeugung entfernt. Eine lokal geschlossene Karte kann daher nicht versehentlich weiter animiert werden.

### `action_dock`

A3 besitzt **keinen eigenen Commandvertrag**. A3 und A4 verwenden beide `normalize_primary_actions(...)`.

Erlaubte Schreibcommands bleiben:

- `profile.update`
- `profile.undo_last`
- `action.execute`

Alle Action-Payloads sind direkt für `application.command_dispatcher.dispatch_command` bestimmt.

## Gemeinsamer Action-Normalisierer

`src/bunkerfrequenz/presentation/interaction_actions.py` ist die einzige Presentation-Zielstelle für:

- erlaubte Commandfelder,
- Pflicht-IDs,
- erlaubte Profilfelder,
- bestätigte Capability-Prüfung,
- Mindest-Zielgröße,
- Fokusrahmen,
- Action-Reihenfolge,
- eindeutige `action_id`.

A3 und A4 dürfen diese Regeln nicht separat nachbauen.

## Animation-Cues

`build_animation_cues(...)` übersetzt ausschließlich bereits bestätigtes und aktuell sichtbares Progressionsfeedback.
# A3 Cinematic Forge – Vertrag 0.6.4

## Ziel

A3 Cinematic Forge ist die visuell stärkere Character-Forge-Komposition. Sie führt **keine neue Fachlogik** ein. A3 verwendet dieselbe Character Projection, denselben lokalen `PresentationState`, dieselben acht Komponenten, dieselben Capabilities und dieselben dispatcher-fertigen Commands wie A4 Ops Deck.

## Grundregel

```text
Character Projection
        ↓
PresentationState
        ↓
8 gemeinsame Komponenten
        ↓
A4 Interaktionsvertrag
        ↓
A3 Cinematic Forge – nur andere Komposition + Animationsmetadaten
```

A3 ruft deshalb `build_a4_ops_deck(...)` als bereits validierten Interaktionsvertrag auf und übernimmt daraus:

- `components`
- Primäraktionen
- Dispatcher-Route
- Command-Payloads
- Primäraktionslimit
- Accessibility-Werte
- ausgewählte View-Komponenten

A3 verändert diese Payloads nicht fachlich.

## Zonen

| Zone | Zweck | Komponenten |
|---|---|---|
| `hero_stage` | große Charakterinszenierung | `CharacterHeader`, `SpecializationCard` |
| `vital_ribbon` | kompakter Live-Status | `StatusSummary` |
| `growth_web` | radiales Entwicklungsnetz | `SkillList`, `TraitList` |
| `context_drawer` | aktuell gewählte Detailansicht | A4-identische View-Referenzen |
| `profile_drawer` | Profilbearbeitung | `ProfileEditor` |
| `story_drawer` | dynamische Biografie | `BiographyTimeline` |
| `action_dock` | Primäraktionen | A4-identische dispatcher-fertige Actions |
| `development_overlay` | Level-/Skill-/Trait-/Resonanz-Inszenierung | `ProgressFeedback` + Cinematic Cues |

## Entwicklungsanimationen

Die Animation ist eine reine Presentation-Reaktion auf bereits bestätigtes Feedback.

| Feedback | Animation |
|---|---|
| `level_up` | `anim.level_up` |
| `skill_level_up` | `anim.skill_up` |
| `trait_unlocked` | `anim.trait_unlock` |
| `trait_tier_up` | `anim.trait_unlock` |
| `specialization_changed` | `anim.specialization` |
| `resonance_rank_up` | `anim.resonance_up` |

### Sicherheits-/UX-Invarianten

Jede verwendete Animation muss:

- `max_blocking_ms = 0` besitzen,
- überspringbar sein,
- einen statischen Fallback besitzen.

Fehlt eine Animation trotz gültigem Feedback, gilt die Manifestregel:

```text
missing_animation_never_blocks_or_changes_game_state
```

A3 erzeugt dann nur einen statischen Feedback-Cue.

## Reduced Motion

Bei `PresentationState.reduced_motion = true`:

- keine Kamerabewegung,
- Animationsdauer im Cue = `0`,
- statischer Fallback,
- identischer fachlicher Feedbackinhalt,
- identische Reihenfolge,
- identische Commands,
- kein Einfluss auf Savegame, Journal oder Character State.

## Resonanz

0.6.4 ergänzt `anim.resonance_up` im `ANIMATION_MANIFEST.json`:

- Motiv: `frequency_ring_lock`
- nicht blockierend,
- überspringbar,
- Fallback: `static_resonance_card`

Damit besitzt auch die Open-End-Entwicklung nach Level 50 eine eigene visuelle Inszenierungsanweisung.

## Accessibility

A3 liest wie A4 aus `UI_MANIFEST.json`:

- Mindest-/bevorzugte Schriftgröße,
- 44-px-Interaktionsziele,
- 3-px-Fokusrahmen,
- Tastaturnavigation,
- Screenreader-Labels,
- High Contrast,
- `color_never_sole_information`.

A3 verwendet für semantische Zustände immer Text + Icon + Tone. Farbe allein ist kein Zustandsträger.

## Nicht-Ziele 0.6.4

- kein konkretes Qt-/Web-/Godot-Rendering,
- keine 3D-Modelle,
- keine erfundenen Avatare,
- kein Ranking,
- kein Network/Telegram,
- keine neue Character-Fachlogik,
- keine neue Persistence,
- keine Änderung der XP-/Trait-/Resonanzmathematik.
| `trait_tier_up` | `anim.trait_tier_up` |
| `specialization_changed` | `anim.specialization` |
| `resonance_rank_up` | `anim.resonance_up` |

0.6.4 ergänzt die bisher fehlenden Manifest-Einträge `anim.trait_tier_up` und `anim.resonance_up`.

### Sicherheitsregel

Eine Animation darf nur als `animated` ausgegeben werden, wenn der Manifest-Eintrag:

- eine gültige nichtnegative Dauer besitzt,
- `max_blocking_ms == 0` setzt,
- `skippable == true` setzt.

Ist eine Animation unbekannt, fehlt sie oder ist sie blockierend konfiguriert, verwendet A3 automatisch die statische Fallback-Karte. Gameplay und Eingabe werden nie blockiert.

## Reduced Motion

Bei `PresentationState.reduced_motion == true` gilt unabhängig vom Animationsmanifest:

```text
mode = static
animation_id = null
duration_ms = 0
input_blocked = false
```

Feedback-ID, Art, Textschlüssel, Details und Reihenfolge bleiben erhalten.

## Dismiss

A3 erzeugt Cinematic Cues ausschließlich aus `ProgressFeedback.data`. Dadurch gilt eine lokal ausgeblendete Feedback-ID gleichzeitig für:

- normale Feedbackkomponente,
- A3 Development Overlay.

Es existiert keine zweite Dismiss-Liste.

## Textauslagerung

A3 ergänzt ausschließlich Textschlüssel in `content/de/ui/character_forge.json`:

- `ui.cinematic.hero_stage`
- `ui.cinematic.vital_ribbon`
- `ui.cinematic.growth_web`
- `ui.cinematic.context_drawer`
- `ui.cinematic.profile_drawer`
- `ui.cinematic.story_drawer`
- `ui.cinematic.action_dock`
- `ui.cinematic.development_overlay`

Fehlende A3-Textschlüssel sind Entwicklungsfehler und erzeugen `KeyError`; technische IDs werden nicht als sichtbarer Ersatztext verwendet.

## A3 ↔ A4 Invarianten

Die Vertragstests verlangen:

1. exakt dieselben acht Komponenten und identische Komponentenpayloads,
2. identische Primäraktionen und Command-Payloads,
3. identische Dispatcher-Route,
4. identische Basis-Accessibility-Werte,
5. identisches Primäraktionslimit und dieselbe Action-Validierung,
6. Unterschiede ausschließlich in Layout-/Zone-/Animationsmetadaten.

## Nicht-Ziele

0.6.4 implementiert nicht:

- konkretes Qt-/Web-/Godot-Rendering,
- neue Character-/Progressionsregeln,
- neue Persistence-Wege,
- Ranking,
- Network/Telegram,
- Economy oder Clubbetrieb.

## Abnahme

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote müssen auf demselben finalen Head grün sein:
Remote auf demselben PR-Head:

- `Runtime Core`
- `Presentation Core`

Zusätzliche Vertragsnachweise:

- A3 und A4 besitzen exakt dieselben Komponentenpayloads,
- A3 und A4 normalisieren dieselben Actions byte-logisch gleich,
- vierte Primäraktion wird abgewiesen,
- doppelte Action-ID wird abgewiesen,
- Dismiss entfernt Karte **und** Animation-Cue,
- Reduced Motion ändert nur Inszenierung,
- alle Animationen sind nicht blockierend,
- fehlende Animation fällt statisch zurück,
- A3 erfindet keine Portraitquelle,
- fehlende sichtbare Textschlüssel blockieren die View-Model-Erzeugung.

## Nächster fachlicher Schritt

Nach erfolgreichem 0.6.4-Abschluss folgt `0.6.5 – Ranking / Network vorbereiten`. Erst danach sollte der 0.7-Vertical-Slice die tatsächliche Render-/Interaktionsruntime festlegen.
Erst bei beiden grünen Gates wird 0.6.4 als abgeschlossen markiert.
