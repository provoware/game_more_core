# BUNKERFREQUENZ 0.8.7-C3 – District-Events einfach erklärt

## Was ist neu?

Nach einer vollständig abgeschlossenen Event-Abrechnung kann jetzt genau **ein** passendes Bezirksereignis entstehen. Das Spiel nutzt dafür den bereits bestätigten Veranstaltungsort und den vorhandenen District-State.

## Was muss ich als Spieler tun?

Nichts zusätzlich. Du spielst den Event-Ablauf wie bisher bis zur Abrechnung. Erst wenn `settlement.complete` erfolgreich bestätigt wurde, darf die Runtime prüfen, ob für den betroffenen Bezirk ein katalogisiertes Ereignis ausgelöst wird.

## Was kann der Browser dabei bestimmen?

Gar nichts an den Folgen. Der Browser sendet weder District-Werte noch Effektstärken noch eine gewünschte Ereignis-ID. Auswahl und Auswirkungen kommen ausschließlich aus den vorhandenen Manifesten und Application-Services.

## Warum wiederholt ein Reload das Ereignis nicht?

Der Trigger wird aus der bereits bestätigten Settlement-Quelle abgeleitet. Dieselbe Abrechnung besitzt dadurch denselben stabilen Trigger. Ein Retry oder Reload kann das Ereignis weder neu würfeln noch doppelt anwenden.

## Was sehe ich davon aktuell?

C3 verbindet zuerst nur die sichere Spiellogik. Eine eigene Ereignis-Timeline im Control Deck folgt bewusst erst in C4. So bleibt die technische Änderung klein, testbar und rückverfolgbar.

## Wenn etwas schiefgeht

Die bestehenden Save-, Journal- und Recovery-Regeln bleiben unverändert. District-Folgen werden weiterhin als katalogisierte `world.district_effect_applied`-Records gespeichert und über den vorhandenen Recovery-Pfad rekonstruiert.
