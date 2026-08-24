# Street-Grenzwerte – Laienhilfe

## Was wurde geprüft?

Straßenbegegnungen dürfen Energie und Stress verändern. Diese Werte sind im Spiel auf **0 bis 100** begrenzt.

Der Grenzwert-Audit prüft deshalb ausdrücklich beide kritischen Richtungen:

- positive Effekte dürfen Energie nicht über 100 und Stress nicht unter 0 drücken,
- negative Effekte dürfen Energie nicht unter 0 und Stress nicht über 100 drücken.

## Was bedeutet das im Spiel?

Wenn eine Begegnung theoretisch `+10 Energie` gibt, du aber schon 99 Energie hast, werden tatsächlich nur `+1` angewendet. Dasselbe gilt umgekehrt bei negativen Effekten. Die Rückmeldung und der gespeicherte Charakterzustand müssen dabei denselben tatsächlich angewendeten Wert zeigen.

## Was wurde bewusst nicht geändert?

- keine Begegnungswahrscheinlichkeiten,
- keine Energie-/Stresswerte im Katalog,
- keine neue Street-Engine,
- keine neue Speicherlogik,
- keine Balanceänderung.

Der Audit ist reine Qualitätssicherung: vorhandenes Verhalten wird an den Grenzwerten regressionsgesichert.

## Spätere sinnvolle Erweiterung

Ein späterer Audit kann zusätzlich alle realen Begegnungen automatisiert über mehrere Startzustände laufen lassen und daraus eine kompakte Grenzwert-Matrix erzeugen. Das wäre besonders hilfreich, falls der Street-Katalog deutlich größer wird.
