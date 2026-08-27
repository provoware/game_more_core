# Street-Mini-Chain Contract Audit

## Kurzfassung

Der Audit ist **positiv mit klarer Architekturgrenze**:

- `street.encounter_resolved` eignet sich als bestätigte Parent-Evidenz.
- Der bestehende `PersistenceKernel` kann Kausalität und Exactly-once ohne Änderung tragen.
- Der District-Childtyp `world.district_followup_resolved` und der District-Resolver dürfen **nicht** wiederverwendet oder kopiert werden.
- Vor einer ersten Street-Micro-Story fehlt genau ein kleiner Street-eigener Vertrag: ein katalogisierter Child-Eventtyp, empfohlen `street.followup_resolved`.

Es wurde in diesem Audit **keine** Storyruntime implementiert.

---

## 1. Warum `street.encounter_resolved` ein guter Parent ist

Jeder bestätigte Street-Walk schreibt zuerst genau einen stabilen Record:

`{walk_instance_id}:001` → `street.encounter_resolved`

Der Record enthält bereits:

- `walk_instance_id`
- `approach_id`
- `encounter_id`
- `polarity`
- `title_key` / `body_key`
- tatsächlich angewendete Effekte
- Street-Vertragsversion

Zusätzlich kommt der Record aus einem bestätigten `character`-Kontext mit `entity_id` und `character_id`. Ein Retry desselben Walks liest genau diesen Record wieder ein und würfelt nicht neu.

**Auditurteil:** Die Parent-Identität ist stabil, replaybar und für eine spätere Folge ausreichend eindeutig.

---

## 2. Was vom District-Vertrag wiederverwendet werden darf

Nicht die District-Storylogik – sondern nur die bereits allgemeine Persistenzmechanik.

Der `PersistenceKernel` unterstützt für jeden erlaubten Eventtyp bereits:

- append-only Journal
- deterministische Event-ID als Exactly-once-Schlüssel
- Konflikt, wenn dieselbe Event-ID mit anderem Typ/Payload erneut kommt
- `causation_id`
- `correlation_id`

Für einen späteren Street-Child sollte daher derselbe Grundsatz gelten:

- `parent_event_id` liegt **im Child-Payload**
- `causation_id = parent_event_id`
- empfohlen: `correlation_id = street-chain:{parent_event_id}`
- deterministische Child-ID, z. B. `street-followup:{parent_event_id}:{followup_id}`

Die Parent-ID muss im Payload liegen, weil die vorhandene Idempotenzprüfung Typ + Payload fingerprintet. Nur so wird ein Retry mit derselben Child-ID, aber anderem Parent, sicher zum Konflikt.

---

## 3. Was ausdrücklich nicht wiederverwendet wird

### Kein District-Childtyp

`world.district_followup_resolved` besitzt District-spezifische Semantik und gehört nicht in die Street-Domäne.

### Kein District-Resolver

Street ist character-/walk-gebunden. District-Ketten sind district-/cadence-gebunden. Eine gemeinsame Storyengine würde unterschiedliche Autoritätsgrenzen vermischen.

### Keine District-ID-Regel

Die Street-Kette braucht keinen künstlichen Bezirksschlüssel. Der naheliegende Bindungspunkt ist der bestätigte lokale Character-Kontext des Parents.

### Keine Browserautorität

Die vorhandene Timeline darf später nur einen bestätigten Child-Record darstellen. Sie darf weder Parent noch Storyfolge selbst erzeugen.

---

## 4. Die eine noch fehlende Vertragsbrücke

Im aktuellen `JOURNAL_MANIFEST.json` existiert **kein** `street.followup_resolved`. Auch die Timeline kennt keinen Street-Childtyp.

Deshalb wäre eine Storyimplementation in diesem Audit verfrüht.

### Empfehlung für Contract V1

Ein späterer `STREET-MINI-CHAIN-CONTRACT-V1` sollte genau festlegen:

1. neuer Eventtyp `street.followup_resolved`,
2. Pflichtfelder `parent_event_id`, `character_id`, `followup_id`, `title_key`, `body_key`,
3. `causation_id = parent_event_id`,
4. `correlation_id = street-chain:{parent_event_id}`,
5. Child und Parent müssen zum selben bestätigten Character gehören,
6. Child entsteht erst bei einem **späteren bestätigten Street-Walk**,
7. pro bestätigtem Walk höchstens ein Follow-up,
8. Retry bleibt Exactly-once,
9. keine Balancewirkung im ersten Story-Slice.

Damit wird der technische Lerneffekt der District-Ketten genutzt, ohne ihre Fachlogik zu kopieren.

---

## 5. Kreativer Kandidatenvergleich für eine spätere Story 001

| Parent aus dem echten Katalog | Erinnerungspotential | Risiko versteckter Mechanik | Eigenständiger Ton | Empfehlung |
|---|---:|---:|---:|---|
| `street.cable_tip` – **Kabeltipp am Bauzaun** | 5/5 | 5/5 niedrig | 5/5 | **15/15** |
| `street.friendly_face` – Bekanntes Gesicht | 5/5 | 3/5 Rufkopplung möglich | 4/5 | 12/15 |
| `street.poster_wall` – Plakatwand im Wandel | 4/5 | 5/5 niedrig | 3/5 | 12/15 |
| `street.open_door` – Tür wird aufgehalten | 4/5 | 4/5 | 3/5 | 11/15 |

### Stärkster Storykern

**Parent:** `street.cable_tip`

Der bestehende Text sagt bereits, dass ein kleiner Techniktrick „später Ärger sparen dürfte“ und dass solche Hinweise hängen bleiben. Das ist eine natürliche Einladung zu Weltgedächtnis, ohne neue Ressource oder Belohnung.

**Späterer, noch nicht implementierter Follow-up-Vorschlag:** `cable_tip_echo`

**Arbeitstitel:** **„Der Tipp macht die Runde.“**

Storyidee: Bei einem späteren Street-Walk hörst du denselben kleinen Techniktrick aus einem anderen Mund. Aus einem beiläufigen Satz ist Szenewissen geworden. Keine Auszahlung, kein Rufbonus, kein Inventargegenstand – nur der Beweis, dass Informationen in dieser Stadt weiterleben.

---

## 6. Regressionen dieses Audits

Der Audit sichert maschinell ab:

- echter Street-Walk erzeugt `street.encounter_resolved` als erstes stabiles Parent-Event,
- Parent ist an den bestätigten Character gebunden,
- Retry würfelt nicht neu und schreibt nichts zusätzlich,
- Produktion besitzt aktuell bewusst keinen `street.followup_resolved`-Vertrag,
- ein solcher nicht katalogisierter Eventtyp wird vom PersistenceKernel fail-closed abgewiesen,
- der unveränderte PersistenceKernel kann in einem isolierten Audit-Probe `causation_id`, `correlation_id`, Exactly-once und Konfliktsemantik generisch tragen.

## Ergebnis

**GO für einen kleinen Street-Chain Contract V1.**

**NO-GO für eine direkte Micro-Story ohne vorherigen Child-Vertrag.**

Der nächste fachliche Slice sollte deshalb zuerst `0.8.8-STORY-STREET-MINI-CHAIN-CONTRACT-V1` sein und noch keine zweite Street-Storyengine bauen.
