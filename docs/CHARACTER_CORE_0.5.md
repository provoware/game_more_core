# Character Core 0.5

## Zweck
0.5 ist der erste echte, headless Laufzeitkern. Er implementiert nur die bereits in 0.4 definierten Character-, Progression-, Action- und Persistence-Verträge. UI, Telegram, Wirtschaft und Weltlogik bleiben getrennt.

## Kernfluss
`CharacterState → ActionResolver → Domain-Events → CharacterActionService → PersistenceKernel → Reload`

## CharacterState
- 16 identische Startskills mit Wert 10
- editierbarer Anzeigename, Alias und Motto getrennt von `character_id`
- Skill-XP, Trait-Evidenz, Trait-Stufen und Spezialisierung als getrennte Zustände
- Validierung vor Serialisierung und nach Reload

## Progression
- Skill-XP-Kurve und Gesamtlevel aus 0.4.1
- fünf Trait-Stufen mit Evidenz-, Level-, Ereignis- und Quellenbedingungen
- Training, Praxis, Krise, Team und Entdeckung erhalten unterschiedliche Evidenzfaktoren
- sechs Spezialisierungen; keine Spezialisierung wird beim Start erzwungen
- Fokus-/Außen-XP-Folgen werden ab bestehender Spezialisierung auf Folgeaktionen angewandt
- 15 Trait-Effektfamilien verändern Ergebnis, Qualität oder passende Skill-XP innerhalb fester Caps
- Level 50 geht in journalisierte, offene Resonanzränge über

## ActionResolver
- deterministische Zufallsquelle aus `world_seed + action_instance_id + server_sequence`
- Systemzeit ist niemals Zufallsseed
- Skillgewichtung beeinflusst Ergebnisqualität
- Risikoprofil wirkt als begrenzter Malus
- aktive, für die Aktion relevante Traits wirken mit Soft-Konflikten deterministisch auf die Auflösung
- Aktionen mutieren nie den übergebenen CharacterState, sondern erzeugen einen neuen Zustand und katalogisierte Domain-Events

## PersistenceKernel
- Journal Schema v2
- globale monotone Sequenz
- SHA-256-Hashkette
- `fsync` vor abgeleitetem State-Write
- State-/Meta-Dateien atomar via Tempdatei + `os.replace`
- idempotente Event-IDs; gleiche Wiederholung wird ignoriert, abweichender Payload wird abgelehnt
- unbekannte Journaltypen können über den Katalog strikt abgewiesen werden
- 60-Sekunden-Autosave-Regel als monotone Zeitentscheidung

## Bewusst nachgelagert
- Presentation-/UI-State und grafische Character-Forge-Runtime
- Economy, Sync und Weltlogik
- sekundäre Spezialisierung und zeitbasierte Wechselträgheit

## Validierung
```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Lokaler Referenzstand 0.5.2: 27/27 Runtime-/Recovery-Tests bestanden; Trait-Regeln stimmen mit dem Manifest überein.
