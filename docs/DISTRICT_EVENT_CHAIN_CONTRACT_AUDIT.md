# District-Ereignisketten – Vertragsaudit

## Worum geht es?

BUNKERFREQUENZ kann bestätigte Bezirksereignisse bereits dauerhaft und replay-sicher festhalten. Die offene Frage dieses Audits ist enger: **Kann ein bestätigtes Bezirksereignis heute schon sicher als Ursache für eine spätere kleine Folgebegegnung dienen, ohne eine zweite Eventengine oder neue Persistenzautorität zu erfinden?**

## Ergebnis in einem Satz

**Teilweise vorbereitet, aber noch nicht implementierungsreif.** Der bestätigte Elternnachweis existiert bereits; ein eigener katalogisierter Journalvertrag für die Folgebegegnung fehlt noch. Deshalb wird in diesem Slice bewusst keine Gameplay-Kette gebaut.

## Was heute schon belastbar vorhanden ist

1. `world.district_effect_applied` ist ein katalogisierter, append-only Journal-Eventtyp.
2. Jeder bestätigte District-Effekt besitzt eine eindeutige Journal-`event_id`.
3. Der Payload trägt `district_id`, `source_type` und `source_id`.
4. Bei echten District-World-Events enthält `source_id` bereits District, ursprünglichen Trigger und katalogisierte District-Event-ID.
5. Der bestehende Runtime-Pfad kann diese Quelle beim Replay wiedererkennen, ohne neu zu würfeln.
6. Die Biografie bleibt reine Projektion: Sie zeigt nur ausdrücklich persistierte `character.biography_entry_added`-Records und darf kein Folgeereignis aus Anzeigezustand erfinden.

Damit existiert eine belastbare **Eltern-Evidenz**, auf die ein späterer Vertrag referenzieren kann.

## Was noch fehlt

Im `JOURNAL_MANIFEST.json` existiert derzeit **kein eigener Eventtyp für eine District-Folgebegegnung oder einen Kettenfortschritt**. Ohne diesen Vertrag wäre jede sofortige Implementierung problematisch:

- eine neue Runtime könnte einen nicht katalogisierten Eventtyp persistieren,
- eine UI-/Biography-Projektion könnte fälschlich zur Gameplay-Autorität werden,
- Replay- und Idempotenzregeln wären für das Kindereignis nicht definiert,
- die Beziehung Elternereignis → Folgeereignis wäre nicht verbindlich festgelegt.

Deshalb lautet die Audit-Entscheidung: **No-Fix für Gameplay in dieser Iteration.**

## Sicherer nächster Vertrags-Slice

Bevor eine erste Micro-Story entsteht, sollte ein kleiner `DISTRICT-CHAIN-CONTRACT-V1` genau folgende Punkte entscheiden und regressionssichern:

- genau **einen** neuen katalogisierten Kind-Eventtyp für eine bestätigte Folgebegegnung,
- eindeutige Referenz auf die bestätigte Eltern-`event_id`,
- District-ID muss zum Elternrecord passen,
- Kind darf nur aus bestätigter Runtime-Autorität entstehen,
- identischer Retry erzeugt kein zweites Kind,
- kein Systemzeit-Seed und kein Browser-/UI-Write,
- Timeline und Biografie lesen das Ergebnis nur read-only.

`JOURNAL_MANIFEST.json` besitzt bereits die optionalen Felder `causation_id` und `correlation_id`. **Bevor sie für den neuen Vertrag gewählt werden**, muss jedoch gezielt geprüft werden, ob der bestehende Persistence-Kernel diese Felder für diesen Runtime-Pfad bereits unverändert schreiben kann. Falls nicht, ist zuerst dieser kleine Persistenzvertrag zu ergänzen; ein freies Payload-Ersatzfeld soll nicht parallel erfunden werden.

## Laienbeispiel

Heute kann das Spiel sicher wissen:

> „In Kreuzberg ist Ereignis A wirklich passiert und hat den Bezirk verändert.“

Was noch nicht vertraglich festgelegt ist:

> „Ereignis A darf später genau einmal Begegnung B auslösen, und B weiß eindeutig, dass A seine Ursache war.“

Erst wenn diese zweite Aussage technisch eindeutig und replay-sicher ist, soll die eigentliche Storyfolge gebaut werden.

## Bewusste Nicht-Ziele dieses Audits

- keine neue Eventengine,
- keine neue Storybegegnung,
- keine Manifest-Erweiterung auf Verdacht,
- keine Änderung von District-Effekten, Cadence oder Seed,
- keine neue Save-/Journal-Struktur,
- keine UI als Gameplay-Autorität.

## Spätere Verbesserungsidee

Nach einem erfolgreichen `DISTRICT-CHAIN-CONTRACT-V1` eignet sich als erster Proof of Concept **genau eine kleine Folgegeschichte mit kurzer Erinnerung**: ein bestätigtes District-Ereignis erzeugt nach einer ebenfalls bestätigten Spielautorität genau eine katalogisierte Anschlussbegegnung; Timeline und Biografie zeigen anschließend dieselbe Ursache-Wirkungs-Kette read-only. Das erhöht Storytiefe, ohne die bestehende District-Engine zu duplizieren.
