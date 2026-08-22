# A4-Personalisierung 0.8.5-B – einfache Anleitung

## Was du jetzt ändern kannst

Nach dem ersten Spielstart erscheint im A4-Client der Bereich **DEIN PROFIL**.

Dort kannst du jederzeit diese sichtbaren Angaben ändern:

- **Anzeigename** – der normale sichtbare Name deiner Figur/Crew
- **Alias** – ein kurzer Künstler-, Szene- oder Crewname
- **Spitznamen** – mehrere Namen, mit Komma getrennt
- **Motto** – ein kurzer persönlicher Satz

Beispiel:

```text
Anzeigename: Pppoppi
Alias: Pegelpilot
Spitznamen: Kabelkönig, Betonkind
Motto: Bass bleibt an
```

Danach auf **PROFIL SPEICHERN** klicken.

## Was absichtlich nicht editierbar ist

Die angezeigte **Technische ID** bleibt unverändert.

Das ist wichtig: Namen dürfen persönlich und frei veränderbar sein, die technische Identität des gespeicherten Characters darf sich dabei aber nicht verschieben. Save, Journal und spätere Rankings referenzieren deshalb weiterhin die stabile Character-ID und nicht den sichtbaren Namen.

## Was beim Speichern passiert

Der Browser verändert den Spielstand nicht direkt.

```text
Profilformular
   ↓
profile.update
   ↓
A4 GameClientSession
   ↓
CharacterProfileService
   ↓
character.profile_updated
   ↓
append-only Journal + bestätigter State
```

Damit gelten für Profiländerungen dieselben Persistenzregeln wie für die schon vorhandene Character-Forge-Profilbearbeitung.

## Wenn etwas nicht angenommen wird

Ein leerer Anzeigename oder ein fachlich ungültiger Wert wird von der Runtime abgewiesen. In diesem Fall bleibt der zuvor bestätigte Zustand erhalten und der Fehler erscheint im Client-Protokoll.

## Neustart / Recovery

Gespeicherte Profiländerungen werden über `character.profile_updated` replayt. Nach Neustart oder Recovery erscheinen deshalb wieder die bestätigten personalisierten Werte.

## Technische Grenze

0.8.5-B ergänzt **keine zweite Profil-Engine** und keine neue Identitätsart. Es wird ausschließlich der bereits vorhandene `CharacterProfileService` in den lokalen A4-Client eingebunden.
