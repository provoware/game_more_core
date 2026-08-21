# Presentation-Vertrag 0.6 – Character Forge

## Status

Die gemeinsame 0.6-Foundation besitzt jetzt:

- eine schreibgeschützte Character-Projektion,
- eine getrennte Biografieprojektion aus validierten Journal-Ereignissen,
- deutsche Skill-/Trait-/Effekt-/Konsequenz-/Spezialisierungs-/Stufenkataloge,
- bestätigte Application-Capabilities und einen zentralen Schreibcommand-Dispatcher aus 0.6.1,
- einen unveränderlichen, rein lokalen Presentation-State,
- bestätigtes deterministisches Progressionsfeedback,
- gezielte Runtime-/Presentation-Tests und getrennte Remote-CI-Gates.

A4 Ops Deck und A3 Cinematic Forge bleiben gemäß `TODO.md` getrennte Folgeiterationen. 0.6.2 führt ausdrücklich noch kein grafisches UI-Framework ein.

## Zweck

Presentation ist die Schicht zwischen Spielkern und sichtbarer Oberfläche:

```text
Spielkern → Application-Leseabfragen → schreibgeschützte Projection → A4 oder A3
Spielkern ← Application-Command                                ← Klick oder Tastatur
                         │
                         └─ bestätigte Event-IDs → Feedback-Projektion

Lokale Ansicht/Filter/Feedback-Ausblendung bleiben ausschließlich im Presentation-State.
```

Eine Projection bereitet Daten nur zur Anzeige auf. Ein Command ist ein klar benannter Auftrag an die Application-Schicht. Die UI verändert niemals selbst `CharacterState`, Journal oder Save-Dateien.

## Verbindliche Grenzen

1. Projection erhält geladenen `CharacterState` und Journal-Einträge, verändert beides aber nicht.
2. Jeder sichtbare Text wird über Schlüssel aus `content/<sprache>/` aufgelöst.
3. A3 und A4 dürfen Daten nur anders anordnen; Feldnamen, Commands und Komponenten bleiben gleich.
4. Profiländerungen gehen ausschließlich an `CharacterProfileService.update()`; Undo an `undo_last_profile_update()`.
5. Spielaktionen gehen ausschließlich an `CharacterActionService.execute()`.
6. Biografie entsteht nur aus validierten Journal-Ereignissen.
7. Feedback reagiert nur auf bestätigte, katalogisierte Domain-/Journal-Ereignisse und blockiert keine Bedienung.
8. Ranking und Sync werden erst angebunden, wenn bestätigte Datenquellen existieren.
9. Presentation liest keine Persistence-Interna; Capabilities und bestätigte Eventrecords werden über Application-Leseabfragen geliefert.
10. Für dieselbe Projektion existiert genau eine kanonische Implementierung.
11. Der Command-Dispatcher verändert keine Domain-Regeln und schreibt niemals direkt in Persistenzdateien.
12. Application liefert nach Schreibaktionen bestätigten Character-State; erst Presentation erzeugt daraus die Anzeigeprojektion.
13. `view.select`, `biography.filter` und `feedback.dismiss` sind lokale Presentation-Transitionen und erzeugen weder Save- noch Journal-Einträge.
14. Reduced Motion verändert nur die Darstellungsform, niemals Inhalt, Reihenfolge oder Gameplay-Zustand.

## Datenvertrag der Character-Projektion

`build_character_projection(character, journal_records, text_catalog, capabilities=None, feedback=None)` liefert ein neues Dictionary. Listen, Capabilities und Feedback sind vom Eingabeobjekt getrennte Kopien; optionale Werte sind `null` oder leere Listen.

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
| `feedback` | `feedback_id`, `source_event_id`, `kind`, `title_key`, `subject_label_key`, `detail_keys`, `reduced_motion` | ausschließlich bereits bestätigtes Presentation-Feedback; detached kopiert. |

Alle von Projection oder Feedback ausgegebenen Textschlüssel müssen im übergebenen Textkatalog existieren. Fehlende Schlüssel sind ein Entwicklungsfehler und werden nicht durch sichtbare Texte im Code kaschiert.

## Biografie

Die Character-Projektion verwendet `build_biography_projection(...)` als einzige zuständige Biografieaufbereitung. Eine zweite Biografie-Implementierung innerhalb der Character-Projektion ist nicht zulässig.

Die erlaubten Biografie-Kategorien stammen aus `manifests/BIOGRAFIE_MANIFEST.json`. Der lokale Filter erhält diesen Katalog als Eingabe; `state.py` führt bewusst keine zweite handgepflegte Kategorienliste.

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

Der Dispatcher prüft Zuordnung/IDs, erlaubt nur die katalogisierten Profilfelder, gibt keine UI-gesteuerten Balanceparameter frei und liefert bestätigten `CharacterState`, Commit-Event-IDs sowie Idempotenzstatus zurück. UI-Feedback wird nicht im Dispatcher erzeugt.

## 0.6.2 – Lokaler Presentation-State

`PresentationState` ist eine unveränderliche (`frozen`) lokale Datenstruktur mit:

- `selected_view`: `overview`, `skills_traits` oder `biography`,
- `biography_filter`: `all` oder eine aus dem Biografie-Manifest übergebene Kategorie,
- `dismissed_feedback_ids`: lokale Menge ausgeblendeter Feedbackkarten,
- `reduced_motion`: rein darstellungsbezogene Option.

Lokale Transitionen:

| Funktion | Command-Bedeutung | Persistenzwirkung |
|---|---|---|
| `select_view(...)` | `view.select` | keine |
| `filter_biography(...)` | `biography.filter` | keine |
| `dismiss_feedback(...)` | `feedback.dismiss` | keine |
| `visible_feedback(...)` | lokale Anzeigeabfrage | keine |

Ungültige lokale IDs erzeugen `PresentationStateError` mit maschinenlesbarem `code`, `field` und `value`.

## 0.6.2 – Bestätigte Eventabfrage

Presentation liest das Journal nicht direkt. `get_confirmed_events(event_ids, persistence)` in der Application-Schicht liefert detached Kopien genau der bereits bestätigten Event-IDs in der angeforderten Reihenfolge.

Regeln:

- leere Bestätigung → leeres Ergebnis,
- leere oder doppelte angeforderte IDs → Validierungsfehler,
- eine als bestätigt bezeichnete, aber im Journal fehlende ID → `PersistenceError`,
- zurückgegebene Records sind Kopien und können das Journal nicht verändern.

## 0.6.2 – Progressionsfeedback

`build_confirmed_feedback(...)` verarbeitet nur Ereignisse, die **beide** Bedingungen erfüllen:

1. ihre `event_id` steht in den bestätigten IDs,
2. ihr `event_type` steht im übergebenen Katalog aus `JOURNAL_MANIFEST.json`.

Unterstützte Feedbacktypen:

| Journal-Ereignis | Feedback-Art |
|---|---|
| `character.level_up` | `level_up` |
| `character.skill_level_up` | `skill_level_up` |
| `character.trait_unlocked` | `trait_unlocked` |
| `character.trait_tier_up` | `trait_tier_up` |
| `character.specialization_changed` | `specialization_changed` |
| `character.resonance_rank_up` | `resonance_rank_up` |

Unbekannte, nicht bestätigte oder unvollständige Ereignisse erzeugen keine Karte. Sie lösen insbesondere kein frei erfundenes Feedback aus.

### Feedback-ID

```text
feedback_id = "feedback:" + SHA256(event_id)
```

Damit ist dieselbe bestätigte Domain-Aktion auf Wiederholung eindeutig erkennbar und lokal ausblendbar.

### Texte

Sichtbare Feedbacktexte liegen ausschließlich in `content/de/ui/feedback.json`. Die Projektion transportiert nur Textschlüssel und Platzhalter.

Skill-, Trait- und Spezialisierungsfeedback kann zusätzlich einen `subject_label_key` auf die bereits vorhandenen katalogisierten Namen verweisen.

### Reduced Motion

`reduced_motion=true` ändert ausschließlich das Darstellungsflag der Feedbackkarte. `feedback_id`, Textschlüssel, Platzhalter, Reihenfolge und fachliche Bedeutung bleiben identisch. Eine spätere Oberfläche zeigt dann eine statische Karte statt bewegter Level-/Skill-Up-Inszenierung.

## Bestätigter Datenfluss 0.6.2

```text
UI-Command
   ↓
Command-Dispatcher
   ↓
bestehender Application-Service
   ↓
Persistence Commit
   ↓
CommandResult.committed_event_ids
   ↓
get_confirmed_events(...)
   ↓
build_confirmed_feedback(...)
   ↓
build_character_projection(..., feedback=...)
```

Bei idempotenter Wiederholung einer bereits bestätigten Action liefert der Dispatcher keine neuen `committed_event_ids`; dadurch entsteht kein zweites Feedback für denselben Commit.

## Gemeinsame Komponenten ab 0.6.3

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

## Abnahme 0.6.2

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
PYTHONPATH=src python3 -m unittest discover -s tests/presentation -v
```

Remote-Gates:

- `.github/workflows/runtime-core.yml`
- `.github/workflows/presentation-core.yml`

Abnahmebedingungen:

- lokaler Presentation-State ist immutable und nicht persistent,
- Biografie-Filter nutzt den kanonischen Kategorienkatalog statt einer zweiten Liste,
- bestätigte Eventrecords kommen über die Application-Grenze,
- Feedback entsteht nur aus bestätigten und journal-katalogisierten Ereignissen,
- Feedback-IDs sind deterministisch aus Event-IDs abgeleitet,
- alle sichtbaren Feedbacktexte sind ausgelagert,
- Reduced Motion verändert keine fachlichen Daten,
- Character-Projektion kopiert Feedback defensiv und validiert dessen Textschlüssel,
- kompletter Command→Commit→Eventquery→Feedback→Projection-Pfad ist getestet,
- idempotenter Replay erzeugt keine neuen Commit-IDs und damit kein doppeltes Feedback,
- Runtime Core und Presentation Core sind auf demselben PR-Head grün.

## Nächste Umsetzung

Nach abgenommenem 0.6.2 folgt gemäß `TODO.md`:

1. gemeinsame Komponenten + A4 Ops Deck,
2. A3 Cinematic Forge auf exakt denselben Bausteinen,
3. Ranking/Network anschließend.
