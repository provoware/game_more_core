# Laienhilfe – District-Event-Katalogfehler lesen

Diese Hilfe ist für Nutzer gedacht, die eigene District-Events prüfen oder einen Startfehler verstehen wollen.

## Was ist neu?

Wenn ein Eintrag in `manifests/DISTRICT_EVENT_MANIFEST.json` ungültig ist, nennt BUNKERFREQUENZ jetzt möglichst genau den betroffenen Eintrag und das Feld.

Beispiel:

`events[0](district.example).effects.heat liegt außerhalb des Vertrags [-5, 5]`

Das bedeutet:

1. `events[0]` ist der erste Ereigniseintrag in der Liste.
2. `district.example` ist seine eindeutige Event-ID.
3. `effects.heat` ist das fehlerhafte Feld.
4. `[-5, 5]` zeigt den erlaubten Wertebereich.

## Was soll ich tun?

Öffne `manifests/DISTRICT_EVENT_MANIFEST.json`, suche zuerst nach der genannten Event-ID und danach nach dem genannten Feld. Ändere nur diesen Wert passend zum Vertrag. Erfinde keine zusätzlichen Metriken; erlaubt sind ausschließlich die im District-State-Vertrag katalogisierten Metriken.

Bei `requirements` gilt dasselbe: Eine Meldung wie `requirements.minimum_xyz verweist auf unbekannte Metrik` bedeutet, dass `xyz` keine erlaubte District-Metrik ist.

## Wichtig

Die Prüfung verändert keinen Spielstand. Ein ungültiger Katalog wird bereits beim Initialisieren abgelehnt, bevor ein District-Event ausgelöst oder dauerhaft geschrieben werden kann.
