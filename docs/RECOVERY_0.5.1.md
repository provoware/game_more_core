# Recovery & Fault Injection 0.5.1

## Zweck

0.5.1 setzt den Persistence Contract aus 0.4.2 als echten Laufzeitpfad um. Ziel ist nicht, Fehler zu verstecken, sondern einen bestätigten Zustand reproduzierbar wiederherzustellen und beschädigte Daten nachvollziehbar zu isolieren.

## Checkpoint-Modell

Der aktuelle State wird in einem Envelope gespeichert:

- `state_envelope_version`
- `applied_sequence`
- `journal_head_hash`
- `data`
- `data_hash`

Damit kann beim Start geprüft werden, ob State, Journal und `save_meta.json` denselben bestätigten Stand beschreiben.

## Snapshots

Snapshots werden als vollständiger, gehashter Zustand mit Journal-Sequenz und Journal-Head abgelegt. `snapshots/index.json` wird aus vorhandenen gültigen Snapshots neu aufgebaut und ist deshalb kein alleiniger Wahrheitsanker.

Pflichtschwellen:

- spätestens nach 50 bestätigten Journal-Ereignissen
- spätestens nach 300 Sekunden seit dem letzten Snapshot

## Recovery-Reihenfolge

1. Journal bis zum letzten gültigen Record prüfen.
2. gültigen State-Checkpoint und gültige Snapshots ermitteln.
3. neuesten sicheren Checkpoint wählen.
4. beschädigten Journal-Tail vor Reparatur nach `recovery/quarantine/` sichern.
5. nachfolgende Journal-Ereignisse deterministisch und idempotent erneut anwenden.
6. State und Meta atomar auf den gültigen Head schreiben.
7. optional `system.recovery_performed` journalisieren.
8. Post-Recovery-Snapshot erzeugen.
9. `recovery/RECOVERY_RECEIPT.json` schreiben.

## Fault Injection

Testbare Crashpunkte:

- `after_journal_durable`
- `after_state_applied`
- `after_meta_committed`

Damit werden genau die Transaktionsgrenzen geprüft, an denen ein realer Prozessabbruch widersprüchliche Dateien hinterlassen könnte.

## Replay-Regel Character Forge

Skill-XP und Trait-Evidenz sind die kausalen Progressionsereignisse. Daraus abgeleitete Level-/Trait-Up-Ereignisse werden beim Replay nicht ein zweites Mal angewendet. Dadurch bleibt Recovery idempotent.

## Undo

Der erste Runtime-Undo ist bewusst eng begrenzt auf die editierbaren Profilfelder:

- Anzeigename
- Alias
- Motto

Undo löscht kein Journal-Ereignis. Es schreibt ein neues `character.profile_updated` mit `compensation_for` auf das ursprüngliche Ereignis. Ein zweites Undo auf denselben letzten Kompensationsschritt wird abgewiesen.

## Kompatibilität

Der rohe State aus `0.5.0-alpha.1` bleibt lesbar und wird zusammen mit vorhandenen Meta-Daten als Legacy-Checkpoint interpretiert. Es gibt keine stille destruktive Migration.

## Abnahme

```bash
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m unittest discover -s tests/runtime -v
```

Lokaler Referenzstand vor Übertragung: **21/21 Tests PASS**.
