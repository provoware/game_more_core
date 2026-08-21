# A4 Ops Deck – Komponentenvertrag 0.6.3

## Ziel

0.6.3 erzeugt noch keine konkrete Qt-, Web- oder Game-Engine-Oberfläche. Die Iteration definiert die **frameworkfreie, testbare View-Model-Schicht**, aus der später A4 Ops Deck und A3 Cinematic Forge gerendert werden.

Der Datenweg bleibt:

```text
Domain / Persistence
        ↓
Application-Grenze
        ↓
Character Projection + bestätigtes Feedback
        ↓
lokaler PresentationState
        ↓
8 gemeinsame Komponenten
        ↓
A4 Ops Deck View Model
        ↓
späterer Renderer
```

A4 erzeugt keine neue Fachlogik, keine zweite Projection und keinen zweiten Command-Dispatcher.

## Acht gemeinsame Komponenten

`src/bunkerfrequenz/presentation/components.py` besitzt genau diese öffentlichen Bausteine:

1. `CharacterHeader`
2. `StatusSummary`
3. `SkillList`
4. `TraitList`
5. `SpecializationCard`
6. `BiographyTimeline`
7. `ProfileEditor`
8. `ProgressFeedback`

Jede Komponente ist ein neues, detached Dictionary. Änderungen am View Model dürfen weder Projection noch `PresentationState` verändern.

### Zuständigkeiten

| Komponente | Eingabe | Aufgabe |
|---|---|---|
| `CharacterHeader` | `overview` | Name, Alias, Spitznamen, Motto, Level, Resonanzrang |
| `StatusSummary` | `overview` | Energie, Stress, Ruf, XP, Resonanz |
| `SkillList` | `skills` | Skillanzeige ohne neue Sortier-/Balance-Regeln |
| `TraitList` | `traits` | Traitstufen, Fortschritt, Wirkung, Konsequenz |
| `SpecializationCard` | `specialization` | aktive Spezialisierung oder sauberer Leerzustand |
| `BiographyTimeline` | `biography` + lokaler State | lokaler Kategorienfilter, keine Journalmutation |
| `ProfileEditor` | `overview` + `capabilities` | editierbare Profildaten und Command-Vertrag |
| `ProgressFeedback` | `feedback` + lokaler State | lokales Dismiss + Reduced-Motion-Darstellungsmodus |

Optional fehlende Inhalte bleiben `null` oder leer. Eine Komponente erfindet keine Spezialisierung, Biografie, Traits, Ziele oder Feedbackkarten.

## ProfileEditor

Der Editor unterstützt ausschließlich die bereits erlaubten Profilfelder:

- `display_name`
- `alias`
- `additional_nicknames`
- `motto`

Er definiert **keinen eigenen Handler**. Seine beiden Action-Verträge verweisen ausdrücklich auf:

```text
application.command_dispatcher.dispatch_command
```

Commandtypen:

- `profile.update`
- `profile.undo_last`

`can_edit_profile` und `can_undo_profile` stammen ausschließlich aus der bestätigten Projection-Capability. Die Komponente errät keine Rechte.

## ProgressFeedback

`ProgressFeedback` filtert ausgeblendete IDs **vor** der Übergabe an einen Renderer. Damit kann ein Renderer nicht versehentlich weiterhin eine lokal ausgeblendete Karte aus der unveränderten Rohprojektion darstellen.

`PresentationState.reduced_motion` verändert nur:

```text
presentation.motion_mode = animated | static
```

Die bestätigten Feedbackdaten selbst bleiben unverändert.

## A4 Ops Deck

`build_a4_ops_deck(...)` nimmt:

- die bestehende Character Projection,
- den lokalen `PresentationState`,
- `UI_MANIFEST.json`,
- den kombinierten sichtbaren Textkatalog,
- optional bestätigte/konkrete Workflowdaten.

Es liest A4-Layout, Workflow-Reihenfolge, maximales Primäraktionslimit und Accessibility-Werte aus `UI_MANIFEST.json` statt sie als zweite Konstante zu pflegen.

### Workflow

Die Reihenfolge stammt aus `focus_model.workflow`:

```text
current_goal
→ next_action
→ result
→ development
→ next_goal
```

Jeder Schritt besitzt:

- `label_key`
- `aria_label_key`
- `icon_id`
- semantischen `tone`
- Referenzen auf gemeinsame Komponenten
- optional extern gelieferten Inhalt

Farbe ist nie alleinige Information: A4 liefert immer Textschlüssel + Icon + semantischen Tone.

## Keine erfundenen Ziele

A4 darf `current_goal`, `result` und `next_goal` nicht aus Characterwerten erraten.

Wenn keine bestätigte fachliche Quelle übergeben wurde:

```text
current_goal = null
result       = null
next_goal    = null
primary_actions = []
```

Eine spätere Mission-, Training-, Event- oder Clubschicht kann diese Workflowkarten liefern, ohne den Character-Forge-Vertrag umzubauen.

## Primäraktionen

A4 zeigt maximal `focus_model.max_primary_actions_visible` Aktionen. Im aktuellen `UI_MANIFEST.json` sind das drei.

Zu viele Aktionen werden **nicht still abgeschnitten**, sondern als Vertragsfehler abgewiesen.

Eine Primäraktion enthält:

```text
action_id
label_key
aria_label_key
icon_id
tone
enabled
keyboard_order
target_px
focus_ring_px
dispatch.route
dispatch.command
```

### Direkte Dispatcher-Kompatibilität

`dispatch.command` ist kein Zwischenformat. Er ist ein vollständig validierter Command für den bestehenden `dispatch_command(...)`.

Erlaubt sind nur:

- `profile.update`
- `profile.undo_last`
- `action.execute`

A4 prüft:

- alle vom Dispatcher benötigten IDs,
- `character_id` gegen die Projection,
- erlaubte Profiländerungsfelder,
- erlaubte optionale Action-Auswahlfelder,
- keine UI-gesteuerten Zusatzparameter wie `base_xp`,
- bestätigte Capability für aktivierte Aktionen.

Damit existiert kein Übersetzer zwischen A4 und Application. Ein aus A4 entnommener Command muss unverändert durch den bestehenden Dispatcher ausführbar sein.

## View-Zuordnung

Die acht Komponenten werden genau einmal gebaut. A4 referenziert sie nur:

| lokaler View | Workspace-Komponenten |
|---|---|
| `overview` | `ProfileEditor`, `SpecializationCard` |
| `skills_traits` | `SkillList`, `TraitList`, `SpecializationCard` |
| `biography` | `BiographyTimeline` |

`CharacterHeader` bleibt im Header. `StatusSummary` und `ProgressFeedback` bilden den Live-Status.

Diese Referenzstruktur verhindert getrennte Kopien derselben Fachkomponente innerhalb des A4-Layouts.

## Accessibility

Folgende Werte kommen direkt aus `UI_MANIFEST.json`:

- Mindestschriftgröße
- bevorzugte Schriftgröße
- Mindestgröße eines Interaktionsziels
- Fokusrahmenbreite
- Tastaturnavigation
- Screenreader-Labels
- High-Contrast-Fähigkeit
- Regel `color_never_sole_information`

Die konkrete Farbpalette bleibt ebenfalls Manifest-/Renderer-Verantwortung; Python-Komponenten codieren keine sichtbaren Farben.

## Textvertrag

Alle sichtbaren A4-/Komponententexte liegen unter `content/de/ui/`.

0.6.3 ergänzt in `character_forge.json` insbesondere:

- Workflowtitel
- Komponententitel
- Profilfeldtitel
- `PROFIL SPEICHERN`
- `AKTION AUSFÜHREN`

`build_a4_ops_deck(...)` validiert rekursiv alle ausgegebenen `*_key`-Felder gegen den übergebenen Katalog. Fehlende sichtbare Texte sind ein Entwicklungsfehler und werden nicht durch technische IDs ersetzt.

## Abnahme 0.6.3

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Zusätzlich müssen auf demselben PR-Head grün sein:

- `Runtime Core`
- `Presentation Core`

Pflichtnachweise:

- exakt acht gemeinsame Komponenten,
- defensive Kopien statt Projection-Mutation,
- Biography-Dismiss/Filter wirken im tatsächlichen Komponentenpayload,
- ProfileEditor referenziert ausschließlich den bestehenden Dispatcher,
- A4 liest Accessibility/Workflow-Limit aus `UI_MANIFEST.json`,
- vierte Primäraktion wird abgewiesen,
- A4 emittiert nur dispatcher-fertige Commands,
- ein emittierter `profile.update`-Command läuft unverändert durch `dispatch_command(...)`,
- nicht freigegebene Commandfelder werden abgewiesen,
- bestätigte Capabilities sperren aktivierte Actions fail-closed,
- fehlende sichtbare Textschlüssel blockieren die A4-Projektion,
- leere optionale Bereiche erzeugen keine erfundenen Daten.

## Danach

0.6.4 baut **A3 Cinematic Forge aus exakt denselben acht Komponenten, derselben Projection, demselben lokalen State und denselben Commands**. Neue Character- oder Persistence-Fachlogik ist dafür nicht zulässig.
