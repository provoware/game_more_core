# District Micro-Story 002 – Hochschul-Audit und Storyentscheidung

## Ziel

Vor einer zweiten District-Folgegeschichte wird nicht einfach ein weiterer Text an die bestehende Kette gehängt. Die drei noch nicht verwendeten District-Events werden nach demselben technischen Vertrag und nach dramaturgischen Kriterien verglichen. Ergebnis dieses Audits ist **eine begründete Empfehlung, noch keine Runtime-Implementierung**.

## Fester technischer Rahmen

Alle Kandidaten müssen den bereits validierten Contract V1 wiederverwenden:

- bestätigter Parent: `world.district_effect_applied`,
- Child: `world.district_followup_resolved`,
- Parent und Child im selben `district_id`,
- `causation_id = parent_event_id`,
- bestehendes `district-chain:{parent_event_id}`-Korrelationsmuster,
- deterministische Child-ID und Exactly-once-Retry,
- keine neue Eventengine, kein Browser-Write, keine neue Persistenzschicht,
- Micro-Story-Nachhall bleibt zunächst **ohne zusätzliche Balancewirkung**.

Micro-Story 001 bleibt Referenz, aber nicht Schablone: `district.power_flicker` erzählt **Störung → Wiederkehr → praktische Erinnerung**. Micro-Story 002 soll die emotionale Grammatik erweitern.

## Bewertungsmethode

Jeder Kandidat erhält 1–5 Punkte in sechs Dimensionen. Maximal sind 30 Punkte möglich.

1. **Konsequenzkraft** – fühlt sich die spätere Folge wie eine glaubwürdige Konsequenz des Parents an?
2. **Kontrast zu Story 001** – entsteht eine neue emotionale Form statt einer Textvariante derselben Idee?
3. **Berlin-/Subkultur-Glaubwürdigkeit** – passt der Nachhall zu temporären Räumen, Mundpropaganda, Kontrolle und improvisierter Szeneorganisation?
4. **Technische Anschlussfähigkeit** – lässt sich die Folge über den vorhandenen Parent-/Child-Vertrag ohne neue Autorität erzeugen?
5. **Wiedererkennungswert** – bleibt nach mehreren Spielzyklen ein klarer eigener Storykern hängen?
6. **Serienrisiko** – 5 bedeutet geringes Risiko, dass später jede District-Meldung automatisch denselben Nachhalltyp bekommt.

## Kandidat A – `district.word_of_mouth_wave`

**Parent:** „Die Nachricht macht die Runde.“

### Möglicher Nachhall

**Leitidee:** Das Gerücht überlebt die eigentliche Welle und wird ungenauer, größer und schwerer kontrollierbar.

Mögliche spätere Storyrichtung:

> „Keiner weiß mehr, wer es zuerst erzählt hat.“
>
> Die ursprüngliche Nacht ist vorbei, aber in neuen Versionen wird sie jedes Mal größer. Namen wechseln, Orte verrutschen, und plötzlich kennen Leute die Geschichte, die nie dort waren.

### Bewertung

| Dimension | Punkte | Begründung |
|---|---:|---|
| Konsequenzkraft | 4 | Mundpropaganda erzeugt plausibel weitere Mundpropaganda. |
| Kontrast zu Story 001 | 4 | Soziale Verzerrung statt technischer Vorsorge. |
| Subkultur-Glaubwürdigkeit | 5 | Szeneinformationen verbreiten sich realistisch über Personenketten. |
| Technische Anschlussfähigkeit | 5 | Parent kann unverändert denselben Folgeeventvertrag nutzen. |
| Wiedererkennungswert | 3 | Stark als Atmosphäre, aber weniger ortsgebunden und visuell. |
| Serienrisiko | 3 | Risiko, dass spätere Storys zu oft nur „Gerücht lebt weiter“ erzählen. |
| **Summe** | **24/30** | Gute soziale Story, aber nicht die stärkste zweite Signatur. |

## Kandidat B – `district.patrol_sweep`

**Parent:** „Mehr Blau in den Nebenstraßen.“

### Möglicher Nachhall

**Leitidee:** Die sichtbaren Kontrollen verschwinden, aber Verhalten und Wege der Szene bleiben verändert.

Mögliche spätere Storyrichtung:

> „Die Streifen sind weg. Die Umwege bleiben.“
>
> Zwei Nächte später steht an der Ecke niemand mehr. Trotzdem gehen Leute noch durch Hinterhöfe, Nachrichten werden knapper und jeder schaut einmal mehr über die Schulter.

### Bewertung

| Dimension | Punkte | Begründung |
|---|---:|---|
| Konsequenzkraft | 5 | Kontrolle kann auch nach ihrem Ende Verhalten prägen. |
| Kontrast zu Story 001 | 4 | Psychologische Gewohnheit statt technischer Vorbereitung. |
| Subkultur-Glaubwürdigkeit | 5 | Routen, Vorsicht und Kommunikationsverhalten passen gut zur Welt. |
| Technische Anschlussfähigkeit | 5 | Kein zusätzlicher Zustand nötig; Parent genügt als Ursache. |
| Wiedererkennungswert | 4 | Klare Formulierung und sichtbare Verhaltensspur. |
| Serienrisiko | 4 | Eigenständig, aber thematisch schnell düster und repetitiv, wenn zu häufig. |
| **Summe** | **27/30** | Sehr starker späterer Kandidat, besonders für einen dunkleren Storybogen. |

## Kandidat C – `district.temporary_space_opens`

**Parent:** „Eine Tür steht plötzlich offen.“

### Empfohlener Nachhall

**Leitidee:** Der Raum verschwindet wieder, aber seine kurze Existenz verwandelt sich in lokales Szenegedächtnis.

**Arbeitstitel:** **„Die Tür ist zu – die Adresse lebt weiter.“**

**Storykern:**

> Der Schlüssel ist weg, das Tor wieder verriegelt. Trotzdem tauchen an der Ecke neue Kreidestriche auf. Leute beschreiben anderen, wo damals der Eingang war. Für ein paar Nächte war es nur ein leerer Raum – jetzt ist es eine Adresse, von der jeder eine andere Version kennt.

Das ist keine Belohnung und kein zweiter Immobilienmechanismus. Der Nachhall beschreibt ausschließlich, wie **temporäre Nutzung kulturelle Erinnerung produziert**.

### Dramaturgischer Bogen

**Chance → Aneignung → kurze Ekstase → Verlust → Mythos**

Damit ergänzt Story 002 die erste Kette:

- Story 001: **Störung → Wiederkehr → praktische Erinnerung**
- Story 002: **Chance → Verlust → kulturelle Erinnerung**

Beide Geschichten handeln von Erinnerung, aber aus unterschiedlichen Ursachen: einmal lernt die Szene, einmal verklärt sie.

### Bewertung

| Dimension | Punkte | Begründung |
|---|---:|---|
| Konsequenzkraft | 5 | Ein ausdrücklich temporärer Raum besitzt eine natürliche spätere Schließung. |
| Kontrast zu Story 001 | 5 | Verlust und Mythos statt Störung und Vorsorge. |
| Subkultur-Glaubwürdigkeit | 5 | Kurz genutzte Räume und weiterlebende Ortsgeschichten sind für die Welt besonders glaubwürdig. |
| Technische Anschlussfähigkeit | 5 | Der vorhandene spätere District-Zyklus reicht als Zeitpunkt; keine neue Uhr oder Property-Autorität nötig. |
| Wiedererkennungswert | 5 | „Die Adresse lebt weiter“ erzeugt einen klaren, ortsbezogenen Storyanker. |
| Serienrisiko | 5 | Eigenständige Signatur; keine allgemeine Vorlage für jeden Eventtyp. |
| **Summe** | **30/30** | Stärkster Kandidat für Micro-Story 002. |

## Entscheidung

**Empfohlen wird `district.temporary_space_opens`.**

Nicht weil es die höchsten positiven District-Effekte besitzt, sondern weil es narrativ den größten zusätzlichen Raum eröffnet, ohne neue Mechanik zu verlangen. Der Parent sagt bereits, dass niemand weiß, wie lange das Fenster bleibt. Eine spätere geschlossene Tür ist damit keine erfundene Gegenmechanik, sondern die natürliche narrative Auflösung desselben temporären Zustands.

## Empfohlener Implementierungsvertrag für den nächsten Slice

Noch nicht in diesem Audit implementieren; für Micro-Story 002 wird empfohlen:

- Parent: `district.temporary_space_opens`
- Follow-up-ID: `temporary_space_afterimage`
- Arbeitstitel: `Die Tür ist zu – die Adresse lebt weiter`
- Zeitpunkt: frühestens ein **späterer bestätigter District-Zyklus desselben Bezirks**
- Child-Typ: vorhandenes `world.district_followup_resolved`
- keine zusätzlichen District-Deltas
- kein Property-Kauf, kein Besitzstatus, kein Geldfluss
- kein Systemzeit-Trigger
- Browser/Timeline bleiben read-only
- identischer Retry bleibt Exactly-once

## Bewusste Nicht-Ziele

- keine generische Storyketten-DSL,
- kein automatischer Nachhall für alle vier District-Events,
- keine neue Ressource „Erinnerung“ oder „Mythos“,
- keine Belohnung für das reine Erscheinen der Story,
- kein Besitzrecht am temporären Raum,
- keine Verknüpfung mit echten Immobilien ohne eigenen späteren Vertrag.

## Spätere Erweiterungsidee

**DISTRICT-STORY-TONE-BALANCE:** Wenn mindestens drei Micro-Stories existieren, sollte ein eigener kleiner Content-Audit prüfen, ob positive, bedrohliche, melancholische und soziale Nachhalltypen ausreichend unterschiedlich verteilt sind. Nutzen: Die Living World entwickelt eine dramaturgische Bandbreite statt nur immer neue Varianten von „etwas war, jetzt erinnert man sich daran“ zu sammeln.
