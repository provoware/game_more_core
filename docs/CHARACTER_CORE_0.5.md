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

## ActionResolver
- deterministische Zufallsquelle aus `world_seed + action_instance_id + server_sequence`
- Systemzeit ist niemals Zufallsseed
- Skillgewichtung beeinflusst Ergebnisqualität
- Risikoprofil wirkt als begrenzter Malus
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

## Noch bewusst offen
- automatisches Quarantäne-/Recovery-Verfahren nach erkanntem korruptem Tail
- Fault-Injection zwischen einzelnen Transaktionsphasen
- Snapshot-Writer/Replay aus Snapshot + Journal
- Resonanzfortschritt nach Level 50
- vollständige Trait-Effektanwendung auf alle Gameplay-Metriken

Diese Punkte bilden 0.5.1; sie werden nicht vorzeitig in den Kern gemischt.

## Validierung
```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Lokaler Referenzstand: 14/14 Tests bestanden sowie 200 aufeinanderfolgende Action/Commit/Reload-Schritte ohne Journalfehler.
