# 0.8.8 – Street Micro-Story 002 Audit

## Ziel

Eine zweite seltene Street-Micro-Story auswählen, ohne neue Runtime-, Journal-, Projection- oder Balancearchitektur einzuführen.

## Bewertungsmaßstab

Jeder Kandidat wird auf fünf Punkte geprüft:

1. **Kausal lesbar:** Die spätere Szene muss glaubhaft aus dem Parent-Ereignis hervorgehen.
2. **Ohne neue Identität:** Kein zusätzlicher NPC-, Orts- oder Inventarvertrag nötig.
3. **Balance-neutral:** Der Nachhall verändert weder Energie, Stress, Ruf, Geld noch Inventar.
4. **Selten genug:** Der Parent soll kein Dauereffekt werden.
5. **Eigener Ton:** Die Geschichte soll sich klar von `street.cable_tip -> cable_tip_echo` und den District-Nachhallen unterscheiden.

## Kandidaten

| Parent | Stärke | Risiko | Urteil |
|---|---|---|---|
| `street.friendly_face` | gute soziale Wiedererkennung | würde ohne NPC-ID schnell erfundene Personenpersistenz behaupten | nicht wählen |
| `street.construction_detour` | klare räumliche Folge | kann leicht wie ein dauerhafter Welt-/Map-Zustand wirken | Reserve |
| `street.lost_glove` | sehr konkrete persönliche Spur, Parent ist selten und bereits katalogisiert | darf keinen Inventar-Recovery-Effekt vortäuschen | **gewählt** |

## Entscheidung

**Empfohlene Story 002:** `street.lost_glove -> lost_glove_fence_echo`

Arbeitstitel: **„Der Handschuh wartet noch.“**

Dramaturgischer Kern: Bei einem späteren bestätigten Street-Walk sieht der Charakter den verlorenen Handschuh über einem Bauzaun hängen. Jemand hat ihn sichtbar aufgehoben und dort abgelegt. Die Stadt reagiert klein, glaubwürdig und ohne neue Figur oder neue Ressource.

## Verbindliche Grenzen für die spätere Umsetzung

- exakt derselbe `street.followup_resolved`-Contract wie Story 001
- Parent ausschließlich `street.encounter_resolved` mit `encounter_id=street.lost_glove`
- bestätigte Parent-`entity_id` bleibt Character-Autorität
- kein Inventargegenstand wird erzeugt, zurückgegeben oder implizit als wiedergewonnen verbucht
- keine Map-, Location- oder NPC-Persistenz
- keine Balancewirkung
- maximal ein Follow-up im bestätigten späteren Street-Walk gemäß bestehendem Contract
- Texte bleiben im deutschen Textkatalog, nicht in der Runtime
- vorhandene read-only Timeline bleibt einzige sichtbare Projection

## Bewusste Nicht-Ziele

Dieser Audit implementiert **keine** zweite Story. Er verändert weder Manifest noch Runtime, Journal, Save, Browser, CSS oder Gameplaywerte.

## Spätere Erweiterungsidee

Nach mindestens zwei Street-Micro-Stories sollte ein kleiner **Story-Tone-Diversity-Audit** prüfen, ob soziale, materielle und räumliche Nachhalle ausgewogen sind, bevor weitere Geschichten ergänzt werden. So bleibt die Stadt abwechslungsreich statt formelhaft.
