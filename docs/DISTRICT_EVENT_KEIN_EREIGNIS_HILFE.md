# District-Events: Wenn diesmal nichts passiert

## Kurz erklärt

Nach einem bestätigten Settlement prüft BUNKERFREQUENZ, ob im betroffenen Bezirk ein katalogisiertes Welt-Ereignis zulässig ist.

Es kann korrekt sein, dass **kein** Ereignis passt. Das ist kein kaputter Spielstand und kein Fehler.

## Was passiert dann?

- Das Settlement bleibt bestätigt.
- Der Bezirk wird durch diesen Ereignis-Schritt nicht verändert.
- Es wird kein künstliches Ersatz-Ereignis erfunden.
- Es wird kein Journal-Eintrag für ein nicht stattgefundenes Ereignis geschrieben.
- Ein späterer bestätigter Trigger darf erneut anhand des dann gültigen Zustands prüfen.

Technisch wird dieser Fall als `no_eligible_event` gemeldet. Er ist ein sicherer No-op: lesen und entscheiden, aber nichts schreiben.

## Warum ist das wichtig?

Ein Ereignissystem darf nicht erzwingen, dass immer irgendetwas passiert. Voraussetzungen wie Heat, Prestige, Polizeidruck oder Szeneaktivität können dazu führen, dass gerade keiner der vorhandenen Katalogeinträge passt. Das Spiel bleibt dann ehrlich bei „kein Ereignis“ statt einen Fehler oder eine erfundene Geschichte zu erzeugen.

## Für Spieler

Du musst nichts reparieren. Spiele normal weiter. Sobald ein späterer bestätigter Spielzustand zu einem katalogisierten Ereignis passt, kann wieder eines ausgelöst werden.

## Für Entwickler

Der No-op darf weder District-State noch Journal verändern. Neue Event-Pakete sollen deshalb niemals einen künstlichen Catch-all-Eintrag nur zur Fehlervermeidung benötigen.

### Spätere Verbesserung

Eine sinnvolle Folgeverbesserung ist eine kleine read-only Diagnose im Entwicklerbereich: Sie könnte anzeigen, **welche Voraussetzungen** aktuell alle District-Events ausschließen. Diese Diagnose darf keine zweite Auswahl- oder Regelengine enthalten, sondern muss dieselbe zentrale Katalogprüfung wiederverwenden.
