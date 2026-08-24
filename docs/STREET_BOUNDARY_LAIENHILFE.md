# Street-Grenzwerte – Laienhilfe

## Was wurde geprüft?

Straßenbegegnungen dürfen Energie, Stress und Ruf verändern. Energie und Stress sind im Spiel auf **0 bis 100** begrenzt; neu erzeugte Street-Ergebnisse dürfen Ruf nicht unter **0** drücken.

Der Grenzwert-Audit prüft deshalb ausdrücklich die kritischen Richtungen:

- positive Effekte dürfen Energie nicht über 100 und Stress nicht unter 0 drücken,
- negative Effekte dürfen Energie nicht unter 0 und Stress nicht über 100 drücken,
- negative Rufeffekte dürfen bei neuen Street-Ergebnissen den kanonischen Ruf-Floor 0 nicht unterschreiten.

## Was bedeutet das im Spiel?

Wenn eine Begegnung theoretisch `+10 Energie` gibt, du aber schon 99 Energie hast, werden tatsächlich nur `+1` angewendet. Dasselbe gilt umgekehrt bei negativen Effekten. Beim Ruf gilt entsprechend: Hast du 2 Ruf und eine Begegnung würde `-10` geben, werden tatsächlich nur `-2` angewendet und der neue Ruf ist 0. Die Rückmeldung und der gespeicherte Charakterzustand müssen dabei denselben tatsächlich angewendeten Wert zeigen.

## Was wurde bewusst nicht geändert?

- keine Begegnungswahrscheinlichkeiten,
- keine Energie-/Stress-/Rufwerte im Katalog,
- keine neue Street-Engine,
- keine neue Speicherlogik,
- keine Balanceänderung.

Der Audit ist reine Qualitätssicherung: vorhandenes Verhalten wird an den Grenzwerten regressionsgesichert.

## Spätere sinnvolle Erweiterung

Ein späterer Audit kann zusätzlich alle realen Begegnungen automatisiert über mehrere Startzustände laufen lassen und daraus eine kompakte Grenzwert-Matrix erzeugen. Das wäre besonders hilfreich, falls der Street-Katalog deutlich größer wird.
