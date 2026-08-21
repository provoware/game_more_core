# Datenmodell 0.4

## CharacterDefinition

Statische narrative Definition:
- `character_definition_id`
- `schema_version`
- `default_name`
- `default_alias`
- `story_profile_id`
- `available_avatar_set`
- `dialog_profile_id`
- `personal_story_set`

## CharacterInstance

Spielerbezogene Identität:
- `character_id`
- `definition_id`
- `player_id`
- `display_name`
- `alias`
- `additional_nicknames[]`
- `motto`
- `avatar_id`
- `symbol_id`
- `created_at`
- `last_modified_at`

## CharacterProgress

Entwicklungszustand:
- `level`
- `total_xp`
- `skill_values{}`
- `skill_xp{}`
- `training_xp{}`
- `practice_xp{}`
- `crisis_xp{}`
- `traits[]`
- `specializations[]`
- `reputation`
- `energy`
- `stress`
- `development_axes{}`

## Trennung

`CharacterDefinition` wird nicht durch Umbenennen verändert. `CharacterInstance` enthält keine Skilllogik. `CharacterProgress` enthält keine sichtbaren Texte.

## Zeit

Vier getrennte Zeitquellen:
- lokale Systemzeit
- bestätigte Onlinezeit
- monotone Laufzeit
- Spielweltzeit

## Persistenz

Journal-Ereignisse enthalten stabile Entity-IDs. Snapshots bilden einen Zustand ab, sind aber nicht die Historie.
