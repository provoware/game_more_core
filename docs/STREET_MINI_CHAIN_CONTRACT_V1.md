# Street Mini-Chain Contract V1

## Zweck

Dieser Vertrag erlaubt BUNKERFREQUENZ, später seltene Straßenbegegnungen mit einer kleinen, verzögerten Folge zu verbinden, ohne die District-Storyengine zu kopieren oder Browserzustand zur Spielautorität zu machen.

## Kanonischer Parent

Nur ein bereits persistiertes `street.encounter_resolved` darf Parent sein. Es muss `entity_type=character` besitzen. Die kanonische Character-Identität ist ausschließlich die bestätigte `entity_id` des Parent-Records.

Das optionale Journalfeld `character_id` ist keine zweite Autorität. Fehlt es, bleibt `entity_id` maßgeblich. Ist es vorhanden und weicht von `entity_id` ab, ist der Parent für eine Street-Kette **nicht zulässig**. Die spätere Runtime muss diesen Fall fail-closed ablehnen.

## Child-Vertrag

Der einzige katalogisierte Childtyp ist `street.followup_resolved`. Sein Payload führt mindestens:

- `parent_event_id`
- `character_id`, gebunden an `parent.entity_id`
- `followup_id`

Kausalität und Identität sind deterministisch:

- `causation_id = parent_event_id`
- `correlation_id = street-chain:{parent_event_id}`
- `event_id = street-followup:{parent_event_id}:{followup_id}`

Ein identischer Retry bleibt über den bestehenden `PersistenceKernel` idempotent. Dieselbe Event-ID mit anderem Inhalt bleibt ein Konflikt.

## Triggergrenze

Contract V1 führt noch **keinen** Storyresolver ein. Für den späteren Resolver gilt bereits verbindlich: Ein Child darf erst durch einen späteren bestätigten Street-Walk entstehen, pro Character darf höchstens ein offenes Follow-up geführt werden. Browser und Client dürfen kein Child schreiben.

## Nicht-Ziele

Keine konkrete Story, keine Texte in Runtimecode, keine Balancewirkung, keine District-Resolver-Kopie, keine zweite Persistence- oder Eventengine und noch keine Timeline-Projection des Childtyps.

## Laienhilfe

Eine normale Straßenbegegnung wird wie ein nummerierter Beleg gespeichert. Eine spätere Folge darf nur dann auf diesen Beleg zeigen, wenn eindeutig dieselbe Spielfigur gemeint ist. Gibt es zwei widersprüchliche Figuren-IDs, wird die Folge nicht erzeugt. So kann später eine kleine Geschichte entstehen, ohne dass das Spiel eine falsche Ursache erfindet.

## Nächster erlaubter Slice

Erst nach grünem Contract V1 darf `STREET-MINI-CHAIN-001` genau eine kleine, balance-neutrale Ursache→Folge-Geschichte auf diesem Vertrag implementieren. Bevorzugter bereits auditierter Kandidat: `street.cable_tip` → `cable_tip_echo`.
