# 0.8.8 – Street Story Tone Diversity Audit

## Ziel

Die zwei vorhandenen Street-Nachhalle dramaturgisch gegen weitere katalogisierte Street-Parents prüfen und Story 003 nur dann freigeben, wenn ein Kandidat klar anders, selten, kausal sauber und ohne neue Persistenz- oder Balancearchitektur umsetzbar ist.

## Bestehende Stories

| Story | Parent → Nachhall | Ton | Motiv | Pointe |
|---|---|---|---|---|
| 001 | `street.cable_tip` → `cable_tip_echo` | sozial-technisch, positiv | Wissen verbreitet sich in der Szene | ein kleiner Tipp bekommt ein Eigenleben |
| 002 | `street.lost_glove` → `lost_glove_fence_echo` | materiell-persönlich, leise menschlich | verlorener Gegenstand taucht sichtbar wieder auf | die Stadt reagiert, ohne Inventar zu verändern |

Damit sind soziale Weitergabe und materielle Wiederbegegnung bereits besetzt. Story 003 sollte deshalb weder erneut „jemand erinnert sich“ noch „ein Ding taucht wieder auf“ erzählen.

## Bewertungsmaßstab

Ein Kandidat gilt nur als freigabefähig, wenn alle Punkte gleichzeitig erfüllt sind:

1. **Eigenständiger Ton:** deutlich andere emotionale Farbe als Story 001 und 002.
2. **Kausal lesbar:** ein späterer Nachhall muss glaubhaft aus genau diesem bestätigten Parent folgen.
3. **Selten genug:** kein ständig sichtbarer Nachhall bei typischen Street-Runden.
4. **Balance-neutral:** keine Energie-, Stress-, Ruf-, Geld- oder Inventarwirkung.
5. **Keine neue Persistenz:** keine dauerhafte NPC-, Orts-, Objekt- oder Map-Identität nötig.
6. **Bestehender Contract:** später ausschließlich über `street.followup_resolved` und denselben Exactly-once-Pfad.

## Kandidaten

| Parent | Tonpotenzial | Stärke | Risiko | Urteil |
|---|---|---|---|---|
| `street.poster_wall` | räumlich, urban, leicht unheimlich | visuell klar anders; Stadt als Schichtung statt Person/Gegenstand | Parent ist mit Gewicht 10 nicht selten; ein wiederkehrendes Motiv könnte fälschlich dauerhaften Ortszustand suggerieren | **zurückstellen** |
| `street.open_door` | sozial-räumlich | einfache Ursache, warme Szene | würde ohne NPC-/Location-ID schnell eine konkrete wiederkehrende Person oder denselben Hinterhof erfinden; tonal zu nah an sozialem Nachhall | **nicht wählen** |
| `street.construction_detour` | räumlich, trocken-komisch | Parent ist relativ selten; klare Berliner Alltagskante | glaubwürdiger späterer Zusammenhang verlangt leicht einen persistenten Baustellen-/Ortszustand, den das Spiel nicht führt | **zurückstellen** |
| `street.sudden_rain` | atmosphärisch | selten und klar anderer Natur-/Umwelttyp | ein späterer kausaler Nachhall wäre ohne künstliche Wetter- oder Ortskontinuität schwach | **nicht wählen** |

## Entscheidung

**Story 003 wird in diesem Audit bewusst noch nicht freigegeben.**

Keiner der geprüften Kandidaten erfüllt aktuell gleichzeitig Tonvielfalt, Seltenheit, starke Kausalität und die bestehende No-Persistence-Grenze. Eine dritte Geschichte nur zur Erhöhung der Stückzahl würde die bisherige Qualität schwächen oder versteckte Weltpersistenz behaupten, die technisch nicht existiert.

Der stärkste Reservekandidat bleibt `street.construction_detour`, weil er selten genug und tonal räumlicher ist. Vor einer späteren Umsetzung braucht er jedoch zuerst eine konkrete Storyidee, deren Folge ohne gespeicherten Ort, Baustellenzustand oder NPC eindeutig verständlich bleibt.

## Verbindliche Grenzen

- keine `micro_story_003` in diesem Audit
- keine Änderung an `STREET_ENCOUNTER_MANIFEST.json`
- keine neue Runtime-, Journal-, Save-, Projection- oder Browserlogik
- keine NPC-, Location-, Objekt- oder Map-Persistenz
- keine Balancewirkung
- derselbe `street.followup_resolved`-Contract bleibt die einzige spätere Street-Kettenarchitektur
- Texte bleiben außerhalb der Spiellogik

## Qualitätswirkung

Der Audit verhindert eine formelhafte dritte Geschichte und macht die Story-Diversity-Grenze explizit prüfbar. Dadurch bleibt die seltene Micro-Story-Funktion ein Qualitätsmerkmal statt ein Content-Zähler.

## Spätere Erweiterungsidee

Ein späterer Kandidaten-Audit darf gezielt nach **nicht-persistenten räumlichen Folgen** suchen: Spuren, Geräusche, temporäre Hinweise oder kollektive Stadtreaktionen, deren Zusammenhang im Text verständlich ist, ohne denselben Ort technisch speichern zu müssen.