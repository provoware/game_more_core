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

Remote auf demselben PR-Head:

- `Runtime Core`
- `Presentation Core`

Erst bei beiden grünen Gates wird 0.6.4 als abgeschlossen markiert.
