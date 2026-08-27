# Street-Mini-Chain Contract Audit

## Kurzfassung

Der Audit ist **positiv für einen kleinen Contract V1 – aber nicht für direkten Storycontent**:

- `street.encounter_resolved` besitzt eine stabile, replaybare Parent-ID und einen bestätigten `character`-Entity-Kontext.
- Der bestehende `PersistenceKernel` kann Kausalität und Exactly-once ohne Änderung tragen.
- Der District-Childtyp `world.district_followup_resolved` und der District-Resolver dürfen **nicht** wiederverwendet oder kopiert werden.
- Vor einer ersten Street-Micro-Story fehlt ein Street-eigener Child-Vertrag, empfohlen `street.followup_resolved`.
- Zusätzlich muss Contract V1 eine heute noch offene Identitätsgrenze schließen: `entity_id` ist beim Street-Walk validiert, das optionale Journalfeld `character_id` kann derzeit jedoch davon abweichen.

Es wurde in diesem Audit **keine** Storyruntime implementiert.

---

## 1. Was die Street-Parent-Evidenz bereits sicher kann

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

Der Service verlangt außerdem `entity_type = character` und `entity_id = character.character_id`. Ein Retry desselben Walks liest genau den persistierten Parent wieder ein und würfelt nicht neu.

**Sicherer heutiger Bindungspunkt:** `entity_type=character` + `entity_id`.

### Neu gefundene Grenze: `character_id` ist noch keine eigene Autorität

Die Review-Regression zeigt bewusst einen realen Vertragsrand: `JournalContext.character_id` wird beim Street-Walk nicht gegen `entity_id` geprüft. Ein technisch widersprüchlicher Kontext kann daher aktuell einen Record mit

- `entity_id = player-local`
- aber `character_id = different-character`

schreiben.

Das ist kein Fehler der bestehenden Street-Begegnung, weil ihre Runtime auf `entity_id` autorisiert. Für eine **neue Kettenfunktion** wäre es aber falsch, das optionale `character_id` ungeprüft als Parent-Bindung zu verwenden.

**Auditurteil:** Parent-ID und Entity-Bindung sind stark genug für Contract V1. Eine Street-Micro-Story bleibt jedoch NO-GO, bis Contract V1 die Character-Identität fail-closed festlegt.

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

Die Street-Kette braucht keinen künstlichen Bezirksschlüssel. Der kanonische Parent ist der bestätigte Street-Record; dessen `entity_id` liefert die heutige Character-Autorität.

### Keine Browserautorität

Die vorhandene Timeline darf später nur einen bestätigten Child-Record darstellen. Sie darf weder Parent noch Storyfolge selbst erzeugen.

---

## 4. Die noch fehlende Vertragsbrücke

Im aktuellen `JOURNAL_MANIFEST.json` existiert **kein** `street.followup_resolved`. Auch die Timeline kennt keinen Street-Childtyp.

Deshalb wäre eine Storyimplementation in diesem Audit verfrüht.

### Verbindliche Empfehlung für Contract V1

Der nächste Slice `0.8.8-STORY-STREET-MINI-CHAIN-CONTRACT-V1` soll genau festlegen und regressionssichern:

1. neuer Eventtyp `street.followup_resolved`,
2. Pflichtfelder `parent_event_id`, `character_id`, `followup_id`, `title_key`, `body_key`,
3. Parent muss `street.encounter_resolved` sein,
4. Parent muss `entity_type = character` besitzen,
5. kanonische Character-ID des Parents ist `entity_id`,
6. wenn Parent-`character_id` vorhanden ist, muss es exakt `entity_id` entsprechen; fehlt es oder widerspricht es dem für die Kette verlangten Vertrag, wird fail-closed nicht verknüpft,
7. Child-`character_id` muss derselben kanonischen Parent-Identität entsprechen,
8. `causation_id = parent_event_id`,
9. `correlation_id = street-chain:{parent_event_id}`,
10. Child entsteht erst bei einem **späteren bestätigten Street-Walk**,
11. pro bestätigtem Walk höchstens ein Follow-up,
12. Retry bleibt Exactly-once,
13. keine Balancewirkung im ersten Story-Slice.

Damit wird der technische Lerneffekt der District-Ketten genutzt, ohne ihre Fachlogik zu kopieren und ohne die neu gefundene Character-Grenze zu verschleiern.

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
- Parent besitzt den bestätigten Character-Entity-Kontext,
- Retry würfelt nicht neu und schreibt nichts zusätzlich,
- eine direkte Regression reproduziert, dass das optionale `character_id` heute vom kanonischen `entity_id` abweichen kann – genau deshalb ist Contract V1 Pflicht,
- Produktion besitzt aktuell bewusst keinen `street.followup_resolved`-Vertrag,
- ein solcher nicht katalogisierter Eventtyp wird vom PersistenceKernel fail-closed abgewiesen,
- der unveränderte PersistenceKernel kann in einem isolierten Audit-Probe `causation_id`, `correlation_id`, Exactly-once und Konfliktsemantik generisch tragen.

## Ergebnis

**BEDINGTES GO für `0.8.8-STORY-STREET-MINI-CHAIN-CONTRACT-V1`.**

**NO-GO für eine direkte Street-Micro-Story.**

Contract V1 muss zuerst den Child-Eventvertrag **und** die Character-Identitätsgrenze eindeutig fail-closed machen. Erst danach darf `STREET-MINI-CHAIN-001` als separater Story-Slice folgen.
