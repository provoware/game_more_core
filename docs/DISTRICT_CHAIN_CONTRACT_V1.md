# District-Chain Contract V1

## Ziel

Dieser Vertrag schafft die kleinste sichere Brücke zwischen einem bereits bestätigten Bezirksereignis und einer späteren Folgebegegnung. Er baut **noch keine Micro-Story** und keine zweite Eventengine.

## Der eine neue Kind-Eventtyp

`world.district_followup_resolved`

Er ist im bestehenden `JOURNAL_MANIFEST.json` katalogisiert und nicht direkt durch den Spieler rückgängig zu machen. Die Autorität bleibt Runtime/Persistence.

## Verbindliche Elternbindung

Eine spätere Folgebegegnung muss mindestens diese Payload-Felder tragen:

- `parent_event_id`: die bestätigte `event_id` des Elternrecords `world.district_effect_applied`
- `district_id`: derselbe Bezirk wie im Elternrecord
- `followup_id`: die katalogisierte Identität der Folge

Zusätzlich nutzt der bestehende Journalpfad:

- `causation_id = parent_event_id`
- `correlation_id = district-chain:{parent_event_id}`
- Child-ID: `district-followup:{parent_event_id}:{followup_id}`

Damit ist die Ursache sowohl maschinenlesbar als auch im idempotenten Payload gebunden.

## Replay- und Exactly-once-Vertrag

Der vorhandene `PersistenceKernel` wird unverändert wiederverwendet:

1. Der erste bestätigte Child-Record wird append-only geschrieben.
2. Derselbe Retry mit derselben `event_id`, demselben Typ und demselben Payload erzeugt **keinen zweiten Record**.
3. Dieselbe Child-ID mit einem anderen `parent_event_id` im Payload ist ein Konflikt und wird abgewiesen.
4. `causation_id` und `correlation_id` werden vom vorhandenen Persistence-Pfad unverändert in den Journalrecord übernommen.

Die Eltern-ID liegt absichtlich auch im Payload. Dadurch gehört sie zur bestehenden Idempotenzprüfung; es wird kein paralleler Replay-Mechanismus eingeführt.

## District-Bindung

Contract V1 schreibt fest, dass die `district_id` des Child-Records zum bestätigten Elternrecord passen muss. Die eigentliche Micro-Story-Runtime muss diese Vorbedingung vor dem Commit prüfen. Dieser Slice implementiert noch keinen Auslöser und verändert deshalb weder Cadence noch District-Werte.

## Was bewusst noch nicht existiert

- kein automatischer Folge-Trigger,
- keine Storyauswahl,
- keine neue Balancewirkung,
- keine neue Save-Struktur,
- kein Browser-/UI-Write,
- keine Timeline- oder Biography-Autorität.

Timeline und Biografie dürfen spätere bestätigte Records nur read-only darstellen.

## Nächster fachlicher Schritt

Als nächster Story-Slice kann **genau eine** Micro-Story den Vertrag verwenden: bestätigten Parent laden, District-Gleichheit prüfen, deterministische `followup_id` wählen, den einen Child-Record genau einmal committen und dieselbe Kausalität anschließend read-only sichtbar machen.
