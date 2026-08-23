# C5 – Warum Bezirksereignisse jetzt Pausen haben

Bezirksereignisse sollen etwas Besonderes bleiben. Deshalb darf nach einem bestätigten Bezirksereignis nicht sofort das nächste folgen.

## Die einfache Regel

- Das erste zulässige Bezirksereignis kann normal auftreten.
- Danach müssen mindestens **24 Stunden bestätigte Spielweltzeit** vergangen sein.
- Maßgeblich ist die bereits bestätigte Startzeit des abgeschlossenen Events (`event.time_window.start_local`).
- Die Uhr des Computers entscheidet den Cooldown nicht.
- Reload oder Retry verkürzt die Pause nicht und würfelt kein neues Ereignis aus.
- Fehlt eine verlässliche bestätigte Spielzeit, wird sicherheitshalber kein neues Bezirksereignis erzeugt.

## Was der Spieler davon hat

Die Timeline wird nicht nach jedem Settlement mit einem weiteren Welt-Ereignis gefüllt. Einzelne Ereignisse bleiben seltener, verständlicher und erzählerisch gewichtiger.

## Was unverändert bleibt

Gewichte, Voraussetzungen und Effekte der vier vorhandenen Bezirksereignisse bleiben unverändert. Auch Journal, Recovery und die read-only Timeline erhalten keine zweite Datenquelle.
