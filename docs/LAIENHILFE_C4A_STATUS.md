# BUNKERFREQUENZ – C4A einfach erklärt

## Was ist bereits fertig?

C4A ist die **sichere Daten- und Textschicht** für die spätere Ereignis-Timeline. Sie liest nur bereits bestätigte Journal-Ereignisse und erzeugt daraus eine geordnete, rein lesende Liste.

Unterstützt werden derzeit:

- bestätigte Straßenbegegnungen,
- bestätigte gelöste Krisen,
- bestätigte District-Weltereignisse.

Die Reihenfolge kommt aus der Journal-`sequence`. Fehlende oder ungültige Texte werden nicht erfunden. Es werden höchstens die letzten 12 bestätigten Einträge projiziert.

## Was sieht der Spieler davon schon?

Noch **keine sichtbare Timeline im Control Deck**. Das ist absichtlich der nächste kleine Schritt C4B.

C4A bedeutet also: Die geprüfte Datenquelle ist vorhanden. C4B darf diese Daten nur noch anzeigen – nicht neu sortieren, nicht verändern und keine eigenen Spielereignisse erzeugen.

## Warum wurde der Projektstatus jetzt aktualisiert?

PR #98 wurde bereits mit den vorgesehenen Remote-Gates geprüft und über `/safe-merge` nach `main` übernommen. Der maschinenlesbare `PROJEKTSTATUS.json` stand danach noch auf C3. Diese Iteration korrigiert genau diese Abweichung und sichert sie mit einem Regressionstest ab.

## Was bleibt unverändert?

- Produkt-Release-Baseline bleibt `0.8.4-alpha.1`.
- Gameplaywerte bleiben unverändert.
- Journal und Save-System bleiben unverändert.
- Browser erhält keine neue Gameplay-Autorität.
- C4B bleibt der nächste sichtbare Ausbau.
