# Persistence Contract 0.4.2

## Ziel
0.4.2 definiert Speichern, Journal, Undo, Snapshots, Migration und Recovery **vor** der Runtime-Implementierung. Der Vertrag schützt Character Forge, Wirtschaft und spätere Synchronisation vor halben Schreibvorgängen und stillen Datenverlusten.

## Kanonischer Zustand
Der rekonstruierbare Spielzustand besteht aus **letztem gültigen Snapshot + danach bestätigten Append-only-Journalereignissen**. UI-Dateien, Caches und Rankings sind keine Wahrheitsquelle.

## Transaktionszustände
`RECEIVED → VALIDATED → PREPARED → JOURNAL_DURABLE → STATE_APPLIED → COMMITTED`

Fehler führen zu `ABORTED` oder `RECOVERY_REQUIRED`. Ein Ereignis gilt erst als bestätigt, wenn sein Journaldatensatz dauerhaft geschrieben und die Zustandsanwendung anhand `event_id` idempotent bestätigt ist.

## Autosave
- Intervall: exakt 60 Sekunden.
- Nur bei geändertem Zustand; Leerlauf erzeugt keine sinnlosen Schreibvorgänge.
- Zusätzlich Flush bei Fokusverlust, sauberem Beenden und kritischen Ereignissen.
- Ein fehlgeschlagener Autosave überschreibt niemals den letzten gültigen Stand.

## Journal
39 definierte Ereignistypen decken Character Forge, Training, Missionen, Inventar, Wirtschaft, Clubs, Welt, Events, Sync und Systemereignisse ab.
Jedes Ereignis besitzt `event_id`, `sequence`, `transaction_id`, Zeit-/Identitätsdaten, Payload und Hash-Kettenbezug.

## Undo
Genau ein sicherer Nutzer-Undo-Schritt ist garantiert, wenn das letzte Kommando laut Manifest reversibel ist. Undo löscht nichts, sondern erzeugt ein Kompensationsereignis. Serverbestätigte gemeinsame Transaktionen werden nicht lokal zurückgedreht; dafür ist später eine fachliche Gegenaktion nötig.

## Snapshots
Snapshot spätestens nach 5 Minuten oder 50 bestätigten Ereignissen. Zusätzlich vor Migration, kritischem Sync, Schemawechsel und größeren Wirtschaftstransaktionen (ab 1000 Spielwährung oder 25 % des verfügbaren Guthabens).

## Crash-/Korruptionsmatrix

- **before_validation** → discard request; Modus: `none`.
- **during_temp_write** → delete temp, keep previous durable state; Modus: `none`.
- **after_temp_fsync_before_atomic_replace** → discard or retry verified temp; Modus: `none`.
- **after_journal_durable_before_state_apply** → replay event by event_id; Modus: `automatic`.
- **during_state_apply** → replay idempotently from last snapshot/journal head; Modus: `automatic`.
- **after_state_apply_before_commit_marker** → reconcile event_id; commit if payload/hash matches; Modus: `automatic`.
- **after_commit_marker** → state is committed; Modus: `none`.
- **broken_latest_snapshot** → fall back to previous valid snapshot and replay journal; Modus: `automatic`.
- **journal_tail_checksum_failure** → quarantine invalid tail; restore through last valid event; Modus: `automatic_with_notice`.
- **hash_chain_break_before_snapshot_head** → stop automatic repair; preserve evidence and require recovery mode; Modus: `safe_mode`.
- **migration_interrupted** → discard migrated copy; retain source; restart migration; Modus: `automatic`.
- **clock_jump_detected** → freeze unsafe passive catch-up; use last safe anchor; Modus: `automatic_with_notice`.

## Migration v1 → v2
Migration geschieht immer auf einer Kopie nach Snapshot/Backup. Ursprungsdateien bleiben unangetastet, bis die neue Version vollständig validiert ist. Event-IDs bleiben erhalten; die neue Hash-Kette der migrierten Kopie wird in einem Migration Receipt dokumentiert.

## Recovery
1. Metadaten prüfen.
2. neuesten gültigen Snapshot bestimmen.
3. Journal ab Snapshot-Head verifizieren.
4. bestätigte Ereignisse idempotent wiederholen.
5. ungültigen Tail isolieren.
6. `RECOVERY_RECEIPT.json` schreiben.
7. neuen sicheren Snapshot erzeugen.

## Zeitanker
Systemzeit ist keine alleinige Wahrheit. Bei verdächtigen Sprüngen wird nur unsicherer passiver Nachholfortschritt eingefroren; lokales aktives Spielen bleibt möglich.

## Nicht Bestandteil von 0.4.2
Keine Datenbank, keine Runtime-Save-Engine, kein Telegram-Sync und keine UI-Implementierung. 0.4.2 definiert ausschließlich den implementierbaren Vertrag.
