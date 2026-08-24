# Street-Grenzwerte – Laienhilfe

## Was wurde geprüft?

Straßenbegegnungen dürfen Energie, Stress und Ruf verändern. Energie und Stress sind im Spiel auf **0 bis 100** begrenzt; neue Street-Ergebnisse dürfen Ruf nicht unter **0** drücken.

Der Grenzwert-Audit prüft deshalb ausdrücklich die kritischen Richtungen:

- positive Effekte dürfen Energie nicht über 100 und Stress nicht unter 0 drücken,
- negative Effekte dürfen Energie nicht unter 0 und Stress nicht über 100 drücken,
- negative Rufeffekte dürfen bei neuen Street-Ergebnissen den kanonischen Ruf-Floor 0 nicht unterschreiten,
- ein bereits bestätigtes Street-Ergebnis am Ruf-Floor darf bei einem Replay nicht noch einmal auf den Charakter angewendet werden.

## Was bedeutet das im Spiel?

Wenn eine Begegnung theoretisch `+10 Energie` gibt, du aber schon 99 Energie hast, werden tatsächlich nur `+1` angewendet. Dasselbe gilt umgekehrt bei negativen Effekten. Beim Ruf gilt entsprechend: Hast du 2 Ruf und eine Begegnung würde `-10` geben, werden tatsächlich nur `-2` angewendet und der neue Ruf ist 0.

Wird genau dieselbe bestätigte Begegnung später wegen Recovery oder Wiederholung erneut gelesen, bleibt der Ruf bei 0. Es entsteht kein zweiter Rufverlust, kein zweites Journal-Ergebnis und kein zusätzlicher Zustandswechsel. Der Replay liefert nur das bereits bestätigte Ergebnis zurück.

## Was wurde bewusst nicht geändert?

- keine Begegnungswahrscheinlichkeiten,
- keine Energie-/Stress-/Rufwerte im Katalog,
- keine neue Street-Engine,
- keine neue Speicherlogik,
- keine Balanceänderung.

Der Audit ist reine Qualitätssicherung: vorhandenes Verhalten wird an der Grenzkante und beim Replay regressionsgesichert.

## Spätere sinnvolle Erweiterungen

- **Katalog-Matrix:** Ein späterer Audit kann alle realen Begegnungen automatisiert über mehrere Startzustände laufen lassen und daraus eine kompakte Grenzwert-Matrix erzeugen. Das wird besonders nützlich, falls der Street-Katalog deutlich größer wird.
- **Replay-Grenzwert-Matrix:** Die gleiche Idempotenzprüfung kann später gesammelt für Energie-Minimum, Energie-Maximum, Stress-Minimum, Stress-Maximum und Ruf-Floor laufen. Nutzen: eine einzige Matrix schützt alle Klemmgrenzen gegen spätere Recovery-Regressionen. Grund: Der aktuelle Slice bleibt absichtlich auf die neu identifizierte Ruf-Floor-Kante begrenzt.
