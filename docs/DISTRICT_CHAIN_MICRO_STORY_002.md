# District-Chain Micro-Story 002 – Laienhilfe

## Was passiert jetzt?

Wenn das bestätigte District-Ereignis **„Eine Tür steht plötzlich offen“** (`district.temporary_space_opens`) passiert, kann daraus später im selben Bezirk genau ein bestätigter Nachhall entstehen.

Die Folge erscheint **nicht sofort**. Erst ein späterer bestätigter District-Zyklus desselben Bezirks darf den katalogisierten Child `temporary_space_afterimage` erzeugen:

**„Die Tür ist zu – die Adresse lebt weiter.“**

Der Schlüssel ist weg und das Tor wieder verriegelt. Trotzdem bleiben Kreidestriche, Wegbeschreibungen und unterschiedliche Geschichten darüber zurück, wo der Eingang einmal war. Aus einem kurzfristig nutzbaren Raum wird lokales Szenegedächtnis.

## Was verändert die Geschichte nicht?

Der Nachhall ist keine Belohnung und keine neue Immobilienmechanik. Er verändert weder Geld noch District-Werte, Energie, Besitz oder andere Balancewerte.

## Welche Technik wird wiederverwendet?

- Parent bleibt ein bestätigter `world.district_effect_applied`-Record.
- Child bleibt `world.district_followup_resolved` aus Contract V1.
- Parent und Child müssen denselben `district_id` besitzen.
- `causation_id` ist die bestätigte Parent-Event-ID.
- `correlation_id` bleibt `district-chain:{parent_event_id}`.
- Die Child-ID bleibt deterministisch.
- Ein identischer Retry erzeugt keinen zweiten Child-Record.
- Pro bestätigtem District-Zyklus wird höchstens ein offener Micro-Story-Nachhall aufgelöst.
- Browser und Timeline bleiben read-only.

## Was sieht man in der Timeline?

Die bereits vorhandene read-only Projection versteht den neuen Child-Typ ohne zweite Darstellungsschicht. Wenn Parent und Child bestätigt, im selben Bezirk und in der richtigen Journal-Reihenfolge vorhanden sind, kann die Timeline anzeigen:

**Folge von: Eine Tür steht plötzlich offen**

Fehlt der Parent oder passt der Bezirk nicht, wird keine Ursache erfunden.

## Warum ist Story 002 anders als Story 001?

- Story 001: **Störung → Wiederkehr → praktische Erinnerung**
- Story 002: **Chance → Verlust → kulturelle Erinnerung**

So wird die Living World breiter, ohne für jede Geschichte eine neue Mechanik zu bauen.

## Nächster sinnvoller Prüfschritt

Nach sicherem Merge dieser Story sollte ein echter Runtime→Persistenz→Projection→Browser-E2E beide District-Ketten in isoliertem Spielstand vollständig erzeugen und sichtbar prüfen. So wird nicht nur der Einzelvertrag, sondern die ganze Nutzerkette bewiesen.
